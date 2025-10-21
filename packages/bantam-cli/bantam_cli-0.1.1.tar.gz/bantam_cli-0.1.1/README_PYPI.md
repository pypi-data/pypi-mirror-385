# Bantam

Bantam is a configurable decoder-only transformer packaged with a CLI for tokenizer training, pre-training, SFT, and chat inference. It runs on pure PyTorch (`torch>=2.1`) and uses the scaled-dot-product/FlashAttention stack for grouped-query attention, sliding windows, and sink tokens without custom kernels.

## Key Features
- Flex-attention based GQA with optional sliding windows and sink tokens.
- Per-layer overrides let you mix head counts, windows, sinks, and MoE routing per block via `layer_configs`.
- SwiGLU dense blocks or Switch/Top-k MoE with router/aux loss controls.
- Rotary embeddings with linear, NTK, and YaRN-style scaling.
- Regex-aware BPE trainer (`bantam-cli trainbpe`) that isolates punctuation, chunks long numbers, and optionally prefills 0–N.
- Unified CLI for model init, pre-training, SFT (full or LoRA), resume, and chat streaming.

## Installation

```bash
python3 -m pip install bantam-cli
```

## CLI Quick Start

```bash
bantam-cli --help          # list commands

# Train a tokenizer from JSONL
bantam-cli trainbpe --input data/pretrain.jsonl --out tokenizers/run1

# Generate starter configs (model + train + SFT)
bantam-cli define --out configs

# Initialise a model directory from split configs
bantam-cli init --mconf configs/models/pretrain_small.yaml --config configs/training/pretrain_small.yaml --out models/bantam-init

# Launch pre-training run
bantam-cli pretrain --mconf configs/models/pretrain_small.yaml --config configs/training/pretrain_small.yaml

# Resume a checkpointed run (model config auto-detected)
bantam-cli continue-pretrain --config configs/training/pretrain_small.yaml --model models/run1/checkpoints/step_20000

# Supervised fine-tuning (LoRA or full)
bantam-cli sft --config configs/training/sft_small.yaml --model models/bantam-init

# Chat with a trained checkpoint
bantam-cli chat --model models/run1/best --format chat
```

Model configs live under `configs/models/` with a `bantam_config` block. Training/SFT configs live under `configs/training/` with `training_args`, optional `sft_args`, and a run `seed`. Relative paths resolve against the YAML file location.

Example per-layer tweak:

```yaml
bantam_config:
  hidden_size: 1024
  num_hidden_layers: 12
  num_attention_heads: 16
  num_key_value_heads: 4
  layer_configs:
    - { window: 2048, num_attention_sinks: 2 }
    - { expert_type: switch, num_experts: 8, moe_capacity_factor: 1.0 }
```

## More Info

- Source code & full documentation: https://github.com/theo-bntm/bantam
- Release checklist: `publish.md` inside the repository

Report issues or ideas via GitHub. Enjoy experimenting with Bantam!
