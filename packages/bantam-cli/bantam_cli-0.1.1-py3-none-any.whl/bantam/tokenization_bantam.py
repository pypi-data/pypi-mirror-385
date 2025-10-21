from typing import ClassVar, Dict, List, Optional, Tuple 
import os
import json
from pathlib import Path

from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
from transformers import AutoTokenizer

from .configuration_bantam import BantamConfig

_DEFAULT_TOKENIZER_FILE = Path(__file__).resolve().parent / "tokenizer.json"


def get_default_tokenizer_dir() -> Path:
	"""Directory containing the project-bundled tokenizer assets."""
	return _DEFAULT_TOKENIZER_FILE.parent

BASE_SPECIAL_TOKENS: List[str] = [
	# --- Core · Standard tokens ---
	# Used by the tokenizer/runtime; not user-visible content.
	"<|UNK|>", "<|PAD|>", "<|BOS|>", "<|EOS|>",

	# --- Core · Roles ---
	# Fences for role-structured prompts; wrap the content from each actor.
	"<|SYSTEM_START|>", "<|SYSTEM_END|>",
	"<|USER_START|>", "<|USER_END|>",
	"<|AGENT_START|>", "<|AGENT_END|>",

	# --- Core · Reasoning & Compute (minimal) ---
	# THINK: internal reasoning (strip before display). COMPUTE: heavy math/code blocks the runtime may sandbox.
	"<|THINK_START|>", "<|THINK_END|>",
	"<|COMPUTE_START|>", "<|COMPUTE_END|>",

	# --- Core · Multimodal fences ---
	# Wrap raw modality payloads so the model/runtime can detect and route them.
	"<|IMAGE_START|>", "<|IMAGE_END|>",
	"<|AUDIO_START|>", "<|AUDIO_END|>",
	"<|VISION_START|>", "<|VISION_END|>",

	# --- Core · Grounding / regions ---
	# Reference regions/objects inside media for grounding (e.g., detection boxes, quads).
	"<|OBJECT_REF_START|>", "<|OBJECT_REF_END|>",
	"<|BOX_START|>", "<|BOX_END|>",
	"<|QUAD_START|>", "<|QUAD_END|>",

	# --- Core · Pads ---
	# Modality-specific padding for training/inference alignment.
	"<|VISION_PAD|>", "<|IMAGE_PAD|>", "<|VIDEO_PAD|>",

	# --- Core · Audio codec fence ---
	# Encoded audio token spans (e.g., neural codec frames).
	"<|AUDIO_TOKEN_START|>", "<|AUDIO_TOKEN_END|>",

	# --- Core · Structured / tool I/O ---
	# Use for strictly-typed blocks and tool traffic so they’re easy to parse/strip.
	"<|JSON_START|>", "<|JSON_END|>",
	"<|TOOL_CALL_START|>", "<|TOOL_CALL_END|>",
	"<|TOOL_RESPONSE_START|>", "<|TOOL_RESPONSE_END|>",

	# --- Planning / Objectives (lean) ---
	# High-level intent and execution framing; keep concise and machine-checkable.
	"<|OBJECTIVES_START|>", "<|OBJECTIVES_END|>",
	"<|TASKS_START|>", "<|TASKS_END|>",
	"<|ASSUMPTIONS_START|>", "<|ASSUMPTIONS_END|>",
	"<|CONSTRAINTS_START|>", "<|CONSTRAINTS_END|>",

	# --- Context & Retrieval (lean) ---
	# Bring in and cite supporting info; great for RAG pipelines.
	"<|CONTEXT_START|>", "<|CONTEXT_END|>",
	"<|CITATIONS_START|>", "<|CITATIONS_END|>",
	"<|PROVENANCE_START|>", "<|PROVENANCE_END|>",

	# --- Reasoning (simple) ---
	# Keep hidden reasoning compact; verify is a short self-check before finalizing.
	"<|REASON_START|>", "<|REASON_END|>",
	"<|VERIFY_START|>", "<|VERIFY_END|>",

	# --- Answer Surfacing (lean) ---
	# Assemble and ship the response; only FINAL must be shown to users by default.
	"<|ANSWER_DRAFT_START|>", "<|ANSWER_DRAFT_END|>",
	"<|SUMMARY_BULLETS_START|>", "<|SUMMARY_BULLETS_END|>",
	"<|ANSWER_FINAL_START|>", "<|ANSWER_FINAL_END|>",

	# --- Safety / Redaction (minimal) ---
	# Use to mark spans that must be removed or masked pre-display/logging.
	"<|REDACT_START|>", "<|REDACT_END|>",

	# --- Reserved extensions (future use) ---
	# Keep these in the tokenizer for painless upgrades without breaking prompts.
	"<|EXT1_START|>", "<|EXT1_END|>",
	"<|EXT2_START|>", "<|EXT2_END|>",
	"<|EXT3_START|>", "<|EXT3_END|>",
	"<|EXT4_START|>", "<|EXT4_END|>",
]

SPECIAL_TOKENS: List[str] = list(dict.fromkeys(BASE_SPECIAL_TOKENS))


def _token_to_attr_name(token: str) -> str:
	if not (token.startswith("<|") and token.endswith("|>")):
		raise ValueError(f"Unexpected token format: {token}")
	return token[2:-2]


SPECIAL_TOKEN_ATTRS: Dict[str, str] = { _token_to_attr_name(tok): tok for tok in SPECIAL_TOKENS }

class BantamTokenizerUtils:
	"""Utility helpers for managing special tokens and formatting prompts."""

	SPECIAL_TOKENS: ClassVar[List[str]] = SPECIAL_TOKENS
	SPECIAL_TOKEN_ATTRS: ClassVar[Dict[str, str]] = SPECIAL_TOKEN_ATTRS

	@staticmethod
	def get_special_tokens() -> List[str]:
		"""Returns the ordered list of special tokens registered for the tokenizer."""
		return BantamTokenizerUtils.SPECIAL_TOKENS.copy()

	@staticmethod
	def get_special_tokens_dict_from_class() -> Dict[str, str]:
		"""Maps special-token attribute names (e.g. BOS) to their literal strings."""
		return BantamTokenizerUtils.SPECIAL_TOKEN_ATTRS.copy()

	@staticmethod
	def format_pretrain_text(text: str, include_eos: bool = False) -> str:
		"""Wraps raw text with BOS/EOS tokens for pretraining."""
		formatted = f"{BantamTokenizerUtils.BOS}{text}"
		if include_eos:
			formatted += BantamTokenizerUtils.EOS
		return formatted

	@staticmethod
	def format_chat_turns(turns: List[Dict[str, str]], include_eos: bool = False) -> str:
		"""
		Builds a formatted chat prompt string from a list of role-content dictionaries.

		Args:
			turns (List[Dict[str, str]]): A list of turns, where each turn is a
										  dictionary with 'role' and 'content'.
			include_eos (bool): Whether to append the EOS token at the end.

		Returns:
			A single string formatted with special chat tokens.
		"""
		chat_str = BantamTokenizerUtils.BOS
		for turn in turns:
			role = turn.get("role")
			content = turn.get("content")
			if not role or content is None:
				continue

			role_map = {
				"system": (BantamTokenizerUtils.SYSTEM_START, BantamTokenizerUtils.SYSTEM_END),
				"user": (BantamTokenizerUtils.USER_START, BantamTokenizerUtils.USER_END),
				"think": (BantamTokenizerUtils.THINK_START, BantamTokenizerUtils.THINK_END),
				"agent": (BantamTokenizerUtils.AGENT_START, BantamTokenizerUtils.AGENT_END),
				"assistant": (BantamTokenizerUtils.AGENT_START, BantamTokenizerUtils.AGENT_END),
				"bantam": (BantamTokenizerUtils.AGENT_START, BantamTokenizerUtils.AGENT_END),
			}
			if role in role_map:
				start_token, end_token = role_map[role]
				chat_str += f"{start_token}{content}{end_token}"

		if include_eos:
			chat_str += BantamTokenizerUtils.EOS
		return chat_str


# Bind each special token string onto the utils class (e.g., BantamTokenizerUtils.BOS).
for _attr_name, _token_str in SPECIAL_TOKEN_ATTRS.items():
	setattr(BantamTokenizerUtils, _attr_name, _token_str)

class BantamTokenizer(PreTrainedTokenizer):
	"""
	Demo/simple tokenizer that expects a vocab.json and splits on spaces.
	Kept for completeness, but not used in training with a BPE tokenizer.json.
	"""
	model_input_names = ["input_ids", "attention_mask"]
	vocab_files_names = {"vocab_file": "vocab.json"}

	def __init__(self, vocab_file, **kwargs):
		self.utils = BantamTokenizerUtils()

		special_tokens = {
			"unk_token": self.utils.UNK,
			"pad_token": self.utils.PAD,
			"bos_token": self.utils.BOS,
			"eos_token": self.utils.EOS,
			"additional_special_tokens": [
				t for t in self.utils.get_special_tokens() 
				if t not in [self.utils.UNK, self.utils.PAD, self.utils.BOS, self.utils.EOS]
			]
		}
		for k, v in special_tokens.items():
			kwargs.setdefault(k, v)

		super().__init__(**kwargs)

		with open(vocab_file, "r", encoding="utf-8") as f:
			self.vocab = json.load(f)

		self.encoder = self.vocab
		self.decoder = {v: k for k, v in self.vocab.items()}

	@property
	def vocab_size(self) -> int:
		return len(self.encoder)

	def get_vocab(self) -> Dict[str, int]:
		return self.encoder.copy()

	def _tokenize(self, text: str) -> List[str]:
		return text.split()

	def _convert_token_to_id(self, token: str) -> int:
		return self.encoder.get(token, self.encoder.get(self.unk_token))

	def _convert_id_to_token(self, index: int) -> str:
		return self.decoder.get(index, self.unk_token)

	def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
		if not os.path.isdir(save_directory):
			os.makedirs(save_directory)
		vocab_file_path = os.path.join(
			save_directory, (filename_prefix + "-" if filename_prefix else "") + "vocab.json"
		)
		with open(vocab_file_path, "w", encoding="utf-8") as f:
			json.dump(self.encoder, f, ensure_ascii=False, indent=2)
		return (vocab_file_path,)


class BantamFastTokenizer(PreTrainedTokenizerFast):
	"""
	Wrapper around HF fast tokenizer that:
	  - loads your BPE tokenizer.json
	  - case-insensitively binds special tokens to EXACT strings found in vocab
	  - registers additional_special_tokens without growing vocab (if they already exist)
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		utils = BantamTokenizerUtils

		vocab_keys = set(self.get_vocab().keys())
		def _variant(tok: str) -> Optional[str]:
			tl = tok.lower()
			for v in vocab_keys:
				if v.lower() == tl:
					return v
			return None

		pad = _variant(utils.PAD) or utils.PAD
		bos = _variant(utils.BOS) or utils.BOS
		eos = _variant(utils.EOS) or utils.EOS
		unk = _variant(utils.UNK) or utils.UNK

		self.pad_token = pad
		self.bos_token = bos
		self.eos_token = eos
		self.unk_token = unk

		addl = []
		for name, tok in utils.get_special_tokens_dict_from_class().items():
			if tok in (utils.UNK, utils.PAD, utils.BOS, utils.EOS):
				continue
			v = _variant(tok)
			if v is not None:
				addl.append(v)

		if addl:
			self.add_special_tokens({"additional_special_tokens": addl}, replace_additional_special_tokens=True)

		self.clean_up_tokenization_spaces = False


AutoTokenizer.register(BantamConfig, fast_tokenizer_class=BantamFastTokenizer)
