"""Default scenario definitions and YAML loading helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from src.models import BusinessAssumptions, DistributionSpec, ScenarioConfig, SimulationSettings

DEFAULT_SCENARIO_NAME = "expected"


def build_default_scenarios() -> dict[str, ScenarioConfig]:
    common_settings = SimulationSettings(
        iterations=1_000,
        random_seed=42,
        enable_marketing=True,
        sample_sizes_to_compare=(100, 1_000, 5_000, 10_000),
    )

    return {
        "conservative": ScenarioConfig(
            name="conservative",
            assumptions=BusinessAssumptions(
                business_name="Monte Claro Coffee Kiosk",
                currency="PHP",
                demand=DistributionSpec(distribution="normal", mean=2_050, standard_deviation=260),
                selling_price=DistributionSpec(distribution="triangular", minimum=112, mode=116, maximum=122),
                variable_cost=DistributionSpec(distribution="triangular", minimum=50, mode=55, maximum=61),
                fixed_cost=DistributionSpec(distribution="normal", mean=98_000, standard_deviation=6_500),
                marketing_spend=10_000,
                marketing_uplift_min=0.01,
                marketing_uplift_max=0.04,
            ),
            settings=common_settings,
        ),
        "expected": ScenarioConfig(
            name="expected",
            assumptions=BusinessAssumptions(
                business_name="Monte Claro Coffee Kiosk",
                currency="PHP",
                demand=DistributionSpec(distribution="normal", mean=2_400, standard_deviation=350),
                selling_price=DistributionSpec(distribution="triangular", minimum=115, mode=120, maximum=128),
                variable_cost=DistributionSpec(distribution="triangular", minimum=48, mode=52, maximum=58),
                fixed_cost=DistributionSpec(distribution="normal", mean=95_000, standard_deviation=8_000),
                marketing_spend=12_000,
                marketing_uplift_min=0.03,
                marketing_uplift_max=0.10,
            ),
            settings=common_settings,
        ),
        "optimistic": ScenarioConfig(
            name="optimistic",
            assumptions=BusinessAssumptions(
                business_name="Monte Claro Coffee Kiosk",
                currency="PHP",
                demand=DistributionSpec(distribution="normal", mean=2_850, standard_deviation=420),
                selling_price=DistributionSpec(distribution="triangular", minimum=118, mode=124, maximum=133),
                variable_cost=DistributionSpec(distribution="triangular", minimum=46, mode=50, maximum=56),
                fixed_cost=DistributionSpec(distribution="normal", mean=93_000, standard_deviation=7_000),
                marketing_spend=15_000,
                marketing_uplift_min=0.05,
                marketing_uplift_max=0.14,
            ),
            settings=common_settings,
        ),
    }


def load_scenarios_from_yaml(path: str | Path) -> dict[str, ScenarioConfig]:
    raw_config = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    scenarios = raw_config.get("scenarios", {})
    return {name: _parse_scenario(name, payload) for name, payload in scenarios.items()}


def _parse_scenario(name: str, payload: dict) -> ScenarioConfig:
    assumptions_payload = payload["assumptions"]
    settings_payload = payload["settings"]

    return ScenarioConfig(
        name=name,
        assumptions=BusinessAssumptions(
            business_name=assumptions_payload["business_name"],
            currency=assumptions_payload["currency"],
            demand=DistributionSpec(**assumptions_payload["demand"]),
            selling_price=DistributionSpec(**assumptions_payload["selling_price"]),
            variable_cost=DistributionSpec(**assumptions_payload["variable_cost"]),
            fixed_cost=DistributionSpec(**assumptions_payload["fixed_cost"]),
            marketing_spend=assumptions_payload.get("marketing_spend", 0.0),
            marketing_uplift_min=assumptions_payload.get("marketing_uplift_min", 0.0),
            marketing_uplift_max=assumptions_payload.get("marketing_uplift_max", 0.0),
        ),
        settings=SimulationSettings(
            iterations=settings_payload["iterations"],
            random_seed=settings_payload.get("random_seed"),
            enable_marketing=settings_payload.get("enable_marketing", True),
            sample_sizes_to_compare=tuple(settings_payload.get("sample_sizes_to_compare", ())),
        ),
    )
