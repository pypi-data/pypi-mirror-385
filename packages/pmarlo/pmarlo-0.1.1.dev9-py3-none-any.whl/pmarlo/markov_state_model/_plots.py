from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import numpy as np

from pmarlo import constants as const

# Protocol describing the attributes expected by this mixin. This allows mypy
# to understand that the concrete class mixing this in provides these members.
from ._base import CKTestResult


class _HasMSMAttrs(Protocol):
    output_dir: Path
    fes_data: Optional[Dict[str, Any]]
    free_energies: Optional[np.ndarray]
    implied_timescales: Any
    time_per_frame_ps: Optional[float]
    dtrajs: List[np.ndarray]
    lag_time: int

    def compute_ck_test_macrostates(
        self, n_macrostates: int = 3, factors: Optional[List[int]] = None
    ) -> CKTestResult: ...


class PlotsMixin:
    def plot_free_energy_surface(
        self: _HasMSMAttrs, save_file: Optional[str] = None, interactive: bool = False
    ) -> None:
        if self.fes_data is None:
            raise ValueError("Free energy surface must be generated first")
        import matplotlib.pyplot as plt

        F = self.fes_data["free_energy"]
        xedges = self.fes_data["xedges"]
        yedges = self.fes_data["yedges"]
        cv1_name = self.fes_data["cv1_name"]
        cv2_name = self.fes_data["cv2_name"]

        if interactive:
            try:
                import plotly.graph_objects as go

                x_centers = 0.5 * (xedges[:-1] + xedges[1:])
                y_centers = 0.5 * (yedges[:-1] + yedges[1:])
                fig = go.Figure(
                    data=go.Contour(
                        z=F.T,
                        x=x_centers,
                        y=y_centers,
                        colorscale="viridis",
                        colorbar=dict(title="Free Energy (kJ/mol)"),
                    )
                )
                fig.update_layout(
                    title=f"Free Energy Surface ({cv1_name} vs {cv2_name})",
                    xaxis_title=cv1_name,
                    yaxis_title=cv2_name,
                )
                if save_file:
                    fig.write_html(str(self.output_dir / f"{save_file}.html"))
                fig.show()
                return
            except Exception:
                interactive = False

        plt.figure(figsize=(10, 8))
        x_centers = 0.5 * (xedges[:-1] + xedges[1:])
        y_centers = 0.5 * (yedges[:-1] + yedges[1:])
        contour = plt.contourf(x_centers, y_centers, F.T, levels=20, cmap="viridis")
        plt.colorbar(contour, label="Free Energy (kJ/mol)")
        plt.xlabel(cv1_name)
        plt.ylabel(cv2_name)
        plt.title(f"Free Energy Surface ({cv1_name} vs {cv2_name})")
        if save_file:
            plt.savefig(
                self.output_dir / f"{save_file}.png", dpi=300, bbox_inches="tight"
            )
        plt.show()

    def plot_free_energy_profile(
        self: _HasMSMAttrs, save_file: Optional[str] = None
    ) -> None:
        if self.free_energies is None:
            raise ValueError("Free energies must be computed first")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))
        state_ids = np.arange(len(self.free_energies))
        plt.bar(state_ids, self.free_energies, alpha=0.7, color="steelblue")
        plt.xlabel("State Index")
        plt.ylabel("Free Energy (kJ/mol)")
        plt.title("Free Energy Profile by State")
        plt.grid(True, alpha=0.3)
        if save_file:
            plt.savefig(
                self.output_dir / f"{save_file}.png", dpi=300, bbox_inches="tight"
            )
        plt.show()

    def plot_implied_timescales(
        self: _HasMSMAttrs, save_file: Optional[str] = None
    ) -> None:
        if self.implied_timescales is None:
            raise ValueError("Implied timescales must be computed first")
        import matplotlib.pyplot as plt

        res = self.implied_timescales
        lag_times = np.asarray(res.lag_times, dtype=float)
        timescales = np.asarray(res.timescales, dtype=float)
        ts_ci = np.asarray(res.timescales_ci, dtype=float)

        dt_ps = self.time_per_frame_ps or 1.0
        lag_ps = lag_times * dt_ps
        ts_ps = timescales * dt_ps
        ts_ci_ps = ts_ci * dt_ps

        unit_label = "ps"
        scale = 1.0
        if (np.max(lag_ps) >= 1000.0) or (np.max(ts_ps) >= 1000.0):
            unit_label = "ns"
            scale = const.MSM_RATE_DISPLAY_SCALE

        lag_plot = lag_ps * scale
        ts_plot = ts_ps * scale
        ts_ci_plot = ts_ci_ps * scale

        plt.figure(figsize=(10, 6))
        for i in range(ts_plot.shape[1]):
            mask = (
                np.isfinite(ts_plot[:, i])
                & np.isfinite(ts_ci_plot[:, i, 0])
                & np.isfinite(ts_ci_plot[:, i, 1])
            )
            if np.any(mask):
                plt.plot(
                    lag_plot[mask],
                    ts_plot[mask, i],
                    "o-",
                    label=f"τ{i+1} ({unit_label})",
                )
                plt.fill_between(
                    lag_plot[mask],
                    ts_ci_plot[mask, i, 0],
                    ts_ci_plot[mask, i, 1],
                    alpha=0.2,
                )
            else:
                plt.plot([], [], label=f"τ{i+1} ({unit_label})")
        plt.plot([], [], " ", label="NaNs indicate unstable eigenvalues at this τ")
        plt.xlabel(f"Lag Time ({unit_label})")
        plt.ylabel(f"Implied Timescale ({unit_label})")
        plt.title("Implied Timescales Analysis")
        plt.legend()
        plt.grid(True, alpha=0.3)
        if save_file:
            plt.savefig(
                self.output_dir / f"{save_file}.png", dpi=300, bbox_inches="tight"
            )
        plt.show()

    def plot_implied_rates(self: _HasMSMAttrs, save_file: Optional[str] = None) -> None:
        if self.implied_timescales is None:
            raise ValueError("Implied timescales must be computed first")
        import matplotlib.pyplot as plt

        res = self.implied_timescales
        lag_times = np.asarray(res.lag_times, dtype=float)
        rates = np.asarray(res.rates, dtype=float)
        rate_ci = np.asarray(res.rates_ci, dtype=float)

        dt_ps = self.time_per_frame_ps or 1.0
        lag_ps = lag_times * dt_ps

        lag_unit = "ps"
        lag_scale = 1.0
        if np.max(lag_ps) >= 1000.0:
            lag_unit = "ns"
            lag_scale = const.MSM_RATE_DISPLAY_SCALE

        rate_unit = "1/ps"
        rate_scale = 1.0
        if np.max(rates) < const.MSM_RATE_DISPLAY_SCALE:
            rate_unit = "1/ns"
            rate_scale = const.MSM_RATE_INVERSE_SCALE

        lag_plot = lag_ps * lag_scale
        rate_plot = rates * rate_scale
        rate_ci_plot = rate_ci * rate_scale

        plt.figure(figsize=(10, 6))
        for i in range(rate_plot.shape[1]):
            mask = (
                np.isfinite(rate_plot[:, i])
                & np.isfinite(rate_ci_plot[:, i, 0])
                & np.isfinite(rate_ci_plot[:, i, 1])
            )
            if np.any(mask):
                plt.plot(
                    lag_plot[mask],
                    rate_plot[mask, i],
                    "o-",
                    label=f"k{i+1} ({rate_unit})",
                )
                plt.fill_between(
                    lag_plot[mask],
                    rate_ci_plot[mask, i, 0],
                    rate_ci_plot[mask, i, 1],
                    alpha=0.2,
                )
            else:
                plt.plot([], [], label=f"k{i+1} ({rate_unit})")
        plt.plot([], [], " ", label="NaNs indicate unstable eigenvalues at this τ")
        plt.xlabel(f"Lag Time ({lag_unit})")
        plt.ylabel(f"Rate ({rate_unit})")
        plt.title("Implied Rates")
        plt.legend()
        plt.grid(True, alpha=0.3)
        if save_file:
            plt.savefig(
                self.output_dir / f"{save_file}.png", dpi=300, bbox_inches="tight"
            )
        plt.show()

    def plot_ck_test(
        self: _HasMSMAttrs,
        save_file: str = "ck_plot.png",
        n_macrostates: int = 3,
        factors: Optional[List[int]] = None,
    ) -> Optional[Path]:
        out_path: Path = self.output_dir / (
            save_file if str(save_file).lower().endswith(".png") else f"{save_file}.png"
        )

        import matplotlib.pyplot as _plt
        from deeptime.markov import TransitionCountEstimator  # type: ignore
        from deeptime.markov.msm import MaximumLikelihoodMSM  # type: ignore
        from deeptime.plots import plot_ck_test  # type: ignore
        from deeptime.util.validation import ck_test  # type: ignore

        base_lag = int(max(1, self.lag_time))
        facs = [2, 3, 4] if factors is None else [int(f) for f in factors if int(f) > 1]
        lags = [base_lag] + [base_lag * f for f in facs]
        models = []
        for L in lags:
            tce = TransitionCountEstimator(
                lagtime=int(L), count_mode="sliding", sparse=False
            )
            C = tce.fit(self.dtrajs).fetch_model()
            ml = MaximumLikelihoodMSM(reversible=True)
            models.append(ml.fit(C).fetch_model())
        from inspect import signature

        params = signature(ck_test).parameters
        ck_params: dict[str, Any] = {"models": models}
        if "n_metastable_sets" in params:
            ck_params["n_metastable_sets"] = int(max(2, n_macrostates))
            ckobj = ck_test(**ck_params)
            fig = plot_ck_test(ckobj)
        elif "n_sets" in params:
            ck_params["n_sets"] = int(max(2, n_macrostates))
            ckobj = ck_test(**ck_params)
            fig = plot_ck_test(ckobj)
        else:
            fig, ax = _plt.subplots(figsize=(6, 4))
            base_model = models[0]
            base_T = np.asarray(base_model.transition_matrix, dtype=float)
            x_vals: list[int] = []
            mse_vals: list[float] = []
            for idx, factor in enumerate(facs, start=1):
                empirical = np.asarray(models[idx].transition_matrix, dtype=float)
                theoretical = np.linalg.matrix_power(base_T, int(factor))
                diff = empirical - theoretical
                mse_vals.append(float(np.mean(diff * diff)))
                x_vals.append(base_lag * int(factor))
            if x_vals:
                ax.plot(x_vals, mse_vals, marker="o")
            ax.set_xlabel("Lag time")
            ax.set_ylabel("MSE")
            ax.set_title("CK test (microstates)")
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
        fig.savefig(str(out_path), dpi=200)
        _plt.close(fig)
        return out_path
