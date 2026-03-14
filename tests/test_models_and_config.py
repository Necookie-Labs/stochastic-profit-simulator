from pathlib import Path

import pytest

from src.config import DEFAULT_SCENARIO_NAME, build_default_scenarios, load_scenarios_from_yaml
from src.models import BusinessAssumptions, DistributionSpec, SimulationSettings, SimulationSummary


def test_default_scenarios_cover_three_market_cases() -> None:
    scenarios = build_default_scenarios()

    assert DEFAULT_SCENARIO_NAME == "expected"
    assert set(scenarios) == {"conservative", "expected", "optimistic"}
    assert scenarios["expected"].assumptions.business_name == "Monte Claro Coffee Kiosk"


def test_yaml_scenarios_match_expected_default() -> None:
    scenarios = load_scenarios_from_yaml(Path("config/simulation_config.yaml"))

    assert scenarios["expected"].assumptions.demand.mean == 2400
    assert scenarios["optimistic"].assumptions.marketing_uplift_max == pytest.approx(0.14)


def test_rejects_invalid_iteration_count() -> None:
    with pytest.raises(ValueError, match="iterations"):
        SimulationSettings(iterations=0)


def test_rejects_invalid_probability_range() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        BusinessAssumptions(
            business_name="Monte Claro Coffee Kiosk",
            currency="PHP",
            demand=DistributionSpec(distribution="normal", mean=2400, standard_deviation=350),
            selling_price=DistributionSpec(distribution="triangular", minimum=115, mode=120, maximum=128),
            variable_cost=DistributionSpec(distribution="triangular", minimum=48, mode=52, maximum=58),
            fixed_cost=DistributionSpec(distribution="normal", mean=95000, standard_deviation=8000),
            marketing_uplift_min=-0.01,
            marketing_uplift_max=0.1,
        )


def test_rejects_invalid_distribution_range() -> None:
    with pytest.raises(ValueError, match="minimum <= mode <= maximum"):
        DistributionSpec(distribution="triangular", minimum=120, mode=115, maximum=128)


def test_rejects_negative_fixed_cost_distribution_mean() -> None:
    with pytest.raises(ValueError, match="mean must be non-negative"):
        DistributionSpec(distribution="normal", mean=-1, standard_deviation=100)


def test_builds_summary_metrics_from_profit_samples() -> None:
    summary = SimulationSummary.from_profit_samples([100.0, 80.0, -20.0, 140.0, 60.0])

    assert summary.mean_profit == pytest.approx(72.0)
    assert summary.median_profit == pytest.approx(80.0)
    assert summary.minimum_profit == pytest.approx(-20.0)
    assert summary.maximum_profit == pytest.approx(140.0)
    assert summary.probability_of_loss == pytest.approx(0.2)
    assert summary.percentile_5 == pytest.approx(-20.0)
    assert summary.percentile_95 == pytest.approx(140.0)
