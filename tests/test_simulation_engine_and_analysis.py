import pytest

from src.analysis import SimulationAnalysisService
from src.config import build_default_scenarios
from src.models import BusinessAssumptions, DistributionSpec, ScenarioConfig, SimulationSettings
from src.simulation import MonteCarloSimulationEngine, SimulationConfigurationError


def test_simulation_engine_returns_trial_level_outputs_and_summary() -> None:
    scenario = build_default_scenarios()["expected"]

    result = MonteCarloSimulationEngine().run(scenario)

    assert result.scenario_name == "expected"
    assert result.iterations == scenario.settings.iterations
    assert len(result.trials) == scenario.settings.iterations
    assert result.summary.maximum_profit >= result.summary.minimum_profit
    assert set(result.summary.percentiles) == {5, 25, 50, 75, 95}


def test_simulation_is_reproducible_when_seed_is_fixed() -> None:
    scenario = build_default_scenarios()["expected"]
    engine = MonteCarloSimulationEngine()

    first_run = engine.run(scenario)
    second_run = engine.run(scenario)

    assert [trial.profit for trial in first_run.trials[:10]] == pytest.approx(
        [trial.profit for trial in second_run.trials[:10]]
    )
    assert first_run.summary.mean_profit == pytest.approx(second_run.summary.mean_profit)


def test_convergence_report_uses_requested_sample_sizes() -> None:
    scenario = build_default_scenarios()["expected"]

    report = SimulationAnalysisService().build_convergence_report(
        scenario,
        sample_sizes=(100, 500, 1_000, 5_000),
    )

    assert [point.sample_size for point in report.points] == [100, 500, 1000, 5000]
    assert all(0 <= point.probability_of_loss <= 1 for point in report.points)


def test_disabling_marketing_removes_uplift_and_spend() -> None:
    scenario = build_default_scenarios()["expected"]
    without_marketing = ScenarioConfig(
        name=scenario.name,
        assumptions=scenario.assumptions,
        settings=SimulationSettings(
            iterations=20,
            random_seed=scenario.settings.random_seed,
            enable_marketing=False,
            sample_sizes_to_compare=scenario.settings.sample_sizes_to_compare,
        ),
    )

    result = MonteCarloSimulationEngine().run(without_marketing)

    assert all(trial.marketing_uplift_rate == 0.0 for trial in result.trials)


def test_simulation_rejects_blank_currency() -> None:
    scenario = ScenarioConfig(
        name="invalid",
        assumptions=BusinessAssumptions(
            business_name="Monte Claro Coffee Kiosk",
            currency="",
            demand=DistributionSpec(distribution="normal", mean=2400, standard_deviation=350),
            selling_price=DistributionSpec(distribution="triangular", minimum=115, mode=120, maximum=128),
            variable_cost=DistributionSpec(distribution="triangular", minimum=48, mode=52, maximum=58),
            fixed_cost=DistributionSpec(distribution="normal", mean=95000, standard_deviation=8000),
        ),
        settings=SimulationSettings(iterations=10, random_seed=7),
    )

    with pytest.raises(SimulationConfigurationError, match="currency"):
        MonteCarloSimulationEngine().run(scenario)
