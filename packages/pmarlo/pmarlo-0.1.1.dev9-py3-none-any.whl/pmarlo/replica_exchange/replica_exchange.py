# Copyright (c) 2025 PMARLO Development Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Replica Exchange Molecular Dynamics (REMD) implementation for enhanced sampling.

This module provides functionality to run replica exchange simulations using OpenMM,
allowing for better exploration of conformational space across multiple temperatures.
"""

import json
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import openmm
from openmm import Platform, unit
from openmm.app import PDBFile, Simulation

from pmarlo import constants as const
from pmarlo.features.deeptica.export import load_cv_model_info
from pmarlo.transform.progress import ProgressCB, ProgressPrinter, ProgressReporter
from pmarlo.utils.logging_utils import (
    announce_stage_cancelled,
    announce_stage_complete,
    announce_stage_failed,
    announce_stage_start,
    format_duration,
)
from pmarlo.utils.path_utils import ensure_directory

from ..demultiplexing.demux import demux_trajectories as _demux_trajectories
from ..markov_state_model.results import REMDResult
from ..utils.integrator import create_langevin_integrator
from ..utils.naming import base_shape_str, permutation_name
from ..utils.replica_utils import exponential_temperature_ladder
from ..utils.validation import all_finite
from .config import RemdConfig
from .diagnostics import (
    compute_diffusion_metrics,
    compute_exchange_statistics,
    retune_temperature_ladder,
)
from .exchange_engine import ExchangeEngine
from .platform_selector import select_platform_and_properties
from .system_builder import (
    create_system,
    load_pdb_and_forcefield,
    log_system_info,
    setup_metadynamics,
)
from .trajectory import ClosableDCDReporter


class RunningStats:
    """Track running mean and standard deviation for vector inputs."""

    def __init__(self, dim: int) -> None:
        if dim <= 0:
            raise ValueError("dim must be a positive integer")
        self._dim = int(dim)
        self._count = 0
        self._mean = np.zeros(self._dim, dtype=float)
        self._m2 = np.zeros(self._dim, dtype=float)

    @property
    def count(self) -> int:
        return self._count

    def update(self, values: Sequence[float] | np.ndarray) -> None:
        arr = np.asarray(values, dtype=float).reshape(-1)
        if arr.size != self._dim:
            raise ValueError(
                f"Expected values of length {self._dim}, received {arr.size}"
            )
        self._count += 1
        delta = arr - self._mean
        self._mean += delta / self._count
        self._m2 += delta * (arr - self._mean)

    def summary(self) -> Tuple[np.ndarray, np.ndarray]:
        if self._count == 0:
            return self._mean.copy(), np.zeros(self._dim, dtype=float)
        if self._count == 1:
            return self._mean.copy(), np.zeros(self._dim, dtype=float)
        variance = self._m2 / max(1, self._count - 1)
        variance = np.clip(variance, a_min=0.0, a_max=None)
        return self._mean.copy(), np.sqrt(variance)


logger = logging.getLogger("pmarlo")


class ReplicaExchange:
    """
    Replica Exchange Molecular Dynamics implementation using OpenMM.

    This class handles the setup and execution of REMD simulations,
    managing multiple temperature replicas and exchange attempts.
    """

    def __init__(
        self,
        pdb_file: str,
        forcefield_files: Optional[List[str]] = None,
        temperatures: Optional[List[float]] = None,
        output_dir: str = "output/replica_exchange",
        exchange_frequency: int = 50,  # Very frequent exchanges for testing
        auto_setup: bool = False,
        dcd_stride: int = 1,
        target_accept: float = 0.30,
        config: Optional[RemdConfig] = None,
        random_seed: Optional[int] = None,
        random_state: int | None = None,
        start_from_checkpoint: Optional[str | Path] = None,
        start_from_pdb: Optional[str | Path] = None,
        jitter_sigma_A: float = 0.0,
        reseed_velocities: bool = False,
        temperature_schedule_mode: str | None = None,
    ):  # Explicit opt-in for auto-setup
        """
        Initialize the replica exchange simulation.

        Args:
            pdb_file: Path to the prepared PDB file
            forcefield_files: List of forcefield XML files
            temperatures: List of temperatures in Kelvin for replicas
            output_dir: Directory to store output files
            exchange_frequency: Number of steps between exchange attempts
            auto_setup: Whether to automatically set up replicas during initialization
            target_accept: Desired per-pair exchange acceptance probability
            random_state: Seed for deterministic behaviour. ``random_seed`` is
                accepted for backward compatibility and is overridden by
                ``random_state`` when both are provided.
        """
        self.pdb_file = pdb_file
        self.forcefield_files = forcefield_files or [
            "amber14-all.xml",
            "amber14/tip3pfb.xml",
        ]
        self.temperatures = temperatures or self._generate_temperature_ladder()
        # Validate temperature ladder when explicitly provided or generated
        self._validate_temperature_ladder(self.temperatures)

        self.output_dir: Path = ensure_directory(Path(output_dir))
        self.exchange_frequency = exchange_frequency
        self.dcd_stride = dcd_stride
        self.target_accept = target_accept
        self.reporter_stride: Optional[int] = None
        self._replica_reporter_stride: List[int] = []
        self.frames_per_replica_target: Optional[int] = None

        # Output directory is guaranteed to exist (parents included)

        # Reproducibility: RNG seeding
        if (
            config
            and hasattr(config, "target_frames_per_replica")
            and getattr(config, "target_frames_per_replica", None) is not None
        ):
            try:
                self.frames_per_replica_target = int(
                    getattr(config, "target_frames_per_replica")
                )
            except Exception:
                self.frames_per_replica_target = None
        if config and getattr(config, "random_seed", None) is not None:
            seed = int(getattr(config, "random_seed"))
        elif random_state is not None:
            seed = int(random_state)
        elif random_seed is not None:
            seed = int(random_seed)
        else:
            seed = int.from_bytes(os.urandom(8), "little") & 0x7FFFFFFF

        self.random_seed = seed
        self.rng = np.random.default_rng(seed)
        self._exchange_engine: ExchangeEngine | None = None
        self._sync_exchange_engine()

        # Resume / restart options
        self.resume_checkpoint: Optional[Path] = (
            Path(start_from_checkpoint) if start_from_checkpoint else None
        )
        self.resume_pdb: Optional[Path] = (
            Path(start_from_pdb) if start_from_pdb else None
        )
        # Jitter sigma in nanometers (A * 0.1)
        try:
            self.resume_jitter_sigma_nm: float = float(jitter_sigma_A) * 0.1
        except Exception:
            self.resume_jitter_sigma_nm = 0.0
        self.reseed_velocities: bool = bool(reseed_velocities)
        self.temperature_schedule_mode: str | None = (
            str(temperature_schedule_mode) if temperature_schedule_mode else None
        )

        # Initialize replicas - Fixed: Added proper type annotations
        self.n_replicas = len(self.temperatures)
        self.replicas: List[Simulation] = (
            []
        )  # Fixed: Added type annotation for Simulation objects
        self.contexts: List[openmm.Context] = (
            []
        )  # Fixed: Added type annotation for OpenMM Context objects
        self.integrators: List[openmm.Integrator] = (
            []
        )  # Fixed: Added type annotation for OpenMM Integrator objects
        self._is_setup = False  # Track setup state

        # Exchange statistics
        self.exchange_attempts = 0
        self.exchanges_accepted = 0
        self.replica_states = list(
            range(self.n_replicas)
        )  # Which temperature each replica is at
        self.state_replicas = list(
            range(self.n_replicas)
        )  # Which replica is at each temperature
        # Per-pair statistics (temperature index pairs)
        self.pair_attempt_counts: dict[tuple[int, int], int] = {}
        self.pair_accept_counts: dict[tuple[int, int], int] = {}

        # Simulation data - Fixed: Added proper type annotations
        self.trajectory_files: List[Path] = (
            []
        )  # Fixed: Added type annotation for Path objects
        self.energies: List[float] = []  # Fixed: Added type annotation for float values
        self.exchange_history: List[List[int]] = (
            []
        )  # Fixed: Added type annotation for nested int lists
        # Diagnostics accumulation
        self.acceptance_matrix: Optional[np.ndarray] = None
        self.replica_visit_counts: Optional[np.ndarray] = None

        # CV bias monitoring (see Prompt 3: periodic logging every 1000 steps)
        self._bias_log_interval: int = 1000
        self._cv_monitor_module: Any | None = None
        self._bias_energy_stats: RunningStats | None = None
        self._bias_cv_stats: RunningStats | None = None
        self._bias_steps_completed = 0
        self._bias_next_log = 0

        logger.info(f"Initialized REMD with {self.n_replicas} replicas")
        logger.info(
            (
                f"Temperature range: {min(self.temperatures):.1f} - "
                f"{max(self.temperatures):.1f} K"
            )
        )

        # Auto-setup if requested (for API consistency)
        if auto_setup:
            logger.info("Auto-setting up replicas...")
            # Ensure a reporter stride exists for auto-setup
            if self.reporter_stride is None:
                self.reporter_stride = max(1, self.dcd_stride)
                logger.info(
                    f"Reporter stride not planned; defaulting to dcd_stride={self.reporter_stride} for auto_setup"
                )
            self.setup_replicas()

    @classmethod
    def from_config(cls, config: RemdConfig) -> "ReplicaExchange":
        """Construct instance using immutable RemdConfig as single source of truth."""
        # Normalize pdb_file to str
        assert config.pdb_file is not None, "pdb_file must be set in config"
        pdb_file_str = str(config.pdb_file)

        return cls(
            pdb_file=pdb_file_str,
            forcefield_files=config.forcefield_files,
            temperatures=config.temperatures,
            output_dir=str(config.output_dir),
            exchange_frequency=config.exchange_frequency,
            auto_setup=config.auto_setup,
            dcd_stride=config.dcd_stride,
            target_accept=config.target_accept,
            config=config,
            random_seed=getattr(config, "random_seed", None),
            start_from_checkpoint=getattr(config, "start_from_checkpoint", None),
            start_from_pdb=getattr(config, "start_from_pdb", None),
            jitter_sigma_A=float(getattr(config, "jitter_sigma_A", 0.0) or 0.0),
            reseed_velocities=bool(getattr(config, "reseed_velocities", False)),
            temperature_schedule_mode=getattr(
                config, "temperature_schedule_mode", None
            ),
        )

    def plan_reporter_stride(
        self,
        total_steps: int,
        equilibration_steps: int,
        target_frames: int = 5000,
    ) -> int:
        """Plan and freeze the reporter stride for this run.

        Decide the DCD stride once, before reporters are added, and store it.
        """
        assert self.reporter_stride is None, "reporter_stride already planned"
        production_steps = max(0, total_steps - equilibration_steps)
        stride = max(1, production_steps // max(1, target_frames))
        self.reporter_stride = stride
        return stride

    def plan_runtime(
        self,
        walltime: float,
        throughput_estimator: Callable[[], float] | float,
        transitions_per_state: int = 50,
        n_states: Optional[int] = None,
        equilibration_fraction: float = 0.1,
        dry_run: bool = False,
    ) -> Dict[str, int]:
        """Plan steps, stride and exchange frequency for a walltime budget.

        Parameters
        ----------
        walltime:
            Total wall-clock time budget in seconds.
        throughput_estimator:
            Either a callable returning estimated MD steps per second or a
            numeric value.
        transitions_per_state:
            Minimum effective transitions required per state.
        n_states:
            Number of states; defaults to the number of replicas.
        equilibration_fraction:
            Fraction of total steps reserved for equilibration.
        dry_run:
            If ``True``, only compute and log the plan without mutating
            instance attributes.
        """

        steps_per_second = (
            float(throughput_estimator())
            if callable(throughput_estimator)
            else float(throughput_estimator)
        )
        total_steps = int(max(1, walltime * steps_per_second))
        min_equil = 200
        equilibration_steps = int(max(min_equil, total_steps * equilibration_fraction))
        production_steps = max(0, total_steps - equilibration_steps)
        states = int(n_states or self.n_replicas)
        target_frames = max(1, transitions_per_state * states)
        stride = max(1, production_steps // target_frames)
        exchange_frequency = max(1, production_steps // target_frames)
        expected_frames = production_steps // stride
        plan = {
            "total_steps": total_steps,
            "equilibration_steps": equilibration_steps,
            "exchange_frequency": exchange_frequency,
            "reporter_stride": stride,
            "expected_frames": expected_frames,
        }
        logger.info(
            (
                "Runtime plan: total_steps=%d equilibration=%d stride=%d "
                "exchange_frequency=%d expected_frames=%d"
            ),
            total_steps,
            equilibration_steps,
            stride,
            exchange_frequency,
            expected_frames,
        )
        if not dry_run:
            self.exchange_frequency = exchange_frequency
            self.plan_reporter_stride(
                total_steps, equilibration_steps, target_frames=target_frames
            )
        return plan

    def _generate_temperature_ladder(
        self,
        min_temp: float = 300.0,
        max_temp: float = 350.0,
        n_replicas: int = 3,
    ) -> List[float]:
        """
        Generate an exponential temperature ladder for optimal exchange
        efficiency.

        Delegates to
        `utils.replica_utils.exponential_temperature_ladder` to avoid
        duplication.
        """
        return exponential_temperature_ladder(min_temp, max_temp, n_replicas)

    def _temperature_index(self, target: float) -> int:
        if not self.temperatures:
            raise ValueError("Temperature ladder is empty; call setup before export.")
        target = float(target)
        return min(
            range(len(self.temperatures)),
            key=lambda idx: abs(float(self.temperatures[idx]) - target),
        )

    def _replica_index_for_temperature(self, target: float) -> int:
        temperature_index = self._temperature_index(target)
        if temperature_index >= len(self.state_replicas):
            raise IndexError(
                "Replica mapping unavailable; ensure simulation has been executed."
            )
        replica_index = int(self.state_replicas[temperature_index])
        if not (0 <= replica_index < len(self.replicas)):
            raise IndexError(
                f"Resolved replica index {replica_index} is outside the valid range."
            )
        return replica_index

    def export_current_structure(
        self,
        destination: str | Path,
        *,
        temperature: float | None = None,
        replica_index: int | None = None,
        keep_atom_ids: bool = True,
    ) -> Path:
        """Write the current structure for a replica to a PDB file.

        Parameters
        ----------
        destination:
            Output PDB filepath.
        temperature:
            Target temperature (Kelvin) whose replica coordinates should be
            exported. Mutually exclusive with ``replica_index``.
        replica_index:
            Explicit replica index to export. Overrides ``temperature``.
        keep_atom_ids:
            Whether to preserve atom serial numbers in the output PDB.

        Returns
        -------
        Path
            Resolved path to the written PDB file.
        """
        if temperature is not None and replica_index is not None:
            raise ValueError("Specify either temperature or replica_index, not both.")

        dest = Path(destination)
        ensure_directory(dest.parent)

        if replica_index is None:
            target_temp = (
                float(temperature)
                if temperature is not None
                else float(self.temperatures[0])
            )
            replica_index = self._replica_index_for_temperature(target_temp)
        elif not (0 <= replica_index < len(self.replicas)):
            raise IndexError(
                f"Replica index {replica_index} is outside the valid range."
            )

        simulation = self.replicas[replica_index]
        state = simulation.context.getState(getPositions=True, enforcePeriodicBox=True)
        positions = state.getPositions()
        with dest.open("w", encoding="utf-8") as handle:
            PDBFile.writeFile(
                simulation.topology,
                positions,
                handle,
                keepIds=bool(keep_atom_ids),
            )
        return dest.resolve()

    def setup_replicas(self, bias_variables: Optional[List] = None):
        """
        Set up all replica simulations with different temperatures.

        Args:
            bias_variables: Optional list of bias variables for metadynamics
        """
        logger.info("Setting up replica simulations...")
        # Enforce stride planning before creating reporters
        assert (
            self.reporter_stride is not None and self.reporter_stride > 0
        ), "reporter_stride is not planned. Call plan_reporter_stride(...) before setup_replicas()"

        pdb, forcefield = load_pdb_and_forcefield(self.pdb_file, self.forcefield_files)
        resume_positions = None
        if self.resume_pdb is not None and Path(self.resume_pdb).exists():
            try:
                pdb_resume = PDBFile(str(self.resume_pdb))
                # Optional small Gaussian jitter in nm
                if self.resume_jitter_sigma_nm > 0.0:
                    import numpy as _np

                    arr = _np.array(
                        [[v.x, v.y, v.z] for v in pdb_resume.positions], dtype=float
                    )
                    noise = _np.random.normal(
                        loc=0.0,
                        scale=float(self.resume_jitter_sigma_nm),
                        size=arr.shape,
                    )
                    arr = arr + noise
                    from openmm import Vec3

                    resume_positions = [
                        Vec3(float(x), float(y), float(z)) * unit.nanometer
                        for x, y, z in arr
                    ]
                else:
                    resume_positions = pdb_resume.positions
                logger.info(
                    "Resuming replicas from PDB positions: %s (jitter_nm=%.4f)",
                    str(self.resume_pdb),
                    float(self.resume_jitter_sigma_nm),
                )
            except Exception as exc:
                logger.warning(
                    "Failed to load resume PDB %s: %s", str(self.resume_pdb), exc
                )
                resume_positions = None
        # Pass CV model info if available
        cv_model_path = getattr(self, "cv_model_path", None)
        cv_scaler_mean = getattr(self, "cv_scaler_mean", None)
        cv_scaler_scale = getattr(self, "cv_scaler_scale", None)

        system = create_system(
            pdb,
            forcefield,
            cv_model_path=cv_model_path,
            cv_scaler_mean=cv_scaler_mean,
            cv_scaler_scale=cv_scaler_scale,
        )
        log_system_info(system, logger)
        self.metadynamics = setup_metadynamics(
            system, bias_variables, self.temperatures[0], self.output_dir
        )

        # Initialize CV monitoring if model path provided
        if cv_model_path is not None:
            try:
                import torch

                info = load_cv_model_info(
                    Path(cv_model_path).parent, Path(cv_model_path).stem
                )
                cv_dim = int(info.get("config", {}).get("cv_dim", 0))
                if cv_dim <= 0:
                    raise ValueError("cv_dim metadata missing from CV model config.")
                self._cv_monitor_module = torch.jit.load(
                    str(cv_model_path), map_location="cpu"
                )
                self._cv_monitor_module.eval()
                self._bias_energy_stats = RunningStats(dim=1)
                self._bias_cv_stats = RunningStats(dim=cv_dim)
                self._bias_steps_completed = 0
                self._bias_next_log = self._bias_log_interval
                logger.info(
                    "CV monitoring initialized (logging interval: %d steps)",
                    self._bias_log_interval,
                )
            except Exception as exc:
                logger.warning(
                    "Unable to initialise CV monitoring for logging: %s", exc
                )
                self._cv_monitor_module = None
                self._bias_energy_stats = None
                self._bias_cv_stats = None
        platform, platform_properties = select_platform_and_properties(
            logger, prefer_deterministic=True if self.random_seed is not None else False
        )

        shared_minimized_positions = None

        for i, temperature in enumerate(self.temperatures):
            logger.info(f"Setting up replica {i} at {temperature}K...")

            integrator = self._create_integrator_for_temperature(temperature)
            # Offset integrator seed per replica
            try:
                integrator.setRandomNumberSeed(int(self.random_seed + i))
            except Exception:
                pass
            simulation = self._create_simulation(
                pdb, system, integrator, platform, platform_properties
            )
            try:
                if resume_positions is not None:
                    simulation.context.setPositions(resume_positions)
                else:
                    simulation.context.setPositions(pdb.positions)
            except Exception:
                simulation.context.setPositions(pdb.positions)
            # Optional velocity reseed on start
            if self.reseed_velocities:
                try:
                    simulation.context.setVelocitiesToTemperature(
                        temperature * unit.kelvin
                    )
                except Exception:
                    pass

            if (
                shared_minimized_positions is not None
                and self._reuse_minimized_positions_quick_minimize(
                    simulation, shared_minimized_positions, i
                )
            ):
                traj_file = self._add_dcd_reporter(simulation, i)
                self._store_replica_data(simulation, integrator, traj_file)
                logger.info(f"Replica {i:02d}: T = {temperature:.1f} K")
                continue

            logger.info(f"  Minimizing energy for replica {i}...")
            self._check_initial_energy(simulation, i)
            minimization_success = self._perform_stage1_minimization(simulation, i)

            if minimization_success:
                shared_minimized_positions = (
                    self._perform_stage2_minimization_and_validation(
                        simulation, i, shared_minimized_positions
                    )
                )

            traj_file = self._add_dcd_reporter(simulation, i)
            self._store_replica_data(simulation, integrator, traj_file)
            logger.info(f"Replica {i:02d}: T = {temperature:.1f} K")

        logger.info("All replicas set up successfully")
        self._is_setup = True

    # --- Helper methods for setup_replicas ---

    def _create_integrator_for_temperature(
        self, temperature: float
    ) -> openmm.Integrator:
        return create_langevin_integrator(temperature, self.random_seed)

    def _create_simulation(
        self,
        pdb: PDBFile,
        system: openmm.System,
        integrator: openmm.Integrator,
        platform: Platform,
        platform_properties: Dict[str, str],
    ) -> Simulation:
        return Simulation(
            pdb.topology, system, integrator, platform, platform_properties or None
        )

    def _reuse_minimized_positions_quick_minimize(
        self,
        simulation: Simulation,
        shared_minimized_positions,
        replica_index: int,
    ) -> bool:
        try:
            simulation.context.setPositions(shared_minimized_positions)
            simulation.minimizeEnergy(
                maxIterations=50,
                tolerance=10.0 * unit.kilojoules_per_mole / unit.nanometer,
            )
            logger.info(
                (
                    f"  Reused minimized coordinates for replica {replica_index} "
                    f"(quick touch-up)"
                )
            )
            return True
        except Exception as exc:
            logger.warning(
                (
                    f"  Failed to reuse minimized coords for replica "
                    f"{replica_index}: {exc}; falling back to full minimization"
                )
            )
            return False

    def _check_initial_energy(self, simulation: Simulation, replica_index: int) -> None:
        try:
            initial_state = simulation.context.getState(getEnergy=True)
            initial_energy = initial_state.getPotentialEnergy()
            logger.info(
                f"  Initial energy for replica {replica_index}: {initial_energy}"
            )
            energy_val = initial_energy.value_in_unit(unit.kilojoules_per_mole)
            if abs(energy_val) > const.NUMERIC_HARD_ENERGY_LIMIT:
                logger.warning(
                    (
                        "  Very high initial energy ("
                        f"{energy_val:.2e} kJ/mol) detected for replica "
                        f"{replica_index}"
                    )
                )
        except Exception as exc:
            logger.warning(
                f"  Could not check initial energy for replica {replica_index}: {exc}"
            )

    def _perform_stage1_minimization(
        self, simulation: Simulation, replica_index: int
    ) -> bool:
        minimization_success = False
        schedule = [(50, 100.0), (100, 50.0), (200, 10.0)]
        for attempt, (max_iter, tolerance_val) in enumerate(schedule):
            try:
                tolerance = tolerance_val * unit.kilojoules_per_mole / unit.nanometer
                simulation.minimizeEnergy(maxIterations=max_iter, tolerance=tolerance)
                logger.info(
                    (
                        "  Stage 1 minimization completed for replica "
                        f"{replica_index} (attempt {attempt + 1})"
                    )
                )
                minimization_success = True
                break
            except Exception as exc:
                logger.warning(
                    (
                        "  Stage 1 minimization attempt "
                        f"{attempt + 1} failed for replica {replica_index}: {exc}"
                    )
                )
                if attempt == len(schedule) - 1:
                    logger.error(
                        f"  All minimization attempts failed for replica {replica_index}"
                    )
                    raise RuntimeError(
                        (
                            f"Energy minimization failed for replica {replica_index} "
                            "after 3 attempts. Structure may be too distorted. "
                            "Consider: 1) Better initial structure, 2) Different "
                            "forcefield, 3) Manual structure preparation"
                        )
                    )
        return minimization_success

    def _perform_stage2_minimization_and_validation(
        self,
        simulation: Simulation,
        replica_index: int,
        shared_minimized_positions,
    ):
        try:
            self._stage2_minimize(simulation, replica_index)
            state = self._get_state_with_positions(simulation)
            energy = state.getPotentialEnergy()
            positions = state.getPositions()
            self._validate_energy(energy, replica_index)
            self._validate_positions(positions, replica_index)
            logger.info(f"  Final energy for replica {replica_index}: {energy}")
            if shared_minimized_positions is None:
                shared_minimized_positions = self._cache_minimized_positions_safe(state)
            return shared_minimized_positions
        except Exception as exc:
            self._log_stage2_failure(replica_index, exc)
            self._log_using_stage1_energy(simulation, replica_index)
            return shared_minimized_positions

    # ---- Helpers for stage 2 minimization (split for C901) ----

    def _stage2_minimize(self, simulation: Simulation, replica_index: int) -> None:
        simulation.minimizeEnergy(
            maxIterations=100, tolerance=1.0 * unit.kilojoules_per_mole / unit.nanometer
        )
        logger.info(f"  Stage 2 minimization completed for replica {replica_index}")

    def _get_state_with_positions(self, simulation: Simulation):
        return simulation.context.getState(
            getPositions=True, getEnergy=True, getVelocities=True
        )

    def _validate_energy(self, energy, replica_index: int) -> None:
        energy_val = float(energy.value_in_unit(unit.kilojoules_per_mole))
        if not all_finite(energy_val):
            raise ValueError(
                (
                    "Invalid energy ("
                    f"{energy}) detected after minimization for replica "
                    f"{replica_index}"
                )
            )
        if abs(energy_val) > const.NUMERIC_SOFT_ENERGY_LIMIT:
            logger.warning(
                (
                    f"  High final energy ({energy_val:.2e} kJ/mol) for "
                    f"replica {replica_index}"
                )
            )

    def _validate_positions(self, positions, replica_index: int) -> None:
        pos_array = positions.value_in_unit(unit.nanometer)
        if not all_finite(pos_array):
            raise ValueError(
                (
                    "Invalid positions detected after minimization for "
                    f"replica {replica_index}"
                )
            )

    def _cache_minimized_positions_safe(self, state):
        try:
            logger.info("  Cached minimized coordinates from replica 0 for reuse")
            return state.getPositions()
        except Exception:
            return None

    def _log_stage2_failure(self, replica_index: int, exc: Exception) -> None:
        logger.error(
            (
                "  Stage 2 minimization or validation failed for replica "
                f"{replica_index}: {exc}"
            )
        )
        logger.warning(
            (
                "  Attempting to continue with Stage 1 result for replica "
                f"{replica_index}"
            )
        )

    def _log_using_stage1_energy(
        self, simulation: Simulation, replica_index: int
    ) -> None:
        try:
            state = simulation.context.getState(getEnergy=True)
            energy = state.getPotentialEnergy()
            logger.info(f"  Using Stage 1 energy for replica {replica_index}: {energy}")
        except Exception:
            raise RuntimeError(
                f"Complete minimization failure for replica {replica_index}"
            )

    def _add_dcd_reporter(self, simulation: Simulation, replica_index: int) -> Path:
        traj_file = self.output_dir / f"replica_{replica_index:02d}.dcd"
        stride = int(
            self.reporter_stride
            if self.reporter_stride is not None
            else max(1, self.dcd_stride)
        )
        dcd_reporter = ClosableDCDReporter(str(traj_file), stride)
        simulation.reporters.append(dcd_reporter)
        self._replica_reporter_stride.append(stride)
        return traj_file

    @staticmethod
    def _validate_temperature_ladder(temps: List[float]) -> None:
        if temps is None:
            raise ValueError("Temperature ladder is None")
        if len(temps) < 2:
            raise ValueError("Temperature ladder must have at least 2 values")
        last = None
        for t in temps:
            if float(t) <= 0.0:
                raise ValueError("Temperatures must be > 0 K")
            if last is not None and float(t) <= float(last):
                raise ValueError("Temperature ladder must be strictly increasing")
            last = t

    def _store_replica_data(
        self,
        simulation: Simulation,
        integrator: openmm.Integrator,
        traj_file: Path,
    ) -> None:
        self.replicas.append(simulation)
        self.integrators.append(integrator)
        self.contexts.append(simulation.context)
        self.trajectory_files.append(traj_file)

    def is_setup(self) -> bool:
        """
        Check if replicas are properly set up.

        Returns:
            True if replicas are set up, False otherwise
        """
        return (
            self._is_setup
            and len(self.contexts) == self.n_replicas
            and len(self.replicas) == self.n_replicas
        )

    def auto_setup_if_needed(self, bias_variables: Optional[List] = None):
        """
        Automatically set up replicas if not already done.

        Args:
            bias_variables: Optional list of bias variables for metadynamics
        """
        if not self.is_setup():
            logger.info("Auto-setting up replicas...")
            self.setup_replicas(bias_variables=bias_variables)

    def _sync_exchange_engine(self) -> ExchangeEngine:
        if self._exchange_engine is None:
            self._exchange_engine = ExchangeEngine(self.temperatures, self.rng)
        else:
            self._exchange_engine.temperatures = self.temperatures
            self._exchange_engine.rng = self.rng
        return self._exchange_engine

    def save_checkpoint_state(self) -> Dict[str, Any]:
        """
        Save the current state for checkpointing.

        Returns:
            Dictionary containing the current state
        """
        if not self.is_setup():
            return {"setup": False}

        # Save critical state information
        state = {
            "setup": True,
            "n_replicas": self.n_replicas,
            "temperatures": self.temperatures,
            "replica_states": self.replica_states.copy(),
            "state_replicas": self.state_replicas.copy(),
            "exchange_attempts": self.exchange_attempts,
            "exchanges_accepted": self.exchanges_accepted,
            "exchange_history": self.exchange_history.copy(),
            "output_dir": str(self.output_dir),
            "exchange_frequency": self.exchange_frequency,
            "random_seed": self.random_seed,
            "rng_state": self.rng.bit_generator.state,
        }

        # Save states in XML for long-term stability across versions
        from openmm import XmlSerializer  # type: ignore

        replica_xml_states: List[str] = []
        for i, context in enumerate(self.contexts):
            try:
                sim_state = context.getState(
                    getPositions=True, getVelocities=True, getEnergy=True
                )
                xml_str = XmlSerializer.serialize(sim_state)
                replica_xml_states.append(xml_str)
            except Exception as e:
                logger.warning(f"Could not save state XML for replica {i}: {e}")
                replica_xml_states.append("")

        state["replica_state_xml"] = replica_xml_states
        # Persist reporter stride data for demux after resume
        state["reporter_stride"] = int(self.reporter_stride or max(1, self.dcd_stride))
        state["replica_reporter_strides"] = self._replica_reporter_stride.copy()
        return state

    def restore_from_checkpoint(
        self, checkpoint_state: Dict[str, Any], bias_variables: Optional[List] = None
    ):
        """
        Restore the replica exchange from a checkpoint state.

        Args:
            checkpoint_state: Previously saved state dictionary
            bias_variables: Optional list of bias variables for metadynamics
        """
        if not checkpoint_state.get("setup", False):
            logger.info(
                "Checkpoint indicates replicas were not set up, setting up now..."
            )
            self.setup_replicas(bias_variables=bias_variables)
            return

        logger.info("Restoring replica exchange from checkpoint...")

        # Restore basic state
        self.exchange_attempts = checkpoint_state.get("exchange_attempts", 0)
        self.exchanges_accepted = checkpoint_state.get("exchanges_accepted", 0)
        self.exchange_history = checkpoint_state.get("exchange_history", [])
        self.replica_states = checkpoint_state.get(
            "replica_states", list(range(self.n_replicas))
        )
        self.state_replicas = checkpoint_state.get(
            "state_replicas", list(range(self.n_replicas))
        )
        # Restore RNG for reproducible continuation
        self.random_seed = checkpoint_state.get("random_seed", self.random_seed)
        rng_state = checkpoint_state.get("rng_state")
        self.rng = np.random.default_rng()
        if rng_state is not None:
            try:
                self.rng.bit_generator.state = rng_state
            except Exception:
                self.rng = np.random.default_rng(self.random_seed)
        else:
            self.rng = np.random.default_rng(self.random_seed)
        self._sync_exchange_engine()

        # If replicas aren't set up, set them up first
        if not self.is_setup():
            logger.info("Setting up replicas for checkpoint restoration...")
            self.setup_replicas(bias_variables=bias_variables)

        # Restore reporter stride info if present
        self.reporter_stride = checkpoint_state.get(
            "reporter_stride", self.reporter_stride
        )
        saved_replica_strides = checkpoint_state.get("replica_reporter_strides")
        if isinstance(saved_replica_strides, list):
            try:
                self._replica_reporter_stride = [int(x) for x in saved_replica_strides]
            except Exception:
                pass

        # Restore replica states from XML if available
        from openmm import XmlSerializer  # type: ignore

        replica_xml = checkpoint_state.get("replica_state_xml", [])
        if replica_xml and len(replica_xml) == self.n_replicas:
            logger.info("Restoring individual replica states from XML...")
            for i, (context, xml_str) in enumerate(zip(self.contexts, replica_xml)):
                if xml_str:
                    try:
                        state_obj = XmlSerializer.deserialize(xml_str)
                        if state_obj.getPositions() is not None:
                            context.setPositions(state_obj.getPositions())
                        if state_obj.getVelocities() is not None:
                            context.setVelocities(state_obj.getVelocities())
                        logger.info(f"Restored state for replica {i}")
                    except Exception as e:
                        logger.warning(f"Could not restore state for replica {i}: {e}")
                        # Continue with default state

        logger.info(
            "Checkpoint restoration complete. Exchange stats: "
            f"{self.exchanges_accepted}/{self.exchange_attempts}"
        )

    def calculate_exchange_probability(self, replica_i: int, replica_j: int) -> float:
        """
        Calculate the probability of exchanging two replicas.

        Args:
            replica_i: Index of first replica
            replica_j: Index of second replica

        Returns:
            Exchange probability
        """
        # BOUNDS CHECKING: Ensure replica indices are valid
        if replica_i < 0 or replica_i >= len(self.contexts):
            raise ValueError(
                f"replica_i={replica_i} is out of bounds [0, {len(self.contexts)})"
            )
        if replica_j < 0 or replica_j >= len(self.contexts):
            raise ValueError(
                f"replica_j={replica_j} is out of bounds [0, {len(self.contexts)})"
            )

        # Get current energies
        state_i = self.contexts[replica_i].getState(getEnergy=True)
        state_j = self.contexts[replica_j].getState(getEnergy=True)

        energy_i = state_i.getPotentialEnergy()
        energy_j = state_j.getPotentialEnergy()

        # Get temperatures
        temp_i = self.temperatures[self.replica_states[replica_i]]
        temp_j = self.temperatures[self.replica_states[replica_j]]

        engine = self._sync_exchange_engine()
        delta = engine.delta_from_values(temp_i, temp_j, energy_i, energy_j)
        prob = engine.probability_from_delta(delta)

        # Debug logging for troubleshooting low acceptance rates
        logger.debug(
            (
                f"Exchange calculation: E_i={energy_i}, E_j={energy_j}, "
                f"T_i={temp_i:.1f}K, T_j={temp_j:.1f}K, "
                f"delta={delta:.3f}, prob={prob:.6f}"
            )
        )

        return float(prob)  # Fixed: Explicit float conversion to avoid Any return type

    def attempt_exchange(
        self,
        replica_i: int,
        replica_j: int,
        energies: Optional[List[openmm.unit.quantity.Quantity]] = None,
    ) -> bool:
        """
        Attempt to exchange two replicas.

        Args:
            replica_i: Index of first replica
            replica_j: Index of second replica

        Returns:
            True if exchange was accepted, False otherwise
        """
        # BOUNDS CHECKING: Ensure replica indices are valid
        self._validate_replica_indices(replica_i, replica_j)

        self.exchange_attempts += 1

        # Calculate exchange probability (use cached energies if provided)
        prob = (
            self._calculate_probability_from_cached(replica_i, replica_j, energies)
            if energies is not None
            else self.calculate_exchange_probability(replica_i, replica_j)
        )

        # Track per-pair stats and perform the exchange if accepted
        state_i_val = self.replica_states[replica_i]
        state_j_val = self.replica_states[replica_j]
        pair = (min(state_i_val, state_j_val), max(state_i_val, state_j_val))
        self.pair_attempt_counts[pair] = self.pair_attempt_counts.get(pair, 0) + 1

        engine = self._sync_exchange_engine()
        if engine.accept(prob):
            self._perform_exchange(replica_i, replica_j)
            self.exchanges_accepted += 1
            self.pair_accept_counts[pair] = self.pair_accept_counts.get(pair, 0) + 1
            logger.debug(
                (
                    f"Exchange accepted: replica {replica_i} <-> {replica_j} "
                    f"(prob={prob:.3f})"
                )
            )
            return True

        logger.debug(
            (
                f"Exchange rejected: replica {replica_i} <-> {replica_j} "
                f"(prob={prob:.3f})"
            )
        )
        return False

    # --- Helper methods for attempt_exchange ---

    def _validate_replica_indices(self, replica_i: int, replica_j: int) -> None:
        if replica_i < 0 or replica_i >= self.n_replicas:
            raise ValueError(
                f"replica_i={replica_i} is out of bounds [0, {self.n_replicas})"
            )
        if replica_j < 0 or replica_j >= self.n_replicas:
            raise ValueError(
                f"replica_j={replica_j} is out of bounds [0, {self.n_replicas})"
            )
        if replica_i >= len(self.contexts):
            raise RuntimeError(
                f"replica_i={replica_i} >= len(contexts)={len(self.contexts)}"
            )
        if replica_j >= len(self.contexts):
            raise RuntimeError(
                f"replica_j={replica_j} >= len(contexts)={len(self.contexts)}"
            )

    def _calculate_probability_from_cached(
        self,
        replica_i: int,
        replica_j: int,
        energies: List[openmm.unit.quantity.Quantity],
    ) -> float:
        engine = self._sync_exchange_engine()
        return engine.calculate_probability(
            self.replica_states,
            energies,
            replica_i,
            replica_j,
        )

    def _perform_exchange(self, replica_i: int, replica_j: int) -> None:
        if replica_i >= len(self.replica_states):
            raise RuntimeError(
                (
                    "replica_states array too small: "
                    f"{len(self.replica_states)}, need {replica_i + 1}"
                )
            )
        if replica_j >= len(self.replica_states):
            raise RuntimeError(
                (
                    "replica_states array too small: "
                    f"{len(self.replica_states)}, need {replica_j + 1}"
                )
            )

        old_state_i = self.replica_states[replica_i]
        old_state_j = self.replica_states[replica_j]
        if old_state_i >= len(self.state_replicas) or old_state_j >= len(
            self.state_replicas
        ):
            raise RuntimeError(
                (
                    "Invalid state indices: "
                    f"{old_state_i}, {old_state_j} vs array size "
                    f"{len(self.state_replicas)}"
                )
            )

        self.replica_states[replica_i] = old_state_j
        self.replica_states[replica_j] = old_state_i

        # Cache a deterministic name for the new permutation of replicas.
        shape_name = base_shape_str((len(self.replica_states),))
        perm_name = permutation_name(tuple(self.replica_states))
        logger.debug(
            "Replica state permutation %s applied (shape %s)", perm_name, shape_name
        )

        self.state_replicas[old_state_i] = replica_j
        self.state_replicas[old_state_j] = replica_i

        self.integrators[replica_i].setTemperature(
            self.temperatures[old_state_j] * unit.kelvin
        )
        self.integrators[replica_j].setTemperature(
            self.temperatures[old_state_i] * unit.kelvin
        )

        # Rescale velocities deterministically instead of redrawing
        Ti = self.temperatures[old_state_i]
        Tj = self.temperatures[old_state_j]
        scale_ij = float(
            np.sqrt(
                max(
                    const.NUMERIC_MIN_POSITIVE,
                    Tj / max(const.NUMERIC_MIN_POSITIVE, Ti),
                )
            )
        )
        vi = self.contexts[replica_i].getState(getVelocities=True).getVelocities()
        vj = self.contexts[replica_j].getState(getVelocities=True).getVelocities()
        self.contexts[replica_i].setVelocities(vi * scale_ij)
        self.contexts[replica_j].setVelocities(vj / scale_ij)

    def run_simulation(
        self,
        total_steps: int = 1000,  # Very fast for testing
        equilibration_steps: int = 100,  # Minimal equilibration
        save_state_frequency: int = 1000,
        checkpoint_manager=None,
        *,
        progress_callback: ProgressCB | None = None,
        cancel_token: Callable[[], bool] | None = None,
    ) -> List[str]:
        """
        Run the replica exchange simulation.

        Args:
            total_steps: Total number of MD steps to run
            equilibration_steps: Number of equilibration steps before data collection
            save_state_frequency: Frequency to save simulation states
            checkpoint_manager: CheckpointManager instance for state tracking
        """
        self._validate_setup_state()
        reporter = ProgressReporter(progress_callback)
        reporter.emit("setup", {"message": "initializing"})
        self._log_run_start(total_steps)
        simulation_start = time.perf_counter()
        # Decide reporter stride BEFORE production; do not mutate during run
        if self.reporter_stride is None:
            stride = self.plan_reporter_stride(
                total_steps, equilibration_steps, target_frames=5000
            )
            logger.info(f"DCD stride planned as {stride} for ~5000 frames/replica")

        def _should_cancel() -> bool:
            try:
                return bool(cancel_token()) if cancel_token is not None else False
            except Exception:
                return False

        cancelled = False
        equilibration_elapsed = 0.0
        if equilibration_steps > 0:
            # Console output
            print("\n" + "=" * 80, flush=True)
            print(
                f"SIMULATION STAGE 1: EQUILIBRATION ({equilibration_steps} steps)",
                flush=True,
            )
            print("=" * 80, flush=True)
            print(f"Running {self.n_replicas} replicas in parallel", flush=True)
            print(
                f"Temperature range: {min(self.temperatures):.1f}K - {max(self.temperatures):.1f}K",
                flush=True,
            )
            print("=" * 80 + "\n", flush=True)

            # Also log
            logger.info("=" * 80)
            logger.info(
                f"SIMULATION STAGE 1: EQUILIBRATION ({equilibration_steps} steps)"
            )
            logger.info("=" * 80)
            logger.info(f"Running {self.n_replicas} replicas in parallel")
            logger.info(
                f"Temperature range: {min(self.temperatures):.1f}K - {max(self.temperatures):.1f}K"
            )
            logger.info("=" * 80)

            equilibration_start = time.perf_counter()
            cancelled = self._run_equilibration_phase(
                equilibration_steps, checkpoint_manager, reporter, _should_cancel
            )
            equilibration_elapsed = time.perf_counter() - equilibration_start
            if cancelled:
                # Console output
                print("\n" + "=" * 80, flush=True)
                print("SIMULATION CANCELLED DURING EQUILIBRATION", flush=True)
                print("=" * 80 + "\n", flush=True)

                # Also log
                logger.warning("=" * 80)
                logger.warning("SIMULATION CANCELLED DURING EQUILIBRATION")
                logger.warning("=" * 80)
                reporter.emit("finished", {"status": "cancelled"})
                return []

            # Console output
            print("\n" + "=" * 80, flush=True)
            print("EQUILIBRATION COMPLETE", flush=True)
            print("=" * 80 + "\n", flush=True)
            if equilibration_elapsed > 0.0:
                equil_summary = (
                    f"Equilibration duration: {format_duration(equilibration_elapsed)}"
                )
                print(equil_summary, flush=True)
                logger.info(equil_summary)

            # Also log
            logger.info("=" * 80)
            logger.info("EQUILIBRATION COMPLETE")
            logger.info("=" * 80)
        if self._skip_production_if_completed(checkpoint_manager):
            return [str(f) for f in self.trajectory_files]
        self._mark_production_started(checkpoint_manager)

        production_steps = total_steps - equilibration_steps

        # Console output
        print("\n" + "=" * 80, flush=True)
        print(f"SIMULATION STAGE 2: PRODUCTION ({production_steps} steps)", flush=True)
        print("=" * 80, flush=True)
        print(f"Running {self.n_replicas} replicas in parallel", flush=True)
        print(f"Exchange attempts every {self.exchange_frequency} steps", flush=True)
        print("=" * 80 + "\n", flush=True)

        # Also log
        logger.info("=" * 80)
        logger.info(f"SIMULATION STAGE 2: PRODUCTION ({production_steps} steps)")
        logger.info("=" * 80)
        logger.info(f"Running {self.n_replicas} replicas in parallel")
        logger.info(f"Exchange attempts every {self.exchange_frequency} steps")
        logger.info("=" * 80)

        production_start = time.perf_counter()
        cancelled = self._run_production_phase(
            total_steps,
            equilibration_steps,
            save_state_frequency,
            checkpoint_manager,
            reporter,
            _should_cancel,
        )
        production_elapsed = time.perf_counter() - production_start
        if cancelled:
            # Console output
            print("\n" + "=" * 80, flush=True)
            print("SIMULATION CANCELLED DURING PRODUCTION", flush=True)
            print("=" * 80, flush=True)
            print("Partial trajectories have been saved", flush=True)
            print("=" * 80 + "\n", flush=True)

            # Also log
            logger.warning("=" * 80)
            logger.warning("SIMULATION CANCELLED DURING PRODUCTION")
            logger.warning("=" * 80)
            logger.warning("Partial trajectories have been saved")
            logger.warning("=" * 80)
            reporter.emit("finished", {"status": "cancelled"})
            return []

        # Console output
        print("\n" + "=" * 80, flush=True)
        print("PRODUCTION COMPLETE", flush=True)
        print("=" * 80, flush=True)
        print("Finalizing trajectories and saving statistics...", flush=True)
        print("=" * 80 + "\n", flush=True)
        if production_elapsed > 0.0:
            prod_summary = f"Production duration: {format_duration(production_elapsed)}"
            print(prod_summary, flush=True)
            logger.info(prod_summary)

        # Also log
        logger.info("=" * 80)
        logger.info("PRODUCTION COMPLETE")
        logger.info("=" * 80)
        logger.info("Finalizing trajectories and saving statistics...")
        logger.info("=" * 80)

        self._mark_production_completed(
            total_steps, equilibration_steps, checkpoint_manager
        )
        self._close_dcd_files()
        self._log_final_stats()
        # Announce outputs before saving results (predictable filenames)
        artifacts = [str(p) for p in self.trajectory_files]
        artifacts += [
            str(self.output_dir / "analysis_results.pkl"),
            str(self.output_dir / "analysis_results.json"),
        ]
        reporter.emit("write_output", {"artifacts": artifacts})
        self.save_results()
        reporter.emit("finished", {"status": "ok"})

        simulation_total_elapsed = time.perf_counter() - simulation_start
        if simulation_total_elapsed > 0.0:
            total_msg = (
                f"Simulation runtime: {format_duration(simulation_total_elapsed)}"
            )
            print(total_msg, flush=True)
            logger.info(total_msg)

        return [str(f) for f in self.trajectory_files]

    # --- Helpers for run_simulation ---

    def _validate_setup_state(self) -> None:
        if not self._is_setup:
            raise RuntimeError(
                "Replicas not properly initialized! Call setup_replicas() first."
            )
        if not self.contexts or len(self.contexts) != self.n_replicas:
            raise RuntimeError(
                (
                    "Replicas not properly initialized! Expected "
                    f"{self.n_replicas} contexts, but got {len(self.contexts)}. "
                    "setup_replicas() may have failed."
                )
            )
        if not self.replicas or len(self.replicas) != self.n_replicas:
            raise RuntimeError(
                (
                    "Replicas not properly initialized! Expected "
                    f"{self.n_replicas} replicas, but got {len(self.replicas)}. "
                    "setup_replicas() may have failed."
                )
            )

    def _log_run_start(self, total_steps: int) -> None:
        logger.info(f"Starting REMD simulation: {total_steps} steps")
        logger.info(f"Exchange attempts every {self.exchange_frequency} steps")

    def _run_equilibration_phase(
        self,
        equilibration_steps: int,
        checkpoint_manager,
        reporter: ProgressReporter | None,
        should_cancel: Callable[[], bool] | None,
    ) -> bool:
        if checkpoint_manager and checkpoint_manager.is_step_completed(
            "gradual_heating"
        ):
            logger.info("Gradual heating already completed OK")
        else:
            cancelled = self._run_gradual_heating(
                equilibration_steps, checkpoint_manager, reporter, should_cancel
            )
            if cancelled:
                return True

        if checkpoint_manager and checkpoint_manager.is_step_completed("equilibration"):
            logger.info("Temperature equilibration already completed OK")
        else:
            cancelled = self._run_temperature_equilibration(
                equilibration_steps, checkpoint_manager, reporter, should_cancel
            )
            if cancelled:
                return True
        return False

    def _run_gradual_heating(
        self,
        equilibration_steps: int,
        checkpoint_manager,
        reporter: ProgressReporter | None,
        should_cancel: Callable[[], bool] | None,
    ) -> bool:
        if checkpoint_manager:
            checkpoint_manager.mark_step_started("gradual_heating")
        heating_steps = max(100, equilibration_steps * 40 // 100)
        temp_min = min(self.temperatures) if self.temperatures else 0.0
        temp_max = max(self.temperatures) if self.temperatures else 0.0
        phase_start = time.perf_counter()
        announce_stage_start(
            "REMD Sub-stage: Gradual Heating",
            logger=logger,
            details=[
                f"Gradual heating span: {heating_steps} steps",
                f"Replica count: {self.n_replicas}",
                f"Temperature ladder: {temp_min:.1f}K -> {temp_max:.1f}K",
            ],
        )
        heat_progress = ProgressPrinter(heating_steps)
        heating_chunk_size = max(10, heating_steps // 20)
        milestones_logged: set[int] = set()
        for heat_step in range(0, heating_steps, heating_chunk_size):
            if should_cancel is not None and should_cancel():
                announce_stage_cancelled(
                    "REMD Sub-stage: Gradual Heating",
                    logger=logger,
                    details=["Cancellation requested during heating ramp."],
                )
                return True
            current_steps = min(heating_chunk_size, heating_steps - heat_step)
            progress_fraction = (heat_step + current_steps) / heating_steps
            progress_fraction = min(max(progress_fraction, 0.0), 1.0)
            for replica_idx, replica in enumerate(self.replicas):
                target_temp = self.temperatures[self.replica_states[replica_idx]]
                current_temp = 50.0 + (target_temp - 50.0) * progress_fraction
                replica.integrator.setTemperature(current_temp * unit.kelvin)
                self._step_with_recovery(
                    replica, current_steps, replica_idx, current_temp
                )
            progress = min(40, (heat_step + current_steps) * 40 // heating_steps)
            heat_progress.draw(heat_step + current_steps)
            heat_progress.newline_if_active()
            progress_percent = int(round(progress_fraction * 100))
            for threshold in (25, 50, 75, 100):
                if progress_percent >= threshold and threshold not in milestones_logged:
                    milestone_message = (
                        f"Gradual heating progress {threshold}% "
                        f"({heat_step + current_steps}/{heating_steps} steps)"
                    )
                    print(milestone_message, flush=True)
                    logger.info(milestone_message)
                    milestones_logged.add(threshold)
            # Report unified equilibrate progress as fraction of total equilibration
            if reporter is not None:
                cur = min(equilibration_steps, heat_step + current_steps)
                reporter.emit(
                    "equilibrate",
                    {"current_step": cur, "total_steps": int(equilibration_steps)},
                )
            temps_preview = [
                50.0
                + (self.temperatures[self.replica_states[i]] - 50.0) * progress_fraction
                for i in range(len(self.replicas))
            ]
            logger.info(
                f"   Heating Progress: {progress}% - Current temps: {temps_preview}"
            )
        heat_progress.close()
        elapsed = time.perf_counter() - phase_start
        if 100 not in milestones_logged:
            milestone_message = (
                f"Gradual heating progress 100% ({heating_steps}/{heating_steps} steps)"
            )
            print(milestone_message, flush=True)
            logger.info(milestone_message)
        if should_cancel is not None and should_cancel():
            announce_stage_cancelled(
                "REMD Sub-stage: Gradual Heating",
                logger=logger,
                details=["Cancellation requested during heating wrap-up."],
            )
            return True
        if checkpoint_manager:
            checkpoint_manager.mark_step_completed(
                "gradual_heating",
                {
                    "heating_steps": heating_steps,
                    "final_temperatures": [
                        self.temperatures[state] for state in self.replica_states
                    ],
                },
            )
        announce_stage_complete(
            "REMD Sub-stage: Gradual Heating",
            logger=logger,
            details=[
                f"Executed {heating_steps} heating steps.",
                f"Duration: {format_duration(elapsed)}",
            ],
        )
        # Completed without cancellation
        return False

    def _step_with_recovery(
        self, replica: Simulation, steps: int, replica_idx: int, temp_k: float
    ) -> None:
        replica.step(steps)

    def _run_temperature_equilibration(
        self,
        equilibration_steps: int,
        checkpoint_manager,
        reporter: ProgressReporter | None,
        should_cancel: Callable[[], bool] | None,
    ) -> bool:
        if checkpoint_manager:
            checkpoint_manager.mark_step_started("equilibration")
        temp_equil_steps = max(100, equilibration_steps * 60 // 100)
        phase_start = time.perf_counter()
        announce_stage_start(
            "REMD Sub-stage: Temperature Equilibration",
            logger=logger,
            details=[
                f"Equilibration span: {temp_equil_steps} steps",
                f"Replica count: {self.n_replicas}",
                "Integrators set to target temperatures for all replicas.",
            ],
        )
        for replica_idx, replica in enumerate(self.replicas):
            target_temp = self.temperatures[self.replica_states[replica_idx]]
            replica.integrator.setTemperature(target_temp * unit.kelvin)
            # Avoid stochastic velocity reseeding here to preserve determinism across
            # repeated runs with the same random_seed. Velocities will continue to
            # evolve deterministically from prior steps under a seeded integrator.
            # replica.context.setVelocitiesToTemperature(target_temp * unit.kelvin)
        equil_chunk_size = max(1, temp_equil_steps // 10)
        temp_progress = ProgressPrinter(temp_equil_steps)
        milestones_logged: set[int] = set()
        for i in range(0, temp_equil_steps, equil_chunk_size):
            if should_cancel is not None and should_cancel():
                return True
            current_steps = min(equil_chunk_size, temp_equil_steps - i)
            for replica_idx, replica in enumerate(self.replicas):
                try:
                    replica.step(current_steps)
                except Exception as exc:
                    if "nan" in str(exc).lower():
                        logger.error(
                            (
                                f"   NaN detected in replica {replica_idx} during "
                                "equilibration - simulation unstable"
                            )
                        )
                        if checkpoint_manager:
                            checkpoint_manager.mark_step_failed(
                                "equilibration", str(exc)
                            )
                        announce_stage_failed(
                            "REMD Sub-stage: Temperature Equilibration",
                            logger=logger,
                            details=[
                                f"Replica {replica_idx} encountered non-finite state.",
                                "Halting equilibration phase.",
                            ],
                        )
                        raise RuntimeError(
                            (
                                "Simulation became unstable for replica "
                                f"{replica_idx}. Try: 1) Better initial structure, "
                                "2) Smaller timestep, 3) More minimization"
                            )
                        )
                    else:
                        raise
            progress = min(100, 40 + (i + current_steps) * 60 // temp_equil_steps)
            temp_progress.draw(i + current_steps)
            temp_progress.newline_if_active()
            progress_fraction = min(
                max((i + current_steps) / max(1, temp_equil_steps), 0.0), 1.0
            )
            progress_percent = int(round(progress_fraction * 100))
            for threshold in (25, 50, 75, 100):
                if progress_percent >= threshold and threshold not in milestones_logged:
                    milestone_message = (
                        f"Temperature equilibration progress {threshold}% "
                        f"({i + current_steps}/{temp_equil_steps} steps)"
                    )
                    print(milestone_message, flush=True)
                    logger.info(milestone_message)
                    milestones_logged.add(threshold)
            if reporter is not None:
                heating_steps = max(100, equilibration_steps * 40 // 100)
                cur = min(equilibration_steps, heating_steps + i + current_steps)
                reporter.emit(
                    "equilibrate",
                    {"current_step": cur, "total_steps": int(equilibration_steps)},
                )
            logger.info(
                (
                    f"   Equilibration Progress: {progress}% "
                    f"({equilibration_steps - temp_equil_steps + i + current_steps}/"
                    f"{equilibration_steps} steps)"
                )
            )
        temp_progress.close()
        elapsed = time.perf_counter() - phase_start
        if 100 not in milestones_logged:
            milestone_message = (
                f"Temperature equilibration progress 100% "
                f"({temp_equil_steps}/{temp_equil_steps} steps)"
            )
            print(milestone_message, flush=True)
            logger.info(milestone_message)
        if should_cancel is not None and should_cancel():
            announce_stage_cancelled(
                "REMD Sub-stage: Temperature Equilibration",
                logger=logger,
                details=["Cancellation requested during temperature equilibration."],
            )
            return True
        if checkpoint_manager:
            checkpoint_manager.mark_step_completed(
                "equilibration",
                {
                    "equilibration_steps": temp_equil_steps,
                    "total_equilibration": equilibration_steps,
                },
            )
        announce_stage_complete(
            "REMD Sub-stage: Temperature Equilibration",
            logger=logger,
            details=[
                f"Executed {temp_equil_steps} temperature-hold steps.",
                f"Duration: {format_duration(elapsed)}",
            ],
        )
        return False

    def _skip_production_if_completed(self, checkpoint_manager) -> bool:
        if checkpoint_manager and checkpoint_manager.is_step_completed(
            "production_simulation"
        ):
            logger.info("Production simulation already completed OK")
            return True
        return False

    def _mark_production_started(self, checkpoint_manager) -> None:
        if checkpoint_manager:
            checkpoint_manager.mark_step_started("production_simulation")

    def _run_production_phase(
        self,
        total_steps: int,
        equilibration_steps: int,
        save_state_frequency: int,
        checkpoint_manager,
        reporter: ProgressReporter | None,
        should_cancel: Callable[[], bool] | None,
    ) -> bool:
        production_steps = total_steps - equilibration_steps
        exchange_steps = production_steps // self.exchange_frequency
        logger.info(
            (
                f"Production: {production_steps} steps with "
                f"{exchange_steps} exchange attempts"
            )
        )
        # Initialize diagnostics once production starts
        if self.acceptance_matrix is None:
            self.acceptance_matrix = np.zeros((self.n_replicas - 1, 2), dtype=int)
        if self.replica_visit_counts is None:
            self.replica_visit_counts = np.zeros(
                (self.n_replicas, self.n_replicas), dtype=int
            )

        prod_progress = (
            ProgressPrinter(max(1, exchange_steps)) if exchange_steps > 0 else None
        )
        last_t = time.time()
        prod_milestones: set[int] = set()
        for step in range(exchange_steps):
            if should_cancel is not None and should_cancel():
                return True
            self._production_step_all_replicas(step, checkpoint_manager)
            energies = self._precompute_energies()
            self._attempt_all_exchanges(energies)
            self.exchange_history.append(self.replica_states.copy())
            # Update visitation histogram
            for r, s in enumerate(self.replica_states):
                if self.replica_visit_counts is not None:
                    self.replica_visit_counts[r, s] += 1
            self._log_production_progress(
                step,
                exchange_steps,
                total_steps,
                equilibration_steps,
                prod_milestones,
            )
            # Unified reporter events
            if reporter is not None:
                # exchange stats after each sweep
                acc_rate = self.exchanges_accepted / max(1, self.exchange_attempts)
                swept = time.time() - last_t
                try:
                    pair_acc = None
                    if self.acceptance_matrix is not None:
                        # rows indexed by pair, col0 attempts, col1 accepts
                        with np.errstate(divide="ignore", invalid="ignore"):
                            rat = self.acceptance_matrix[:, 1] / np.maximum(
                                1, self.acceptance_matrix[:, 0]
                            )
                            pair_acc = [float(x) for x in np.nan_to_num(rat)]
                except Exception:
                    pair_acc = None
                reporter.emit(
                    "exchange",
                    {
                        "sweep_index": int(step + 1),
                        "n_replicas": int(self.n_replicas),
                        "acceptance_mean": float(acc_rate),
                        "step_time_s": round(swept, 3),
                        **(
                            {"acceptance_per_pair": pair_acc}
                            if pair_acc is not None
                            else {}
                        ),
                        "temperatures": [float(t) for t in self.temperatures],
                    },
                )
                # production progress as MD steps
                production_steps = max(0, total_steps - equilibration_steps)
                cur_steps = min((step + 1) * self.exchange_frequency, production_steps)
                reporter.emit(
                    "simulate",
                    {
                        "current_step": int(cur_steps),
                        "total_steps": int(production_steps),
                    },
                )
                last_t = time.time()
            if prod_progress is not None:
                acc_rate = self.exchanges_accepted / max(1, self.exchange_attempts)
                prod_progress.draw(step + 1, suffix=f"acc {acc_rate*100:.1f}%")
                prod_progress.newline_if_active()
            if (step + 1) * self.exchange_frequency % save_state_frequency == 0:
                self.save_checkpoint(step + 1)
        if prod_progress is not None:
            prod_progress.close()
        return False

    def _production_step_all_replicas(self, step: int, checkpoint_manager) -> None:
        for replica_idx, replica in enumerate(self.replicas):
            try:
                replica.step(self.exchange_frequency)
            except Exception as exc:
                if "nan" in str(exc).lower():
                    logger.error(
                        "NaN detected in replica %d during production phase",
                        replica_idx,
                    )
                    try:
                        _ = replica.context.getState(
                            getPositions=True, getVelocities=True
                        )
                        logger.info(
                            "Attempting to save current state before failure..."
                        )
                    except Exception:
                        pass
                    raise RuntimeError(
                        (
                            "Simulation became unstable for replica "
                            f"{replica_idx} at production step {step}. "
                            "Consider: 1) Longer equilibration, 2) Smaller timestep, "
                            "3) Different initial structure"
                        )
                    )
                else:
                    raise
        self._update_bias_monitor()

    def _update_bias_monitor(self) -> None:
        if (
            self._cv_monitor_module is None
            or self._bias_energy_stats is None
            or self._bias_cv_stats is None
        ):
            return
        import torch

        for replica in self.replicas:
            state = replica.context.getState(
                getPositions=True, getEnergy=True, groups={1}
            )
            energy = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
            self._bias_energy_stats.update(np.array([energy]))
            positions = np.array(
                state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
            )
            pos_tensor = torch.tensor(positions, dtype=torch.float32)
            try:
                box_vectors = state.getPeriodicBoxVectors(asNumpy=True)
                box = torch.tensor(box_vectors, dtype=torch.float32)
            except Exception:
                box = torch.eye(3, dtype=torch.float32)
            with torch.inference_mode():
                cvs = self._cv_monitor_module.compute_cvs(pos_tensor, box)
            cv_values = cvs.detach().cpu().numpy()
            if cv_values.ndim > 1:
                cv_vector = cv_values.mean(axis=0)
            else:
                cv_vector = cv_values
            self._bias_cv_stats.update(cv_vector)
        self._bias_steps_completed += self.exchange_frequency
        if self._bias_steps_completed >= self._bias_next_log:
            mean_e, std_e = self._bias_energy_stats.summary()
            mean_cv, std_cv = self._bias_cv_stats.summary()
            logger.info(
                "Bias stats after %d steps: energy mean=%.6f std=%.6f; CV mean=%s std=%s",
                self._bias_steps_completed,
                float(mean_e[0]),
                float(std_e[0]),
                np.array2string(mean_cv, precision=4),
                np.array2string(std_cv, precision=4),
            )
            self._bias_next_log += self._bias_log_interval

    def _precompute_energies(self) -> List[Any]:
        energies: List[Any] = []
        for idx, ctx in enumerate(self.contexts):
            e_state = ctx.getState(getEnergy=True)
            energies.append(e_state.getPotentialEnergy())
        self.energies = energies
        return energies

    def _attempt_all_exchanges(self, energies: List[Any]) -> None:
        for i in range(0, self.n_replicas - 1, 2):
            try:
                accepted = self.attempt_exchange(i, i + 1, energies=energies)
                # Update acceptance matrix (even pairs in column 0)
                if self.acceptance_matrix is not None:
                    row = i
                    self.acceptance_matrix[row, 0] += 1  # attempts
                    if accepted:
                        self.acceptance_matrix[row, 1] += 1  # accepts
            except Exception as exc:
                logger.warning(
                    (
                        f"Exchange attempt failed between replicas {i} and {i+1}: "
                        f"{exc}"
                    )
                )
        for i in range(1, self.n_replicas - 1, 2):
            try:
                accepted = self.attempt_exchange(i, i + 1, energies=energies)
                # Update acceptance matrix (odd pairs in next rows)
                if self.acceptance_matrix is not None:
                    row = i
                    self.acceptance_matrix[row, 0] += 1
                    if accepted:
                        self.acceptance_matrix[row, 1] += 1
            except Exception as exc:
                logger.warning(
                    (
                        f"Exchange attempt failed between replicas {i} and {i+1}: "
                        f"{exc}"
                    )
                )

    def _log_production_progress(
        self,
        step: int,
        exchange_steps: int,
        total_steps: int,
        equilibration_steps: int,
        milestones_logged: set[int],
    ) -> None:
        if exchange_steps <= 0:
            progress_percent = 100
        else:
            progress_percent = min(100, (step + 1) * 100 // exchange_steps)
        acceptance_rate = self.exchanges_accepted / max(1, self.exchange_attempts)
        completed_steps = (step + 1) * self.exchange_frequency + equilibration_steps
        logger.debug(
            (
                f"   Production Progress: {progress_percent}% "
                f"({step + 1}/{exchange_steps} exchanges, "
                f"{completed_steps}/{total_steps} total steps) "
                f"| Acceptance: {acceptance_rate:.3f}"
            )
        )
        for threshold in (25, 50, 75, 100):
            if progress_percent >= threshold and threshold not in milestones_logged:
                milestone_message = (
                    f"Production progress {threshold}% "
                    f"({completed_steps}/{total_steps} steps, "
                    f"acceptance {acceptance_rate*100:.1f}%)"
                )
                print(milestone_message, flush=True)
                logger.info(milestone_message)
                milestones_logged.add(threshold)

    def _mark_production_completed(
        self, total_steps: int, equilibration_steps: int, checkpoint_manager
    ) -> None:
        production_steps = total_steps - equilibration_steps
        exchange_steps = production_steps // self.exchange_frequency
        if checkpoint_manager:
            checkpoint_manager.mark_step_completed(
                "production_simulation",
                {
                    "production_steps": production_steps,
                    "exchange_steps": exchange_steps,
                    "final_acceptance_rate": self.exchanges_accepted
                    / max(1, self.exchange_attempts),
                },
            )

    def _log_final_stats(self) -> None:
        final_acceptance = self.exchanges_accepted / max(1, self.exchange_attempts)
        logger.info("=" * 60)
        logger.info("REPLICA EXCHANGE SIMULATION COMPLETED")
        logger.info(f"Final exchange acceptance rate: {final_acceptance:.3f}")
        logger.info(f"Total exchanges attempted: {self.exchange_attempts}")
        logger.info(f"Total exchanges accepted: {self.exchanges_accepted}")
        logger.info("=" * 60)
        console_acceptance = (
            f"Final exchange acceptance: {final_acceptance:.3f} "
            f"({final_acceptance * 100:.1f}%)"
        )
        print(console_acceptance, flush=True)

        # Warn on poor acceptance
        if final_acceptance < 0.15 or final_acceptance > 0.6:
            logger.warning(
                (
                    "Exchange acceptance %.2f out of recommended [0.15, 0.60]. "
                    "Consider increasing number of replicas or widening temperature range."
                ),
                final_acceptance,
            )
            print(
                (
                    "WARNING: Exchange acceptance outside recommended range "
                    f"(observed {final_acceptance:.2f})."
                ),
                flush=True,
            )

        # Diffusion diagnostics
        try:
            diff = compute_diffusion_metrics(
                self.exchange_history, self.exchange_frequency
            )
            if diff.get("mean_abs_disp_per_10k_steps", 0.0) < 0.5:
                logger.warning(
                    (
                        "Replica index diffusion is low (%.2f per 10k steps). "
                        "Consider wider T-range or more replicas."
                    ),
                    diff.get("mean_abs_disp_per_10k_steps", 0.0),
                )
                print(
                    (
                        "WARNING: Replica diffusion low "
                        f"({diff.get('mean_abs_disp_per_10k_steps', 0.0):.2f} per 10k steps)."
                    ),
                    flush=True,
                )
        except Exception:
            pass

    def _close_dcd_files(self):
        """Close and flush all DCD files to ensure data is written."""
        logger.info("Closing DCD files...")

        for i, replica in enumerate(self.replicas):
            # Close DCD reporters safely
            dcd_reporters = [
                r for r in replica.reporters if isinstance(r, ClosableDCDReporter)
            ]
            for reporter in dcd_reporters:
                try:
                    reporter.close()
                    logger.debug(f"Closed DCD file for replica {i}")
                except Exception as e:
                    logger.warning(f"Error closing DCD file for replica {i}: {e}")

            # Remove DCD reporters from the simulation
            replica.reporters = [
                r for r in replica.reporters if not isinstance(r, ClosableDCDReporter)
            ]

        # Force garbage collection to ensure file handles are released
        import gc

        gc.collect()

        logger.info("DCD files closed and flushed")

    def save_checkpoint(self, step: int):
        """Save simulation checkpoint."""
        checkpoint_file = self.output_dir / f"checkpoint_step_{step:06d}.pkl"
        checkpoint_data = self.save_checkpoint_state()
        checkpoint_data["step"] = step
        with open(checkpoint_file, "wb") as f:
            pickle.dump(checkpoint_data, f)

    def save_results(self) -> None:
        """Save final simulation results."""
        results_file = self.output_dir / "analysis_results.pkl"
        json_file = self.output_dir / "analysis_results.json"
        result = REMDResult(
            temperatures=np.asarray(self.temperatures),
            n_replicas=self.n_replicas,
            exchange_frequency=self.exchange_frequency,
            exchange_attempts=self.exchange_attempts,
            exchanges_accepted=self.exchanges_accepted,
            final_acceptance_rate=self.exchanges_accepted
            / max(1, self.exchange_attempts),
            replica_states=self.replica_states,
            state_replicas=self.state_replicas,
            exchange_history=self.exchange_history,
            trajectory_files=[str(f) for f in self.trajectory_files],
            acceptance_matrix=self.acceptance_matrix,
            replica_visitation_histogram=self.replica_visit_counts,
            frames_per_replica=self._compute_frames_per_replica(),
            effective_sample_size=None,
        )
        with open(results_file, "wb") as pkl_f:
            pickle.dump({"remd": result}, pkl_f)
        with open(json_file, "w") as json_f:
            json.dump({"remd": result.to_dict(metadata_only=True)}, json_f)
        logger.info(f"Results saved to {results_file}")
        # Write exchange diagnostics JSON for app visibility
        try:
            diag = {
                "acceptance_mean": float(
                    self.exchanges_accepted / max(1, self.exchange_attempts)
                ),
                "exchange_frequency": int(self.exchange_frequency),
                "temperatures": [float(t) for t in self.temperatures],
            }
            diag.update(
                compute_diffusion_metrics(
                    self.exchange_history, self.exchange_frequency
                )
            )
            extra = compute_exchange_statistics(
                self.exchange_history,
                self.n_replicas,
                self.pair_attempt_counts,
                self.pair_accept_counts,
            )
            # Extract per-pair acceptance as a compact list ordered by neighbor index
            pair_rates = []
            for i in range(max(0, self.n_replicas - 1)):
                pair = (i, i + 1)
                att = self.pair_attempt_counts.get(pair, 0)
                acc = self.pair_accept_counts.get(pair, 0)
                pair_rates.append(float(acc / max(1, att)))
            diag["acceptance_per_pair"] = pair_rates
            diag["average_round_trip_time"] = extra.get("average_round_trip_time", 0.0)
            dfile = self.output_dir / "exchange_diagnostics.json"
            with open(dfile, "w", encoding="utf-8") as fh:
                json.dump(diag, fh, sort_keys=True, separators=(",", ":"))
            logger.info("Exchange diagnostics saved to %s", str(dfile))
            # Also save under a canonical name for future tooling
            with open(
                self.output_dir / "remd_diagnostics.json", "w", encoding="utf-8"
            ) as fh2:
                json.dump(diag, fh2, sort_keys=True, separators=(",", ":"))
        except Exception as exc:
            logger.debug("Failed to save exchange diagnostics: %s", exc)

        # Write provenance.json and temps.txt
        try:
            prov = {
                "temperature_schedule": {
                    "mode": self.temperature_schedule_mode or "auto-linear",
                    "temperatures": [float(t) for t in self.temperatures],
                },
                "exchange_frequency_steps": int(self.exchange_frequency),
                "random_seed": int(self.random_seed),
            }
            prov_file = self.output_dir / "provenance.json"
            with open(prov_file, "w", encoding="utf-8") as fh:
                json.dump(prov, fh, sort_keys=True, separators=(",", ":"))
            # temps.txt, one per line
            with open(self.output_dir / "temps.txt", "w", encoding="utf-8") as tf:
                for t in self.temperatures:
                    tf.write(f"{float(t):.6f}\n")
        except Exception as exc:
            logger.debug("Failed to write provenance/temps: %s", exc)

    def tune_temperature_ladder(
        self, target_acceptance: Optional[float] = None
    ) -> List[float]:
        """Adjust the temperature ladder for a desired acceptance rate.

        Uses :func:`retune_temperature_ladder` to estimate new temperature
        spacings based on the accumulated pairwise acceptance statistics. The
        suggested temperatures replace ``self.temperatures``; callers should
        re-run :meth:`setup_replicas` before continuing the simulation.

        Parameters
        ----------
        target_acceptance:
            Desired neighbour acceptance probability. If ``None``,
            :attr:`target_accept` is used.

        Returns
        -------
        List[float]
            The updated temperature ladder.
        """

        target = (
            float(target_acceptance)
            if target_acceptance is not None
            else float(self.target_accept)
        )
        logger.info("Retuning temperature ladder toward target acceptance %.2f", target)
        stats = retune_temperature_ladder(
            self.temperatures,
            self.pair_attempt_counts,
            self.pair_accept_counts,
            target_acceptance=target,
            output_json=str(self.output_dir / "temperatures_suggested.json"),
            dry_run=True,
        )
        self.temperatures = stats["suggested_temperatures"]
        self.n_replicas = len(self.temperatures)
        self._sync_exchange_engine()
        return self.temperatures

    def _compute_frames_per_replica(self) -> List[int]:
        frames: List[int] = []
        # Use streaming probe to avoid loading files and to keep plugins quiet
        try:
            from pmarlo.io.trajectory_reader import MDTrajReader as _MDTReader

            reader = _MDTReader(topology_path=str(self.pdb_file))
        except Exception:
            reader = None  # type: ignore[assignment]

        for traj_file in self.trajectory_files:
            try:
                if not traj_file.exists():
                    frames.append(0)
                    continue
                if reader is not None:
                    frames.append(int(reader.probe_length(str(traj_file))))
                else:
                    # Fallback: import mdtraj only if necessary
                    import mdtraj as md  # type: ignore

                    t = md.load(str(traj_file), top=str(self.pdb_file))
                    frames.append(int(t.n_frames))
            except Exception:
                frames.append(0)
        return frames

    def demux_trajectories(
        self,
        *,
        target_temperature: float = 300.0,
        equilibration_steps: int = 100,
        progress_callback: ProgressCB | None = None,
    ) -> Optional[str]:
        """Delegate to the dedicated demux module for better visibility."""
        return _demux_trajectories(
            self,
            target_temperature=target_temperature,
            equilibration_steps=equilibration_steps,
            progress_callback=progress_callback,
        )

    def get_exchange_statistics(self) -> Dict[str, Any]:
        """Get exchange statistics and diagnostics."""
        if not self.exchange_history:
            return {}

        # Calculate mixing statistics
        replica_visits = np.zeros((self.n_replicas, self.n_replicas))
        for states in self.exchange_history:
            for replica, state in enumerate(states):
                replica_visits[replica, state] += 1

        # Normalize to get probabilities (not currently used downstream)
        _ = replica_visits / max(1, len(self.exchange_history))

        extra = compute_exchange_statistics(
            self.exchange_history,
            self.n_replicas,
            self.pair_attempt_counts,
            self.pair_accept_counts,
        )

        return {
            "total_exchange_attempts": self.exchange_attempts,
            "total_exchanges_accepted": self.exchanges_accepted,
            "overall_acceptance_rate": self.exchanges_accepted
            / max(1, self.exchange_attempts),
            **extra,
        }


def setup_bias_variables(pdb_file: str) -> List:
    """
    Set up bias variables for metadynamics.

    Args:
        pdb_file: Path to the PDB file

    Returns:
        List of bias variables
    """
    import mdtraj as md
    from openmm import CustomTorsionForce
    from openmm.app.metadynamics import BiasVariable

    # Load trajectory to get dihedral indices
    traj0 = md.load_pdb(pdb_file)
    phi_indices, _ = md.compute_phi(traj0)

    if len(phi_indices) == 0:
        logger.warning("No phi dihedrals found - proceeding without bias variables")
        return []

    bias_variables = []

    # Add phi dihedral as bias variable
    for i, phi_atoms in enumerate(phi_indices[:2]):  # Use first 2 phi dihedrals
        phi_atoms = [int(atom) for atom in phi_atoms]

        phi_force = CustomTorsionForce("theta")
        phi_force.addTorsion(*phi_atoms, [])

        phi_cv = BiasVariable(
            phi_force,
            -np.pi,  # minValue
            np.pi,  # maxValue
            0.35,  # biasWidth (~20 degrees)
            True,  # periodic
        )

        bias_variables.append(phi_cv)
        logger.info(f"Added phi dihedral {i+1} as bias variable: atoms {phi_atoms}")

    return bias_variables


# Example usage function
def run_remd_simulation(
    pdb_file: str,
    output_dir: str = "output/replica_exchange",
    total_steps: int = 1000,  # VERY FAST for testing
    equilibration_steps: int = 100,  # Default equilibration steps
    temperatures: Optional[List[float]] = None,
    use_metadynamics: bool = True,
    checkpoint_manager=None,
    target_accept: float = 0.30,
    tuning_steps: int = 0,
) -> Optional[str]:  # Fixed: Changed return type to Optional[str] to allow None returns
    """
    Convenience function to run a complete REMD simulation.

    Args:
        pdb_file: Path to prepared PDB file
        output_dir: Directory for output files
        total_steps: Total simulation steps
        equilibration_steps: Number of equilibration steps before production
        temperatures: Temperature ladder (auto-generated if None)
        use_metadynamics: Whether to use metadynamics biasing
        checkpoint_manager: CheckpointManager instance for state tracking
        target_accept: Desired per-pair acceptance probability when tuning
        tuning_steps: If >0, run a short pre-production simulation for ladder
            tuning with this many steps

    Returns:
        Path to demultiplexed trajectory at 300K, or None if failed
    """

    # Stage: Replica Initialization
    if checkpoint_manager and not checkpoint_manager.is_step_completed(
        "replica_initialization"
    ):
        checkpoint_manager.mark_step_started("replica_initialization")

    # Set up bias variables if requested
    bias_variables = setup_bias_variables(pdb_file) if use_metadynamics else None

    # Create and configure REMD
    remd = ReplicaExchange(
        pdb_file=pdb_file,
        temperatures=temperatures,
        output_dir=output_dir,
        exchange_frequency=50,  # Very frequent exchanges for testing
        target_accept=target_accept,
    )

    # Plan DCD reporter stride before reporters are created in setup
    remd.plan_reporter_stride(
        total_steps=total_steps,
        equilibration_steps=equilibration_steps,
        target_frames=5000,
    )

    # Set up replicas
    remd.setup_replicas(bias_variables=bias_variables)

    if tuning_steps > 0:
        remd.run_simulation(total_steps=tuning_steps, equilibration_steps=0)
        remd.tune_temperature_ladder()
        remd.setup_replicas(bias_variables=bias_variables)

    # Save state
    if checkpoint_manager:
        checkpoint_manager.save_state(
            {
                "remd_config": {
                    "pdb_file": pdb_file,
                    "temperatures": remd.temperatures,
                    "output_dir": output_dir,
                    "exchange_frequency": remd.exchange_frequency,
                    "bias_variables": bias_variables,
                }
            }
        )
        checkpoint_manager.mark_step_completed(
            "replica_initialization",
            {
                "n_replicas": remd.n_replicas,
                "temperature_range": f"{min(remd.temperatures):.1f}-{max(remd.temperatures):.1f}K",
            },
        )
    elif checkpoint_manager and checkpoint_manager.is_step_completed(
        "replica_initialization"
    ):
        # Load existing state
        state_data = checkpoint_manager.load_state()
        remd_config = state_data.get("remd_config", {})

        # Recreate REMD object
        remd = ReplicaExchange(
            pdb_file=pdb_file,
            temperatures=temperatures,
            output_dir=output_dir,
            exchange_frequency=50,
            target_accept=target_accept,
        )

        # Set up bias variables if they were used
        bias_variables = remd_config.get("bias_variables") if use_metadynamics else None

        # Plan reporter stride prior to setup
        remd.plan_reporter_stride(
            total_steps=total_steps,
            equilibration_steps=equilibration_steps,
            target_frames=5000,
        )

        # Only setup replicas if we haven't done energy minimization yet
        if not checkpoint_manager.is_step_completed("energy_minimization"):
            remd.setup_replicas(bias_variables=bias_variables)
            if tuning_steps > 0:
                remd.run_simulation(total_steps=tuning_steps, equilibration_steps=0)
                remd.tune_temperature_ladder()
                remd.setup_replicas(bias_variables=bias_variables)
    else:
        # Non-checkpoint mode
        bias_variables = setup_bias_variables(pdb_file) if use_metadynamics else None
        remd = ReplicaExchange(
            pdb_file=pdb_file,
            temperatures=temperatures,
            output_dir=output_dir,
            exchange_frequency=50,
            target_accept=target_accept,
        )
        # Plan reporter stride prior to setup
        remd.plan_reporter_stride(
            total_steps=total_steps,
            equilibration_steps=equilibration_steps,
            target_frames=5000,
        )
        remd.setup_replicas(bias_variables=bias_variables)
        if tuning_steps > 0:
            remd.run_simulation(total_steps=tuning_steps, equilibration_steps=0)
            remd.tune_temperature_ladder()
            remd.setup_replicas(bias_variables=bias_variables)

    # Run simulation with checkpoint integration
    remd.run_simulation(
        total_steps=total_steps,
        equilibration_steps=equilibration_steps,
        checkpoint_manager=checkpoint_manager,
    )

    # Demultiplex for analysis (separate step - don't fail the entire simulation)
    demux_traj = None
    if checkpoint_manager and not checkpoint_manager.is_step_completed(
        "trajectory_demux"
    ):
        if checkpoint_manager:
            checkpoint_manager.mark_step_started("trajectory_demux")

        # Small delay to ensure DCD files are fully written to disk
        import time

        logger.info("Waiting for DCD files to be fully written...")
        time.sleep(2.0)

        try:
            demux_traj = remd.demux_trajectories(
                target_temperature=300.0, equilibration_steps=equilibration_steps
            )
        except Exception as exc:  # noqa: BLE001
            if checkpoint_manager:
                checkpoint_manager.mark_step_failed("trajectory_demux", str(exc))
            raise
        if demux_traj:
            logger.info(f"Demultiplexing successful: {demux_traj}")
            if checkpoint_manager:
                checkpoint_manager.mark_step_completed(
                    "trajectory_demux", {"demux_file": demux_traj}
                )
        else:
            logger.warning("Demultiplexing returned no trajectory")
            if checkpoint_manager:
                checkpoint_manager.mark_step_failed(
                    "trajectory_demux", "No frames found for demultiplexing"
                )

        # Always log that the simulation itself was successful
        logger.info("REMD simulation completed successfully")
        logger.info("Raw trajectory files are available for manual analysis")
    else:
        logger.info(
            "Trajectory demux already completed or checkpoint manager not available"
        )

    # Print statistics
    stats = remd.get_exchange_statistics()
    logger.info(f"REMD Statistics: {stats}")

    return demux_traj
