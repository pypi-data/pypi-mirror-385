"""
Command-line utility for exporting Bantam models to ONNX.

This script is able to export both the standard forward pass (prompt decoding)
and an incremental decoding graph that consumes past key/value caches.  The
wrapper takes care of converting the internal `BantamKVCache` structure into
plain tensors so that ONNX runtimes can feed and consume the cached states.
"""

from __future__ import annotations

import base64
import hashlib
import inspect
import io
import json
from pathlib import Path
import zipfile
from typing import Iterable, List, Optional, Sequence, Tuple

import torch
import typer

from .configuration_bantam import BantamConfig
from .modeling_bantam import BantamForCausalLM, BantamKVCache

app = typer.Typer(
    help="Export a Bantam model to ONNX for deployment or interoperability.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


_DTYPE_MAP = {
    "float32": torch.float32,
    "fp32": torch.float32,
    "float": torch.float32,
    "float16": torch.float16,
    "fp16": torch.float16,
    "half": torch.float16,
    "bfloat16": torch.bfloat16,
    "bf16": torch.bfloat16,
}


def _zip_directory(path: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(path.rglob("*")):
            if file.is_file():
                arcname = file.relative_to(path).as_posix()
                zf.write(file, arcname)
    return buffer.getvalue()


def _embed_tokenizer_metadata(onnx_path: Path, tokenizer_dir: Path) -> None:
    if not tokenizer_dir.exists():
        raise FileNotFoundError(f"Tokenizer directory not found: {tokenizer_dir}")
    data = _zip_directory(tokenizer_dir)
    if not data:
        raise ValueError(f"Tokenizer directory {tokenizer_dir} is empty; nothing to embed.")
    payload = base64.b64encode(data).decode("utf-8")
    digest = hashlib.sha256(data).hexdigest()

    import onnx

    model = onnx.load(str(onnx_path))
    existing = {prop.key: prop.value for prop in model.metadata_props}
    existing["bantam_tokenizer"] = payload
    existing["bantam_tokenizer_sha256"] = digest
    existing["bantam_tokenizer_format"] = "zip+base64"
    existing["bantam_tokenizer_files"] = tokenizer_dir.name
    existing["bantam_tokenizer_bytes"] = str(len(data))

    del model.metadata_props[:]
    for key in sorted(existing.keys()):
        entry = model.metadata_props.add()
        entry.key = key
        entry.value = existing[key]

    onnx.save(model, str(onnx_path))


def _resolve_dtype(s: str) -> torch.dtype:
    key = s.strip().lower()
    if key not in _DTYPE_MAP:
        raise typer.BadParameter(f"Unsupported dtype '{s}'. Expected one of: {', '.join(sorted(_DTYPE_MAP))}")
    return _DTYPE_MAP[key]


def _ensure_device(device_spec: str) -> torch.device:
    device_spec = device_spec.strip().lower()
    if device_spec.startswith("cuda"):
        if not torch.cuda.is_available():
            raise typer.BadParameter("CUDA device requested but torch.cuda.is_available() is False.")
        return torch.device(device_spec)
    if device_spec.startswith("cpu"):
        return torch.device("cpu")
    if device_spec.startswith("mps"):
        if not torch.backends.mps.is_available():
            raise typer.BadParameter("MPS device requested but not available in this build of PyTorch.")
        return torch.device("mps")
    raise typer.BadParameter(f"Unsupported device specifier '{device_spec}'.")


def _trim_cache_state(state, length: int):
    if isinstance(state, list):
        return [tensor[..., :length, :].contiguous() for tensor in state]
    return state[..., :length, :].contiguous()


class _LayerCacheAdapter:
    def __init__(self, layer_idx: int, attn_module):
        self.layer_idx = layer_idx
        self.attn = attn_module

    def pack(self, state):
        if isinstance(state, list):
            return self.attn._pack_cache_states(state)
        return state

    def unpack(self, tensor):
        return self.attn._unpack_cache_states(tensor)


class _BantamOnnxWrapper(torch.nn.Module):
    def __init__(self, model: BantamForCausalLM, adapters: Sequence[_LayerCacheAdapter], include_cache: bool):
        super().__init__()
        self.model = model
        self.adapters = list(adapters)
        self.include_cache = include_cache

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, *past_tensors: torch.Tensor):
        cache = None
        if self.include_cache:
            expected = len(self.adapters) * 2
            if len(past_tensors) != expected:
                raise RuntimeError(
                    f"Expected {expected} past tensors (got {len(past_tensors)}). "
                    "Each layer requires a key/value pair."
                )
            cache = BantamKVCache()
            for layer_idx, adapter in enumerate(self.adapters):
                key_tensor = past_tensors[2 * layer_idx]
                value_tensor = past_tensors[2 * layer_idx + 1]
                cache._ensure_layer(layer_idx)
                cache.key[layer_idx] = adapter.unpack(key_tensor)
                cache.value[layer_idx] = adapter.unpack(value_tensor)
                cache.lengths[layer_idx] = key_tensor.shape[-2]

        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            past_key_values=cache,
            use_cache=self.include_cache,
            return_dict=True,
        )
        logits = outputs.logits

        if not self.include_cache:
            return logits

        present: List[torch.Tensor] = []
        for layer_idx, adapter in enumerate(self.adapters):
            state_k = cache.key[layer_idx] if cache is not None else None
            state_v = cache.value[layer_idx] if cache is not None else None
            if state_k is None or state_v is None:
                raise RuntimeError(f"Missing cache tensors for layer {layer_idx}.")
            present.append(adapter.pack(state_k))
            present.append(adapter.pack(state_v))
        return (logits, *present)


def _load_model(model_path: str, device: torch.device, dtype: torch.dtype) -> BantamForCausalLM:
    config = BantamConfig.from_pretrained(model_path)
    model = BantamForCausalLM.from_pretrained(model_path, config=config)
    model.eval()
    if dtype in (torch.float16, torch.bfloat16) and device.type == "cpu":
        raise typer.BadParameter(f"Dtype {dtype} is not supported on CPU. Choose float32 or run on GPU.")
    model.to(device=device, dtype=dtype, non_blocking=True)
    return model


def _build_cache_tensors(
    model: BantamForCausalLM,
    adapters: Sequence[_LayerCacheAdapter],
    batch_size: int,
    past_len: int,
    device: torch.device,
) -> Tuple[torch.Tensor, ...]:
    cache = BantamKVCache()
    if past_len <= 0:
        raise typer.BadParameter("--past-len must be greater than zero when --with-cache is enabled.")

    input_ids = torch.zeros((batch_size, past_len), dtype=torch.long, device=device)
    attention_mask = torch.ones((batch_size, past_len), dtype=torch.long, device=device)

    with torch.no_grad():
        _ = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            past_key_values=cache,
            use_cache=True,
            return_dict=False,
        )

    packed: List[torch.Tensor] = []
    for idx, adapter in enumerate(adapters):
        length = cache.lengths[idx]
        if length <= 0:
            raise RuntimeError(f"Prefill failed to populate cache for layer {idx}.")
        key_state = _trim_cache_state(cache.key[idx], length)
        value_state = _trim_cache_state(cache.value[idx], length)
        packed.append(adapter.pack(key_state).detach())
        packed.append(adapter.pack(value_state).detach())
    return tuple(packed)


def _build_attention_mask(
    batch_size: int,
    active_tokens: int,
    total_tokens: int,
    device: torch.device,
) -> torch.Tensor:
    if total_tokens < active_tokens:
        raise typer.BadParameter("attention-len cannot be smaller than the number of active tokens.")
    mask = torch.zeros((batch_size, total_tokens), dtype=torch.long, device=device)
    if active_tokens > 0:
        mask[:, :active_tokens] = 1
    return mask


def _log_summary(summary_path: Optional[Path], payload: dict) -> None:
    if summary_path is None:
        return
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


@app.command("export")
def export_command(
    model_path: str = typer.Argument(..., help="Directory or model hub identifier containing Bantam weights."),
    output: Path = typer.Option(..., "--output", "-o", help="Destination ONNX file."),
    batch_size: int = typer.Option(1, "--batch-size", "-b", min=1, help="Batch size to trace during export."),
    seq_len: int = typer.Option(128, "--seq-len", "-s", min=1, help="Number of decoder tokens for the traced step."),
    past_len: Optional[int] = typer.Option(
        None,
        "--past-len",
        help="Length of cached tokens. Required when exporting with past key values.",
    ),
    attention_len: Optional[int] = typer.Option(
        None,
        "--attention-len",
        help="Total attention mask length (defaults to seq_len or past_len + seq_len when caches are enabled).",
    ),
    opset: int = typer.Option(17, "--opset", help="ONNX opset version."),
    dtype: str = typer.Option("float32", "--dtype", help="Floating point precision to convert the model to."),
    device: str = typer.Option("cpu", "--device", help="Device to run the export on (cpu, cuda, cuda:0, mps)."),
    with_cache: bool = typer.Option(
        False,
        "--with-cache/--without-cache",
        help="Include past key/value tensors in the exported graph.",
    ),
    external_data: bool = typer.Option(
        False,
        "--external-data/--single-file",
        help="Store weights using the external data format (needed for >2GB files).",
    ),
    constant_folding: bool = typer.Option(
        True,
        "--constant-folding/--no-constant-folding",
        help="Enable constant folding during ONNX export.",
    ),
    summary_path: Optional[Path] = typer.Option(
        None,
        "--summary",
        help="Optional JSON file to record metadata about the export.",
    ),
    tokenizer_path: Optional[Path] = typer.Option(
        None,
        "--tokenizer",
        "-t",
        help="Embed a tokenizer directory into the ONNX metadata for single-file usage.",
    ),
    verbose: bool = typer.Option(False, "--verbose/--quiet", help="Print additional diagnostics during export."),
) -> None:
    """Export Bantam checkpoints to ONNX, optionally including KV-cache inputs and outputs."""
    torch.set_grad_enabled(False)

    resolved_dtype = _resolve_dtype(dtype)
    resolved_device = _ensure_device(device)
    tokenizer_path = tokenizer_path.expanduser().resolve() if tokenizer_path else None
    if tokenizer_path is not None:
        if not tokenizer_path.exists():
            raise typer.BadParameter(f"Tokenizer path not found: {tokenizer_path}")
        if not any(p.is_file() for p in tokenizer_path.rglob("*")):
            raise typer.BadParameter(f"Tokenizer directory '{tokenizer_path}' does not contain any files.")

    model = _load_model(model_path, resolved_device, resolved_dtype)
    adapters = [_LayerCacheAdapter(i, layer.attn) for i, layer in enumerate(model.model.layers)]

    attention_tokens = seq_len
    past_inputs: Tuple[torch.Tensor, ...] = tuple()

    if with_cache:
        if past_len is None:
            raise typer.BadParameter("--past-len must be provided when --with-cache is specified.")
        past_inputs = _build_cache_tensors(model, adapters, batch_size, past_len, resolved_device)
        attention_tokens = past_len + seq_len
    elif past_len is not None and verbose:
        typer.echo("⚠️  --past-len was provided but caches are disabled; ignoring.", err=True)

    total_attention = attention_len or attention_tokens
    attention_mask = _build_attention_mask(batch_size, attention_tokens, total_attention, resolved_device)
    input_ids = torch.zeros((batch_size, seq_len), dtype=torch.long, device=resolved_device)

    wrapper = _BantamOnnxWrapper(model, adapters, include_cache=with_cache).to(resolved_device)
    wrapper.eval()

    input_names: List[str] = ["input_ids", "attention_mask"]
    example_inputs: List[torch.Tensor] = [input_ids, attention_mask]
    dynamic_axes = {
        "input_ids": {0: "batch", 1: "decoder_seq"},
        "attention_mask": {0: "batch", 1: "total_seq"},
        "logits": {0: "batch", 1: "decoder_seq"},
    }

    output_names: List[str] = ["logits"]

    if with_cache:
        for layer_idx in range(len(adapters)):
            k_name = f"past_key_{layer_idx}"
            v_name = f"past_value_{layer_idx}"
            input_names.extend([k_name, v_name])
            example_inputs.append(past_inputs[2 * layer_idx])
            example_inputs.append(past_inputs[2 * layer_idx + 1])

            dynamic_axes[k_name] = {0: "batch", 2: f"past_seq_layer_{layer_idx}"}
            dynamic_axes[v_name] = {0: "batch", 2: f"past_seq_layer_{layer_idx}"}

        for layer_idx in range(len(adapters)):
            pk_name = f"present_key_{layer_idx}"
            pv_name = f"present_value_{layer_idx}"
            output_names.extend([pk_name, pv_name])
            dynamic_axes[pk_name] = {0: "batch", 2: f"present_seq_layer_{layer_idx}"}
            dynamic_axes[pv_name] = {0: "batch", 2: f"present_seq_layer_{layer_idx}"}

    output.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        typer.echo(f"Exporting model from '{model_path}' to '{output}' (opset={opset})...")
        typer.echo(f" - device={resolved_device}, dtype={resolved_dtype}")
        typer.echo(f" - batch_size={batch_size}, seq_len={seq_len}, attention_tokens={attention_tokens}")
        if with_cache:
            typer.echo(f" - caches enabled with past_len={past_len}")
        typer.echo(f" - external_data={external_data}, constant_folding={constant_folding}")

    try:
        import onnx  # noqa: F401
    except ImportError as exc:
        typer.echo("❌ ONNX Python package is not installed. Install it with `pip install onnx` and retry.", err=True)
        raise typer.Exit(code=1) from exc

    export_kwargs = dict(
        export_params=True,
        do_constant_folding=constant_folding,
        opset_version=opset,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
    )
    signature = inspect.signature(torch.onnx.export)
    if "use_external_data_format" in signature.parameters:
        export_kwargs["use_external_data_format"] = external_data
    elif external_data:
        typer.echo(
            "⚠️  The installed torch.onnx.export does not support external data format; generating a single file.",
            err=True,
        )

    torch.onnx.export(
        wrapper,
        tuple(example_inputs),
        str(output),
        **export_kwargs,
    )

    if tokenizer_path is not None:
        _embed_tokenizer_metadata(output, tokenizer_path)
        if verbose:
            typer.echo(f"Embedded tokenizer from {tokenizer_path} into ONNX metadata.")

    metadata = {
        "model_path": model_path,
        "output": str(output),
        "with_cache": with_cache,
        "batch_size": batch_size,
        "seq_len": seq_len,
        "attention_len": total_attention,
        "opset": opset,
        "dtype": str(resolved_dtype),
        "device": str(resolved_device),
        "num_layers": len(adapters),
        "tokenizer_embedded": bool(tokenizer_path),
    }
    if with_cache:
        metadata["past_len"] = past_len
    if tokenizer_path is not None:
        metadata["tokenizer_dir"] = str(tokenizer_path)
    _log_summary(summary_path, metadata)

    if verbose:
        typer.echo("✅ ONNX export completed.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
