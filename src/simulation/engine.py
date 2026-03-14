"""Monte Carlo simulation engine for monthly business profit analysis."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.models import (
    BusinessAssumptions,
    DistributionSpec,
    ScenarioConfig,
    SimulationRunResult,
    SimulationSummary,
    SimulationTrial,
)


class SimulationConfigurationError(ValueError):
    """Raised when a scenario configuration cannot be simulated safely."""


class SimulationExecutionError(RuntimeError):
    """Raised when a simulation run fails unexpectedly."""


@dataclass(slots=True)
class MonteCarloSimulationEngine:
    """Runs reproducible trial-based simulations from one scenario config."""

    percentile_points: tuple[int, ...] = (5, 25, 50, 75, 95)

    def run(self, scenario: ScenarioConfig) -> SimulationRunResult:
        self._validate_scenario(scenario)
        rng = np.random.default_rng(scenario.settings.random_seed)

        try:
            assumptions = scenario.assumptions
            iterations = scenario.settings.iterations
            demand = self._sample_distribution(assumptions.demand, iterations, rng)
            demand = np.rint(np.clip(demand, 0, None)).astype(int)

            uplift = np.zeros(iterations, dtype=float)
            marketing_spend = 0.0
            if scenario.settings.enable_marketing:
                marketing_spend = assumptions.marketing_spend
                uplift = rng.uniform(
                    assumptions.marketing_uplift_min,
                    assumptions.marketing_uplift_max,
                    size=iterations,
                )

            effective_demand = np.rint(demand * (1.0 + uplift)).astype(int)
            selling_price = np.clip(
                self._sample_distribution(assumptions.selling_price, iterations, rng),
                0,
                None,
            )
            variable_cost = np.clip(
                self._sample_distribution(assumptions.variable_cost, iterations, rng),
                0,
                None,
            )
            fixed_cost = np.clip(
                self._sample_distribution(assumptions.fixed_cost, iterations, rng),
                0,
                None,
            )

            revenue = effective_demand * selling_price
            total_cost = (effective_demand * variable_cost) + fixed_cost + marketing_spend
            profit = revenue - total_cost

            trials = [
                SimulationTrial(
                    demand_units=int(effective_demand[index]),
                    selling_price=float(selling_price[index]),
                    variable_cost_per_unit=float(variable_cost[index]),
                    fixed_cost=float(fixed_cost[index]),
                    marketing_uplift_rate=float(uplift[index]),
                    revenue=float(revenue[index]),
                    total_cost=float(total_cost[index]),
                    profit=float(profit[index]),
                )
                for index in range(iterations)
            ]
        except Exception as exc:  # pragma: no cover - defensive wrapper
            raise SimulationExecutionError(
                f"Simulation run failed for scenario '{scenario.name}'."
            ) from exc

        return SimulationRunResult(
            scenario_name=scenario.name,
            currency=scenario.assumptions.currency,
            iterations=scenario.settings.iterations,
            random_seed=scenario.settings.random_seed,
            trials=trials,
            summary=SimulationSummary.from_profit_samples(
                [trial.profit for trial in trials],
                percentile_points=self.percentile_points,
            ),
        )

    def _sample_distribution(
        self,
        distribution: DistributionSpec,
        iterations: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        if distribution.distribution == "triangular":
            return rng.triangular(
                distribution.minimum,
                distribution.mode,
                distribution.maximum,
                size=iterations,
            )
        if distribution.distribution == "normal":
            return rng.normal(distribution.mean, distribution.standard_deviation, size=iterations)
        if distribution.distribution == "uniform":
            return rng.uniform(distribution.minimum, distribution.maximum, size=iterations)
        raise SimulationConfigurationError(
            f"Unsupported distribution '{distribution.distribution}'."
        )

    def _validate_scenario(self, scenario: ScenarioConfig) -> None:
        assumptions: BusinessAssumptions = scenario.assumptions
        if not scenario.name.strip():
            raise SimulationConfigurationError("scenario name must not be empty.")
        if not assumptions.currency.strip():
            raise SimulationConfigurationError("currency must not be empty.")
        if scenario.settings.iterations <= 0:
            raise SimulationConfigurationError("iterations must be greater than 0.")
