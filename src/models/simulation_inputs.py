"""Validated input models for Monte Carlo business simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, median


def _require_non_negative(value: float | int, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative.")


def _require_probability(value: float, field_name: str) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{field_name} must be between 0 and 1.")


@dataclass(slots=True, frozen=True)
class DistributionSpec:
    """Describes a distribution the simulation engine can sample from."""

    distribution: str
    minimum: float | None = None
    mode: float | None = None
    maximum: float | None = None
    mean: float | None = None
    standard_deviation: float | None = None

    def __post_init__(self) -> None:
        distribution = self.distribution.lower()
        object.__setattr__(self, "distribution", distribution)

        if distribution == "triangular":
            if None in (self.minimum, self.mode, self.maximum):
                raise ValueError("Triangular distributions require minimum, mode, and maximum.")
            if not self.minimum <= self.mode <= self.maximum:
                raise ValueError("Triangular distributions require minimum <= mode <= maximum.")
        elif distribution == "normal":
            if self.mean is None or self.standard_deviation is None:
                raise ValueError("Normal distributions require mean and standard_deviation.")
            if self.standard_deviation <= 0:
                raise ValueError("standard_deviation must be greater than 0.")
        elif distribution == "uniform":
            if self.minimum is None or self.maximum is None:
                raise ValueError("Uniform distributions require minimum and maximum.")
            if self.minimum > self.maximum:
                raise ValueError("Uniform distributions require minimum <= maximum.")
        else:
            raise ValueError(f"Unsupported distribution '{self.distribution}'.")

        for name in ("minimum", "mode", "maximum", "mean"):
            value = getattr(self, name)
            if value is not None:
                _require_non_negative(value, name)


@dataclass(slots=True, frozen=True)
class BusinessAssumptions:
    """Business-level assumptions for one monthly simulation scenario."""

    business_name: str
    currency: str
    demand: DistributionSpec
    selling_price: DistributionSpec
    variable_cost: DistributionSpec
    fixed_cost: DistributionSpec
    marketing_spend: float = 0.0
    marketing_uplift_min: float = 0.0
    marketing_uplift_max: float = 0.0

    def __post_init__(self) -> None:
        _require_non_negative(self.marketing_spend, "marketing_spend")
        _require_probability(self.marketing_uplift_min, "marketing_uplift_min")
        _require_probability(self.marketing_uplift_max, "marketing_uplift_max")
        if self.marketing_uplift_min > self.marketing_uplift_max:
            raise ValueError("marketing_uplift_min must be less than or equal to marketing_uplift_max.")


@dataclass(slots=True, frozen=True)
class SimulationSettings:
    """Controls repeatability and scale of a simulation run."""

    iterations: int = 1_000
    random_seed: int | None = 42
    enable_marketing: bool = True
    sample_sizes_to_compare: tuple[int, ...] = field(default_factory=lambda: (100, 1_000, 5_000))

    def __post_init__(self) -> None:
        if self.iterations <= 0:
            raise ValueError("iterations must be greater than 0.")
        if self.random_seed is not None and self.random_seed < 0:
            raise ValueError("random_seed must be non-negative when provided.")
        if not self.sample_sizes_to_compare:
            raise ValueError("sample_sizes_to_compare must include at least one value.")
        if any(sample_size <= 0 for sample_size in self.sample_sizes_to_compare):
            raise ValueError("sample_sizes_to_compare values must be greater than 0.")


@dataclass(slots=True, frozen=True)
class ScenarioConfig:
    """Simulation-ready bundle of assumptions and settings."""

    name: str
    assumptions: BusinessAssumptions
    settings: SimulationSettings


@dataclass(slots=True, frozen=True)
class SimulationSummary:
    """Compact metrics a simulation engine can return after one run."""

    mean_profit: float
    median_profit: float
    profit_standard_deviation: float
    probability_of_loss: float
    percentile_5: float
    percentile_95: float

    @classmethod
    def from_profit_samples(cls, profits: list[float]) -> "SimulationSummary":
        if not profits:
            raise ValueError("profits must include at least one sample.")

        ordered = sorted(profits)
        loss_count = sum(1 for profit in ordered if profit < 0)
        fifth_index = max(0, int(0.05 * (len(ordered) - 1)))
        ninety_fifth_index = min(len(ordered) - 1, int(0.95 * (len(ordered) - 1)))
        avg = mean(ordered)
        variance = sum((profit - avg) ** 2 for profit in ordered) / len(ordered)

        return cls(
            mean_profit=avg,
            median_profit=median(ordered),
            profit_standard_deviation=variance**0.5,
            probability_of_loss=loss_count / len(ordered),
            percentile_5=ordered[fifth_index],
            percentile_95=ordered[ninety_fifth_index],
        )
