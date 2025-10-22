from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Iterable

import numpy as np

from pmarlo import constants as const

try:  # pragma: no cover - optional ML stack
    import torch  # type: ignore
except Exception:  # pragma: no cover - torch optional dependency
    torch = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - type checking only
    import torch as _torch_mod  # noqa: F401


@dataclass(slots=True)
class LossHistory:
    losses: list[float] = field(default_factory=list)
    val_losses: list[float] = field(default_factory=list)
    val_scores: list[float] = field(default_factory=list)

    def record_train(self, metrics: Dict[str, Any]) -> None:
        for key in ("train_loss", "loss"):
            if key in metrics:
                try:
                    self.losses.append(float(metrics[key]))
                except Exception:
                    pass
                break

    def record_val(self, metrics: Dict[str, Any]) -> None:
        if "val_loss" in metrics:
            try:
                self.val_losses.append(float(metrics["val_loss"]))
            except Exception:
                pass
        for key in ("val_score", "val_vamp2"):
            if key in metrics:
                try:
                    self.val_scores.append(float(metrics[key]))
                except Exception:
                    pass
                break


def collect_history_metrics(history: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "loss_curve": list(map(float, history.get("loss_curve", []))) or [],
        "val_loss_curve": list(map(float, history.get("val_loss_curve", []))) or [],
        "val_score_curve": list(map(float, history.get("val_score_curve", []))) or [],
    }


def vamp2_proxy(Y: np.ndarray, idx_t: Iterable[int], idx_tau: Iterable[int]) -> float:
    idx_t_arr = np.asarray(list(idx_t), dtype=int)
    idx_tau_arr = np.asarray(list(idx_tau), dtype=int)
    if Y.size == 0 or idx_t_arr.size == 0 or idx_tau_arr.size == 0:
        return 0.0
    A = np.asarray(Y[idx_t_arr], dtype=np.float64)
    B = np.asarray(Y[idx_tau_arr], dtype=np.float64)
    A -= np.mean(A, axis=0, keepdims=True)
    B -= np.mean(B, axis=0, keepdims=True)
    A_std = np.std(A, axis=0, ddof=1) + const.NUMERIC_MIN_POSITIVE
    B_std = np.std(B, axis=0, ddof=1) + const.NUMERIC_MIN_POSITIVE
    A /= A_std
    B /= B_std
    if A.shape[0] <= 1:
        return 0.0
    r = np.sum(A * B, axis=0) / float(A.shape[0] - 1)
    return float(np.mean(r * r))


def project_model(net: Any, Z: np.ndarray) -> np.ndarray:
    """Project numpy features through a torch module if available."""

    if torch is None:  # pragma: no cover - optional dependency guard
        raise ImportError(
            "project_model requires torch; install optional extra 'pmarlo[mlcv]'"
        )

    with torch.no_grad():
        tensor = torch.as_tensor(Z, dtype=torch.float32)
        out = net(tensor)
        if isinstance(out, torch.Tensor):
            out = out.detach().cpu().numpy()
        return np.asarray(out, dtype=np.float32)


def summarize_history(history: LossHistory) -> Dict[str, Any]:
    return {
        "loss_curve": history.losses,
        "val_loss_curve": history.val_losses,
        "val_score_curve": history.val_scores,
    }
