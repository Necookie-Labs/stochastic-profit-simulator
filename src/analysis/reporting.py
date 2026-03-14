"""Summary and convergence utilities for Monte Carlo profit simulations."""

from __future__ import annotations

from dataclasses import dataclass

from src.models import (
    ConvergencePoint,
    ConvergenceReport,
    ScenarioConfig,
    SimulationSettings,
    SimulationSummary,
)
from src.simulation.engine import MonteCarloSimulationEngine


@dataclass(slots=True)
class SimulationAnalysisService:
    """Builds summary statistics and convergence views from simulation results."""

    percentile_points: tuple[int, ...] = (5, 25, 50, 75, 95)

    def summarize_profits(self, profits: list[float]) -> SimulationSummary:
        return SimulationSummary.from_profit_samples(
            profits,
            percentile_points=self.percentile_points,
        )

    def build_convergence_report(
        self,
        scenario: ScenarioConfig,
        sample_sizes: tuple[int, ...] | None = None,
    ) -> ConvergenceReport:
        checkpoints = sample_sizes or scenario.settings.sample_sizes_to_compare
        if not checkpoints:
            raise ValueError("sample_sizes must include at least one value.")

        ordered_checkpoints = sorted(set(checkpoints))
        points: list[ConvergencePoint] = []

        for sample_size in ordered_checkpoints:
            convergence_scenario = ScenarioConfig(
                name=scenario.name,
                assumptions=scenario.assumptions,
                settings=SimulationSettings(
                    iterations=sample_size,
                    random_seed=scenario.settings.random_seed,
                    enable_marketing=scenario.settings.enable_marketing,
                    sample_sizes_to_compare=scenario.settings.sample_sizes_to_compare,
                ),
            )
            result = MonteCarloSimulationEngine(
                percentile_points=self.percentile_points
            ).run(convergence_scenario)
            points.append(
                ConvergencePoint(
                    sample_size=sample_size,
                    mean_profit=result.summary.mean_profit,
                    median_profit=result.summary.median_profit,
                    probability_of_loss=result.summary.probability_of_loss,
                )
            )

        return ConvergenceReport(
            scenario_name=scenario.name,
            currency=scenario.assumptions.currency,
            points=points,
        )
