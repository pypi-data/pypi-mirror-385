"""Replica exchange experiment runner that requires the canonical REMD stack."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Optional

from pmarlo.replica_exchange.config import RemdConfig
from pmarlo.replica_exchange.replica_exchange import (
    ReplicaExchange,
    setup_bias_variables,
)
from pmarlo.utils.path_utils import ensure_directory
from pmarlo.utils.replica_utils import exponential_temperature_ladder

from .benchmark_utils import (
    build_remd_baseline_object,
    compute_threshold_comparison,
    get_environment_info,
    initialize_baseline_if_missing,
    update_trend,
)
from .kpi import (
    RuntimeMemoryTracker,
    build_benchmark_record,
    compute_replica_exchange_success_rate,
    compute_wall_clock_per_step,
    default_kpi_metrics,
    write_benchmark_json,
)
from .utils import default_output_root, set_seed, timestamp_dir

logger = logging.getLogger(__name__)


@dataclass
class ReplicaExchangeConfig:
    pdb_file: str
    output_dir: str = f"{default_output_root()}/replica_exchange"
    temperatures: Optional[List[float]] = None  # defaults handled by class
    total_steps: int = 800
    equilibration_steps: int = 200
    exchange_frequency: int = 50
    use_metadynamics: bool = True
    tmin: float = 300.0
    tmax: float = 350.0
    nreplicas: int = 6
    seed: int | None = None


def run_replica_exchange_experiment(config: ReplicaExchangeConfig) -> Dict:
    """Run the REMD benchmark experiment and collect KPI metrics."""

    set_seed(config.seed)
    run_dir = timestamp_dir(config.output_dir)
    cm = SimpleNamespace(setup_run_directory=lambda: None)

    temps: Optional[List[float]]
    if config.temperatures is None:
        temps = exponential_temperature_ladder(
            config.tmin, config.tmax, config.nreplicas
        )
    else:
        temps = config.temperatures

    remd_config = RemdConfig(
        pdb_file=config.pdb_file,
        temperatures=temps,
        output_dir=str(run_dir / "remd"),
        exchange_frequency=config.exchange_frequency,
        dcd_stride=2000,
        auto_setup=False,
        random_seed=config.seed,
    )

    factory = getattr(ReplicaExchange, "from_config", None)
    if callable(factory):
        remd = factory(remd_config)
    else:
        remd = ReplicaExchange(**asdict(remd_config))

    bias_vars = (
        setup_bias_variables(config.pdb_file) if config.use_metadynamics else None
    )

    if hasattr(remd, "plan_reporter_stride"):
        remd.plan_reporter_stride(
            total_steps=config.total_steps,
            equilibration_steps=config.equilibration_steps,
            target_frames=5000,
        )
    remd.setup_replicas(bias_variables=bias_vars)

    with RuntimeMemoryTracker() as tracker:
        remd.run_simulation(
            total_steps=config.total_steps,
            equilibration_steps=config.equilibration_steps,
            checkpoint_manager=cm,
        )

    stats = remd.get_exchange_statistics()

    ensure_directory(run_dir)
    (run_dir / "remd").mkdir(exist_ok=True)

    with open(run_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2)
    with open(run_dir / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    input_desc = {
        "parameters": asdict(config),
        "description": "Replica exchange experiment input",
    }
    with open(run_dir / "input.json", "w", encoding="utf-8") as f:
        json.dump(input_desc, f, indent=2)

    kpis = default_kpi_metrics(
        conformational_coverage=None,
        transition_matrix_accuracy=None,
        replica_exchange_success_rate=compute_replica_exchange_success_rate(stats),
        runtime_seconds=tracker.runtime_seconds,
        memory_mb=tracker.max_rss_mb,
    )

    enriched_input = {
        **asdict(config),
        **get_environment_info(),
        "seconds_per_step": compute_wall_clock_per_step(
            tracker.runtime_seconds, config.total_steps
        ),
        "num_exchange_attempts": (
            stats.get("total_exchange_attempts") if isinstance(stats, dict) else None
        ),
        "overall_acceptance_rate": (
            stats.get("overall_acceptance_rate") if isinstance(stats, dict) else None
        ),
        "seed": config.seed,
    }

    record = build_benchmark_record(
        algorithm="replica_exchange",
        experiment_id=run_dir.name,
        input_parameters=enriched_input,
        kpi_metrics=kpis,
        notes="REMD run",
        errors=[],
    )
    write_benchmark_json(run_dir, record)

    root_dir = Path(config.output_dir)
    baseline_object = build_remd_baseline_object(
        input_parameters=enriched_input,
        results=kpis,
    )
    initialize_baseline_if_missing(root_dir, baseline_object)
    update_trend(root_dir, baseline_object)

    trend_path = root_dir / "trend.json"
    if trend_path.exists():
        with open(trend_path, "r", encoding="utf-8") as tf:
            trend = json.load(tf)
        if isinstance(trend, list) and len(trend) >= 2:
            prev = trend[-2]
            curr = trend[-1]
            comparison = compute_threshold_comparison(prev, curr)
            with open(run_dir / "comparison.json", "w", encoding="utf-8") as cf:
                json.dump(comparison, cf, indent=2)

    logger.info("Replica exchange experiment complete: %s", run_dir)
    return {
        "run_dir": str(run_dir),
        "stats": stats,
        "trajectories_dir": str(run_dir / "remd"),
    }
