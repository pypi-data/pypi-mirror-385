"""Optimizer utilities for Bantam.

This module mirrors the behaviour of the external ``muon-optimizer`` package while keeping
the implementation in-repo so that we can modify it safely.  It exposes a simple factory
that returns either the Muon+auxiliary Adam optimizer or a standard AdamW setup based on
training configuration.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

import torch
import torch.nn as nn


##############################
# Muon implementation (local)
##############################

def _zeropower_via_newtonschulz5(G: torch.Tensor, steps: int) -> torch.Tensor:
    """Newton-Schulz iteration to orthogonalise a matrix."""
    assert G.ndim >= 2
    a, b, c = (3.4445, -4.7750, 2.0315)
    X = G.bfloat16()
    if G.size(-2) > G.size(-1):
        X = X.mT

    X = X / (X.norm(dim=(-2, -1), keepdim=True) + 1e-7)
    for _ in range(steps):
        A = X @ X.mT
        B = b * A + c * A @ A
        X = a * X + B @ X

    if G.size(-2) > G.size(-1):
        X = X.mT
    return X


def _muon_update(
    grad: torch.Tensor,
    momentum: torch.Tensor,
    *,
    beta: float = 0.95,
    ns_steps: int = 5,
    nesterov: bool = True,
    lr_correction: bool = True,
    clip_by_layer: bool = False,
) -> torch.Tensor:
    if grad is None:
        return torch.zeros_like(momentum)
    momentum.lerp_(grad, 1 - beta)
    update = grad.lerp_(momentum, beta) if nesterov else momentum
    original_shape = update.shape
    reshape_2d = False
    if update.ndim > 2:
        update = update.reshape(update.shape[0], -1)
        reshape_2d = True
    update = _zeropower_via_newtonschulz5(update, steps=ns_steps)
    if lr_correction:
        last = max(update.shape[-2], 1)
        width = max(update.shape[-1], 1)
        update = update * max(1.0, float(last) / float(width)) ** 0.5
    if clip_by_layer:
        norm = update.norm()
        if torch.isfinite(norm) and norm > 1.0:
            update = update / (norm + 1e-12)
    if reshape_2d:
        update = update.reshape(original_shape)
    return update.to(grad.dtype)


def _adam_update(
    grad: torch.Tensor,
    buf1: torch.Tensor,
    buf2: torch.Tensor,
    step: int,
    betas: Tuple[float, float],
    eps: float,
    *,
    bias_correction: bool = True,
) -> torch.Tensor:
    buf1.lerp_(grad, 1 - betas[0])
    buf2.lerp_(grad.square(), 1 - betas[1])
    if bias_correction:
        buf1c = buf1 / (1 - betas[0] ** step)
        buf2c = buf2 / (1 - betas[1] ** step)
    else:
        buf1c, buf2c = buf1, buf2
    return buf1c / (buf2c.sqrt() + eps)


class SingleDeviceMuonWithAuxAdam(torch.optim.Optimizer):
    """Single-device Muon + auxiliary AdamW optimiser."""

    def __init__(self, param_groups: Iterable[Dict[str, Any]]):
        groups: List[Dict[str, Any]] = []
        for group in param_groups:
            assert "use_muon" in group, "param group must include 'use_muon' flag"
            group = dict(group)  # shallow copy so we can mutate defaults safely
            if group["use_muon"]:
                group.setdefault("lr", 0.02)
                group.setdefault("momentum", 0.95)
                group.setdefault("weight_decay", 0.0)
                group.setdefault("lr_correction", True)
                group.setdefault("clip_by_layer", False)
                expected_keys = {
                    "params",
                    "lr",
                    "momentum",
                    "weight_decay",
                    "use_muon",
                    "lr_correction",
                    "clip_by_layer",
                }
            else:
                group.setdefault("lr", 3e-4)
                group.setdefault("betas", (0.9, 0.95))
                group.setdefault("eps", 1e-10)
                group.setdefault("weight_decay", 0.0)
                group.setdefault("bias_correction", True)
                expected_keys = {
                    "params",
                    "lr",
                    "betas",
                    "eps",
                    "weight_decay",
                    "use_muon",
                    "bias_correction",
                }
            assert set(group.keys()) == expected_keys
            groups.append(group)
        super().__init__(groups, dict())

    @torch.no_grad()
    def step(self) -> None:  # type: ignore[override]
        for group in self.param_groups:
            if group["use_muon"]:
                for p in group["params"]:
                    if p.grad is None:
                        continue
                    state = self.state[p]
                    if len(state) == 0:
                        state["momentum_buffer"] = torch.zeros_like(p)
                    update = _muon_update(
                        p.grad,
                        state["momentum_buffer"],
                        beta=group["momentum"],
                        lr_correction=bool(group.get("lr_correction", True)),
                        clip_by_layer=bool(group.get("clip_by_layer", False)),
                    )
                    p.mul_(1 - group["lr"] * group["weight_decay"])
                    p.add_(update, alpha=-group["lr"])
            else:
                beta1, beta2 = group["betas"]
                for p in group["params"]:
                    grad = p.grad
                    if grad is None:
                        continue
                    state = self.state[p]
                    if len(state) == 0:
                        state["exp_avg"] = torch.zeros_like(p)
                        state["exp_avg_sq"] = torch.zeros_like(p)
                        state["step"] = 0
                    state["step"] += 1
                    update = _adam_update(
                        grad,
                        state["exp_avg"],
                        state["exp_avg_sq"],
                        state["step"],
                        (beta1, beta2),
                        group["eps"],
                        bias_correction=bool(group.get("bias_correction", True)),
                    )
                    p.mul_(1 - group["lr"] * group["weight_decay"])
                    p.add_(update, alpha=-group["lr"])


#########################################
# Factory helpers used by the trainer API
#########################################


def _group_muon_parameters(
    model: nn.Module,
    *,
    exclude_embeddings: bool = True,
) -> Tuple[List[nn.Parameter], List[nn.Parameter], List[nn.Parameter]]:
    muon_params: List[nn.Parameter] = []
    adam_decay: List[nn.Parameter] = []
    adam_no_decay: List[nn.Parameter] = []

    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        is_bias = name.endswith(".bias")
        lname = name.lower()
        is_norm = ("norm" in lname) or ("ln" in lname)
        is_embed = ("embed" in lname) or ("lm_head" in lname)
        wants_muon = (p.ndim >= 2) and (not is_bias) and (not is_norm)
        if wants_muon and exclude_embeddings:
            wants_muon = not is_embed

        if wants_muon:
            muon_params.append(p)
        else:
            if (p.ndim >= 2) and (not is_bias) and (not is_norm):
                adam_decay.append(p)
            else:
                adam_no_decay.append(p)

    return muon_params, adam_decay, adam_no_decay


def _group_adamw_parameters(model: nn.Module) -> Tuple[List[nn.Parameter], List[nn.Parameter]]:
    decay: List[nn.Parameter] = []
    no_decay: List[nn.Parameter] = []
    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        is_bias = name.endswith(".bias")
        lname = name.lower()
        is_norm = ("norm" in lname) or ("ln" in lname)
        if (p.ndim >= 2) and (not is_bias) and (not is_norm):
            decay.append(p)
        else:
            no_decay.append(p)
    return decay, no_decay


def _build_muon_optimizer(model: nn.Module, targs: Any) -> Tuple[torch.optim.Optimizer, str]:
    muon_params, adam_decay, adam_no_decay = _group_muon_parameters(
        model, exclude_embeddings=getattr(targs, "muon_exclude_embeddings", True)
    )

    param_groups: List[Dict[str, Any]] = []
    adam_lr = getattr(targs, "lr", 3e-4)
    beta1 = getattr(targs, "muon_beta1", None)
    if beta1 is None:
        beta1 = getattr(targs, "beta1", 0.9) if hasattr(targs, "beta1") else 0.9
    beta2 = getattr(targs, "muon_beta2", getattr(targs, "beta2", 0.95))
    adam_betas = (float(beta1), float(beta2))
    base_eps = getattr(targs, "optim_eps", None)
    if base_eps is None:
        base_eps = getattr(targs, "adam_eps", 1e-8)
    optim_eps = float(getattr(targs, "muon_eps", base_eps))
    weight_decay = getattr(targs, "weight_decay", 0.0)
    bias_correction = bool(getattr(targs, "muon_bias_correction", True))
    clip_by_layer = bool(getattr(targs, "muon_clip_by_layer", False))
    lr_correction = bool(getattr(targs, "muon_lr_correction", True))

    if adam_decay:
        param_groups.append(dict(
            params=adam_decay,
            use_muon=False,
            lr=adam_lr,
            betas=adam_betas,
            eps=optim_eps,
            weight_decay=weight_decay,
            bias_correction=bias_correction,
        ))
    if adam_no_decay:
        param_groups.append(dict(
            params=adam_no_decay,
            use_muon=False,
            lr=adam_lr,
            betas=adam_betas,
            eps=optim_eps,
            weight_decay=0.0,
            bias_correction=bias_correction,
        ))

    muon_lr = getattr(targs, "muon_lr", None)
    muon_lr = muon_lr if muon_lr is not None else adam_lr
    muon_momentum = getattr(targs, "muon_momentum", 0.95)
    if muon_params:
        muon_sorted = sorted(muon_params, key=lambda p: p.numel(), reverse=True)
        param_groups.append(dict(
            params=muon_sorted,
            use_muon=True,
            lr=muon_lr,
            momentum=muon_momentum,
            weight_decay=weight_decay,
            lr_correction=lr_correction,
            clip_by_layer=clip_by_layer,
        ))

    if not param_groups:
        raise RuntimeError("No parameters found for optimizer setup.")

    optimizer = SingleDeviceMuonWithAuxAdam(param_groups)

    n_muon = sum(p.numel() for p in muon_params)
    n_adam_decay = sum(p.numel() for p in adam_decay)
    n_adam_no = sum(p.numel() for p in adam_no_decay)
    parts = [
        "🧪 Muon optimizer:",
        f"muon_lr={muon_lr:g}",
        f"momentum={muon_momentum:g}",
        f"muon_params={n_muon/1e6:.2f}M",
        f"adam_lr={adam_lr:g}",
        f"adam_betas=({adam_betas[0]:.2f},{adam_betas[1]:.2f})",
        f"optim_eps={optim_eps:.1e}",
        f"bias_correction={'on' if bias_correction else 'off'}",
        f"adam_decay={n_adam_decay/1e6:.2f}M",
        f"adam_nodecay={n_adam_no/1e6:.2f}M",
        f"weight_decay={weight_decay:g}",
        f"muon_clip={'on' if clip_by_layer else 'off'}",
        f"muon_lr_corr={'on' if lr_correction else 'off'}",
    ]
    return optimizer, " | ".join(parts)


def _build_adamw_optimizer(model: nn.Module, targs: Any) -> Tuple[torch.optim.Optimizer, str]:
    decay, no_decay = _group_adamw_parameters(model)
    if not decay and not no_decay:
        raise RuntimeError("No parameters found for optimizer setup.")

    lr = getattr(targs, "lr", 3e-4)
    betas = (0.9, getattr(targs, "beta2", 0.95))
    base_eps = getattr(targs, "optim_eps", None)
    if base_eps is None:
        base_eps = getattr(targs, "adam_eps", 1e-8)
    eps = float(base_eps)
    weight_decay = getattr(targs, "weight_decay", 0.0)

    param_groups: List[Dict[str, Any]] = []
    if decay:
        param_groups.append(dict(params=decay, weight_decay=weight_decay))
    if no_decay:
        param_groups.append(dict(params=no_decay, weight_decay=0.0))

    optimizer = torch.optim.AdamW(param_groups, lr=lr, betas=betas, eps=eps)

    parts = [
        "⚙️ AdamW optimizer:",
        f"lr={lr:g}",
        f"betas=({betas[0]:.2f},{betas[1]:.2f})",
        f"eps={eps:.1e}",
        f"weight_decay={weight_decay:g}",
        f"decay_params={sum(p.numel() for p in decay)/1e6:.2f}M",
        f"nodecay_params={sum(p.numel() for p in no_decay)/1e6:.2f}M",
    ]
    return optimizer, " | ".join(parts)


def build_optimizer(model: nn.Module, targs: Any) -> Tuple[torch.optim.Optimizer, str]:
    """Return the configured optimiser and a human-readable summary string."""

    opt_name = getattr(targs, "optimizer", "muon") or "muon"
    opt_name = opt_name.lower()
    if opt_name == "muon":
        return _build_muon_optimizer(model, targs)
    if opt_name in {"adamw", "adam", "adam_w"}:
        return _build_adamw_optimizer(model, targs)
    raise ValueError(f"Unknown optimizer '{opt_name}'. Supported values: 'adamw', 'muon'.")


__all__ = [
    "build_optimizer",
    "SingleDeviceMuonWithAuxAdam",
]
