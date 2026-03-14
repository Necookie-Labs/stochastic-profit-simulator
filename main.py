"""Entry point for the Monte Carlo business analysis workflow."""

from src.analysis import SimulationAnalysisService
from src.config import DEFAULT_SCENARIO_NAME, load_scenarios_from_yaml
from src.simulation import MonteCarloSimulationEngine


def main() -> None:
    scenarios = load_scenarios_from_yaml("config/simulation_config.yaml")
    scenario = scenarios[DEFAULT_SCENARIO_NAME]

    engine = MonteCarloSimulationEngine()
    analysis = SimulationAnalysisService()
    result = engine.run(scenario)
    convergence = analysis.build_convergence_report(
        scenario,
        sample_sizes=(100, 500, 1_000, 5_000),
    )

    summary = result.summary
    print(f"Scenario: {result.scenario_name}")
    print(f"Iterations: {result.iterations}")
    print(f"Mean profit: {summary.mean_profit:,.2f} {result.currency}")
    print(f"Median profit: {summary.median_profit:,.2f} {result.currency}")
    print(f"Std. dev.: {summary.profit_standard_deviation:,.2f} {result.currency}")
    print(f"Min/Max profit: {summary.minimum_profit:,.2f} / {summary.maximum_profit:,.2f} {result.currency}")
    print(f"Probability of loss: {summary.probability_of_loss:.2%}")
    print(
        "Selected percentiles: "
        + ", ".join(
            f"P{percentile}={value:,.2f} {result.currency}"
            for percentile, value in summary.percentiles.items()
        )
    )
    print("Convergence checkpoints:")
    for point in convergence.points:
        print(
            f"  n={point.sample_size}: mean={point.mean_profit:,.2f} {result.currency}, "
            f"loss={point.probability_of_loss:.2%}"
        )


if __name__ == "__main__":
    main()
