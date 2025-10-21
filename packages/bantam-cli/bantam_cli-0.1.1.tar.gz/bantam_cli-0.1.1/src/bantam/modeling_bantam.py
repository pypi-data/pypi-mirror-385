from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    if torch.cuda.is_available():
        torch.backends.cuda.enable_flash_sdp(True)
        torch.backends.cuda.enable_mem_efficient_sdp(True)
except (AttributeError, RuntimeError):
    pass

from transformers import PreTrainedModel, GenerationMixin
from transformers.modeling_outputs import BaseModelOutputWithPast, CausalLMOutputWithPast
from transformers.models.auto.configuration_auto import AutoConfig
from transformers.models.auto.modeling_auto import AutoModelForCausalLM

from .configuration_bantam import BantamConfig

class BantamRMSNorm(nn.Module):
    """Root-mean-square LayerNorm (no bias, no mean-centering). Stable in bf16."""
    def __init__(self, hidden_size: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        dtype = x.dtype
        x_float = x.float()
        var = x_float.pow(2).mean(-1, keepdim=True)
        x_norm = x_float * torch.rsqrt(var + self.eps)
        return (self.weight * x_norm).to(dtype)


class BantamSwiGLU(nn.Module):
    """
    Standard SwiGLU MLP:
      out = W3( SiLU(W1 x) ⊙ W2 x )
    Mark W3 as residual_out for scaled residual init.
    """
    def __init__(self, hidden_size: int, intermediate_size: int, bias: bool = True, dropout: float = 0.0):
        super().__init__()
        self.w1 = nn.Linear(hidden_size, intermediate_size, bias=bias)  # gate
        self.w2 = nn.Linear(hidden_size, intermediate_size, bias=bias)  # up
        self.w3 = nn.Linear(intermediate_size, hidden_size, bias=bias)  # down
        self.w3.is_residual_out = True
        self.dropout = nn.Dropout(dropout) if dropout and dropout > 0.0 else None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = F.silu(self.w1(x)) * self.w2(x)
        if self.dropout is not None:
            h = self.dropout(h)
        return self.w3(h)


class BantamRotaryEmbedding(nn.Module):
    """
    RoPE cache with optional scaling:
      - {"type": "linear",  "factor": f}
      - {"type": "dynamic", "factor": f, "original_max_position_embeddings": <int, optional>}
      - {"type": "yarn",    "factor": f, "attention_factor": <float, optional>}
    Notes:
      • "dynamic" matches the common NTK-aware scheme by changing the effective base.
      • "yarn" here applies position scaling like linear; pair it with attention_factor
        by setting config.attn_temperature ≈ attention_factor to complete YaRN.
    """
    def __init__(self, config: BantamConfig, device=None):
        super().__init__()
        self.dim = int(getattr(config, "max_head_dim", config.head_dim))
        self.base = float(config.rope_theta)
        self.max_position_embeddings = int(config.max_position_embeddings)
        self.scaling = config.rope_scaling or None

        inv = 1.0 / (self.base ** (torch.arange(0, self.dim, 2, dtype=torch.float32, device=device) / self.dim))
        self.register_buffer("inv_freq", inv, persistent=False)

        # cache
        self.max_seq_len_cached = 0
        self.register_buffer("cos_cached", torch.empty(0), persistent=False)
        self.register_buffer("sin_cached", torch.empty(0), persistent=False)

    def _apply_scaling(self, t: torch.Tensor, seq_len: int) -> torch.Tensor:
        if not self.scaling:
            return t

        typ = str(self.scaling.get("rope_type", self.scaling.get("type", "linear"))).lower()
        factor = float(self.scaling.get("factor", 1.0))

        if typ == "linear":
            return t / max(factor, 1e-6)

        if typ in ("dynamic", "dynamic_ntk", "ntk"):
            # NTK-aware (dynamic) scaling: change the effective base, emulate by scaling t.
            # new_base = base * ((factor * seq_len / orig_max) - (factor - 1)) ** (dim / (dim - 2))
            orig_max = int(self.scaling.get("original_max_position_embeddings", self.max_position_embeddings))
            # guard rails
            seq_len = max(seq_len, 1)
            num = (factor * float(seq_len) / float(orig_max)) - (factor - 1.0)
            num = max(num, 1e-6)
            exponent = float(self.dim) / max(float(self.dim - 2), 1.0)
            new_base = self.base * (num ** exponent)
            # since freqs = t ⊗ inv_freq(base), scaling t by base/new_base implements the new base
            return t * (self.base / new_base)

        if typ == "yarn":
            # Position scaling like linear; combine with attention_factor via attn_temperature.
            return t / max(factor, 1e-6)

        # unknown types -> identity
        return t

    def _set_cache(self, seq_len: int, device, dtype):
        self.max_seq_len_cached = seq_len
        t = torch.arange(seq_len, device=device, dtype=self.inv_freq.dtype)
        t = self._apply_scaling(t, seq_len)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)  # (seq, dim/2)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos().to(dtype), persistent=False)
        self.register_buffer("sin_cached", emb.sin().to(dtype), persistent=False)

    def forward(self, want_dtype: torch.dtype, device: torch.device, needed_seq_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
        need = max(needed_seq_len, int(getattr(self, "max_seq_len_cached", 0)))
        if (need > self.max_seq_len_cached) or (self.cos_cached.dtype != want_dtype) or (self.cos_cached.device != device):
            self._set_cache(need, device, want_dtype)
        return self.cos_cached[:need], self.sin_cached[:need]


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


def apply_rope(
    q: torch.Tensor, k: torch.Tensor,
    cos: torch.Tensor, sin: torch.Tensor,
    position_ids: torch.Tensor,
    rotary_dim: Optional[int] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    RoPE that accepts packed position_ids (e.g., (B,P,Q), (B,Q,P), (B,1,Q))
    and normalizes them to (B,Q) before indexing the cos/sin caches.
    """
    B, H, Q, D = q.shape

    # --- normalize position_ids to (B, Q) ---
    if position_ids is None:
        raise ValueError("position_ids must be provided")

    if position_ids.dim() == 1:
        # (Q,) -> (B,Q)
        position_ids = position_ids.unsqueeze(0).expand(B, Q)
    elif position_ids.dim() == 2:
        # (B,Q) already fine
        pass
    elif position_ids.dim() == 3:
        # common packed shapes
        if position_ids.size(-1) == Q:          # (B,P,Q) or (B,1,Q)
            position_ids = position_ids.amax(dim=1)   # -> (B,Q)
        elif position_ids.size(1) == Q:         # (B,Q,P) or (B,Q,1)
            position_ids = position_ids.amax(dim=-1)  # -> (B,Q)
        else:
            raise ValueError(f"Unsupported packed position_ids shape {tuple(position_ids.shape)}; "
                             f"expected last or second dim to be Q={Q}.")
    else:
        raise ValueError(f"Unsupported position_ids rank {position_ids.dim()} (expected 1–3).")

    # Index rotary caches and apply
    rotary_dim = int(rotary_dim or q.shape[-1])
    if rotary_dim > q.shape[-1] or rotary_dim > k.shape[-1]:
        raise ValueError(
            f"Rotary dimension {rotary_dim} exceeds head dims "
            f"(q={q.shape[-1]}, k={k.shape[-1]})"
        )
    cos = cos[position_ids].unsqueeze(1).to(q.dtype)[..., :rotary_dim]  # (B,1,Q,D_rot)
    sin = sin[position_ids].unsqueeze(1).to(q.dtype)[..., :rotary_dim]
    q_slice = q[..., :rotary_dim]
    k_slice = k[..., :rotary_dim]
    q_rot = (q_slice * cos) + (rotate_half(q_slice) * sin)
    k_rot = (k_slice * cos) + (rotate_half(k_slice) * sin)
    if rotary_dim == q.shape[-1]:
        return q_rot, k_rot
    # concatenate untouched tail if rotary dim < head dim
    return torch.cat([q_rot, q[..., rotary_dim:]], dim=-1), torch.cat([k_rot, k[..., rotary_dim:]], dim=-1)



class BantamKVCache:
    def __init__(self):
        self.key: List[Optional[torch.Tensor]] = []
        self.value: List[Optional[torch.Tensor]] = []
        self.lengths: List[int] = []

    def _ensure_layer(self, layer_idx: int) -> None:
        while len(self.key) <= layer_idx:
            self.key.append(None)
            self.value.append(None)
            self.lengths.append(0)

    def update(self, k, v, layer_idx, max_len=None, cache_kwargs=None):
        cache_kwargs = cache_kwargs or {}
        self._ensure_layer(layer_idx)

        cap_hint = cache_kwargs.get("max_len") or cache_kwargs.get("max_cache_len")
        if cap_hint is None and max_len is not None:
            cap_hint = max_len
        if isinstance(cap_hint, torch.Tensor):
            cap_hint = int(cap_hint.max().item())
        if cap_hint is not None:
            cap_hint = int(cap_hint)

        if isinstance(k, (list, tuple)):
            if not isinstance(v, (list, tuple)):
                raise TypeError("Values must match key grouping when updating KV cache.")
            k_list = list(k)
            v_list = list(v)
            return self._update_grouped(k_list, v_list, layer_idx, cap_hint)

        return self._update_dense(k, v, layer_idx, cap_hint)

    def enforce_window(self, layer_idx: int, max_len: Optional[int], num_sinks: int = 0):
        self._ensure_layer(layer_idx)
        tensor_k = self.key[layer_idx]
        tensor_v = self.value[layer_idx]
        if tensor_k is None:
            return None, None

        curr_len = self.lengths[layer_idx]

        if isinstance(tensor_k, list):
            if max_len is None or max_len <= 0 or curr_len <= max_len:
                trimmed_k = [tk[..., :curr_len, :] for tk in tensor_k]
                trimmed_v = [tv[..., :curr_len, :] for tv in tensor_v]
                return trimmed_k, trimmed_v

            new_k_list: List[torch.Tensor] = []
            new_v_list: List[torch.Tensor] = []
            new_len = 0
            for k_group, v_group in zip(tensor_k, tensor_v):
                k_trim, length = self._apply_window_slice(k_group, curr_len, max_len, num_sinks)
                v_trim, length_v = self._apply_window_slice(v_group, curr_len, max_len, num_sinks)
                if length != length_v:
                    raise ValueError("Key/value length mismatch when enforcing KV window.")
                new_k_list.append(k_trim)
                new_v_list.append(v_trim)
                new_len = length
            self.key[layer_idx] = new_k_list
            self.value[layer_idx] = new_v_list
            self.lengths[layer_idx] = new_len
            return new_k_list, new_v_list

        if max_len is None or max_len <= 0:
            return tensor_k[..., :curr_len, :], tensor_v[..., :curr_len, :]

        if curr_len <= max_len:
            return tensor_k[..., :curr_len, :], tensor_v[..., :curr_len, :]

        new_k, new_len = self._apply_window_slice(tensor_k, curr_len, max_len, num_sinks)
        new_v, new_len_v = self._apply_window_slice(tensor_v, curr_len, max_len, num_sinks)
        if new_len != new_len_v:
            raise ValueError("Key/value length mismatch when enforcing KV window.")

        self.key[layer_idx] = new_k
        self.value[layer_idx] = new_v
        self.lengths[layer_idx] = new_len
        return new_k, new_v

    def _init_storage(self, tensor: torch.Tensor, cap_hint: Optional[int]):
        new_len = tensor.shape[-2]
        capacity = max(new_len, cap_hint or new_len)
        head_dim = tensor.shape[-1]
        shape_prefix = tensor.shape[:-2]
        storage = torch.empty(shape_prefix + (capacity, head_dim), dtype=tensor.dtype, device=tensor.device)
        storage[..., :new_len, :] = tensor
        return storage, new_len

    def _append_storage(
        self,
        storage: torch.Tensor,
        tensor: torch.Tensor,
        curr_len: int,
        cap_hint: Optional[int],
    ):
        new_len = tensor.shape[-2]
        required = curr_len + new_len
        desired = max(required, cap_hint or required)
        if desired > storage.shape[-2]:
            new_capacity = max(storage.shape[-2] * 2, desired)
            shape_prefix = storage.shape[:-2]
            head_dim = storage.shape[-1]
            new_storage = torch.empty(shape_prefix + (new_capacity, head_dim), dtype=storage.dtype, device=storage.device)
            if curr_len > 0:
                new_storage[..., :curr_len, :] = storage[..., :curr_len, :]
            storage = new_storage
        storage[..., curr_len:required, :] = tensor
        return storage, required

    def _update_dense(self, k: torch.Tensor, v: torch.Tensor, layer_idx: int, cap_hint: Optional[int]):
        tensor_k = self.key[layer_idx]
        tensor_v = self.value[layer_idx]
        curr_len = self.lengths[layer_idx]

        if tensor_k is None or tensor_v is None:
            tensor_k, length = self._init_storage(k, cap_hint)
            tensor_v, length_v = self._init_storage(v, cap_hint)
            if length != length_v:
                raise ValueError("Key/value length mismatch during KV cache initialization.")
            self.key[layer_idx] = tensor_k
            self.value[layer_idx] = tensor_v
            self.lengths[layer_idx] = length
        else:
            if isinstance(tensor_k, list) or isinstance(tensor_v, list):
                raise TypeError("KV cache format mismatch: expected dense tensors for this layer.")
            tensor_k, length = self._append_storage(tensor_k, k, curr_len, cap_hint)
            tensor_v, length_v = self._append_storage(tensor_v, v, curr_len, cap_hint)
            if length != length_v:
                raise ValueError("Key/value length mismatch during KV cache append.")
            self.key[layer_idx] = tensor_k
            self.value[layer_idx] = tensor_v
            self.lengths[layer_idx] = length

        return tensor_k[..., : self.lengths[layer_idx], :], tensor_v[..., : self.lengths[layer_idx], :]

    def _update_grouped(
        self,
        k_list: List[torch.Tensor],
        v_list: List[torch.Tensor],
        layer_idx: int,
        cap_hint: Optional[int],
    ):
        if len(k_list) != len(v_list):
            raise ValueError("Grouped KV update requires matching number of key/value tensors.")
        if not k_list:
            return [], []

        base_len = k_list[0].shape[-2]
        for idx, tensor in enumerate(k_list[1:], start=1):
            if tensor.shape[-2] != base_len:
                raise ValueError(f"Grouped KV tensors must share sequence length; mismatch at group {idx}.")

        tensor_k = self.key[layer_idx]
        tensor_v = self.value[layer_idx]
        curr_len = self.lengths[layer_idx]

        if tensor_k is None or tensor_v is None:
            new_k_list: List[torch.Tensor] = []
            new_v_list: List[torch.Tensor] = []
            lengths = []
            for new_k, new_v in zip(k_list, v_list):
                storage_k, length = self._init_storage(new_k, cap_hint)
                storage_v, length_v = self._init_storage(new_v, cap_hint)
                if length != length_v:
                    raise ValueError("Grouped KV initialization produced mismatched key/value lengths.")
                new_k_list.append(storage_k)
                new_v_list.append(storage_v)
                lengths.append(length)
            if len(set(lengths)) != 1:
                raise ValueError("Grouped KV initialization requires uniform lengths across groups.")
            self.key[layer_idx] = new_k_list
            self.value[layer_idx] = new_v_list
            self.lengths[layer_idx] = lengths[0]
        else:
            if not isinstance(tensor_k, list) or not isinstance(tensor_v, list):
                raise TypeError("KV cache format mismatch: expected grouped tensors for this layer.")
            if len(tensor_k) != len(k_list):
                raise ValueError("Number of KV groups changed between updates.")
            lengths = []
            for idx, (storage_k, storage_v, new_k, new_v) in enumerate(zip(tensor_k, tensor_v, k_list, v_list)):
                updated_k, length = self._append_storage(storage_k, new_k, curr_len, cap_hint)
                updated_v, length_v = self._append_storage(storage_v, new_v, curr_len, cap_hint)
                if length != length_v:
                    raise ValueError(f"Key/value length mismatch in grouped KV cache for group {idx}.")
                tensor_k[idx] = updated_k
                tensor_v[idx] = updated_v
                lengths.append(length)
            if len(set(lengths)) != 1:
                raise ValueError("Grouped KV cache requires uniform sequence length across groups.")
            self.lengths[layer_idx] = lengths[0]

        trimmed_k = [tk[..., : self.lengths[layer_idx], :] for tk in self.key[layer_idx]]
        trimmed_v = [tv[..., : self.lengths[layer_idx], :] for tv in self.value[layer_idx]]
        return trimmed_k, trimmed_v

    def _apply_window_slice(
        self,
        tensor: torch.Tensor,
        curr_len: int,
        max_len: int,
        num_sinks: int,
    ):
        if max_len <= 0:
            return tensor[..., :0, :], 0
        sink_keep = min(num_sinks, curr_len)
        remaining = max(curr_len - sink_keep, 0)
        tail_len = min(max_len, remaining)
        start = curr_len - tail_len
        pieces = []
        if sink_keep > 0:
            pieces.append(tensor[..., :sink_keep, :])
        if tail_len > 0:
            pieces.append(tensor[..., start:curr_len, :])
        new_tensor = torch.cat(pieces, dim=-2) if pieces else tensor[..., :0, :]
        return new_tensor, new_tensor.shape[-2]

    def get_seq_length(self, layer_idx: int = 0) -> int:
        if layer_idx >= len(self.lengths):
            return 0
        return self.lengths[layer_idx]


@dataclass
class _HeadGroupSpec:
    query_heads: int
    kv_heads: int
    head_dim: int

    @property
    def q_dim(self) -> int:
        return self.query_heads * self.head_dim

    @property
    def kv_dim(self) -> int:
        return self.kv_heads * self.head_dim

    @property
    def repeat_factor(self) -> int:
        return self.query_heads // self.kv_heads


class BantamAttention(nn.Module):
    """Causal attention with GQA, sliding-window support, and attention sinks."""

    def __init__(self, config: BantamConfig, layer_idx: int):
        super().__init__()
        self.cfg = config
        self.layer_idx = layer_idx

        lc = self.cfg.layer_cfg(layer_idx)

        def _get(name, default):
            v = getattr(lc, name, None)
            return default if v is None else v

        target_heads = int(_get("num_attention_heads", int(config.num_attention_heads)))
        target_kv = int(_get("num_key_value_heads", int(config.num_key_value_heads)))
        attn_bias = bool(_get("attention_bias", bool(getattr(config, "attention_bias", False))))

        groups_cfg = getattr(lc, "attention_head_groups", None)
        self._use_grouped_heads = bool(groups_cfg)

        if groups_cfg:
            groups: List[_HeadGroupSpec] = []
            for idx, raw in enumerate(groups_cfg):
                if raw is None:
                    raise ValueError(f"Layer {layer_idx}: attention_head_groups[{idx}] is None")
                if not isinstance(raw, dict):
                    raise TypeError(
                        f"Layer {layer_idx}: attention_head_groups[{idx}] must be dict, got {type(raw)}"
                    )
                head_dim = raw.get("head_dim")
                if head_dim is None:
                    raise ValueError(f"Layer {layer_idx}: attention_head_groups[{idx}] missing 'head_dim'")
                query_heads = raw.get("query_heads", raw.get("num_query_heads"))
                if query_heads is None:
                    raise ValueError(
                        f"Layer {layer_idx}: attention_head_groups[{idx}] missing 'query_heads'/'num_query_heads'"
                    )
                kv_heads = raw.get("kv_heads", raw.get("num_kv_heads", 1))
                query_heads = int(query_heads)
                kv_heads = int(kv_heads)
                head_dim = int(head_dim)
                if query_heads <= 0 or kv_heads <= 0 or head_dim <= 0:
                    raise ValueError(
                        f"Layer {layer_idx}: attention_head_groups[{idx}] must have positive heads and head_dim"
                    )
                if query_heads % kv_heads != 0:
                    raise ValueError(
                        f"Layer {layer_idx}: attention_head_groups[{idx}] requires query_heads ({query_heads}) "
                        f"to be divisible by kv_heads ({kv_heads})"
                    )
                groups.append(_HeadGroupSpec(query_heads=query_heads, kv_heads=kv_heads, head_dim=head_dim))

            total_heads = sum(g.query_heads for g in groups)
            total_kv = sum(g.kv_heads for g in groups)
            if total_heads != target_heads:
                raise ValueError(
                    f"Layer {layer_idx}: sum of query_heads in attention_head_groups ({total_heads}) "
                    f"does not match num_attention_heads ({target_heads})"
                )
            if total_kv != target_kv:
                raise ValueError(
                    f"Layer {layer_idx}: sum of kv_heads in attention_head_groups ({total_kv}) "
                    f"does not match num_key_value_heads ({target_kv})"
                )

            self.groups = groups
            self.num_heads = total_heads
            self.num_kv = total_kv
            self.total_q_dim = sum(g.q_dim for g in groups)
            self.total_kv_dim = sum(g.kv_dim for g in groups)
            self.head_dim = None
            self.num_groups = None
        else:
            self._use_grouped_heads = False
            self.num_heads = target_heads
            self.num_kv = target_kv
            if self.num_heads <= 0 or self.num_kv <= 0:
                raise ValueError("num_attention_heads and num_key_value_heads must be positive")
            derived_head_dim = int(config.hidden_size) // int(self.num_heads)
            cfg_head_dim = int(getattr(config, "head_dim", derived_head_dim))
            if int(config.hidden_size) != int(self.num_heads) * int(derived_head_dim):
                raise ValueError(
                    f"hidden_size ({config.hidden_size}) must equal num_heads ({self.num_heads}) "
                    f"* head_dim ({derived_head_dim}) when using uniform head dimensions."
                )
            if cfg_head_dim != derived_head_dim:
                raise ValueError(
                    f"Inconsistent head_dim: config.head_dim={cfg_head_dim} but derived hidden_size/num_heads => {derived_head_dim}."
                )
            self.head_dim = derived_head_dim
            assert self.num_heads % self.num_kv == 0, (
                f"num_heads ({self.num_heads}) must be divisible by num_key_value_heads ({self.num_kv})."
            )
            self.num_groups = self.num_heads // self.num_kv
            self.groups = [
                _HeadGroupSpec(query_heads=self.num_heads, kv_heads=self.num_kv, head_dim=self.head_dim)
            ]
            self.total_q_dim = self.num_heads * self.head_dim
            self.total_kv_dim = self.num_kv * self.head_dim

        self.q_proj = nn.Linear(config.hidden_size, self.total_q_dim, bias=attn_bias)
        self.k_proj = nn.Linear(config.hidden_size, self.total_kv_dim, bias=attn_bias)
        self.v_proj = nn.Linear(config.hidden_size, self.total_kv_dim, bias=attn_bias)
        self.o_proj = nn.Linear(self.total_q_dim, config.hidden_size, bias=attn_bias)
        self.o_proj.is_residual_out = True

        self.max_head_dim = int(getattr(config, "max_head_dim", max(g.head_dim for g in self.groups)))
        offset = 0
        group_meta = []
        for g in self.groups:
            group_meta.append((offset, offset + g.kv_heads, g.head_dim))
            offset += g.kv_heads
        self._kv_group_meta = group_meta

        if config.qk_norm:
            if self._use_grouped_heads:
                dims = sorted({g.head_dim for g in self.groups})
                self.q_norms = nn.ModuleDict(
                    {str(d): BantamRMSNorm(d, eps=config.qk_norm_eps) for d in dims}
                )
                self.k_norms = nn.ModuleDict(
                    {str(d): BantamRMSNorm(d, eps=config.qk_norm_eps) for d in dims}
                )
                self.q_norm = None
                self.k_norm = None
            else:
                self.q_norm = BantamRMSNorm(self.head_dim, eps=config.qk_norm_eps)
                self.k_norm = BantamRMSNorm(self.head_dim, eps=config.qk_norm_eps)
                self.q_norms = None
                self.k_norms = None
        else:
            self.q_norm = None
            self.k_norm = None
            self.q_norms = None
            self.k_norms = None

        self.num_sinks = int(_get("num_attention_sinks", int(getattr(config, "num_attention_sinks", 0))))
        self.sink_boost = float(_get("sink_boost", float(getattr(config, "sink_boost", 0.0))))

        self._window = _get("window", None)

    @property
    def window(self) -> Optional[int]:
        return self._window

    def _build_allowed_mask(
        self,
        kv_keep_mask: torch.Tensor,
        q_keep_mask: torch.Tensor,
        past_visible: torch.Tensor,
        window: Optional[int],
        prefix_len: int,
    ) -> torch.Tensor:
        B, K = kv_keep_mask.shape
        Q = q_keep_mask.shape[-1]
        device = kv_keep_mask.device

        kv_idx = torch.arange(K, device=device).view(1, 1, K)
        q_idx = torch.arange(Q, device=device).view(1, Q, 1)
        past = past_visible.view(B, 1, 1)

        valid = kv_keep_mask[:, None, :] & q_keep_mask[:, :, None]
        causal = kv_idx <= (q_idx + past)

        if window is not None:
            lower = torch.clamp(q_idx + past - (window - 1), min=0)
            causal = causal & (kv_idx >= lower)
        if prefix_len > 0:
            causal = causal | (kv_idx < prefix_len)

        return valid & causal

    def _manual_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        allowed: torch.Tensor,
        *,
        scale: float,
        sink_boost: float,
        prefix_len: int,
        cap: float,
        repeat_factor: int,
    ) -> torch.Tensor:
        B, H, Q, _ = q.shape
        K = k.shape[-2]
        device = q.device

        if repeat_factor > 1:
            k = k.repeat_interleave(repeat_factor, dim=1)
            v = v.repeat_interleave(repeat_factor, dim=1)

        scores = torch.matmul(q, k.transpose(-2, -1)) * scale
        min_val = torch.finfo(scores.dtype).min
        mask = allowed[:, None, :, :].to(scores.device)
        scores = scores.masked_fill(~mask, min_val)

        if sink_boost != 0.0 and prefix_len > 0:
            kv_idx = torch.arange(K, device=device).view(1, 1, 1, K)
            boost = (kv_idx < prefix_len).to(scores.dtype) * mask.to(scores.dtype)
            scores = scores + sink_boost * boost

        if cap > 0.0:
            scores = cap * torch.tanh(scores / cap)

        attn = torch.softmax(scores, dim=-1)
        return torch.matmul(attn, v)

    def _attention_core(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        allowed: torch.Tensor,
        *,
        scale: float,
        sink_boost: float,
        prefix_len: int,
        cap: float,
        repeat_factor: int,
    ) -> torch.Tensor:
        if cap > 0.0:
            return self._manual_attention(
                q, k, v, allowed, scale=scale, sink_boost=sink_boost, prefix_len=prefix_len, cap=cap, repeat_factor=repeat_factor
            )

        if repeat_factor > 1:
            k = k.repeat_interleave(repeat_factor, dim=1)
            v = v.repeat_interleave(repeat_factor, dim=1)

        B, _, Q, _ = q.shape
        K = k.shape[-2]
        min_val = torch.finfo(q.dtype).min
        attn_bias = torch.full((B, 1, Q, K), min_val, dtype=q.dtype, device=q.device)
        attn_bias = attn_bias.masked_fill(allowed[:, None, :, :], 0.0)

        if sink_boost != 0.0 and prefix_len > 0:
            kv_idx = torch.arange(K, device=q.device).view(1, 1, 1, K)
            boost_mask = (kv_idx < prefix_len).expand(B, 1, Q, K)
            boost_mask = boost_mask & allowed[:, None, :, :]
            attn_bias = attn_bias + sink_boost * boost_mask.to(attn_bias.dtype)

        return F.scaled_dot_product_attention(
            q,
            k,
            v,
            attn_mask=attn_bias,
            is_causal=False,
        )

    def _pack_cache_states(self, states: List[torch.Tensor]) -> torch.Tensor:
        if not states:
            raise ValueError("Cannot pack empty cache state list.")
        if len(states) != len(self._kv_group_meta):
            raise ValueError(
                f"Cache packing mismatch: expected {len(self._kv_group_meta)} groups, got {len(states)}."
            )
        base = states[0]
        B, _, seq_len, _ = base.shape
        packed = base.new_zeros((B, self.num_kv, seq_len, self.max_head_dim))
        for (start, end, head_dim), tensor in zip(self._kv_group_meta, states):
            expected_heads = end - start
            if tensor.shape[1] != expected_heads:
                raise ValueError(
                    f"Cache packing mismatch: expected {expected_heads} kv heads, got {tensor.shape[1]}."
                )
            if tensor.shape[-1] != head_dim:
                raise ValueError(
                    f"Cache packing mismatch: expected head dim {head_dim}, got {tensor.shape[-1]}."
                )
            packed[:, start:end, :, :head_dim] = tensor
        return packed

    def _unpack_cache_states(self, packed: torch.Tensor) -> List[torch.Tensor]:
        if packed is None:
            return [None] * len(self.groups)
        if packed.shape[1] != self.num_kv:
            raise ValueError(
                f"Cache unpack mismatch: expected {self.num_kv} kv heads, got {packed.shape[1]}."
            )
        slices = []
        for start, end, head_dim in self._kv_group_meta:
            chunk = packed[:, start:end, :, :head_dim].contiguous()
            slices.append(chunk)
        return slices

    def forward(
        self,
        x: torch.Tensor,
        position_ids: torch.Tensor,
        cos: torch.Tensor,
        sin: torch.Tensor,
        attention_mask: Optional[torch.Tensor],
        past: Optional[BantamKVCache],
        **hf_kwargs,
    ) -> torch.Tensor:
        B, Q, _ = x.shape
        device = x.device

        q_proj = self.q_proj(x)
        k_proj = self.k_proj(x)
        v_proj = self.v_proj(x)

        q_groups: List[torch.Tensor] = []
        k_groups: List[torch.Tensor] = []
        v_groups: List[torch.Tensor] = []
        q_offset = k_offset = v_offset = 0

        for group in self.groups:
            q_slice = q_proj[..., q_offset:q_offset + group.q_dim].contiguous()
            k_slice = k_proj[..., k_offset:k_offset + group.kv_dim].contiguous()
            v_slice = v_proj[..., v_offset:v_offset + group.kv_dim].contiguous()
            q_offset += group.q_dim
            k_offset += group.kv_dim
            v_offset += group.kv_dim

            q_tensor = q_slice.view(B, Q, group.query_heads, group.head_dim).transpose(1, 2)
            k_tensor = k_slice.view(B, Q, group.kv_heads, group.head_dim).transpose(1, 2)
            v_tensor = v_slice.view(B, Q, group.kv_heads, group.head_dim).transpose(1, 2)

            if self.q_norms is not None:
                key = str(group.head_dim)
                q_tensor = self.q_norms[key](q_tensor)
                k_tensor = self.k_norms[key](k_tensor)
            elif self.q_norm is not None and self.k_norm is not None:
                q_tensor = self.q_norm(q_tensor)
                k_tensor = self.k_norm(k_tensor)

            q_tensor, k_tensor = apply_rope(
                q_tensor, k_tensor, cos, sin, position_ids, rotary_dim=group.head_dim
            )

            q_groups.append(q_tensor)
            k_groups.append(k_tensor)
            v_groups.append(v_tensor)

        effective_sw = int(self.window) if (self.window is not None) else None
        cache_position = hf_kwargs.get("cache_position", None)

        if past is not None:
            max_len = (effective_sw + Q) if (effective_sw is not None) else None
            cache_kwargs = {}
            if cache_position is not None:
                cache_kwargs["cache_position"] = cache_position
            if max_len is not None:
                cache_kwargs["max_len"] = max_len
                cache_kwargs.setdefault("max_cache_len", max_len)
            update_kwargs = {"cache_kwargs": cache_kwargs}
            if isinstance(past, BantamKVCache):
                update_kwargs["max_len"] = max_len
            if isinstance(past, BantamKVCache):
                k_updated, v_updated = past.update(k_groups, v_groups, self.layer_idx, **update_kwargs)
                k_groups = list(k_updated) if isinstance(k_updated, (list, tuple)) else [k_updated]
                v_groups = list(v_updated) if isinstance(v_updated, (list, tuple)) else [v_updated]
                if max_len is not None:
                    k_trim, v_trim = past.enforce_window(self.layer_idx, max_len, self.num_sinks)
                    if k_trim is not None:
                        k_groups = list(k_trim) if isinstance(k_trim, (list, tuple)) else [k_trim]
                        v_groups = list(v_trim) if isinstance(v_trim, (list, tuple)) else [v_trim]
            else:
                packed_k = self._pack_cache_states(k_groups)
                packed_v = self._pack_cache_states(v_groups)
                packed_k, packed_v = past.update(packed_k, packed_v, self.layer_idx, **update_kwargs)
                k_groups = self._unpack_cache_states(packed_k)
                v_groups = self._unpack_cache_states(packed_v)

        if not k_groups:
            raise ValueError("Attention requires at least one head group after cache processing.")
        if len(k_groups) != len(self.groups):
            raise ValueError(
                f"KV cache returned {len(k_groups)} groups but attention expects {len(self.groups)}."
            )

        K = k_groups[0].shape[-2]
        for kg in k_groups[1:]:
            if kg.shape[-2] != K:
                raise ValueError("All head groups must share the same sequence length for attention.")

        if isinstance(attention_mask, dict):
            attention_mask = (
                attention_mask["sliding_attention"] if (self.window is not None) else attention_mask["full_attention"]
            )

        kv_keep_mask: Optional[torch.Tensor] = None
        q_keep_mask: Optional[torch.Tensor] = None

        if attention_mask is not None:
            attention_mask = attention_mask.to(device)
            if attention_mask.dim() == 2:
                if past is not None and self.num_sinks > 0 and K < attention_mask.shape[-1]:
                    tail = max(K - self.num_sinks, 0)
                    layer_keep = (
                        torch.cat([attention_mask[:, :self.num_sinks], attention_mask[:, -tail:]], dim=-1)
                        if tail > 0
                        else attention_mask[:, :self.num_sinks]
                    )
                else:
                    layer_keep = attention_mask[:, -K:]
                layer_keep = layer_keep.to(torch.bool)
                kv_keep_mask = layer_keep
                q_keep_mask = layer_keep[:, -Q:]
            else:
                raise ValueError(f"Unsupported attention_mask shape {tuple(attention_mask.shape)}")

        if kv_keep_mask is None:
            kv_keep_mask = torch.ones((B, K), dtype=torch.bool, device=device)
        else:
            kv_keep_mask = kv_keep_mask.to(device=device, dtype=torch.bool)

        if q_keep_mask is None:
            q_keep_mask = torch.ones((B, Q), dtype=torch.bool, device=device)
        else:
            q_keep_mask = q_keep_mask.to(device=device, dtype=torch.bool)

        kv_lengths = kv_keep_mask.sum(dim=-1)
        q_lengths = q_keep_mask.sum(dim=-1)
        past_visible = (kv_lengths - q_lengths).clamp_min(0)

        keep_prefix = self.num_sinks if past is not None else 0
        prefix_len = min(keep_prefix, K)

        allowed = self._build_allowed_mask(kv_keep_mask, q_keep_mask, past_visible, effective_sw, prefix_len)

        tau = float(getattr(self.cfg, "attn_temperature", 1.0))
        cap = float(getattr(self.cfg, "attn_logit_softcapping", 0.0))
        sink_boost = self.sink_boost if (prefix_len > 0 and self.sink_boost != 0.0) else 0.0
        drop = self.cfg.attention_dropout if self.training else 0.0

        attn_chunks: List[torch.Tensor] = []
        for idx, group in enumerate(self.groups):
            q_g = q_groups[idx]
            k_g = k_groups[idx]
            v_g = v_groups[idx]
            scale = 1.0 / (math.sqrt(group.head_dim) * tau)
            ctx = self._attention_core(
                q_g,
                k_g,
                v_g,
                allowed,
                scale=scale,
                sink_boost=sink_boost,
                prefix_len=prefix_len,
                cap=cap,
                repeat_factor=group.repeat_factor,
            )
            if drop and drop > 0.0:
                ctx = F.dropout(ctx, p=drop, training=True)
            attn_chunks.append(ctx.transpose(1, 2).contiguous().view(B, Q, group.q_dim))

        y = torch.cat(attn_chunks, dim=-1)

        if self.cfg.residual_dropout and self.training:
            y = F.dropout(y, p=self.cfg.residual_dropout, training=True)

        return self.o_proj(y)


class BantamMoEBlock(nn.Module):
    def __init__(
        self,
        hidden_size: int,
        expert_ffn_size: int,
        *,
        num_experts: int,
        router_type: str = "switch",
        top_k: int = 1,
        capacity_factor: float = 1.0,
        router_jitter: float = 0.0,
        drop_policy: str = "first",
        aux_loss_weight: float = 0.0,
        use_bias: bool = True,
        dropout: float = 0.0,
        router_z_loss_weight: float = 0.0,   # ← NEW
    ):
        super().__init__()
        assert num_experts >= 1, "num_experts must be >= 1"

        self.hidden_size = int(hidden_size)
        self.num_experts = int(num_experts)
        self.router_type = str(router_type).lower()
        self.top_k = int(top_k)
        self.capacity_factor = float(capacity_factor)
        self.router_jitter = float(router_jitter)
        self.drop_policy = str(drop_policy).lower()
        self.aux_loss_weight = float(aux_loss_weight)
        self.router_z_loss_weight = float(router_z_loss_weight)

        self.router = nn.Linear(hidden_size, num_experts, bias=True)
        self.experts = nn.ModuleList(
            [BantamSwiGLU(hidden_size, expert_ffn_size, bias=use_bias, dropout=dropout) for _ in range(num_experts)]
        )
        for e in self.experts:
            if hasattr(e.w3, "is_residual_out"):
                e.w3.is_residual_out = True

    def _balance_aux(self, probs: torch.Tensor, dispatched_counts: torch.Tensor) -> torch.Tensor:
        if self.aux_loss_weight <= 0.0:
            return probs.new_zeros(())
        S = max(1, probs.shape[0])
        importance = probs.sum(dim=0) / float(S)             # [E]
        load = dispatched_counts.to(probs.dtype) / float(S)  # [E]
        aux = (importance * load).sum() * float(self.num_experts)
        return aux * self.aux_loss_weight

    def _router_z_loss(self, logits: torch.Tensor) -> torch.Tensor:
        if self.router_z_loss_weight <= 0.0:
            return logits.new_zeros(())
        z = torch.logsumexp(logits.float(), dim=-1)  # [S]
        return (z ** 2).mean() * self.router_z_loss_weight

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        B, T, H = x.shape
        S = B * T
        X = x.reshape(S, H)

        # Router
        X_router = X.to(self.router.weight.dtype)
        logits = self.router(X_router)
        if self.router_jitter > 0.0 and self.training:
            logits = logits + torch.randn_like(logits) * self.router_jitter
        probs = F.softmax(logits.float(), dim=-1)  # [S,E]

        # Dense MoE
        if self.router_type in ("dense", "dense_moe"):
            outs = [self.experts[e](x) for e in range(self.num_experts)]  # [B,T,H] each
            Y = torch.stack(outs, dim=-2)  # [B,T,E,H]
            w = probs.view(B, T, self.num_experts, 1).to(Y.dtype)
            Y = (Y * w).sum(dim=-2)  # [B,T,H]
            aux = self._balance_aux(probs, dispatched_counts=probs.new_zeros(self.num_experts))
            aux = aux + self._router_z_loss(logits)
            return Y.to(x.dtype), aux.to(x.dtype)

        # Sparse MoE (switch / top-k)
        k = 1 if self.router_type == "switch" else max(1, self.top_k)
        topk_vals, topk_idx = torch.topk(probs, k, dim=-1)  # [S,k]
        topk_vals = topk_vals / (topk_vals.sum(dim=-1, keepdim=True) + 1e-9)

        capacity = int(math.ceil(self.capacity_factor * S / float(self.num_experts)))
        out = X_router.new_zeros(S, H)
        load_counts = torch.zeros(self.num_experts, device=X.device, dtype=torch.float32)

        perm = (
            torch.randperm(S, device=X.device)
            if (self.drop_policy == "random" and self.training)
            else torch.arange(S, device=X.device)
        )

        for j in range(k):
            e_idx = topk_idx[:, j]
            e_w = topk_vals[:, j]
            e_idx_p = e_idx[perm]

            for e in range(self.num_experts):
                mask_p = (e_idx_p == e)
                if not mask_p.any():
                    continue
                pos = torch.cumsum(mask_p.to(torch.int32), dim=0) - 1
                keep_p = mask_p & (pos < capacity)
                if not keep_p.any():
                    continue
                sel_p = keep_p.nonzero(as_tuple=False).squeeze(1)
                sel = perm[sel_p]
                y = self.experts[e](X_router[sel])     # [N,H]
                w = e_w[sel].unsqueeze(1).to(y.dtype)
                out[sel] = out[sel] + y * w
                load_counts[e] += float(sel.numel())

        aux = self._balance_aux(probs, load_counts) + self._router_z_loss(logits)
        return out.view(B, T, H).to(x.dtype), aux.to(x.dtype)
    

class DropPath(nn.Module):
    def __init__(self, p: float = 0.0):
        super().__init__()
        self.p = float(max(0.0, p))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.p == 0.0 or not self.training:
            return x
        keep = 1.0 - self.p
        # per-sample mask, broadcast over non-batch dims
        shape = (x.shape[0],) + (1,) * (x.dim() - 1)
        mask = x.new_empty(shape).bernoulli_(keep).div_(keep)
        return x * mask


class BantamDecoderLayer(nn.Module):
    def __init__(self, config: BantamConfig, layer_idx: int):
        super().__init__()
        self.cfg = config
        self.layer_idx = layer_idx
        self.attn = BantamAttention(config, layer_idx)

        lc = config.layer_cfg(layer_idx)
        ff_width = int(lc.intermediate_size)

        # MoE toggle
        etype = (lc.expert_type or "dense_mlp").lower()
        self.is_moe = etype in ("dense_moe", "switch", "topk", "sparse")

        if self.is_moe:
            num_experts = int(lc.num_experts or 0)
            assert num_experts > 0, f"Layer {layer_idx}: num_experts must be set for expert_type={etype}"
            expert_ffn_size = int(lc.moe_intermediate_size or ff_width)
            top_k = int(lc.moe_top_k or (1 if etype == "switch" else 2))
            cap = float(lc.moe_capacity_factor or 1.0)
            jitter = float(lc.moe_router_jitter or 0.0)
            drop_pol = str(lc.moe_drop_policy or "first")
            aux_w = float(lc.moe_aux_loss_weight or 0.0)
            zlw = float(getattr(lc, "moe_router_z_loss_weight", 0.0))  # optional

            self.ff = BantamMoEBlock(
                hidden_size=config.hidden_size,
                expert_ffn_size=expert_ffn_size,
                num_experts=num_experts,
                router_type=("topk" if etype == "sparse" else etype),
                top_k=top_k,
                capacity_factor=cap,
                router_jitter=jitter,
                drop_policy=drop_pol,
                aux_loss_weight=aux_w,
                use_bias=True if lc.moe_use_bias is None else bool(lc.moe_use_bias),
                dropout=config.mlp_dropout,
                router_z_loss_weight=zlw,
            )
        else:
            self.ff = BantamSwiGLU(config.hidden_size, ff_width, bias=True, dropout=config.mlp_dropout)

        self.input_norm = BantamRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_norm = BantamRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

        # Linear schedule: 0 → rate across depth
        rate = float(getattr(config, "stochastic_depth_rate", 0.0))
        p = rate * float(layer_idx + 1) / float(max(1, config.num_hidden_layers))
        self.drop_path = DropPath(p=p)

        self.gradient_checkpointing = False

    def _forward_impl(self, x, position_ids, cos, sin, attention_mask, past: Optional[BantamKVCache], **hf_kwargs):
        aux = x.new_zeros(())
        residual = x
        x = self.input_norm(x)
        x = self.attn(x, position_ids, cos, sin, attention_mask, past, **hf_kwargs)
        x = residual + self.drop_path(x)  # ← drop-path on attn branch

        residual = x
        x = self.post_norm(x)
        if self.is_moe:
            y, aux = self.ff(x)
        else:
            y = self.ff(x)
        return residual + self.drop_path(y), aux  # ← drop-path on MLP/MoE branch

    def forward(self, x, position_ids, cos, sin, attention_mask, past: Optional[BantamKVCache], **hf_kwargs):
        if self.training and self.gradient_checkpointing:
            def custom_forward(*inputs):
                return self._forward_impl(*inputs, **hf_kwargs)  # returns (out, aux)
            out, aux = torch.utils.checkpoint.checkpoint(
                custom_forward, x, position_ids, cos, sin, attention_mask, past, use_reentrant=False
            )
            return out, aux
        return self._forward_impl(x, position_ids, cos, sin, attention_mask, past, **hf_kwargs)


class BantamPreTrainedModel(PreTrainedModel):
    config_class = BantamConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["BantamDecoderLayer"]  # ✅ was ["DecoderLayer"]

    _supports_attention_backend = True
    _supports_sdpa = True
    _supports_flash_attn = True
    _supports_flash_attn_2 = True

    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
            if getattr(module, "is_residual_out", False):
                n = max(1, getattr(self.config, "num_hidden_layers", 1))
                module.weight.data.mul_(1.0 / math.sqrt(2 * n))
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)

class BantamModel(BantamPreTrainedModel):
    def __init__(self, config: BantamConfig):
        super().__init__(config)
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        self.layers = nn.ModuleList([BantamDecoderLayer(config, i) for i in range(config.num_hidden_layers)])
        self.norm = BantamRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary = BantamRotaryEmbedding(config)
        self.gradient_checkpointing = False
        self._embed_scale = math.sqrt(config.hidden_size) if getattr(config, "scaled_embeddings", False) else None
        self.post_init()

    def gradient_checkpointing_enable(self, gradient_checkpointing_kwargs: Optional[dict] = None):
        super().gradient_checkpointing_enable(gradient_checkpointing_kwargs)
        self.gradient_checkpointing = True
        for layer in self.layers:
            layer.gradient_checkpointing = True

    def gradient_checkpointing_disable(self):
        super().gradient_checkpointing_disable()
        self.gradient_checkpointing = False
        for layer in self.layers:
            layer.gradient_checkpointing = False

    def get_input_embeddings(self):
        return self.embed_tokens

    def set_input_embeddings(self, value):
        self.embed_tokens = value

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[BantamKVCache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,  
    ) -> BaseModelOutputWithPast:

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is None and inputs_embeds is None:
            raise ValueError("You must specify either input_ids or inputs_embeds")

        x = self.embed_tokens(input_ids) if inputs_embeds is None else inputs_embeds

        if self._embed_scale:
            x = x * self._embed_scale

        B, Q = x.shape[:2]
        device = x.device
        past_len = past_key_values.get_seq_length(0) if past_key_values is not None else 0

        # --------- position_ids: build only from a 2-D mask; otherwise let caller provide ----------
        if position_ids is None:
            if attention_mask is not None and attention_mask.dim() == 2:
                # standard (B,S) mask -> (B,Q) positions
                pos = attention_mask.long().cumsum(-1) - 1
                pos = pos.masked_fill(attention_mask == 0, 0)
                position_ids = pos[:, -Q:]
            else:
                # fallback: contiguous positions
                position_ids = torch.arange(past_len, past_len + Q, device=device).unsqueeze(0).expand(B, Q)

        # If a packed collator supplied (B,P,Q)/(B,Q,P)/(B,1,Q), normalize to (B,Q)
        if position_ids.dim() == 3:
            if position_ids.size(-1) == Q:
                position_ids = position_ids.amax(dim=1)     # (B,P,Q) -> (B,Q)
            elif position_ids.size(1) == Q:
                position_ids = position_ids.amax(dim=-1)    # (B,Q,P) -> (B,Q)
            elif position_ids.size(1) == 1:
                position_ids = position_ids.squeeze(1)      # (B,1,Q) -> (B,Q)
            else:
                raise ValueError(f"Unsupported packed position_ids shape {tuple(position_ids.shape)}")
        elif position_ids.dim() == 1:
            position_ids = position_ids.unsqueeze(0).expand(B, Q)
        elif position_ids.dim() != 2:
            raise ValueError(f"position_ids must be (B,Q); got rank {position_ids.dim()}")

        max_allowed = (past_len + Q) - 1
        if max_allowed >= 0:
            pos_max = position_ids.max(dim=-1, keepdim=True).values
            overflow = (pos_max - max_allowed).clamp_min(0)
            if overflow.max() > 0:
                position_ids = (position_ids - overflow).clamp_min_(0)

        # Rotary cache for prompt+cache length
        need = past_len + Q
        cos, sin = self.rotary(x.dtype, device, need)

        hidden_states = x
        all_hidden_states = [] if output_hidden_states else None
        moe_aux_total = x.new_zeros(())

        for i, layer in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states.append(hidden_states)
            hidden_states, aux = layer(
                hidden_states, position_ids, cos, sin, attention_mask, past_key_values, **kwargs
            )
            moe_aux_total = moe_aux_total + aux

        hidden_states = self.norm(hidden_states)
        if output_hidden_states:
            all_hidden_states.append(hidden_states)

        # stash for the LM head to consume
        self._moe_aux_loss = moe_aux_total

        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=past_key_values,
            hidden_states=tuple(all_hidden_states) if output_hidden_states else None,
            attentions=None if not (output_attentions) else None,
        )


class BantamForCausalLM(BantamPreTrainedModel, GenerationMixin):
    main_input_name = "input_ids"
    _tied_weights_keys = ["lm_head.weight"]

    def __init__(self, config: BantamConfig):
        super().__init__(config)
        self.model = BantamModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()

    # Embedding / head passthroughs
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, new_embeds): self.model.embed_tokens = new_embeds
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings

    # --------------------- Core forward (pure LM) ---------------------
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[BantamKVCache] = None,
        labels: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ) -> CausalLMOutputWithPast:
        use_cache = bool(use_cache if use_cache is not None else (self.config.use_cache if self.training is False else False))
        cache = past_key_values if use_cache else None
        if use_cache and cache is None:
            cache = BantamKVCache()

        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=cache,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            # Only compute hidden states when the caller explicitly asks for them
            output_hidden_states=bool(output_hidden_states),
            return_dict=True,
        )
        hidden = outputs.last_hidden_state
        logits = self.lm_head(hidden)

        # NEW: optional final logit softcapping
        cap = float(getattr(self.config, "final_logit_softcapping", 0.0))
        if cap > 0.0:
            logits = torch.tanh(logits / cap) * cap

        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            ce = F.cross_entropy(
                shift_logits.view(-1, self.config.vocab_size),
                shift_labels.view(-1),
                ignore_index=-100,
                label_smoothing=float(self.config.label_smoothing) if getattr(self.config, "label_smoothing", 0.0) else 0.0,
            )
            loss = ce
            moe_aux = getattr(self.model, "_moe_aux_loss", None)
            if moe_aux is not None:
                loss = loss + moe_aux
            z_w = float(getattr(self.config, "z_loss_weight", 0.0))
            if z_w > 0.0:
                with torch.no_grad():
                    mask = (shift_labels.view(-1) != -100)
                if mask.any():
                    z = torch.logsumexp(shift_logits.view(-1, shift_logits.size(-1))[mask], dim=-1)
                    z_loss = (z ** 2).mean()
                    loss = loss + z_w * z_loss

        return CausalLMOutputWithPast(
            loss=loss, logits=logits, past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states if output_hidden_states else None,
            attentions=None,
        )

    # ----------------- HF generation IO -----------------
    def _reorder_cache(self, past_key_values: BantamKVCache, beam_idx: torch.LongTensor) -> BantamKVCache:
        if past_key_values is None: return None
        for i in range(len(past_key_values.key)):
            entry_k = past_key_values.key[i]
            entry_v = past_key_values.value[i]
            if entry_k is None:
                continue
            if isinstance(entry_k, list):
                past_key_values.key[i] = [k.index_select(0, beam_idx) for k in entry_k]
                past_key_values.value[i] = [v.index_select(0, beam_idx) for v in entry_v]
            else:
                past_key_values.key[i] = entry_k.index_select(0, beam_idx)
                past_key_values.value[i] = entry_v.index_select(0, beam_idx)
        return past_key_values

    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, **kwargs):
        if attention_mask is None:
            attention_mask = input_ids.new_ones(input_ids.shape, dtype=torch.long)
        if past_key_values is not None:
            input_ids = input_ids[:, -1:]
            attention_mask = torch.cat([attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1)
            position_ids = attention_mask.long().sum(dim=1, keepdim=True) - 1
            position_ids = position_ids.to(input_ids.device)
        else:
            position_ids = None
        return dict(
            input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids,
            past_key_values=past_key_values, use_cache=kwargs.get("use_cache", True),
        )

# Register with Auto Classes
AutoConfig.register("bantam", BantamConfig)
AutoModelForCausalLM.register(BantamConfig, BantamForCausalLM)
