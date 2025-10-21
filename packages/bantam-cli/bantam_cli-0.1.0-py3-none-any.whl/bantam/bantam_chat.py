from dataclasses import dataclass
from typing import List, Dict, Optional, Generator, Union

import torch
from transformers import (
    AutoTokenizer,
)
from transformers.generation.logits_process import (
    LogitsProcessorList,
    NoRepeatNGramLogitsProcessor,
    RepetitionPenaltyLogitsProcessor,
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper,
)

from .tokenization_bantam import BantamTokenizerUtils as U
from .modeling_bantam import BantamForCausalLM


def _to_ids(tokenizer, text: str) -> List[int]:
    return tokenizer(text, add_special_tokens=False)["input_ids"]


@dataclass
class GenerateConfig:
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 0
    repetition_penalty: float = 1.05
    do_sample: Optional[bool] = None  
    no_repeat_ngram_size: Optional[int] = 4
    extra: Optional[dict] = None


class BantamChat:
    """
    One class to chat/generate with Bantam models (pretrained or SFT).
    - Chat format uses U.format_chat_turns(...) + AGENT_START.
    - Pretrain format uses U.format_pretrain_text(...).
    - Streaming implemented via incremental decoding (no HF streamer quirks).
    """

    def __init__(self, model: BantamForCausalLM, tokenizer, device: Optional[Union[str, torch.device]] = None):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device or (model.device if hasattr(model, "device") else ("cuda" if torch.cuda.is_available() else "cpu"))

        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token or U.EOS

        for tok_text in (U.BOS, U.EOS, U.USER_START, U.USER_END, U.AGENT_START, U.AGENT_END):
            tid = self.tokenizer.convert_tokens_to_ids(tok_text)
            if tid is None or tid < 0:
                raise RuntimeError(f"Special token not in vocab: {tok_text}")

        self._stop_texts = [U.AGENT_END, self.tokenizer.eos_token or U.EOS]
        self._stop_ids: List[List[int]] = []
        for s in self._stop_texts:
            if s is None:
                continue
            self._stop_ids.append(_to_ids(self.tokenizer, s))

    @classmethod
    def from_pretrained(
        cls,
        model_path: str,
        *,
        dtype: Optional[torch.dtype] = None,
        device_map: Optional[Union[str, Dict]] = "auto",
        try_merge_lora: bool = True,
    ):
        """
        Load tokenizer + model; merge LoRA adapters if present at model_path.
        """
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        if dtype is None:
            # prefer bf16 if supported, else fp16
            dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

        load_kwargs = {}
        if device_map is not None:
            load_kwargs["device_map"] = device_map
        try:
            base = BantamForCausalLM.from_pretrained(model_path, dtype=dtype, **load_kwargs)
        except TypeError:
            base = BantamForCausalLM.from_pretrained(model_path, torch_dtype=dtype, **load_kwargs)

        model = base
        if try_merge_lora:
            try:
                from peft import PeftModel
                model = PeftModel.from_pretrained(base, model_path)
                model = model.merge_and_unload()
            except Exception:
                pass

        model.eval()
        return cls(model=model, tokenizer=tokenizer)

    def _build_inputs_chat(self, messages: List[Dict[str, str]]) -> Dict[str, torch.Tensor]:
        """
        Format chat messages and append an empty agent turn so the prompt ends with <|AGENT_START|>.
        """
        prompt = U.format_chat_turns(messages, include_eos=False)
        if not prompt.endswith(U.AGENT_START):
            prompt += U.AGENT_START
        enc = self.tokenizer(prompt, add_special_tokens=False, return_tensors="pt")
        return {
            key: tensor.to(self.model.device)
            for key, tensor in enc.items()
            if key in {"input_ids", "attention_mask"}
        }

    def _build_inputs_pretrain(self, text: str) -> Dict[str, torch.Tensor]:
        prompt = U.format_pretrain_text(text, include_eos=False)
        enc = self.tokenizer(prompt, add_special_tokens=False, return_tensors="pt")
        return {
            key: tensor.to(self.model.device)
            for key, tensor in enc.items()
            if key in {"input_ids", "attention_mask"}
        }

    def stream(
        self,
        *,
        format: str,  # "chat" | "pretrain"
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
        gen: Optional[GenerateConfig] = None,
    ) -> Generator[str, None, str]:
        """
        Streaming generator. Yields text deltas and returns the final text (on StopIteration.value).
        """
        gen = gen or GenerateConfig()
        do_sample = gen.do_sample if gen.do_sample is not None else (gen.temperature is not None and gen.temperature > 0)

        # Build inputs
        inputs: Dict[str, torch.Tensor]
        if format == "chat":
            if messages is None:
                raise ValueError("messages is required for format='chat'")
            inputs = self._build_inputs_chat(messages)
        elif format == "pretrain":
            if prompt is None:
                raise ValueError("prompt is required for format='pretrain'")
            inputs = self._build_inputs_pretrain(prompt)
        else:
            raise ValueError("format must be 'chat' or 'pretrain'")

        eos_token_ids: List[List[int]] = [seq for seq in self._stop_ids if len(seq) > 0]

        logits_processors = LogitsProcessorList()
        if gen.repetition_penalty and gen.repetition_penalty != 1.0:
            logits_processors.append(RepetitionPenaltyLogitsProcessor(gen.repetition_penalty))
        if gen.no_repeat_ngram_size and gen.no_repeat_ngram_size > 0:
            logits_processors.append(NoRepeatNGramLogitsProcessor(gen.no_repeat_ngram_size))

        warpers = LogitsProcessorList()
        if do_sample:
            if gen.temperature and gen.temperature != 1.0:
                warpers.append(TemperatureLogitsWarper(gen.temperature))
            if gen.top_k and gen.top_k > 0:
                warpers.append(TopKLogitsWarper(gen.top_k))
            if gen.top_p and 0.0 < gen.top_p < 1.0:
                warpers.append(TopPLogitsWarper(gen.top_p))

        max_new_tokens = int(gen.max_new_tokens)
        generated = inputs["input_ids"]
        attention = inputs.get("attention_mask")
        if attention is None:
            attention = torch.ones_like(generated, dtype=torch.long, device=generated.device)
        else:
            attention = attention.clone()

        full_text = ""
        prompt_len = generated.shape[1]
        past_key_values = None
        model_input_ids = generated

        for _ in range(max_new_tokens):
            model_kwargs = {"input_ids": model_input_ids, "use_cache": True}
            model_kwargs["attention_mask"] = attention
            if past_key_values is not None:
                model_kwargs["past_key_values"] = past_key_values

            with torch.inference_mode():
                outputs = self.model(**model_kwargs)

            logits = outputs.logits[:, -1, :]
            past_key_values = outputs.past_key_values

            scores = logits_processors(generated, logits)
            if do_sample and len(warpers) > 0:
                scores = warpers(generated, scores)
                probs = torch.nn.functional.softmax(scores, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                if do_sample and len(warpers) > 0:
                    scores = warpers(generated, scores)
                next_token = torch.argmax(scores, dim=-1, keepdim=True)

            generated = torch.cat([generated, next_token], dim=-1)
            ones = torch.ones((attention.size(0), 1), dtype=attention.dtype, device=attention.device)
            attention = torch.cat([attention, ones], dim=-1)
            model_input_ids = next_token

            decoded = self.tokenizer.decode(generated[0, prompt_len:], skip_special_tokens=False)
            delta = decoded[len(full_text):]
            trimmed_delta = delta
            for stop_text in (self._stop_texts + [U.AGENT_END, U.EOS]):
                while stop_text and trimmed_delta.endswith(stop_text):
                    trimmed_delta = trimmed_delta[: -len(stop_text)]
            if trimmed_delta:
                yield trimmed_delta
            full_text = decoded

            stop_hit = False
            for seq in eos_token_ids:
                if len(seq) <= generated.shape[1]:
                    tail = generated[0, -len(seq):].tolist()
                    if tail == seq:
                        stop_hit = True
                        break
            if stop_hit:
                break

        full = full_text
        for s in self._stop_texts:
            if s and s in full:
                full = full.split(s)[0]
                break

        for s in [U.AGENT_END, U.EOS]:
            if s:
                full = full.replace(s, "")
        return full.strip()

    def generate(
        self,
        *,
        format: str,  # "chat" | "pretrain"
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
        gen: Optional[GenerateConfig] = None,
    ) -> str:
        """
        Non-streaming convenience: collects from .stream().
        """
        collector = []
        it = self.stream(format=format, messages=messages, prompt=prompt, gen=gen)
        try:
            for chunk in it:
                collector.append(chunk)
        except StopIteration as e:
            if e.value:
                return e.value
        full = "".join(collector)
        for s in self._stop_texts:
            if s and s in full:
                full = full.split(s)[0]
                break
        for s in [U.AGENT_END, U.EOS]:
            if s:
                full = full.replace(s, "")
        return full.strip()
