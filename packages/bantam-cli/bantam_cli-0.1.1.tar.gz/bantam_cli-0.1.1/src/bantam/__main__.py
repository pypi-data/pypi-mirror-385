# __main__.py

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import typer
import yaml
import torch
from pathlib import Path
import time
import textwrap
import traceback
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from importlib import resources as importlib_resources

# External library imports
from transformers import AutoTokenizer
# no direct use of PeftModel here; keep PEFT use in trainer only

# --- Import Bantam Architecture and Trainer Components (FIXED) ---
from .configuration_bantam import BantamConfig
from .modeling_bantam import BantamForCausalLM
from .export_onnx import export_command as export_onnx_command
from .tokenization_bantam import BantamTokenizerUtils, get_default_tokenizer_dir
from .trainer import TrainingArgs, BantamTrainer 
from .bantam_chat import BantamChat, GenerateConfig


app = typer.Typer(
    help="CLI for training, fine-tuning, and interacting with Bantam models.",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

CONFIG_TEMPLATE_MAP = {
    Path("models/model.yaml"): "model.yaml",
    Path("training/pretrain.yaml"): "pretrain.yaml",
    Path("training/sft.yaml"): "sft.yaml",
}
CONFIG_TEMPLATE_PACKAGE = "bantam.config_templates"

class PromptFormat(str, Enum):
    chat = "chat"
    pretrain = "pretrain"

_DEPRECATED_TOKENIZER_KEYS = {
    "tokenizer_auto_tune",
    "tokenizer_vocab_sweep",
    "tokenizer_eval_frac",
    "tokenizer_eval_max_lines",
    "tokenizer_early_delta",
    "tokenizer_early_patience",
    "tokenizer_min_frequency",
    "tokenizer_max_token_length",
    "tokenizer_score_w_tpc",
    "tokenizer_score_w_rare",
    "tokenizer_score_w_gini",
    "tokenizer_score_w_k90",
    "tokenizer_rare_threshold",
    "tokenizer_tie_break_on_smaller_vocab",
    "tokenizer_mfreq_ramp",
    "tokenizer_mfreq_base",
    "tokenizer_mfreq_table",
}


def _load_yaml_dict(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected top-level mapping in config: {config_path}")
    return data


def load_model_config(model_config_path: Path) -> BantamConfig:
    data = _load_yaml_dict(model_config_path)
    model_section = data.get("bantam_config", data)
    if not isinstance(model_section, dict):
        raise ValueError(f"Model config must be a mapping: {model_config_path}")
    return BantamConfig(**model_section)


def load_training_bundle(config_path: Path) -> Tuple[TrainingArgs, Dict[str, Any], int]:
    data = _load_yaml_dict(config_path)

    training_args_data = dict(data.get("training_args", {}) or {})
    removed = [key for key in list(training_args_data.keys()) if key in _DEPRECATED_TOKENIZER_KEYS]
    for key in removed:
        training_args_data.pop(key, None)
    if removed:
        print(
            "⚠️  Ignoring deprecated tokenizer training keys: "
            + ", ".join(sorted(removed))
        )

    training_args = TrainingArgs(**training_args_data)
    seed = int(data.get("seed", 42))
    training_args.seed = seed

    # resolve relative paths (dataset/tokenizer/out_dir)
    training_args.resolve_paths(config_path)

    sft_args = data.get("sft_args", {}) or {}

    return training_args, sft_args, seed


def _print_model_summary(model: torch.nn.Module):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print("--- Model Summary ---")
    print(f"Total Parameters:       {total_params/1e6:.2f}M")
    print(f"Trainable Parameters: {trainable_params/1e6:.2f}M")
    print("---------------------")


@app.command(name="init")
def init(
    model_config_path: Path = typer.Option(..., "--mconf", "-m", help="Path to the model config YAML file."),
    config_path: Path = typer.Option(..., "--config", "-c", help="Path to the training config YAML file."),
    output_dir: Path = typer.Option(..., "--out", "-o", help="Directory to save the initialized model.")
):
    """
    Initialize a new Bantam model with random weights (no training) 
    and export the tokenizer alongside it.
    """
    print("--- 🛠️ Initializing Bantam model (random weights) ---")
    try:
        cfg = load_model_config(model_config_path)
        targs, _, _ = load_training_bundle(config_path)

        # 1. Load tokenizer (use bundled default unless caller overrides)
        tokenizer_spec = targs.tokenizer or str(get_default_tokenizer_dir())
        tokenizer_path = Path(tokenizer_spec)
        if tokenizer_path.exists():
            load_target = tokenizer_path.parent if tokenizer_path.is_file() else tokenizer_path
            tokenizer = AutoTokenizer.from_pretrained(str(load_target), trust_remote_code=True)
        else:
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_spec, trust_remote_code=True)

        actual_vocab_size = len(tokenizer)
        if cfg.vocab_size != actual_vocab_size:
            print(
                f"ℹ️  Updating vocab_size from {cfg.vocab_size} to {actual_vocab_size} based on tokenizer."
            )
            cfg.vocab_size = actual_vocab_size
        if tokenizer.pad_token_id is not None:
            cfg.pad_token_id = int(tokenizer.pad_token_id)
        if tokenizer.bos_token_id is not None:
            cfg.bos_token_id = int(tokenizer.bos_token_id)
        if tokenizer.eos_token_id is not None:
            cfg.eos_token_id = int(tokenizer.eos_token_id)

        # 2. Build model from config (random init)
        model = BantamForCausalLM(cfg)
        _print_model_summary(model)

        # 3. Save everything to the output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(output_dir)
        cfg.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        print(f"--- ✅ Model + Tokenizer initialized and saved to {output_dir} ---")

    except Exception as e:
        print(f"❌ Error during model initialization: {e}")
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def trainbpe(
    input_paths: List[Path] = typer.Option(..., "--input", "-i", help="Path(s) to JSONL files or directories containing JSONL files."),
    output_dir: Path = typer.Option(..., "--out", "-o", help="Directory to save the trained tokenizer."),
    text_field: str = typer.Option("text", "--text-field", help="JSON field containing the text to tokenize."),
    vocab_size: int = typer.Option(16384, "--vocab-size", help="Target vocabulary size for the tokenizer."),
    min_frequency: int = typer.Option(2, "--min-frequency", help="Minimum token frequency to keep in the vocab."),
    lowercase: bool = typer.Option(False, "--lowercase/--keep-case", help="Lowercase text before training."),
    strip_accents: bool = typer.Option(False, "--strip-accents/--keep-accents", help="Strip accents before training."),
    limit_alphabet: Optional[int] = typer.Option(None, "--limit-alphabet", help="Limit the alphabet size before training."),
    max_samples: Optional[int] = typer.Option(None, "--max-samples", help="Stop after processing this many samples."),
    show_progress: bool = typer.Option(True, "--progress/--no-progress", help="Show training progress."),
    regex_clean: bool = typer.Option(True, "--regex-clean/--no-regex-clean", help="Apply regex-based symbol isolation and digit grouping."),
    regex_symbols: str = typer.Option("?-*=+!@#$%^&()[]{}<>/\\|:;.,~`\"'", "--regex-symbols", help="Characters to isolate as standalone tokens during regex clean."),
    digit_group_size: int = typer.Option(2, "--digit-group-size", help="Maximum digit run length before inserting a separator."),
):
    """Train a Byte-Pair Encoding tokenizer from JSONL data."""
    print("--- 🧪 Training Bantam BPE Tokenizer ---")
    try:
        result = BantamTrainer.train_bpe_tokenizer(
            input_paths=input_paths,
            output_dir=output_dir,
            text_field=text_field,
            vocab_size=vocab_size,
            min_frequency=min_frequency,
            lowercase=lowercase,
            strip_accents=strip_accents,
            limit_alphabet=limit_alphabet,
            max_samples=max_samples,
            show_progress=show_progress,
            regex_clean=regex_clean,
            regex_symbols=regex_symbols,
            digit_group_size=digit_group_size,
        )
        print(f"✅ Tokenizer saved to {result['output_dir']}")
        print(f"   • vocab_size: {result['vocab_size']}")
        print(f"   • records_used: {result['records_used']}")
        print(
            "   • records_skipped: {records} (empty={empty}, missing={missing}, json_error={json})".format(
                records=result["records_skipped"],
                empty=result["skipped_breakdown"]["empty"],
                missing=result["skipped_breakdown"]["missing_field"],
                json=result["skipped_breakdown"]["json_error"],
            )
        )
        print(f"   • metadata: {result['metadata_path']}")
    except Exception as e:
        print(f"❌ Error during tokenizer training: {e}")
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command(name="define")
def config_define(
    output_dir: Optional[Path] = typer.Option(
        None,
        "--out",
        "-o",
        help="Directory to write config templates. Defaults to ./configs.",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Allow overwriting existing files."),
):
    """Materialise starter config templates (model + training)."""

    target_root = (output_dir or Path.cwd() / "configs").expanduser().resolve()

    conflicts = []
    for rel_path in CONFIG_TEMPLATE_MAP:
        target_path = target_root / rel_path
        if target_path.exists() and not overwrite:
            conflicts.append(target_path)
    if conflicts:
        print("❌ Refusing to overwrite existing files:")
        for path in conflicts:
            print(f"   - {path}")
        print("   Use --overwrite to replace them.")
        raise typer.Exit(code=1)

    written: List[Path] = []
    for rel_path, resource_name in CONFIG_TEMPLATE_MAP.items():
        target_path = target_root / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        template_data = importlib_resources.read_text(CONFIG_TEMPLATE_PACKAGE, resource_name, encoding="utf-8")
        target_path.write_text(template_data, encoding="utf-8")
        written.append(target_path)

    print("✅ Config templates written:")
    for path in written:
        print(f"   - {path}")

@app.command()
def pretrain(
    model_config_path: Path = typer.Option(..., "--mconf", "-m", help="Path to the model config YAML file."),
    config_path: Path = typer.Option(..., "--config", "-c", help="Path to the training config YAML file."),
    resume_from: Path = typer.Option(None, "--resume-from", help="Resume full training state from this checkpoint dir."),
    save_every_n: int = typer.Option(None, help="Override save_every_n interval from config."),
    keep_last_k: int = typer.Option(None, help="Keep only the last K checkpoints in out_dir/checkpoints."),
    save_on_improve: bool = typer.Option(None, help="Save checkpoints only when loss improves by at least improve_delta."),
    improve_delta: float = typer.Option(None, help="Minimum loss improvement to trigger a save when save_on_improve=True."),
    log_loss_to_csv: bool = typer.Option(None, help="Enable CSV loss logging under out_dir/logs."),
):
    """
    Start a new pre-training run.
    """
    print("--- 🚀 Starting New Pre-training Run ---")
    try:
        cfg = load_model_config(model_config_path)
        targs, _, seed = load_training_bundle(config_path)
        targs.seed = seed

        # Optional CLI overrides for checkpointing/logging
        if resume_from is not None:
            targs.resume_from_checkpoint = str(resume_from)
        if save_every_n is not None:
            targs.save_every_n = int(save_every_n)
        if keep_last_k is not None:
            targs.keep_last_k = int(keep_last_k)
        if save_on_improve is not None:
            targs.save_on_improve = bool(save_on_improve)
        if improve_delta is not None:
            targs.improve_delta = float(improve_delta)
        if log_loss_to_csv is not None:
            targs.log_loss_to_csv = bool(log_loss_to_csv)

        output_dir = Path(targs.out_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for fig, status in BantamTrainer.train_pretrain_and_stream(cfg, targs):
            print(status)
            if fig:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                fig.savefig(output_dir / f"pretrain_loss_{timestamp}.png")

        print("--- ✅ Pre-training Finished ---")

    except Exception as e:
        tb = ''.join(traceback.TracebackException.from_exception(e).format(chain=True))
        print(f"❌ Error during pretrain: {str(e)}\n\n{tb}")
        raise typer.Exit(code=1)


@app.command()
def continue_pretrain(
    model_config_path: Optional[Path] = typer.Option(
        None,
        "--mconf",
        "-M",
        help="Optional path to a model config YAML. Defaults to the config stored in --model.",
    ),
    config_path: Path = typer.Option(..., "--config", "-c", help="Path to the training config YAML file."),
    model_path: Path = typer.Option(..., "--model", "-m", help="Path to the checkpoint directory to resume from."),
):
    print(f"--- 🚀 Continuing Pre-training (full resume) from {model_path} ---")
    try:
        if model_config_path is not None:
            cfg = load_model_config(model_config_path)
        else:
            cfg = BantamConfig.from_pretrained(str(model_path))
        targs, _, seed = load_training_bundle(config_path)
        output_dir = Path(targs.out_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prefer full-state resume when directory comes from our checkpoints
        targs.resume_from_checkpoint = str(model_path)
        targs.seed = seed

        for fig, status in BantamTrainer.train_pretrain_and_stream(cfg, targs):
            print(status)
            if fig:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                fig.savefig(output_dir / f"continue_pretrain_loss_{timestamp}.png")

        print("--- ✅ Pre-training Finished ---")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        raise typer.Exit(code=1)


@app.command()
def sft(
    config_path: Path = typer.Option(..., "--config", "-c", help="Path to the training config YAML file."),
    model_path: Path = typer.Option(..., "--model", "-m", help="Path to the base model to fine-tune (or base for LoRA resume)."),
    resume_from: Path = typer.Option(None, "--resume-from", help="Resume SFT from a prior checkpoint directory (LoRA or full)."),
    save_every_n: int = typer.Option(None, help="Override save_every_n interval from config."),
    keep_last_k: int = typer.Option(None, help="Keep only the last K checkpoints in out_dir/checkpoints."),
    save_on_improve: bool = typer.Option(None, help="Save checkpoints only when loss improves by at least improve_delta."),
    improve_delta: float = typer.Option(None, help="Minimum loss improvement to trigger a save when save_on_improve=True."),
    log_loss_to_csv: bool = typer.Option(None, help="Enable CSV loss logging under out_dir/logs."),
):
    """
    Supervised Fine-Tuning (SFT). Mode (lora|full) is taken from the config `sft_args.mode`.
    """
    print(f"--- 🚀 Starting SFT on {model_path} ---")
    try:
        targs, sft_args, seed = load_training_bundle(config_path)

        output_dir = Path(targs.out_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Apply SFT overrides from YAML onto TrainingArgs
        for k, v in (sft_args or {}).items():
            if hasattr(targs, k):
                setattr(targs, k, v)
            else:
                print(f"ℹ️ Ignoring unknown SFT arg: {k}={v}")
        # Point to base checkpoint for SFT, and optional resume
        targs.finetune_from = str(model_path)
        if resume_from is not None:
            targs.resume_from_checkpoint = str(resume_from)

        # Optional CLI overrides for checkpointing/logging
        if save_every_n is not None:
            targs.save_every_n = int(save_every_n)
        if keep_last_k is not None:
            targs.keep_last_k = int(keep_last_k)
        if save_on_improve is not None:
            targs.save_on_improve = bool(save_on_improve)
        if improve_delta is not None:
            targs.improve_delta = float(improve_delta)
        if log_loss_to_csv is not None:
            targs.log_loss_to_csv = bool(log_loss_to_csv)
        targs.seed = seed

        # Call with a single TrainingArgs object
        for fig, status in BantamTrainer.train_sft_and_stream(targs):
            print(status)
            if fig:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                fig.savefig(output_dir / f"sft_loss_{timestamp}.png")

        print("--- ✅ SFT Finished ---")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        raise typer.Exit(code=1)


@app.command()
def chat(
    model_path: Path = typer.Option(..., "--model", "-m"),
    max_new_tokens: int = typer.Option(256),
    temp: float = typer.Option(0.6, help="Temperature (0 = greedy)"),
    system_prompt: str = typer.Option("You are a helpful AI assistant.", help="(chat mode only)"),
    format: PromptFormat = typer.Option(PromptFormat.chat, "--format", help="chat|pretrain"),
):
    """
    Interact with a Bantam model using a unified streaming endpoint.
    """
    model_path = model_path.expanduser()
    candidate = model_path if model_path.is_absolute() else Path.cwd() / model_path
    if not candidate.exists():
        parent = candidate.parent if candidate.parent.exists() else Path.cwd()
        possibles = sorted(
            p for p in parent.iterdir()
            if p.is_dir() and (p / "config.json").exists()
        )
        print(f"❌ Model path not found: {candidate}")
        if possibles:
            print("Available checkpoints in parent directory:")
            for p in possibles:
                print(f"  - {p}")
        raise typer.Exit(code=1)


    resolved_model_path = candidate.resolve()

    print("--- 💬 Bantam Chat Interface ---")
    print(f"Loading model from: {resolved_model_path} (format={format})")

    try:
        # One loader for both full models and LoRA adapters
        bc = BantamChat.from_pretrained(str(resolved_model_path), try_merge_lora=True)

        # quick summary
        total_params = sum(p.numel() for p in bc.model.parameters())
        trainable_params = sum(p.numel() for p in bc.model.parameters() if p.requires_grad)
        print("--- Model Summary ---")
        print(f"Total Parameters:   {total_params/1e6:.2f}M")
        print(f"Trainable Params:   {trainable_params/1e6:.2f}M")
        print("---------------------")

        gen_cfg = GenerateConfig(
            max_new_tokens=max_new_tokens,
            temperature=temp,
            top_p=0.9,
            do_sample=(temp > 0.0),
        )

        fmt = format.value
        if fmt == "chat":
            print("Type 'exit' or 'quit' to end the session.")
            history: List[Dict[str, str]] = []
            if system_prompt:
                history.append({"role": "system", "content": system_prompt})

            while True:
                user_input = input("\n> You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                history.append({"role": "user", "content": user_input})

                print("\n> Bantam: ", end="", flush=True)
                stream = bc.stream(format="chat", messages=history, gen=gen_cfg)
                # live print streaming pieces
                response_chunks = []
                for piece in stream:
                    response_chunks.append(piece)
                    print(piece, end="", flush=True)

                # finalize cleaned text
                response = bc.generate(format="chat", messages=history, gen=gen_cfg) \
                           if False else "".join(response_chunks)
                # Post-trim to be safe
                for s in [BantamTokenizerUtils.AGENT_END, BantamTokenizerUtils.EOS]:
                    response = response.replace(s, "")
                response = response.strip()
                print("")  # newline after model output

                history.append({"role": "agent", "content": response})

        else:
            print("Plain LM mode. Type 'exit' or 'quit' to end.")
            while True:
                user_input = input("\n> Prompt: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                print("\n> Model: ", end="", flush=True)
                stream = bc.stream(format="pretrain", prompt=user_input, gen=gen_cfg)
                for piece in stream:
                    print(piece, end="", flush=True)
                print("")

    except Exception as e:
        print(f"\n❌ An error occurred during chat setup or inference: {e}")
        traceback.print_exc()
        raise typer.Exit(code=1)


# ---- tool integrations ----
app.command(name="export-onnx")(export_onnx_command)


if __name__ == "__main__":
    app()
