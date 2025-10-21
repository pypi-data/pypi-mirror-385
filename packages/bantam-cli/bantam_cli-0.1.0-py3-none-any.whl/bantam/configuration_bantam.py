from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from types import SimpleNamespace
from transformers import PretrainedConfig


@dataclass
class LayerConfigSpec:
    """
    Per-layer overrides. Any field left as None falls back to the global default.
    """
    num_attention_heads: Optional[int] = None
    num_key_value_heads: Optional[int] = None
    intermediate_size: Optional[int] = None
    window: Optional[int] = None
    attention_bias: Optional[bool] = None
    num_attention_sinks: Optional[int] = None
    sink_boost: Optional[float] = None
    attention_head_groups: Optional[List[Dict[str, Any]]] = None

    # ------------------ MoE: per-layer controls ------------------
    expert_type: Optional[str] = None
    num_experts: Optional[int] = None
    moe_top_k: Optional[int] = None
    moe_capacity_factor: Optional[float] = None
    moe_router_jitter: Optional[float] = None
    moe_drop_policy: Optional[str] = None
    moe_aux_loss_weight: Optional[float] = None
    moe_intermediate_size: Optional[int] = None
    moe_use_bias: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LayerConfigSpec":
        return cls(**d)


@dataclass
class BantamConfig(PretrainedConfig):
    model_type: str = "bantam"

    def __init__(
        self,
        # Core LM shape
        hidden_size: int = 2048,
        intermediate_size: int = 5632,
        num_hidden_layers: int = 24,
        num_attention_heads: int = 32,
        num_key_value_heads: int = 8,
        vocab_size: int = 32000,
        max_position_embeddings: int = 4096,
        head_dim: Optional[int] = None,
        attention_head_groups: Optional[List[Dict[str, Any]]] = None,
        rms_norm_eps: float = 1e-6,

        # RoPE
        rope_theta: float = 10000.0,
        rope_scaling: Optional[Dict[str, Any]] = None,

        # Attention
        attention_bias: bool = False,
        attention_dropout: float = 0.0,
        initializer_range: float = 0.02,

        # Tokens
        pad_token_id: int = 0,
        bos_token_id: int = 1,
        eos_token_id: int = 2,
        tie_word_embeddings: bool = True,

        # Attention sinks
        num_attention_sinks: int = 0,
        sink_boost: float = 0.0,

        # Impl & regularization
        qk_norm: bool = False,
        qk_norm_eps: float = 1e-6,
        mlp_dropout: float = 0.0,
        residual_dropout: float = 0.0,

        # Loss shaping
        label_smoothing: float = 0.0,
        z_loss_weight: float = 0.0,

        # Generation cache default
        use_cache: bool = False,

        # NEW stability / scaling features
        scaled_embeddings: bool = False,
        attn_logit_softcapping: float = 0.0,
        final_logit_softcapping: float = 0.0,

        # Per-layer overrides
        layer_configs: Optional[List[Dict[str, Any]]] = None,

        **kwargs,
    ):

        for legacy_key in [
            "attn_impl",
            "attn_implementation",
            "requested_attn_impl",
            "use_flex_attention",
            "block_mask_cache_cap",
            "block_mask_cache_device",
        ]:
            kwargs.pop(legacy_key, None)

        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )

        # Core LM
        self.vocab_size = int(vocab_size)
        self.hidden_size = int(hidden_size)
        self.intermediate_size = int(intermediate_size)
        self.num_hidden_layers = int(num_hidden_layers)
        self.num_attention_heads = int(num_attention_heads)
        self.num_key_value_heads = int(num_key_value_heads)
        self.max_position_embeddings = int(max_position_embeddings)
        self.head_dim = int(head_dim) if head_dim is not None else (self.hidden_size // self.num_attention_heads)
        self.attention_head_groups = (
            None if attention_head_groups is None else [dict(group) for group in attention_head_groups]
        )
        self.rms_norm_eps = float(rms_norm_eps)

        # RoPE
        self.rope_theta = float(rope_theta)
        self.rope_scaling = rope_scaling

        # Attention
        self.attention_bias = bool(attention_bias)
        self.attention_dropout = float(attention_dropout)
        self.initializer_range = float(initializer_range)

        # Attention sinks
        self.num_attention_sinks = int(num_attention_sinks)
        self.sink_boost = float(sink_boost)

        # Impl & regularization
        self.qk_norm = bool(qk_norm)
        self.qk_norm_eps = float(qk_norm_eps)
        self.mlp_dropout = float(mlp_dropout)
        self.residual_dropout = float(residual_dropout)

        # Loss shaping
        self.label_smoothing = float(label_smoothing)
        self.z_loss_weight = float(z_loss_weight)

        # Cache
        self.use_cache = bool(use_cache)

        # NEW: stability/scaling toggles
        self.scaled_embeddings = bool(scaled_embeddings)
        self.attn_logit_softcapping = float(attn_logit_softcapping)
        self.final_logit_softcapping = float(final_logit_softcapping)
        # Block-mask cache hints (used by BantamAttention)

        # ---------------------- Per-layer normalization ----------------------
        allowed_keys = set(k for k in LayerConfigSpec().__dict__.keys())
        norm: List[Dict[str, Any]] = []
        if layer_configs is None:
            norm = [dict() for _ in range(self.num_hidden_layers)]
        else:
            for i, item in enumerate(layer_configs[: self.num_hidden_layers]):
                if isinstance(item, LayerConfigSpec):
                    d = item.to_dict()
                elif isinstance(item, dict):
                    d = {k: v for k, v in item.items() if k in allowed_keys and v is not None}
                else:
                    raise TypeError(f"layer_configs[{i}] must be dict or LayerConfigSpec, got {type(item)}")
                norm.append(d)
            if len(norm) < self.num_hidden_layers:
                norm.extend([dict() for _ in range(self.num_hidden_layers - len(norm))])
        self.layer_configs: List[Dict[str, Any]] = norm

        def _max_group_dim(groups: Optional[List[Dict[str, Any]]]) -> int:
            if not groups:
                return 0
            max_dim = 0
            for group in groups:
                hd = group.get("head_dim")
                if hd is None:
                    continue
                max_dim = max(max_dim, int(hd))
            return max_dim

        layer_max = 0
        for cfg in self.layer_configs:
            layer_max = max(layer_max, _max_group_dim(cfg.get("attention_head_groups")))

        self.max_head_dim = max(self.head_dim, _max_group_dim(self.attention_head_groups), layer_max)

    def layer_cfg(self, i: int) -> SimpleNamespace:
        base = dict(
            num_attention_heads=self.num_attention_heads,
            num_key_value_heads=self.num_key_value_heads,
            intermediate_size=self.intermediate_size,

            # default: full attention unless overridden in layer
            window=None,
            attention_head_groups=self.attention_head_groups,

            attention_bias=self.attention_bias,
            num_attention_sinks=self.num_attention_sinks,
            sink_boost=self.sink_boost,

            # MoE defaults
            expert_type=None,
            num_experts=None,
            moe_top_k=None,
            moe_capacity_factor=None,
            moe_router_jitter=None,
            moe_drop_policy=None,
            moe_aux_loss_weight=None,
            moe_intermediate_size=None,
            moe_use_bias=None,
        )
        if 0 <= i < self.num_hidden_layers and self.layer_configs and i < len(self.layer_configs):
            for k, v in self.layer_configs[i].items():
                if v is not None:
                    base[k] = v
        return SimpleNamespace(**base)
