import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, IterableDataset
from torch.amp import GradScaler, autocast
from torch.optim.lr_scheduler import LambdaLR

import json
import re
import random
import time
import traceback
import math
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, List, Dict, Generator, Any, Iterable
import shutil
import csv
import numpy as np

from textwrap import shorten

# External libraries
from tqdm import tqdm
import matplotlib.pyplot as plt
from datasets import load_dataset
from transformers import AutoTokenizer, PreTrainedTokenizerBase, PreTrainedTokenizerFast
from peft import LoraConfig, get_peft_model

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel as ByteLevelPreTokenizer
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.normalizers import Sequence, NFKC, Lowercase, StripAccents, Strip
from tokenizers.trainers import BpeTrainer

from .optimizer import build_optimizer


# Import Bantam components
from .configuration_bantam import BantamConfig
from .modeling_bantam import BantamForCausalLM
from .tokenization_bantam import BantamTokenizerUtils as U, get_default_tokenizer_dir

DEFAULT_TOKENIZER_DIR = str(get_default_tokenizer_dir())


def _from_pretrained_with_dtype(loader, *args, dtype=None, **kwargs):
    if dtype is None:
        return loader(*args, **kwargs)
    try:
        return loader(*args, dtype=dtype, **kwargs)
    except TypeError:
        return loader(*args, torch_dtype=dtype, **kwargs)


@dataclass
class TrainingArgs:
    # IO
    dataset: str = "./data/EnglishMini.jsonl"     # JSONL path (pretrain or SFT)
    tokenizer: str = DEFAULT_TOKENIZER_DIR
    out_dir: str = "./models"

    # HF dataset support
    use_hf: bool = False               # turn on to use a Hugging Face dataset
    hf_name: Optional[str] = None      # e.g. "c4", "openwebtext", "lmsys/sharegpt"
    hf_subset: Optional[str] = None    # e.g. "en" for c4/en
    hf_split: str = "train"            # "train", "validation", etc.
    hf_streaming: bool = True          # stream instead of loading into memory
    hf_text_field: str = "text"        # for pretraining corpora
    hf_messages_field: str = "messages"  # for chat/SFT corpora ("messages" or "conversations")
    shuffle_buffer_size: int = 10_000  # streaming shuffle buffer (HF datasets)

    # Repro & init
    seed: int = 1337
    init_from_checkpoint: Optional[str] = None
    finetune_from: Optional[str] = None
    strict_vocab_match: bool = False
    save_tag: Optional[str] = None
    # Checkpointing
    save_every_n: Optional[int] = None   # save checkpoint every N optimizer steps (None disables)
    keep_last_k: Optional[int] = None    # keep only last K checkpoints (None disables pruning)
    save_on_improve: bool = False        # if true, only save when loss improves by at least improve_delta
    improve_delta: float = 0.0           # minimum improvement in loss to trigger save when save_on_improve
    resume_from_checkpoint: Optional[str] = None  # path to a checkpoint dir to resume from
    log_loss_to_csv: bool = False        # append per-step loss rows to CSV under out_dir/logs
    # Local JSONL dataset parsing (pretrain)
    dataset_text_field: str = "text"     # key to read from local .jsonl records
    min_sample_token_length: int = 8     # skip samples shorter than this many tokens
    resume_from_checkpoint: Optional[str] = None  # path to a checkpoint dir to resume from

    # Precision
    precision: str = "bf16"

    # Optim
    optimizer: str = "muon"
    lr: float = 5e-5
    weight_decay: float = 0.10
    beta2: float = 0.95
    adam_eps: float = 1e-8
    grad_clip: float = 1.0
    optim_eps: Optional[float] = None
    lr_scheduler: str = "cosine"
    min_lr_ratio: float = 0.0
    muon_lr: Optional[float] = None
    muon_momentum: float = 0.95
    muon_exclude_embeddings: bool = True
    muon_beta1: Optional[float] = None
    muon_beta2: Optional[float] = None
    muon_eps: Optional[float] = None
    muon_bias_correction: bool = True
    muon_clip_by_layer: bool = False
    muon_lr_correction: bool = True

    # Batching / schedule
    batch_size: int = 1
    accum_steps: int = 32
    epochs: int = 3
    warmup_frac: float = 0.10
    log_every_n: int = 10
    steps_per_epoch: Optional[int] = None   # REQUIRED when streaming (no __len__)
    overfit_subset: Optional[int] = None    # head() limit for debugging (records, not blocks)

    # Memory
    use_gradient_checkpoint: bool = False

    # Dataloader
    num_workers: int = 2
    pin_memory: bool = True
    persistent_workers: bool = True

    # SFT-only knobs
    sft_mode: str = "lora"
    lora_r: int = 64
    lora_alpha: int = 96
    lora_dropout: float = 0.05
    include_agent_end: bool = True
    include_eos: bool = False
    mask_user_queries: bool = True

    # path resolver
    def resolve_paths(self, cfg_path: Path):
        base = cfg_path.parent
        for f in ("dataset", "tokenizer", "out_dir", "init_from_checkpoint", "finetune_from"):
            val = getattr(self, f, None)
            if val:
                p = Path(val)
                if not p.is_absolute():
                    setattr(self, f, str((base / p).resolve()))


class BlockDataset(Dataset):
    """
    Packs fixed-length blocks for pretraining.
    """
    def __init__(self, packed_blocks: List[List[int]]):
        self.packed_blocks = packed_blocks

    def __len__(self):
        return len(self.packed_blocks)

    def __getitem__(self, idx):
        return {"input_ids": self.packed_blocks[idx]}

    @classmethod
    def from_file(
        cls,
        path: str,
        seq_len: int,
        tokenizer: PreTrainedTokenizerBase,
        seed: int,
        overfit_subset: Optional[int] = None,
        *,
        text_field: str = "text",
        min_sample_token_length: int = 1,
    ):
        if not Path(path).exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")

        ftype = "json" if path.endswith(".jsonl") else "text"
        ds = load_dataset(ftype, data_files={"train": path}, split="train").shuffle(seed=seed)
        if overfit_subset:
            ds = ds.select(range(overfit_subset))

        buffer: List[int] = []
        packed_blocks: List[List[int]] = []
        skipped_empty = 0
        skipped_short = 0
        for sample in tqdm(ds, desc="Packing dataset"):
            text = sample.get(text_field, "")
            if not isinstance(text, str) or not text.strip():
                skipped_empty += 1
                continue
            formatted_text = U.format_pretrain_text(text, include_eos=True)
            ids = tokenizer.encode(formatted_text, add_special_tokens=False)
            if len(ids) < int(min_sample_token_length):
                skipped_short += 1
                continue
            buffer.extend(ids)

            while len(buffer) >= seq_len:
                chunk = buffer[:seq_len]
                buffer = buffer[seq_len:]
                packed_blocks.append(list(chunk))

        random.seed(seed)
        random.shuffle(packed_blocks)
        if skipped_empty or skipped_short:
            print(f"[BlockDataset] Skipped {skipped_empty} empty and {skipped_short} short samples (field='{text_field}').")
        return cls(packed_blocks)

@dataclass
class DataCollatorForSFT:
    pad_token_id: int
    pad_to_multiple_of: Optional[int] = 8  # set to None at BS=1 to avoid padding

    def __call__(self, features):
        input_ids = [f["input_ids"] for f in features]
        labels    = [f["labels"]    for f in features]
        attn      = [f["attention_mask"] for f in features]
        p_len     = [f["prompt_len"] for f in features]
        lmask     = [f["loss_mask"]  for f in features]

        # Skip multiple-of padding for BS=1 (no kernel benefit, saves tokens)
        eff_mult = self.pad_to_multiple_of if len(features) > 1 else None

        def _pad(seq_list, pad_value):
            padded = nn.utils.rnn.pad_sequence(seq_list, batch_first=True, padding_value=pad_value)
            if eff_mult:
                L = padded.size(1); m = eff_mult
                if L % m != 0:
                    extra = m - (L % m)
                    pad = torch.full((padded.size(0), extra), pad_value, dtype=padded.dtype, device=padded.device)
                    padded = torch.cat([padded, pad], dim=1)
            return padded

        return {
            "input_ids": _pad(input_ids, self.pad_token_id),
            "labels":    _pad(labels, -100),
            "attention_mask": _pad(attn, False),
            "prompt_len": torch.stack(p_len, dim=0),
            "loss_mask":  _pad(lmask, 0.0).to(torch.float32),
        }

class ChatSFTDatasetV2(Dataset):
    """
    Builds prompt/target pairs for SFT that truly instruction-tune.

    - The *entire* conversation sample is wrapped with <|BOS|> ... <|EOS|>
    - Prompt ALWAYS ends with <|AGENT_START|>
    - Supervise assistant content + <|AGENT_END|> + <|EOS|>
    - Turn-aware truncation: preserves the final user turn (when possible)
      and never trims away the trailing <|AGENT_START|> in the prompt
    - Returns prompt_len and loss_mask; optional upweight of last turn
    """
    def __init__(
        self,
        path: str,
        tokenizer,
        max_len: int,
        include_agent_end: bool = True,
        include_eos: bool = True,       # enforce EOS at end of sample
        min_target_tokens: int = 4,
        last_turn_weight: float = 1.0,  # 1.0 = no extra weight
        mask_user_queries: bool = True,
    ):
        self.tok = tokenizer
        self.max_len = int(max_len)
        self.include_agent_end = bool(include_agent_end)
        self.include_eos = bool(include_eos)
        self.min_target_tokens = int(min_target_tokens)
        self.last_turn_weight = float(last_turn_weight)
        self.mask_user_queries = bool(mask_user_queries)

        raw = [json.loads(line) for line in Path(path).read_text().splitlines()]
        self.samples = []

        def _norm(msgs: List[Dict[str, str]]) -> List[Dict[str, str]]:
            out = []
            for m in msgs:
                if not isinstance(m, dict):
                    continue
                role = m.get("role")
                content = m.get("content", "")
                # ShareGPT-style fallback
                if role is None and "from" in m and "value" in m:
                    role = "user" if m["from"] in {"human", "user"} else "assistant"
                    content = m.get("value", "")
                role = "agent" if role == "assistant" else role
                if role not in {"user", "agent"}:  # treat system/developer as user preamble
                    role = "user"
                out.append({"role": role, "content": content})
            return out

        for s in raw:
            msgs = _norm(s.get("messages", []))
            last_agent = max((i for i, m in enumerate(msgs) if m.get("role") == "agent"), default=-1)
            if last_agent <= 0:
                continue
            if not (msgs[last_agent].get("content") or "").strip():
                continue
            self.samples.append({"messages": msgs, "last_idx": last_agent})

        if not self.samples:
            raise ValueError("No valid SFT samples with a non-empty agent reply found.")

        # sanity: required special tokens exist
        for tok_text in (U.BOS, U.EOS, U.AGENT_START, U.AGENT_END, U.USER_START, U.USER_END):
            tid = self.tok.convert_tokens_to_ids(tok_text)
            if tid is None or tid < 0:
                raise ValueError(f"Special token not found in tokenizer vocab: {tok_text}")

        # Precompute special token id lists (avoid re-encoding every item)
        self._ids = {
            "BOS": self.tok(U.BOS, add_special_tokens=False)["input_ids"],
            "EOS": self.tok(U.EOS, add_special_tokens=False)["input_ids"],
            "AS":  self.tok(U.AGENT_START, add_special_tokens=False)["input_ids"],
            "US":  self.tok(U.USER_START, add_special_tokens=False)["input_ids"],
            "AE":  self.tok(U.AGENT_END, add_special_tokens=False)["input_ids"],
        }

    def __len__(self):
        return len(self.samples)

    def _encode(self, s: str) -> List[int]:
        return self.tok(s, add_special_tokens=False)["input_ids"]

    @staticmethod
    def _last_occurrence(ids: List[int], needle: List[int]) -> int:
        for k in range(len(ids) - len(needle), -1, -1):
            if ids[k:k+len(needle)] == needle:
                return k
        return -1

    def __getitem__(self, idx):
        ex = self.samples[idx]
        msgs = ex["messages"]
        j = ex["last_idx"]

        ctx_msgs  = msgs[:j]
        agent_msg = msgs[j]

        # Build context (starts with <|BOS|>), then append AGENT_START manually.
        # Do NOT add EOS here, or you'd close the conversation before the answer.
        ctx_str    = U.format_chat_turns(ctx_msgs, include_eos=False)  # includes BOS at the very start
        prompt_str = ctx_str + U.AGENT_START
        prompt_ids = self._encode(prompt_str)

        # Ensure BOS is at the very start (defensive)
        bos_ids = self._ids["BOS"]
        if not (len(prompt_ids) >= len(bos_ids) and prompt_ids[:len(bos_ids)] == bos_ids):
            prompt_ids = bos_ids + prompt_ids

        as_ids = self._ids["AS"]

        # Target (assistant answer [+ AGENT_END]) + optional EOS
        target_core_text = (agent_msg.get("content", "") or "")
        if self.include_agent_end:
            target_core_text += U.AGENT_END
        target_core_ids = self._encode(target_core_text)

        eos_ids = self._ids["EOS"] if self.include_eos else []

        input_ids = prompt_ids + target_core_ids + eos_ids

        # Turn-aware truncation (preserve last user turn, keep trailing AGENT_START, keep EOS)
        if len(input_ids) > self.max_len:
            excess = len(input_ids) - self.max_len
            us_ids = self._ids["US"]

            # Safe left trim region of the prompt:
            #   [BOS][ ... allowed-to-drop ... ][AGENT_START]
            last_user_idx  = self._last_occurrence(prompt_ids, us_ids)
            must_keep_tail = len(as_ids)
            left_drop_cap  = max(0, len(prompt_ids) - len(bos_ids) - must_keep_tail)
            if last_user_idx >= 0:
                cap_by_last_user = max(0, last_user_idx - len(bos_ids))
                left_drop_cap = min(left_drop_cap, cap_by_last_user)

            drop_left = min(excess, left_drop_cap)
            if drop_left > 0:
                prompt_ids = bos_ids + prompt_ids[len(bos_ids) + drop_left:]
                excess -= drop_left

            if excess > 0:
                # Trim target_core from the right, keep EOS
                keep_core = max(0, len(target_core_ids) - excess)
                keep_core = max(keep_core, max(0, self.min_target_tokens - len(eos_ids)))
                target_core_ids = target_core_ids[:keep_core]
                excess = 0

            input_ids = prompt_ids + target_core_ids + eos_ids

            if len(input_ids) > self.max_len:
                # Last resort: drop more left of prompt (after BOS, before AGENT_START)
                overflow = len(input_ids) - self.max_len
                safe_room = max(0, len(prompt_ids) - len(bos_ids) - must_keep_tail)
                drop2 = min(overflow, safe_room)
                if drop2 > 0:
                    prompt_ids = bos_ids + prompt_ids[len(bos_ids) + drop2:]
                    input_ids = prompt_ids + target_core_ids + eos_ids
                if len(input_ids) > self.max_len:
                    # Keep rightmost to ensure EOS remains
                    input_ids = input_ids[-self.max_len:]
                    # Try to enforce BOS at the front if possible
                    if not (len(input_ids) >= len(bos_ids) and input_ids[:len(bos_ids)] == bos_ids):
                        if len(bos_ids) <= len(input_ids):
                            input_ids[:len(bos_ids)] = bos_ids

        # Compute prompt_len = position right after the last AGENT_START
        as_pos = self._last_occurrence(input_ids, as_ids)
        if as_pos < 0:
            prompt_len = min(len(prompt_ids), len(input_ids))
        else:
            prompt_len = min(as_pos + len(as_ids), len(input_ids))

        labels = [-100] * prompt_len + input_ids[prompt_len:]
        attn   = [True] * len(input_ids)

        # Optional sanity checks (enable while debugging)
        # if self.include_eos:
        #     assert input_ids[:len(bos_ids)] == bos_ids, "Sample must start with BOS"
        #     assert input_ids[-len(self._ids['EOS']):] == self._ids['EOS'], "Sample must end with EOS"

        if self.mask_user_queries:
            loss_mask = [0.0] * prompt_len + [1.0] * (len(input_ids) - prompt_len)
        else:
            loss_mask = [1.0] * len(input_ids)
        if self.last_turn_weight != 1.0 and (len(input_ids) - prompt_len) > 0:
            loss_mask[prompt_len:] = [self.last_turn_weight] * (len(input_ids) - prompt_len)

        return {
            "input_ids":  torch.tensor(input_ids, dtype=torch.long),
            "labels":     torch.tensor(labels,    dtype=torch.long),
            "attention_mask": torch.tensor(attn, dtype=torch.bool),
            "prompt_len": torch.tensor(prompt_len, dtype=torch.long),
            "loss_mask":  torch.tensor(loss_mask, dtype=torch.float32),
        }
    
class HFBlockIterableDataset(IterableDataset):
    """
    Streams a HF dataset and yields fixed-length blocks of token ids for pretraining.
    - Uses on-the-fly tokenization and packing (no full corpus in memory).
    - Shuffles with a streaming buffer.
    """
    def __init__(
        self,
        name: str,
        subset: Optional[str],
        split: str,
        tokenizer: PreTrainedTokenizerBase,
        seq_len: int,
        text_field: str = "text",
        seed: int = 1337,
        buffer_size: int = 10_000,
        streaming: bool = True,
        overfit_subset: Optional[int] = None,  
    ):
        self.name = name
        self.subset = subset
        self.split = split
        self.tokenizer = tokenizer
        self.seq_len = int(seq_len)
        self.text_field = text_field
        self.seed = int(seed)
        self.buffer_size = int(buffer_size)
        self.streaming = bool(streaming)
        self.overfit_subset = overfit_subset

        ds = load_dataset(self.name, name=self.subset, split=self.split, streaming=self.streaming)
        ds = ds.shuffle(seed=self.seed, buffer_size=self.buffer_size)
        self.ds = ds

    def __iter__(self):
        rng = random.Random(self.seed)
        token_buffer: List[int] = []
        seen = 0

        for sample in self.ds:
            if self.overfit_subset is not None and seen >= self.overfit_subset:
                break
            text = sample.get(self.text_field, "")
            if not isinstance(text, str) or not text.strip():
                continue
            formatted_text = U.format_pretrain_text(text, include_eos=True)
            ids = self.tokenizer.encode(formatted_text, add_special_tokens=False)
            if len(ids) < 1:
                continue
            token_buffer.extend(ids)
            seen += 1

            while len(token_buffer) >= self.seq_len:
                chunk = token_buffer[:self.seq_len]
                token_buffer = token_buffer[self.seq_len:]
                yield {"input_ids": list(chunk)}

class HFChatSFTIterableDataset(IterableDataset):
    """
    Streams a HF chat/instruction dataset and yields tokenized examples for SFT.
    - Normalizes roles to {user, agent}
    - Emits samples wrapped with <|BOS|> ... <|EOS|>
    - Ensures prompt ends with <|AGENT_START|>
    - Turn-aware truncation that preserves the final user turn
    - Emits prompt_len and loss_mask (optionally upweight last turn)
    """
    def __init__(
        self,
        name: str,
        subset: Optional[str],
        split: str,
        tokenizer: PreTrainedTokenizerBase,
        max_len: int,
        messages_field: str = "messages",
        include_agent_end: bool = True,
        include_eos: bool = True,
        seed: int = 1337,
        buffer_size: int = 10_000,
        streaming: bool = True,
        overfit_subset: Optional[int] = None,
        min_target_tokens: int = 4,
        last_turn_weight: float = 1.0,
        mask_user_queries: bool = True,
    ):
        self.name = name
        self.subset = subset
        self.split = split
        self.tok = tokenizer
        self.max_len = int(max_len)
        self.messages_field = messages_field
        self.include_agent_end = bool(include_agent_end)
        self.include_eos = bool(include_eos)
        self.seed = int(seed)
        self.buffer_size = int(buffer_size)
        self.streaming = bool(streaming)
        self.overfit_subset = overfit_subset
        self.min_target_tokens = int(min_target_tokens)
        self.last_turn_weight = float(last_turn_weight)
        self.mask_user_queries = bool(mask_user_queries)

        ds = load_dataset(self.name, name=self.subset, split=self.split, streaming=self.streaming)
        self.ds = ds.shuffle(seed=self.seed, buffer_size=self.buffer_size)

        # sanity: required special tokens exist
        for tok_text in (U.BOS, U.EOS, U.AGENT_START, U.AGENT_END, U.USER_START, U.USER_END):
            tid = self.tok.convert_tokens_to_ids(tok_text)
            if tid is None or tid < 0:
                raise ValueError(f"Special token not found in tokenizer vocab: {tok_text}")

        # Precompute special ids
        self._ids = {
            "BOS": self.tok(U.BOS, add_special_tokens=False)["input_ids"],
            "EOS": self.tok(U.EOS, add_special_tokens=False)["input_ids"],
            "AS":  self.tok(U.AGENT_START, add_special_tokens=False)["input_ids"],
            "US":  self.tok(U.USER_START, add_special_tokens=False)["input_ids"],
        }

    def _encode(self, s: str) -> List[int]:
        return self.tok(s, add_special_tokens=False)["input_ids"]

    @staticmethod
    def _normalize_messages(raw_msgs: Any) -> List[Dict[str, str]]:
        msgs = []
        if not isinstance(raw_msgs, list):
            return msgs
        for m in raw_msgs:
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            content = m.get("content")
            if role is None and content is None:
                _from = m.get("from")
                content = m.get("value", "")
                role = "user" if _from in {"human", "user"} else "assistant"
            role = "agent" if role == "assistant" else role
            if role not in {"user", "agent"}:
                role = "user"
            msgs.append({"role": role, "content": (content or "")})
        return msgs

    @staticmethod
    def _last_occurrence(ids: List[int], needle: List[int]) -> int:
        for k in range(len(ids) - len(needle), -1, -1):
            if ids[k:k+len(needle)] == needle:
                return k
        return -1

    def __iter__(self):
        seen = 0
        bos_ids = self._ids["BOS"]
        eos_ids = self._ids["EOS"]
        as_ids  = self._ids["AS"]
        us_ids  = self._ids["US"]

        for rec in self.ds:
            if self.overfit_subset is not None and seen >= self.overfit_subset:
                break
            msgs = self._normalize_messages(rec.get(self.messages_field, []))

            last_agent = max((i for i, m in enumerate(msgs) if m.get("role") == "agent"), default=-1)
            if last_agent <= 0:
                continue
            if not (msgs[last_agent].get("content") or "").strip():
                continue

            ctx_msgs  = msgs[:last_agent]
            agent_msg = msgs[last_agent]

            # Context + AGENT_START (no EOS here)
            ctx_str    = U.format_chat_turns(ctx_msgs, include_eos=False)
            prompt_str = ctx_str + U.AGENT_START
            prompt_ids = self._encode(prompt_str)

            # Ensure BOS sits at the front
            if not (len(prompt_ids) >= len(bos_ids) and prompt_ids[:len(bos_ids)] == bos_ids):
                prompt_ids = bos_ids + prompt_ids

            # Target (+AGENT_END) + EOS
            target_text = (agent_msg.get("content") or "")
            if self.include_agent_end:
                target_text += U.AGENT_END
            target_ids = self._encode(target_text)
            end_ids    = eos_ids if self.include_eos else []

            input_ids = prompt_ids + target_ids + end_ids

            # Turn-aware truncation
            if len(input_ids) > self.max_len:
                excess = len(input_ids) - self.max_len
                must_keep_tail = len(as_ids)
                left_drop_cap  = max(0, len(prompt_ids) - len(bos_ids) - must_keep_tail)
                last_user_idx  = self._last_occurrence(prompt_ids, us_ids)
                if last_user_idx >= 0:
                    cap_by_last_user = max(0, last_user_idx - len(bos_ids))
                    left_drop_cap = min(left_drop_cap, cap_by_last_user)

                drop_left = min(excess, left_drop_cap)
                if drop_left > 0:
                    prompt_ids = bos_ids + prompt_ids[len(bos_ids) + drop_left:]
                    excess -= drop_left

                if excess > 0:
                    keep_core = max(0, len(target_ids) - excess)
                    keep_core = max(keep_core, max(0, self.min_target_tokens - len(end_ids)))
                    target_ids = target_ids[:keep_core]
                    excess = 0

                input_ids = prompt_ids + target_ids + end_ids

                if len(input_ids) > self.max_len:
                    overflow = len(input_ids) - self.max_len
                    safe_room = max(0, len(prompt_ids) - len(bos_ids) - must_keep_tail)
                    drop2 = min(overflow, safe_room)
                    if drop2 > 0:
                        prompt_ids = bos_ids + prompt_ids[len(bos_ids) + drop2:]
                        input_ids = prompt_ids + target_ids + end_ids
                    if len(input_ids) > self.max_len:
                        input_ids = input_ids[-self.max_len:]
                        if not (len(input_ids) >= len(bos_ids) and input_ids[:len(bos_ids)] == bos_ids):
                            if len(bos_ids) <= len(input_ids):
                                input_ids[:len(bos_ids)] = bos_ids

            as_pos = self._last_occurrence(input_ids, as_ids)
            prompt_len = (as_pos + len(as_ids)) if as_pos >= 0 else min(len(prompt_ids), len(input_ids))

            labels = [-100] * prompt_len + input_ids[prompt_len:]
            attn   = [True] * len(input_ids)

            # Optional sanity checks
            # if self.include_eos:
            #     assert input_ids[:len(bos_ids)] == bos_ids
            #     assert input_ids[-len(eos_ids):] == eos_ids

            if self.mask_user_queries:
                loss_mask = [0.0] * prompt_len + [1.0] * (len(input_ids) - prompt_len)
            else:
                loss_mask = [1.0] * len(input_ids)
            if self.last_turn_weight != 1.0 and (len(input_ids) - prompt_len) > 0:
                loss_mask[prompt_len:] = [self.last_turn_weight] * (len(input_ids) - prompt_len)

            seen += 1
            yield {
                "input_ids":  torch.tensor(input_ids, dtype=torch.long),
                "labels":     torch.tensor(labels,    dtype=torch.long),
                "attention_mask": torch.tensor(attn, dtype=torch.bool),
                "prompt_len": torch.tensor(prompt_len, dtype=torch.long),
                "loss_mask":  torch.tensor(loss_mask, dtype=torch.float32),
            }


class BantamTrainer:
    """Helper methods for training/finetuning the Bantam model."""

    @staticmethod
    def train_bpe_tokenizer(
        input_paths: Iterable[Path],
        output_dir: Path,
        *,
        text_field: str = "text",
        vocab_size: int = 49152,
        min_frequency: int = 2,
        lowercase: bool = False,
        strip_accents: bool = False,
        limit_alphabet: Optional[int] = None,
        max_samples: Optional[int] = None,
        show_progress: bool = True,
        regex_clean: bool = True,
        regex_symbols: str = "?-*=+!@#$%^&()[]{}<>/\\|:;.,~`\"'",
        digit_group_size: int = 2,
    ) -> Dict[str, Any]:
        """Train a Byte-Level BPE tokenizer from one or more JSONL files."""

        resolved_files: List[Path] = []
        for raw_path in input_paths:
            path = Path(raw_path)
            if path.is_dir():
                resolved_files.extend(sorted(p for p in path.glob("*.jsonl") if p.is_file()))
            else:
                resolved_files.append(path)

        # Normalize, dedupe, and validate.
        uniq_files: List[Path] = []
        seen = set()
        for fp in resolved_files:
            abs_fp = fp.resolve()
            if abs_fp in seen:
                continue
            if not abs_fp.exists():
                raise FileNotFoundError(f"Dataset file not found: {abs_fp}")
            if not abs_fp.is_file():
                raise ValueError(f"Expected a file, got: {abs_fp}")
            seen.add(abs_fp)
            uniq_files.append(abs_fp)

        if not uniq_files:
            raise ValueError("No input JSONL files provided for tokenizer training.")

        if max_samples is not None and max_samples <= 0:
            raise ValueError("max_samples must be positive when provided.")
        if limit_alphabet is not None and limit_alphabet <= 0:
            raise ValueError("limit_alphabet must be positive when provided.")
        if digit_group_size is not None and digit_group_size <= 0:
            raise ValueError("digit_group_size must be positive.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        special_tokens = U.get_special_tokens()
        core_tokens = {U.UNK, U.PAD, U.BOS, U.EOS}
        additional_specials = [tok for tok in special_tokens if tok not in core_tokens]

        tokenizer = Tokenizer(BPE(unk_token=U.UNK))
        tokenizer.pre_tokenizer = ByteLevelPreTokenizer()

        normalizers = [NFKC()]
        if lowercase:
            normalizers.append(Lowercase())
        if strip_accents:
            normalizers.append(StripAccents())
        if regex_clean:
            normalizers.append(Strip())
        tokenizer.normalizer = Sequence(normalizers) if len(normalizers) > 1 else normalizers[0]

        tokenizer.decoder = ByteLevelDecoder()

        trainer_kwargs = dict(
            vocab_size=int(vocab_size),
            min_frequency=int(min_frequency),
            special_tokens=special_tokens,
            show_progress=show_progress,
        )
        if limit_alphabet is not None:
            trainer_kwargs["limit_alphabet"] = int(limit_alphabet)

        trainer = BpeTrainer(**trainer_kwargs)

        stats = {
            "files": [str(p) for p in uniq_files],
            "lines_total": 0,
            "records_used": 0,
            "skipped_empty": 0,
            "skipped_missing_field": 0,
            "skipped_json_error": 0,
        }

        symbol_pattern = re.compile(f"([{re.escape(regex_symbols)}])") if (regex_clean and regex_symbols) else None
        digit_pattern = (
            re.compile(rf"(\d{{{digit_group_size}}})(?=\d)") if (regex_clean and digit_group_size is not None) else None
        )

        def _python_regex_clean(s: str) -> str:
            if symbol_pattern is not None:
                s = symbol_pattern.sub(r" \1 ", s)
            if digit_pattern is not None:
                s = digit_pattern.sub(r"\1 ", s)
            if regex_clean:
                s = re.sub(r"\s{2,}", " ", s)
                s = s.strip()
            return s

        def sample_iterator():
            for jsonl_path in uniq_files:
                with open(jsonl_path, "r", encoding="utf-8") as handle:
                    for line in handle:
                        stats["lines_total"] += 1
                        raw = line.strip()
                        if not raw:
                            stats["skipped_empty"] += 1
                            continue
                        try:
                            record = json.loads(raw)
                        except json.JSONDecodeError:
                            stats["skipped_json_error"] += 1
                            continue

                        value = record.get(text_field)
                        if not isinstance(value, str):
                            stats["skipped_missing_field"] += 1
                            continue

                        text = value.strip()
                        if regex_clean:
                            text = _python_regex_clean(text)
                        if not text:
                            stats["skipped_empty"] += 1
                            continue

                        stats["records_used"] += 1
                        yield text

                        if max_samples is not None and stats["records_used"] >= max_samples:
                            return

        tokenizer.train_from_iterator(
            sample_iterator(),
            trainer=trainer,
            length=max_samples if max_samples is not None else None,
        )

        hf_tokenizer = PreTrainedTokenizerFast(
            tokenizer_object=tokenizer,
            bos_token=U.BOS,
            eos_token=U.EOS,
            unk_token=U.UNK,
            pad_token=U.PAD,
            additional_special_tokens=additional_specials,
            model_max_length=16_384,
        )
        hf_tokenizer.padding_side = "right"
        hf_tokenizer.truncation_side = "right"
        hf_tokenizer.clean_up_tokenization_spaces = False

        hf_tokenizer.save_pretrained(output_dir)

        metadata = {
            "vocab_size_target": int(vocab_size),
            "vocab_size_actual": int(len(hf_tokenizer)),
            "min_frequency": int(min_frequency),
            "lowercase": bool(lowercase),
            "strip_accents": bool(strip_accents),
            "limit_alphabet": limit_alphabet,
            "text_field": text_field,
            "max_samples": max_samples,
            "regex_clean": bool(regex_clean),
            "regex_symbols": regex_symbols,
            "digit_group_size": int(digit_group_size),
            "stats": stats,
        }

        with open(output_dir / "bpe_training_args.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "output_dir": str(output_dir.resolve()),
            "metadata_path": str((output_dir / "bpe_training_args.json").resolve()),
            "vocab_size": int(len(hf_tokenizer)),
            "records_used": stats["records_used"],
            "records_skipped": stats["skipped_empty"]
            + stats["skipped_missing_field"]
            + stats["skipped_json_error"],
            "skipped_breakdown": {
                "empty": stats["skipped_empty"],
                "missing_field": stats["skipped_missing_field"],
                "json_error": stats["skipped_json_error"],
            },
        }

    @staticmethod
    def _build_optimizer(model: nn.Module, targs: TrainingArgs) -> Tuple[torch.optim.Optimizer, str]:
        return build_optimizer(model, targs)

    @staticmethod
    def _build_scheduler(
        optimizer: torch.optim.Optimizer,
        targs: TrainingArgs,
        warmup_steps: int,
        total_steps: int,
    ) -> Tuple[LambdaLR, str]:
        total_steps = max(int(total_steps), 1)
        warmup_steps = max(int(warmup_steps), 0)
        sched_name = (targs.lr_scheduler or "cosine").strip().lower()
        min_ratio = max(0.0, float(getattr(targs, "min_lr_ratio", 0.0) or 0.0))

        if sched_name in {"cosine", "cosine_decay", "cosineanneal"}:
            decay_steps = max(1, total_steps - warmup_steps)

            def lr_lambda(step: int) -> float:
                if warmup_steps > 0 and step < warmup_steps:
                    return float(step) / float(max(1, warmup_steps))
                progress = float(step - warmup_steps) / float(decay_steps)
                progress = min(max(progress, 0.0), 1.0)
                cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
                return min_ratio + (1.0 - min_ratio) * cosine

            scheduler = LambdaLR(optimizer, lr_lambda)
            msg = f"📉 LR scheduler: cosine (warmup={warmup_steps:,}, min_lr_ratio={min_ratio:.4f})"
            return scheduler, msg

        if sched_name in {"constant", "none", "fixed"}:
            scheduler = LambdaLR(optimizer, lambda _: 1.0)
            msg = "📉 LR scheduler: constant (no decay)"
            return scheduler, msg

        raise ValueError(f"Unknown lr_scheduler '{targs.lr_scheduler}'. Supported: cosine, constant.")

    @staticmethod
    def _count_params(model: nn.Module) -> Tuple[int, int]:
        total = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        return total, trainable

    @staticmethod
    def _effective_layer_settings(cfg) -> List[Dict[str, Any]]:
        """
        Build the effective config per layer (heads, kv, ff, window, + MoE).
        Falls back to global defaults when fields are missing.
        """
        n = int(getattr(cfg, "num_hidden_layers", 0))
        defaults = dict(
            heads=int(getattr(cfg, "num_attention_heads", 0)),
            kv=int(getattr(cfg, "num_key_value_heads", 0)),
            ff=int(getattr(cfg, "intermediate_size", 0)),
            window=None,
            attention_head_groups=getattr(cfg, "attention_head_groups", None),
            # --- MoE defaults (None => dense MLP) ---
            expert_type=None,
            num_experts=None,
            moe_top_k=None,
            moe_ff=None,
            moe_capacity_factor=None,
            moe_router_jitter=None,
            moe_drop_policy=None,
            moe_aux_loss_weight=None,
        )

        lcfgs = list(getattr(cfg, "layer_configs", []) or [])
        legacy_windows = list(getattr(cfg, "per_layer_window", []) or [])

        eff: List[Dict[str, Any]] = []
        for i in range(n):
            cur = dict(defaults)
            # Layer overrides
            if i < len(lcfgs) and lcfgs[i] is not None:
                d = lcfgs[i]
                if "num_attention_heads" in d and d["num_attention_heads"] is not None:
                    cur["heads"] = int(d["num_attention_heads"])
                if "num_key_value_heads" in d and d["num_key_value_heads"] is not None:
                    cur["kv"] = int(d["num_key_value_heads"])
                if "intermediate_size" in d and d["intermediate_size"] is not None:
                    cur["ff"] = int(d["intermediate_size"])
                if "window" in d:
                    cur["window"] = d["window"]  # may be None or int
                if "attention_head_groups" in d and d["attention_head_groups"] is not None:
                    cur["attention_head_groups"] = d["attention_head_groups"]

                # --- MoE fields (if present) ---
                et = d.get("expert_type", None)
                if et is not None:
                    cur["expert_type"] = str(et).lower()
                if d.get("num_experts") is not None:
                    cur["num_experts"] = int(d["num_experts"])
                if d.get("moe_top_k") is not None:
                    cur["moe_top_k"] = int(d["moe_top_k"])
                if d.get("moe_intermediate_size") is not None:
                    cur["moe_ff"] = int(d["moe_intermediate_size"])
                if d.get("moe_capacity_factor") is not None:
                    cur["moe_capacity_factor"] = float(d["moe_capacity_factor"])
                if d.get("moe_router_jitter") is not None:
                    cur["moe_router_jitter"] = float(d["moe_router_jitter"])
                if d.get("moe_drop_policy") is not None:
                    cur["moe_drop_policy"] = str(d["moe_drop_policy"])
                if d.get("moe_aux_loss_weight") is not None:
                    cur["moe_aux_loss_weight"] = float(d["moe_aux_loss_weight"])

            if cur["window"] is None and i < len(legacy_windows):
                cur["window"] = legacy_windows[i]

            # convenience flags / normalization
            et = (cur["expert_type"] or "").lower()
            cur["is_moe"] = et in {"switch", "topk", "sparse", "dense_moe"}
            if et == "sparse":
                cur["expert_type"] = "topk"
            if cur["expert_type"] == "switch":
                cur["moe_top_k"] = int(cur["moe_top_k"] or 1)

            eff.append(cur)
        return eff

    @staticmethod
    def _arch_report(model) -> str:
        cfg = model.config
        H  = int(getattr(cfg, "hidden_size", 0))
        HD = int(getattr(cfg, "head_dim", 0))

        def _format_head_groups(groups):
            if not groups:
                return None
            parts = []
            for g in groups:
                if g is None:
                    continue
                q = g.get("query_heads") or g.get("num_query_heads")
                kv = g.get("kv_heads") or g.get("num_kv_heads") or g.get("num_key_value_heads")
                hd = g.get("head_dim")
                if q is None or hd is None:
                    continue
                kv_suffix = f"/kv{int(kv)}" if kv is not None else ""
                parts.append(f"{int(q)}x{int(hd)}{kv_suffix}")
            return "[" + ", ".join(parts) + "]" if parts else None

        lines = []
        lines.append("🧩 Model topology")
        lines.append(
            "  defaults: "
            f"hidden_size={cfg.hidden_size}  head_dim={cfg.head_dim}  "
            f"heads={cfg.num_attention_heads}  kv_heads={cfg.num_key_value_heads}  ff={cfg.intermediate_size}"
        )
        lines.append(
            f"  vocab_size={cfg.vocab_size}  max_pos={cfg.max_position_embeddings}  "
            f"rope_theta={getattr(cfg, 'rope_theta', None)}  rope_scaling={getattr(cfg, 'rope_scaling', None)}"
        )
        default_group_repr = _format_head_groups(getattr(cfg, "attention_head_groups", None))
        if default_group_repr:
            lines.append(f"  default head groups: {default_group_repr}")
        n_sinks = int(getattr(cfg, "num_attention_sinks", 0))
        sink_boost = float(getattr(cfg, "sink_boost", 0.0))
        lines.append(f"  sinks: {'disabled' if n_sinks <= 0 else f'count={n_sinks} boost={sink_boost}'}")

        backend_desc = "SDPA (CPU)"
        if torch.cuda.is_available():
            backends = []
            try:
                if torch.backends.cuda.flash_sdp_enabled():
                    backends.append("flash")
                if torch.backends.cuda.mem_efficient_sdp_enabled():
                    backends.append("mem_eff")
                if torch.backends.cuda.math_sdp_enabled() and not backends:
                    backends.append("math")
            except AttributeError:
                backends.append("cuda")
            backend_desc = "SDPA (" + ", ".join(backends) + ")"
        lines.append(f"  attention backend: {backend_desc}")

        eff = BantamTrainer._effective_layer_settings(cfg)

        windows = [e["window"] for e in eff]
        heads   = [e["heads"]  for e in eff]
        kvs     = [e["kv"]     for e in eff]
        ffs     = [e["ff"]     for e in eff]
        layer_group_repr = [_format_head_groups(e.get("attention_head_groups")) for e in eff]

        # Window stats
        full_ct  = sum(1 for w in windows if w is None)
        slide_ct = sum(1 for w in windows if isinstance(w, int) and w >= 1)
        slide_vals = [int(w) for w in windows if isinstance(w, int) and w >= 1]
        min_sw = min(slide_vals) if slide_vals else None
        max_sw = max(slide_vals) if slide_vals else None

        # Overrides summary (dense fields)
        def _is_uniform(vals, ref): return all(v == ref for v in vals)
        has_head_over = not _is_uniform(heads, int(getattr(cfg, "num_attention_heads", 0)))
        has_kv_over   = not _is_uniform(kvs,   int(getattr(cfg, "num_key_value_heads", 0)))
        has_ff_over   = not _is_uniform(ffs,   int(getattr(cfg, "intermediate_size", 0)))
        has_win_over  = (slide_ct > 0) or (full_ct < len(eff))
        has_group_over = any(gr != default_group_repr for gr in layer_group_repr)

        parts = []
        if has_head_over: parts.append(f"heads[{min(heads)}..{max(heads)}]")
        if has_kv_over:   parts.append(f"kv[{min(kvs)}..{max(kvs)}]")
        if has_ff_over:   parts.append(f"ff[{min(ffs)}..{max(ffs)}]")
        if has_win_over:
            if slide_vals:
                parts.append(f"windows: full={full_ct} sliding={slide_ct} (min={min_sw} max={max_sw})")
            else:
                parts.append(f"windows: full={full_ct} sliding={slide_ct}")
        if has_group_over:
            uniq = sorted({gr for gr in layer_group_repr if gr})
            if uniq:
                parts.append("head_groups={" + ", ".join(uniq) + "}")
        lines.append("  per-layer overrides: " + (", ".join(parts) if parts else "none (all layers use defaults)"))

        # --- MoE summary (if any) ---
        moe_layers = [i for i, e in enumerate(eff) if e.get("is_moe", False)]
        if moe_layers:
            E_list   = [eff[i]["num_experts"] for i in moe_layers]
            K_list   = [eff[i]["moe_top_k"] or (1 if eff[i]["expert_type"] == "switch" else None) for i in moe_layers]
            moe_ffs  = [eff[i]["moe_ff"] or eff[i]["ff"] for i in moe_layers]
            types    = sorted({eff[i]["expert_type"] for i in moe_layers})
            active_ffn_params = 0
            for i in moe_layers:
                et  = eff[i]["expert_type"]
                k   = (eff[i]["moe_top_k"] or (1 if et == "switch" else 1))
                mff = (eff[i]["moe_ff"] or eff[i]["ff"])
                active_ffn_params += 3 * H * mff * k

            lines.append(
                "  MoE: "
                f"layers={len(moe_layers)} at {moe_layers} | types={','.join(types)} | "
                f"E[{min(E_list)}..{max(E_list)}]  k[{min(K_list)}..{max(K_list)}]  moe_ff[{min(moe_ffs)}..{max(moe_ffs)}]"
            )
            lines.append(f"    approx active FFN params/token (sparse path): {active_ffn_params/1e6:.2f}M")

        # Per-layer readout
        lines.append(f"  layers (full={full_ct}, sliding={slide_ct})")
        for i, e in enumerate(eff):
            tag = "full" if (e["window"] is None) else f"sw={int(e['window'])}"
            group_str = layer_group_repr[i]
            if e.get("is_moe", False):
                et = e["expert_type"]
                E  = e["num_experts"]
                k  = e["moe_top_k"] or (1 if et == "switch" else 1)
                mff = e["moe_ff"] or e["ff"]
                aux = e.get("moe_aux_loss_weight", None)
                aux_str = (f" aux={aux:g}" if aux not in (None, 0.0) else "")
                line = (
                    f"    L{i:02d}: {tag}  h={e['heads']} kv={e['kv']} ff={e['ff']}  "
                    f"[MoE {et}: E={E} k={k} e_ff={mff}{aux_str}]"
                )
            else:
                line = f"    L{i:02d}: {tag}  h={e['heads']} kv={e['kv']} ff={e['ff']}"
            if group_str:
                line += f"  hg={group_str}"
            lines.append(line)

        # Parameter counts
        total = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        lines.append(f"  params: total={total/1e6:.2f}M  trainable={trainable/1e6:.2f}M")

        # One-liner
        moe_bit = "" if not moe_layers else f" | MoE={len(moe_layers)}L (E[{min(E_list)}..{max(E_list)}], k[{min(K_list)}..{max(K_list)}])"
        one_liner = (
            f"Topology: {cfg.num_hidden_layers}L | full={full_ct} | sliding={slide_ct}"
            + (f" | sw[min={min_sw} max={max_sw}]" if slide_vals else "")
            + f" | sinks={n_sinks}{moe_bit}"
        )
        lines.append("  " + shorten(one_liner, width=140, placeholder="…"))
        return "\n".join(lines)

    @staticmethod
    def _bind_special_tokens_strict(tok: PreTrainedTokenizerBase) -> None:
        tok.pad_token = U.PAD
        tok.bos_token = U.BOS
        tok.eos_token = U.EOS
        n = len(tok)
        for name, text, tid in [
            ("PAD", U.PAD, tok.pad_token_id),
            ("BOS", U.BOS, tok.bos_token_id),
            ("EOS", U.EOS, tok.eos_token_id),
        ]:
            if tid is None or not (0 <= tid < n):
                raise ValueError(f"{name} token '{text}' not found in tokenizer vocab (id={tid}, size={n}).")

    @staticmethod
    def _sync_model_and_tokenizer(
        model: BantamForCausalLM,
        tok: PreTrainedTokenizerBase,
        *,
        strict_vocab_match: bool = False,
    ) -> None:
        n_tok = len(tok)
        emb_n = model.get_input_embeddings().num_embeddings
        if emb_n != n_tok:
            if strict_vocab_match:
                raise RuntimeError(
                    f"Embedding size ({emb_n}) != tokenizer size ({n_tok}); strict mode forbids resize."
                )
            model.resize_token_embeddings(n_tok)
        if tok.pad_token_id is None or not (0 <= tok.pad_token_id < n_tok):
            raise ValueError(f"pad_token_id {tok.pad_token_id} invalid for tokenizer size {n_tok}.")
        model.config.vocab_size = n_tok
        model.config.pad_token_id = tok.pad_token_id

    @staticmethod
    def _load_model_and_tokenizer(
        targs: TrainingArgs,
        cfg: BantamConfig,
        dtype: torch.dtype,
        device: torch.device,
        model_path: Optional[str] = None,
        *,
        strict_vocab_match: bool = False,
    ):
        path_exists = model_path and Path(model_path).exists()
        tokenizer_path = str(model_path) if path_exists else targs.tokenizer

        tok = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
        BantamTrainer._bind_special_tokens_strict(tok)

        if path_exists:
            status = f"Loading model from checkpoint: {model_path}"
            model = _from_pretrained_with_dtype(
                BantamForCausalLM.from_pretrained,
                model_path,
                dtype=dtype,
            ).to(device=device, dtype=dtype)
        else:
            status = "No checkpoint found. Initializing new model from config."
            cfg.vocab_size = len(tok)
            cfg.pad_token_id = tok.pad_token_id
            model = BantamForCausalLM(cfg).to(device=device, dtype=dtype)

        BantamTrainer._sync_model_and_tokenizer(model, tok, strict_vocab_match=strict_vocab_match)
        return tok, model, status

    @staticmethod
    def _plot(losses: List[float], title: str) -> plt.Figure:
        fig = plt.figure(figsize=(10, 4))
        plt.plot(losses, label="loss", linewidth=2.0)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xlabel("Update Step")
        plt.ylabel("Loss")
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        return fig

    @staticmethod
    def _save_checkpoint(
        base_dir: Path,
        model: BantamForCausalLM,
        tok: PreTrainedTokenizerBase,
        optimizer: torch.optim.Optimizer,
        scheduler: Any,
        scaler: Any,
        targs: TrainingArgs,
        *,
        step: int,
        epoch: int,
        best_loss: Optional[float] = None,
    ) -> Path:
        base_dir.mkdir(parents=True, exist_ok=True)
        # HF artifacts (force safetensors)
        try:
            model.save_pretrained(base_dir, safe_serialization=True)
        except TypeError:
            # Fallback for older transformers without the arg
            model.save_pretrained(base_dir)
        tok.save_pretrained(base_dir)
        # Torch training state
        try:
            torch.save(optimizer.state_dict(), base_dir / "optimizer.pt")
        except Exception:
            pass
        try:
            torch.save(scheduler.state_dict(), base_dir / "scheduler.pt")
        except Exception:
            pass
        try:
            if hasattr(scaler, "is_enabled") and scaler.is_enabled():
                torch.save(scaler.state_dict(), base_dir / "scaler.pt")
        except Exception:
            pass
        # RNG states for reproducibility
        try:
            rng_state = {
                "torch": torch.get_rng_state(),
                "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
                "random": random.getstate(),
                "numpy": np.random.get_state(),
            }
            torch.save(rng_state, base_dir / "rng_state.pt")
        except Exception:
            pass
        # Minimal resume metadata
        state = {"step": step, "epoch": epoch, "time": time.time(), "best_loss": float(best_loss) if best_loss is not None else None}
        try:
            with open(base_dir / "training_state.json", "w") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass
        try:
            with open(base_dir / "training_args.json", "w") as f:
                json.dump(asdict(targs), f, indent=2)
        except Exception:
            pass
        return base_dir

    @staticmethod
    def _load_checkpoint_state(
        resume_dir: Path,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
        scaler: Optional[Any] = None,
    ) -> Tuple[int, int, float]:
        step = 0
        epoch = 0
        best_loss = float("inf")
        # Load counters
        try:
            with open(resume_dir / "training_state.json", "r") as f:
                st = json.load(f)
                step = int(st.get("step", 0))
                epoch = int(st.get("epoch", 0))
                if st.get("best_loss", None) is not None:
                    best_loss = float(st["best_loss"])
        except Exception:
            pass
        # Load optimizer/scheduler/scaler
        try:
            if optimizer is not None and (resume_dir / "optimizer.pt").exists():
                optimizer.load_state_dict(torch.load(resume_dir / "optimizer.pt", map_location="cpu"))
        except Exception:
            pass
        try:
            if scheduler is not None and (resume_dir / "scheduler.pt").exists():
                scheduler.load_state_dict(torch.load(resume_dir / "scheduler.pt", map_location="cpu"))
        except Exception:
            pass
        try:
            if scaler is not None and hasattr(scaler, "is_enabled") and scaler.is_enabled() and (resume_dir / "scaler.pt").exists():
                scaler.load_state_dict(torch.load(resume_dir / "scaler.pt", map_location="cpu"))
        except Exception:
            pass
        # Restore RNG states
        try:
            rng_path = resume_dir / "rng_state.pt"
            if rng_path.exists():
                rs = torch.load(rng_path, map_location="cpu")
                if rs.get("torch", None) is not None:
                    torch.set_rng_state(rs["torch"])
                if torch.cuda.is_available() and rs.get("cuda", None) is not None:
                    torch.cuda.set_rng_state_all(rs["cuda"])  # list of tensors
                if rs.get("random", None) is not None:
                    random.setstate(rs["random"])  # type: ignore[arg-type]
                if rs.get("numpy", None) is not None:
                    np.random.set_state(rs["numpy"])  # type: ignore[arg-type]
        except Exception:
            pass
        return step, epoch, best_loss

    @staticmethod
    def _prune_checkpoints(root: Path, prefix: str, keep_last_k: Optional[int]) -> None:
        if not keep_last_k or keep_last_k <= 0:
            return
        if not root.exists():
            return
        entries = []
        for p in root.iterdir():
            if not p.is_dir():
                continue
            name = p.name
            if not name.startswith(prefix):
                continue
            # try parse step number after 'step_'
            step_val = -1
            if "step_" in name:
                try:
                    frag = name.split("step_")[1].split("_")[0]
                    step_val = int(frag)
                except Exception:
                    step_val = -1
            entries.append((step_val, p.stat().st_mtime, p))
        if not entries:
            return
        # sort by step then mtime
        entries.sort(key=lambda x: (x[0], x[1]))
        to_delete = entries[:-keep_last_k]
        for _, __, path in to_delete:
            try:
                shutil.rmtree(path)
            except Exception:
                pass

    @staticmethod
    def _init_loss_logger(out_dir: str, mode: str) -> Optional[Path]:
        try:
            logs_root = Path(out_dir) / "logs"
            logs_root.mkdir(parents=True, exist_ok=True)
            ts = time.strftime("%Y%m%d-%H%M%S")
            log_path = logs_root / f"loss_{mode}_{ts}.csv"
            with open(log_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["epoch", "step", "loss"])
            return log_path
        except Exception:
            return None

    @staticmethod
    def _append_loss(log_path: Optional[Path], epoch: int, step: int, loss: float) -> None:
        if log_path is None:
            return
        try:
            with open(log_path, "a", newline="") as f:
                w = csv.writer(f)
                w.writerow([epoch, step, float(loss)])
        except Exception:
            pass

    @staticmethod
    def _loader_kwargs(targs: TrainingArgs) -> Dict:
        return dict(
            batch_size=targs.batch_size,
            shuffle=True,
            num_workers=targs.num_workers,
            pin_memory=targs.pin_memory,
            persistent_workers=(targs.num_workers > 0 and targs.persistent_workers),
        )

    @staticmethod
    def _pretrain_collate(features: List[Dict[str, List[int]]]) -> Dict[str, torch.Tensor]:
        ids = [torch.tensor(f["input_ids"], dtype=torch.long) for f in features]
        input_ids = torch.stack(ids, dim=0)
        attention_mask = torch.ones_like(input_ids, dtype=torch.bool)
        labels = input_ids.clone()
        return {"input_ids": input_ids, "labels": labels, "attention_mask": attention_mask}

    @staticmethod
    def train_pretrain_and_stream(cfg: BantamConfig, targs: TrainingArgs):
        """
        - Loads tokenizer from targs.tokenizer
        - Initializes model from cfg unless targs.init_from_checkpoint is set
        - Streams progress (yield fig_or_none, message)
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        torch.manual_seed(targs.seed)

        dtype_map = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}
        torch_dtype = dtype_map.get(targs.precision, torch.float32)
        scaler = GradScaler(enabled=(targs.precision == "fp16"))

        resume_dir = Path(targs.resume_from_checkpoint) if targs.resume_from_checkpoint else None

        if resume_dir and resume_dir.exists():
            tok = AutoTokenizer.from_pretrained(str(resume_dir), trust_remote_code=True)
            BantamTrainer._bind_special_tokens_strict(tok)
            model = _from_pretrained_with_dtype(
                BantamForCausalLM.from_pretrained,
                str(resume_dir),
                dtype=torch_dtype,
            )
        else:
            tok = AutoTokenizer.from_pretrained(targs.tokenizer, trust_remote_code=True)
            BantamTrainer._bind_special_tokens_strict(tok)
            if targs.init_from_checkpoint:
                model = _from_pretrained_with_dtype(
                    BantamForCausalLM.from_pretrained,
                    targs.init_from_checkpoint,
                    dtype=torch_dtype,
                )
            else:
                cfg.vocab_size = len(tok)
                cfg.pad_token_id = tok.pad_token_id
                model = BantamForCausalLM(cfg)

        # Ensure parameters/ buffers live on the target device and use the requested precision
        model.to(device=device, dtype=torch_dtype)
        BantamTrainer._sync_model_and_tokenizer(model, tok, strict_vocab_match=targs.strict_vocab_match)

        model.config.use_cache = False

        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass
        if torch.cuda.is_available():
            try:
                torch.backends.cuda.enable_flash_sdp(True)
                torch.backends.cuda.enable_mem_efficient_sdp(True)
                # math kernel remains as fallback; keep default enabled
            except AttributeError:
                pass

        yield None, f"🌱 [BOOT] device={device} precision={targs.precision}"
        model.train()
        yield None, BantamTrainer._arch_report(model)

        if targs.use_gradient_checkpoint:
            model.model.gradient_checkpointing_enable()
            yield None, "🧠 Gradient checkpointing enabled."

        yield None, "📚 Packing dataset…"
        if targs.use_hf:
            if not targs.hf_name:
                raise ValueError("use_hf=True requires hf_name (e.g., 'c4', 'lmsys/sharegpt').")

            dataset = HFBlockIterableDataset(
                name=targs.hf_name, subset=targs.hf_subset, split=targs.hf_split,
                tokenizer=tok, seq_len=model.config.max_position_embeddings,
                text_field=targs.hf_text_field, seed=targs.seed,
                buffer_size=targs.shuffle_buffer_size, streaming=targs.hf_streaming,
                overfit_subset=targs.overfit_subset,
            )

            loader = DataLoader(
                dataset,
                batch_size=targs.batch_size,
                shuffle=False,
                num_workers=0,
                pin_memory=False,
                persistent_workers=False,
                collate_fn=BantamTrainer._pretrain_collate,
            )
            if not targs.steps_per_epoch:
                raise ValueError("steps_per_epoch must be set when streaming HF datasets.")
            total_steps = targs.steps_per_epoch * targs.epochs
            warmup_steps = int(total_steps * targs.warmup_frac)
            yield None, f"🧮 HF streaming enabled | steps/epoch={targs.steps_per_epoch:,} | total updates={total_steps:,}"
        else:
            dataset = BlockDataset.from_file(
                targs.dataset,
                model.config.max_position_embeddings,
                tok,
                targs.seed,
                targs.overfit_subset,
                text_field=targs.dataset_text_field or "text",
                min_sample_token_length=max(1, int(targs.min_sample_token_length or 1)),
            )
            loader = DataLoader(
                dataset,
                batch_size=targs.batch_size,
                shuffle=True,
                num_workers=0,
                pin_memory=False,
                persistent_workers=False,
                collate_fn=BantamTrainer._pretrain_collate,
            )
            total_steps = (len(loader) // targs.accum_steps) * targs.epochs
            warmup_steps = int(total_steps * targs.warmup_frac)
            yield None, f"🧮 Dataset ready: {len(dataset):,} blocks | total updates={total_steps:,}"

        optimizer, opt_msg = BantamTrainer._build_optimizer(model, targs)
        scheduler, sched_msg = BantamTrainer._build_scheduler(optimizer, targs, warmup_steps, total_steps)
        yield None, opt_msg
        yield None, f"⚙️ Optimizer ready. Warmup: {warmup_steps:,}"
        yield None, sched_msg

        losses, step, t0 = [], 0, time.time()
        best_loss = float("inf")
        log_path = BantamTrainer._init_loss_logger(targs.out_dir, "pretrain") if targs.log_loss_to_csv else None
        optimizer.zero_grad(set_to_none=True)
        # Resume training state if requested
        start_epoch = 0
        if resume_dir and resume_dir.exists():
            s_step, s_epoch, s_best = BantamTrainer._load_checkpoint_state(resume_dir, optimizer, scheduler, scaler)
            step = s_step
            start_epoch = s_epoch
            best_loss = s_best if np.isfinite(s_best) else float("inf")
            yield None, f"⏪ Resumed pretraining at epoch {start_epoch}, step {step} from {resume_dir}"

            if start_epoch >= targs.epochs:
                if step >= total_updates:
                    yield None, (
                        "ℹ️ Checkpoint already completed all configured epochs. "
                        "Increase training_args.epochs or steps_per_epoch to continue training."
                    )
                    return
                adjusted_epoch = max(targs.epochs - 1, 0)
                if adjusted_epoch != start_epoch:
                    yield None, (
                        f"ℹ️ Restarting at epoch {adjusted_epoch + 1}/{targs.epochs} to continue from partial checkpoint."
                    )
                start_epoch = adjusted_epoch

        for epoch in range(start_epoch, targs.epochs):
            yield None, f"--- Starting Epoch {epoch + 1}/{targs.epochs} ---"
            updates_this_epoch = 0

            for i, batch in enumerate(tqdm(loader, desc=f"Epoch {epoch+1}",
                                        total=None if not targs.use_hf else (targs.steps_per_epoch * targs.accum_steps))):
                input_ids      = batch["input_ids"].to(device, non_blocking=False)
                labels         = batch["labels"].to(device, non_blocking=False)
                attention_mask = batch.get("attention_mask")
                am = None
                if attention_mask is not None:
                    # Decide on CPU to avoid a device sync from Tensor.all() on GPU
                    all_true = attention_mask.all().item()
                    if not bool(all_true):
                        am = attention_mask.to(device=device, dtype=torch.bool, non_blocking=True).contiguous()

                with autocast(device_type=device.type, dtype=torch_dtype, enabled=(targs.precision != "fp32")):
                    outputs = model(input_ids=input_ids, labels=labels, attention_mask=am, use_cache=False)
                    loss = outputs.loss

                scaler.scale(loss / targs.accum_steps).backward()

                if (i + 1) % targs.accum_steps == 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), targs.grad_clip)
                    scaler.step(optimizer); scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                    scheduler.step()

                    step += 1
                    updates_this_epoch += 1
                    losses.append(loss.item())
                    BantamTrainer._append_loss(log_path, epoch + 1, step, loss.item())
                    prev_best = best_loss
                    improved_for_gate = (loss.item() <= prev_best - float(targs.improve_delta))
                    best_loss = min(prev_best, loss.item())
                    if step % targs.log_every_n == 0:
                        fig = BantamTrainer._plot(losses, "Pre-training Loss")
                        ups = step / (time.time() - t0)
                        yield fig, f"Ep {epoch+1} | Step {step}/{total_steps} | Loss {loss.item():.4f} | {ups:.2f} UPS"
                        plt.close(fig)

                    # Periodic checkpointing
                    should_save = bool(targs.save_every_n) and (step % int(targs.save_every_n) == 0)
                    if should_save and targs.save_on_improve:
                        should_save = improved_for_gate
                    if should_save:
                        ckpt_dir = Path(targs.out_dir) / "checkpoints" / f"pretrain_step_{step:06d}_{time.strftime('%Y%m%d-%H%M%S')}"
                        BantamTrainer._save_checkpoint(ckpt_dir, model, tok, optimizer, scheduler, scaler, targs, step=step, epoch=epoch, best_loss=best_loss)
                        yield None, f"💾 Checkpoint saved at step {step} → {ckpt_dir}"
                        BantamTrainer._prune_checkpoints(Path(targs.out_dir) / "checkpoints", "pretrain_step_", targs.keep_last_k)

                    if targs.use_hf and updates_this_epoch >= targs.steps_per_epoch:
                        break

        ts = time.strftime("%Y%m%d-%H%M%S")
        save_tag = f"_{targs.save_tag}" if targs.save_tag else ""
        save_dir = Path(targs.out_dir) / f"bantam_pretrain{save_tag}_{ts}"
        save_dir.mkdir(parents=True, exist_ok=True)
        yield None, f"💾 Saving final model to {save_dir}"
        BantamTrainer._save_checkpoint(save_dir, model, tok, optimizer, scheduler, scaler, targs, step=step, epoch=targs.epochs, best_loss=best_loss)
        fig = BantamTrainer._plot(losses, "Final Pre-training Loss")
        yield fig, "✅ Pre-training complete!"
        plt.close(fig)

    @staticmethod
    def train_sft_and_stream(targs: TrainingArgs):
        """
        - Loads tokenizer from targs.finetune_from (or targs.tokenizer)
        - Loads base model from targs.finetune_from / init_from_checkpoint (required)
        - Applies LoRA or full finetune based on targs.sft_mode
        - Streams progress (yield fig_or_none, message)
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        torch.manual_seed(targs.seed)

        dtype_map = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}
        torch_dtype = dtype_map.get(targs.precision, torch.float32)
        scaler = torch.amp.GradScaler(enabled=(targs.precision == "fp16"))

        resume_dir = Path(targs.resume_from_checkpoint) if targs.resume_from_checkpoint else None

        # Initialize tokenizer/model, possibly from a resume checkpoint (handles LoRA/full)
        mode = targs.sft_mode.lower()
        ckpt_mode_tag = "lora" if mode == "lora" else "full"
        if resume_dir and resume_dir.exists():
            is_lora_ckpt = (resume_dir / "adapter_config.json").exists()
            # Tokenizer prefers checkpoint dir
            try:
                tok = AutoTokenizer.from_pretrained(str(resume_dir), trust_remote_code=True)
            except Exception:
                base_path_fallback = targs.finetune_from or targs.init_from_checkpoint or targs.tokenizer
                tok = AutoTokenizer.from_pretrained(base_path_fallback, trust_remote_code=True)
            BantamTrainer._bind_special_tokens_strict(tok)

            if is_lora_ckpt:
                base_path = targs.finetune_from or targs.init_from_checkpoint
                if not base_path:
                    yield None, "❌ Resuming LoRA SFT requires a base model via finetune_from or init_from_checkpoint."
                    return
                base_model = _from_pretrained_with_dtype(
                    BantamForCausalLM.from_pretrained,
                    base_path,
                    dtype=torch_dtype,
                )
                from peft import PeftModel
                model = PeftModel.from_pretrained(base_model, str(resume_dir))
                mode = "lora"
                ckpt_mode_tag = "lora"
            else:
                model = _from_pretrained_with_dtype(
                    BantamForCausalLM.from_pretrained,
                    str(resume_dir),
                    dtype=torch_dtype,
                )
                mode = "full"
                ckpt_mode_tag = "full"
        else:
            base_path = targs.finetune_from or targs.init_from_checkpoint
            if not base_path:
                yield None, "❌ SFT requires a base checkpoint: set training_args.finetune_from or init_from_checkpoint."
                return

            tok = AutoTokenizer.from_pretrained(base_path or targs.tokenizer, trust_remote_code=True)
            BantamTrainer._bind_special_tokens_strict(tok)

            model = _from_pretrained_with_dtype(
                BantamForCausalLM.from_pretrained,
                base_path,
                dtype=torch_dtype,
            )

        model.to(device=device, dtype=torch_dtype)
        BantamTrainer._sync_model_and_tokenizer(model, tok, strict_vocab_match=targs.strict_vocab_match)
        model.config.use_cache = False

        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass
        if torch.cuda.is_available():
            try:
                torch.backends.cuda.enable_flash_sdp(True)
                torch.backends.cuda.enable_mem_efficient_sdp(True)
            except AttributeError:
                pass

        if not (resume_dir and resume_dir.exists()):
            if mode == "lora":
                lora_cfg = LoraConfig(
                    r=targs.lora_r, lora_alpha=targs.lora_alpha, lora_dropout=targs.lora_dropout,
                    task_type="CAUSAL_LM",
                    target_modules=["q_proj","k_proj","v_proj","o_proj","w1","w2","w3"],
                )
                model = get_peft_model(model, lora_cfg)
                model.print_trainable_parameters()
                ckpt_mode_tag = "lora"
            else:
                for p in model.parameters():
                    p.requires_grad_(True)
                total, trainable = BantamTrainer._count_params(model)
                yield None, f"🧵 Full-parameter SFT: {trainable/1e6:.2f}M / {total/1e6:.2f}M trainable"
                ckpt_mode_tag = "full"

        model.config.use_cache = False

        model.train()
        max_len = model.config.max_position_embeddings or 2048

        if targs.use_hf:
            dataset = HFChatSFTIterableDataset(
                name=targs.hf_name, subset=targs.hf_subset, split=targs.hf_split,
                tokenizer=tok, max_len=max_len,
                messages_field=targs.hf_messages_field,
                include_agent_end=targs.include_agent_end, include_eos=targs.include_eos,
                seed=targs.seed, buffer_size=targs.shuffle_buffer_size,
                streaming=targs.hf_streaming, overfit_subset=targs.overfit_subset,
                mask_user_queries=targs.mask_user_queries,
            )
            collator = DataCollatorForSFT(pad_token_id=tok.pad_token_id, pad_to_multiple_of=8)
            loader = DataLoader(
                dataset,
                collate_fn=collator,
                batch_size=targs.batch_size,
                shuffle=False,
                num_workers=0,
                pin_memory=targs.pin_memory,
                persistent_workers=False,
            )
            if not targs.steps_per_epoch:
                raise ValueError("steps_per_epoch must be set when streaming HF datasets for SFT.")
            total_updates = targs.steps_per_epoch * targs.epochs
            warmup_steps = max(0, int(total_updates * targs.warmup_frac))
            dataset_msg = f"📚 SFT (HF streaming) | subset={targs.hf_subset or '—'} | split={targs.hf_split} | steps/epoch={targs.steps_per_epoch:,}"
        else:
            dataset = ChatSFTDatasetV2(
                targs.dataset, tok, max_len=max_len,
                include_agent_end=targs.include_agent_end, include_eos=targs.include_eos,
                mask_user_queries=targs.mask_user_queries,
            )
            collator = DataCollatorForSFT(pad_token_id=tok.pad_token_id, pad_to_multiple_of=8)
            loader = DataLoader(
                dataset, collate_fn=collator,
                batch_size=targs.batch_size, shuffle=True,
                num_workers=targs.num_workers, pin_memory=targs.pin_memory,
                persistent_workers=(targs.num_workers > 0 and targs.persistent_workers),
                multiprocessing_context="spawn",
            )
            total_updates = (len(loader) // targs.accum_steps) * targs.epochs
            warmup_steps = max(0, int(total_updates * targs.warmup_frac))
            dataset_msg = f"📚 SFT dataset={len(dataset):,}"

        optimizer, opt_msg = BantamTrainer._build_optimizer(model, targs)
        scheduler, sched_msg = BantamTrainer._build_scheduler(optimizer, targs, warmup_steps, total_updates)
        yield None, opt_msg
        yield None, f"{dataset_msg} | total updates={total_updates:,} | warmup={warmup_steps:,}"
        yield None, sched_msg

        losses, step, t0 = [], 0, time.time()
        best_loss = float("inf")
        log_path = BantamTrainer._init_loss_logger(targs.out_dir, "sft") if targs.log_loss_to_csv else None
        optimizer.zero_grad(set_to_none=True)

        # Resume training state if requested
        start_epoch = 0
        if resume_dir and resume_dir.exists():
            s_step, s_epoch, s_best = BantamTrainer._load_checkpoint_state(resume_dir, optimizer, scheduler, scaler)
            step = s_step
            start_epoch = s_epoch
            best_loss = s_best if np.isfinite(s_best) else float("inf")
            yield None, f"⏪ Resumed SFT at epoch {start_epoch}, step {step} from {resume_dir}"

            if start_epoch >= targs.epochs:
                if step >= total_updates:
                    yield None, (
                        "ℹ️ Checkpoint already completed all configured epochs. "
                        "Increase training_args.epochs or steps_per_epoch to continue training."
                    )
                    return
                adjusted_epoch = max(targs.epochs - 1, 0)
                if adjusted_epoch != start_epoch:
                    yield None, (
                        f"ℹ️ Restarting at epoch {adjusted_epoch + 1}/{targs.epochs} to continue from partial checkpoint."
                    )
                start_epoch = adjusted_epoch

        if targs.use_gradient_checkpoint:
            model.model.gradient_checkpointing_enable()
            yield None, "🧠 Gradient checkpointing enabled."

        for epoch in range(start_epoch, targs.epochs):
            updates_this_epoch = 0
            pbar_total = targs.steps_per_epoch * targs.accum_steps if targs.use_hf else None
            for i, batch in enumerate(tqdm(loader, desc=f"SFT Epoch {epoch+1}", total=pbar_total)):
                fwd_kwargs = {k: v.to(device, non_blocking=True) for k, v in batch.items()}

                with autocast(device_type=device.type, dtype=torch_dtype, enabled=(targs.precision != "fp32")):
                    out = model(**fwd_kwargs, use_cache=False)
                    loss = out.loss

                    if "loss_mask" in fwd_kwargs:
                        shift_logits = out.logits[:, :-1, :].contiguous()
                        shift_labels = fwd_kwargs["labels"][:, 1:].contiguous()
                        shift_mask   = fwd_kwargs["loss_mask"][:, 1:].contiguous()

                        valid = (shift_labels != -100).to(shift_mask.dtype)
                        loss_fct = nn.CrossEntropyLoss(reduction="none", ignore_index=-100)
                        token_loss = loss_fct(
                            shift_logits.view(-1, shift_logits.size(-1)),
                            shift_labels.view(-1)
                        ).view_as(shift_labels)

                        weighted = token_loss * shift_mask * valid
                        denom = (shift_mask * valid).sum().clamp_min(1e-6)
                        loss = weighted.sum() / denom

                if torch.isnan(loss) or torch.isinf(loss):
                    yield None, "⚠️ Skipped a batch due to NaN/Inf loss."
                    continue

                scaler.scale(loss / targs.accum_steps).backward()

                if (i + 1) % targs.accum_steps == 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), targs.grad_clip)
                    scaler.step(optimizer); scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                    scheduler.step()

                    step += 1
                    losses.append(loss.item())
                    BantamTrainer._append_loss(log_path, epoch + 1, step, loss.item())
                    prev_best = best_loss
                    improved_for_gate = (loss.item() <= prev_best - float(targs.improve_delta))
                    best_loss = min(prev_best, loss.item())
                    if targs.use_hf:
                        updates_this_epoch += 1

                    if step % targs.log_every_n == 0:
                        title = f"SFT {'LoRA' if mode=='lora' else 'Full'} Loss"
                        fig = BantamTrainer._plot(losses, title)
                        ups = step / (time.time() - t0)
                        yield fig, f"Ep {epoch+1} | Step {step}/{total_updates} | Loss {loss.item():.4f} | {ups:.2f} UPS"
                        plt.close(fig)

                    # Periodic checkpointing
                    should_save = bool(targs.save_every_n) and (step % int(targs.save_every_n) == 0)
                    if should_save and targs.save_on_improve:
                        should_save = improved_for_gate
                    if should_save:
                        ckpt_dir = Path(targs.out_dir) / "checkpoints" / f"sft_{ckpt_mode_tag}_step_{step:06d}_{time.strftime('%Y%m%d-%H%M%S')}"
                        BantamTrainer._save_checkpoint(ckpt_dir, model, tok, optimizer, scheduler, scaler, targs, step=step, epoch=epoch, best_loss=best_loss)
                        yield None, f"💾 Checkpoint saved at step {step} → {ckpt_dir}"
                        BantamTrainer._prune_checkpoints(Path(targs.out_dir) / "checkpoints", f"sft_{ckpt_mode_tag}_step_", targs.keep_last_k)

                    if targs.use_hf and updates_this_epoch >= targs.steps_per_epoch:
                        break

        ts = time.strftime("%Y%m%d-%H%M%S")
        tag = "lora" if mode == "lora" else "full"
        save_tag = f"_{targs.save_tag}" if targs.save_tag else ""
        save_dir = Path(targs.out_dir) / f"bantam_sft_{tag}{save_tag}_{ts}"
        yield None, f"💾 Saving SFT artifacts to {save_dir}"
        BantamTrainer._save_checkpoint(save_dir, model, tok, optimizer, scheduler, scaler, targs, step=step, epoch=targs.epochs, best_loss=best_loss)
        fig = BantamTrainer._plot(losses, f"Final SFT {'LoRA' if mode=='lora' else 'Full'} Loss")
        yield fig, f"✅ SFT finished. Saved to {save_dir}"
        plt.close(fig)
