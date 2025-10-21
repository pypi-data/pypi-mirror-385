# Bantam

Bantam is a research-first, production-realistic decoder-only transformer. The core model is compact, fully configurable, and leans on PyTorch's flash/scaled-dot-product attention stack so grouped-query attention, sliding windows, and sink tokens all coexist without custom CUDA. The surrounding tools cover tokenizer training, pre-training, SFT (full or LoRA), and interactive chat so you can iterate quickly on ideas.

---

## Highlights

- **Flash attention everywhere** – grouped-query attention with optional sliding windows and sink tokens runs on PyTorch's FlashAttention kernels (and falls back to SDPA when needed). Score modulation provides attention-temperature scaling and tanh soft-capping, and bias boosts keep sink tokens sticky.
- **Per-layer customization** – every layer can override head counts, feed-forward width, sliding window, sinks, and MoE routing behaviour through `layer_configs`.
- **SwiGLU and sparse experts** – dense SwiGLU is the default; sparse Switch/Top‑k experts include load-balancing and router z-loss terms. Residual projections opt into scaled-init handling.
- **RoPE with scaling modes** – linear, NTK/dynamic, and YaRN-style scaling are all supported, sharing a single rotary cache.
- **Tokenizer pipeline** – bundled special tokens plus a CLI BPE trainer with regex-aware punctuation splitting, digit chunking, and optional number prefill (0–N) so numeric tokens survive training.
- **Unified CLI** – `bantam-cli` (or `python -m bantam`) handles model initialisation, BPE training, pre-training, SFT, continuation, and chat streaming.

---

## Repository layout

- `src/bantam/` – installable package (model, config, tokenizer utilities, trainer, CLI, chat helper).
- `configs/models/` – model architecture YAMLs (pure `bantam_config` blocks).
- `configs/training/` – run configs with `training_args`, optional `sft_args`, and seeds.
- `scripts/` – helper utilities (e.g. dataset mixing).
- `research/` – papers/notes that inform the implementation.
- `publish.md` – release checklist for PyPI/TestPyPI.

Install in editable mode to hack on `src/` directly without artifact juggling.

---

## Installation & setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
bantam-cli --help
# equivalently
python -m bantam --help
```

On WSL with repos on `/mnt/c`, consider creating the virtualenv on the Linux side (e.g. `~/projects/bantam/.venv`) for better I/O performance before running `pip install -e`.

---

## Tokenizer workflow

The project ships a default `tokenizer.json` plus helper utilities in `tokenization_bantam.py`. Special tokens cover core runtime flow (BOS/EOS/PAD/UNK), role fencing (`<|SYSTEM_START|>` …), reasoning spans (`<|THINK_START|>` …), multimodal placeholders, tool I/O, and reserved future slots. `BantamTokenizerUtils` exposes the list so training and inference stay in sync.

Train a new tokenizer straight from JSONL text columns:

```bash
bantam-cli trainbpe \
  --input ./data/pretrain.jsonl \
  --out ./tokenizers/my-tokenizer \
  --text-field text \
  --vocab-size 51200 \
  --min-frequency 2
```

`trainbpe` accepts multiple `--input` paths (files or directories), applies optional lowercasing/accents stripping, and enables regex preprocessing by default:

- punctuation in `--regex-symbols` is isolated so symbols become standalone tokens,
- long digit runs are split into `--digit-group-size` chunks,
- numbers up to `--prefill-numbers-upto` are inserted into the vocab post-training.

Outputs:

- `tokenizer.json`, `tokenizer_config.json`, and related Hugging Face files under `--out`;
- `bpe_training_args.json` describing the run (files consumed, regex settings, records skipped, numbers added).

Point `training_args.tokenizer` (or CLI `--tokenizer`) at the new directory to use it everywhere else.

---

## Model architecture

Each layer follows: RMSNorm → Flash/SDPA attention → RMSNorm → SwiGLU/MoE → residual adds with optional dropout and stochastic depth. Key components:

### Attention

- Grouped-query attention (GQA) with head projections sized `hidden_size / num_heads`.
- RoPE applied after optional per-head RMSNorm on Q/K.
- Sliding windows restrict context without breaking caches; window length can vary per layer.
- Sink tokens preserve global anchors; score modifiers add boosts and optional tanh soft-capping.
- Block masks are cached per device/shape to avoid repeated recomputation.
- Implementation uses PyTorch's scaled-dot-product attention (`torch>=2.1`) with automatic FlashAttention kernels where available. Masks degrade gracefully to full attention when windows/sinks are disabled.

### Rotary embeddings

`BantamRotaryEmbedding` maintains cosine/sine caches and supports:

- linear scaling (`factor`),
- NTK/dynamic scaling (`type: dynamic`, optional `original_max_position_embeddings`),
- YaRN-style scaling (pair with `attn_temperature`).

Position IDs are normalised from packed shapes to `(batch, seq)` automatically.

### Feed-forward & MoE

- Dense path uses SwiGLU with optional dropout; down projections flag `is_residual_out` for init scaling.
- MoE path instantiates SwiGLU experts with either Switch (top-1) or Top-k routing. Capacity factors, jitter, drop policy, auxiliary loss weights, and router z-loss weight are configurable per layer.

### Normalisation, residuals, stability

- RMSNorm throughout (bf16 friendly).
- Optional q/k norm per attention head.
- Residual dropout plus stochastic depth (linear schedule across layers).
- Loss shaping knobs: label smoothing, z-loss, final logit soft-capping.
- Generation cache keeps a prefix for sink tokens when sliding windows are active.

---

## Configuration surface

`BantamConfig` drives the model. Useful fields include:

- **Core shape**: `hidden_size`, `intermediate_size`, `num_hidden_layers`, `num_attention_heads`, `num_key_value_heads`, `vocab_size`, `max_position_embeddings`.
- **Attention**: `attention_bias`, `attention_dropout`, `num_attention_sinks`, `sink_boost`, `attn_temperature`, `attn_logit_softcapping`, `block_mask_cache_cap/device`.
- **RoPE**: `rope_theta`, `rope_scaling`.
- **Regularisation**: `qk_norm`, `qk_norm_eps`, `mlp_dropout`, `residual_dropout`, `stochastic_depth_rate`.
- **Loss**: `label_smoothing`, `z_loss_weight`, `final_logit_softcapping`.
- **MoE**: `expert_type`, `num_experts`, `moe_top_k`, `moe_capacity_factor`, `moe_router_jitter`, `moe_drop_policy`, `moe_aux_loss_weight`, `moe_router_z_loss_weight`, `moe_intermediate_size`.

Per-layer overrides live in `layer_configs` (list of dicts or `LayerConfigSpec`). Example:

```python
from bantam.configuration_bantam import BantamConfig

cfg = BantamConfig(
    hidden_size=2048,
    num_hidden_layers=24,
    num_attention_heads=32,
    num_key_value_heads=8,
    rope_scaling={"type": "dynamic", "factor": 2.0},
    attn_temperature=0.7,
    layer_configs=[
        {"window": 2048, "num_attention_sinks": 2, "sink_boost": 0.5},
        *[{"expert_type": "switch", "num_experts": 8, "moe_capacity_factor": 1.0} for _ in range(8)],
    ],
)
```

Instantiate with `BantamForCausalLM(cfg)` to start from scratch or load checkpoints via `from_pretrained`.

---

## Training stack

The trainer in `src/bantam/trainer.py` handles both pre-training and SFT:

- **Datasets** – local JSONL (`training_args.dataset`) or Hugging Face streaming (`use_hf`, `hf_name`, `hf_subset`, `hf_split`). Local JSONL is tokenised via `BlockDataset` with BOS/EOS wrapping and block packing.
- **Batching** – `batch_size`, `accum_steps`, `steps_per_epoch` for streaming datasets. Min sample length filters skip short rows.
- **Optimisation** – AdamW defaults or the built-in Muon + auxiliary Adam optimiser with parameter-aware grouping (`training_args.optimizer`, `muon_lr`, `muon_momentum`, `muon_exclude_embeddings`).
- **Precision** – bf16 by default, configurable via `training_args.precision`.
- **Checkpointing** – save frequency, keep-last-n pruning, loss-based saves, CSV logging, full resume (model + optimizer + scheduler + scalers).
- **SFT** – LoRA via PEFT (`sft_mode: lora`) or full fine-tune. Chat-style datasets expect `messages`/`conversations` with role/content pairs.
- **Tokenizer integration** – `training_args.tokenizer` points at local directories (new BPE runs or bundled tokenizer).

The CLI wraps these flows (see below) but you can also call `BantamTrainer` helpers directly from Python if you need custom orchestration.

---

## CLI commands

All commands support `-h/--help` for detailed options.

- `bantam-cli trainbpe` – train a regex-aware tokenizer (see Tokenizer workflow).
- `bantam-cli define --out <dir>` – materialise model + training + SFT config templates into `<dir>` (defaults to `./configs`).
- `bantam-cli init --mconf <model_yaml> --config <train_yaml> --out <dir>` – materialise a random-weight model + tokenizer into `<dir>`.
- `bantam-cli pretrain --mconf <model_yaml> --config <train_yaml>` – launch a new pre-training run, emitting streamed status lines and optional PNG loss plots.
- `bantam-cli continue-pretrain --config <train_yaml> --model <checkpoint>` – resume from a checkpoint directory (uses the model config stored with the checkpoint; pass `--mconf` only to override it).
- `bantam-cli sft --config <train_yaml> --model <base>` – supervised fine-tuning (LoRA or full). Use `--resume-from` to continue a prior SFT run.
- `bantam-cli chat --model <path>` – stream generations from a saved checkpoint. Supports chat-format prompts (system/user/assistant tokens) and raw LM prompts.

Run `python -m bantam` if you prefer the module entry point.

---

## Configuration files

Configs are split between model definitions and run settings:

- **Model YAMLs** (`configs/models/*.yaml`) contain a single `bantam_config` mapping that feeds `BantamConfig`.
- **Training YAMLs** (`configs/training/*.yaml`) hold the run `seed`, a `training_args` block, and optional `sft_args`. Relative paths resolve against the training YAML location, so keep paths local to that file.

### `bantam_config` reference

Important knobs (see `src/bantam/configuration_bantam.py` for the exhaustive dataclass):

- **Core shape** – `hidden_size`, `intermediate_size`, `num_hidden_layers`, `num_attention_heads`, `num_key_value_heads`, `head_dim`, `vocab_size`, `max_position_embeddings`, `tie_word_embeddings`.
- **Attention** – `attn_impl`, `attention_bias`, `attention_dropout`, `num_attention_sinks`, `sink_boost`, `attn_temperature`, `attn_logit_softcapping`, `scaled_embeddings`, `final_logit_softcapping`.
- **RoPE** – `rope_theta`, `rope_scaling` (`type`, `factor`, `original_max_position_embeddings`, `short_factor`).
- **Normalisation & regularisation** – `rms_norm_eps`, `qk_norm`, `qk_norm_eps`, `mlp_dropout`, `residual_dropout`, `stochastic_depth_rate`, `initializer_range`.
- **MoE** – `expert_type`, `num_experts`, `moe_top_k`, `moe_intermediate_size`, `moe_capacity_factor`, `moe_router_jitter`, `moe_drop_policy`, `moe_aux_loss_weight`, `moe_router_z_loss_weight`.
- **Layer overrides** – `layer_configs` list lets you override per-layer `window`, feed-forward widths, MoE routing, sink counts, etc. Null windows imply global attention for that block.
- **Loss shaping** – `label_smoothing`, `z_loss_weight`, `final_logit_softcapping`.

### `training_args` reference

Parameters accepted by `TrainingArgs`, grouped by theme:

- **Paths & I/O** – `dataset`, `tokenizer`, `out_dir`, `init_from_checkpoint`, `finetune_from`, `resume_from_checkpoint`, `save_tag`.
- **Dataset controls** – `use_hf`, `hf_name`, `hf_subset`, `hf_split`, `hf_streaming`, `hf_text_field`, `hf_messages_field`, `shuffle_buffer_size`, `dataset_text_field`, `min_sample_token_length`, `overfit_subset`.
- **Batching & schedule** – `batch_size`, `accum_steps`, `epochs`, `steps_per_epoch`, `warmup_frac`, `log_every_n`.
- **Optimisation** –
  - `optimizer`: `"muon"` (default) for Muon + auxiliary Adam, or `"adamw"` for plain AdamW.
  - `lr`, `weight_decay`, `beta2`, `optim_eps`, `grad_clip`, `lr_scheduler`, `min_lr_ratio` – shared between optimisers (older configs using `adam_eps` are still honoured).
  - `muon_lr` (defaults to `lr` when null), `muon_momentum`, `muon_exclude_embeddings`, `muon_beta1`, `muon_beta2`, `muon_eps`, `muon_bias_correction`, `muon_clip_by_layer`, `muon_lr_correction` – Muon-specific knobs (each falls back to the shared values when omitted).
- **Precision & scaling** – `precision` (`bf16`, `fp16`, `fp32`), gradient accumulation (`accum_steps`), `use_gradient_checkpoint`.
- **Checkpointing & logging** – `save_every_n`, `keep_last_k`, `save_on_improve`, `improve_delta`, `log_loss_to_csv`.
- **Data loader** – `num_workers`, `pin_memory`, `persistent_workers`.
- **SFT defaults** – `sft_mode`, `lora_r`, `lora_alpha`, `lora_dropout`, `include_agent_end`, `include_eos`, `mask_user_queries` (overridable via `sft_args`).

### Example configuration pair

```yaml
# configs/models/my_model.yaml
bantam_config:
  model_type: bantam
  hidden_size: 1024
  intermediate_size: 2816
  num_hidden_layers: 16
  num_attention_heads: 16
  num_key_value_heads: 4
  head_dim: 64
  max_position_embeddings: 2048
  rope_theta: 10000
  rope_scaling: { type: dynamic, factor: 2.0 }
  rms_norm_eps: 1.0e-6
  attention_dropout: 0.0
  mlp_dropout: 0.0
  residual_dropout: 0.0
  layer_configs:
    - { window: 1024, intermediate_size: 3072 }
    - { window: null, intermediate_size: 3072 }
    - { window: 1024, expert_type: "topk", num_experts: 8, moe_top_k: 2, moe_capacity_factor: 1.25 }
```

```yaml
# configs/training/my_run.yaml
seed: 1337

training_args:
  dataset: ../../data/pretrain.jsonl
  tokenizer: ../../tokenizers/my-tokenizer
  out_dir: ../../models/run1
  optimizer: muon            # or "adamw"
  lr: 3.0e-4
  muon_lr: null              # fall back to lr
  muon_momentum: 0.95
  muon_exclude_embeddings: true
  weight_decay: 0.1
  beta2: 0.95
  optim_eps: 1.0e-8
  grad_clip: 1.0
  batch_size: 1
  accum_steps: 32
  epochs: 2
  warmup_frac: 0.10
  steps_per_epoch: 2000
  precision: bf16
  save_every_n: 5000
  keep_last_k: 3
  use_gradient_checkpoint: false
  num_workers: 2
  pin_memory: true
  persistent_workers: true

  # Optional SFT defaults (merged for SFT runs)
  sft_mode: lora
  lora_r: 64
  lora_alpha: 96
  lora_dropout: 0.05
  include_agent_end: true
  include_eos: false
  mask_user_queries: true
```

---

## Chat helper

`bantam-cli chat` uses `BantamChat` to wrap `BantamForCausalLM` with streaming generation. Provide chat turns (`system`, `user`, `assistant`) or switch to raw pretrain mode. LoRA adapters in the model directory are detected and merged automatically when possible.

---

## Publishing

See `publish.md` for the full PyPI/TestPyPI release checklist (version bumping, builds, uploads, and smoke tests for the CLI).

---

## License & contributions

Bantam is distributed for research use; check the repository license for details. Issues and PRs are welcome—just make sure to run the compile check (`python3 -m compileall src/bantam`) and update relevant docs (including this README) when behaviour changes.
