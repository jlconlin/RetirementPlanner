import math

import numpy as np

from retirement_model import (
    DEFAULT_SCENARIO,
    deterministic_summary,
    find_earliest_retirement_age,
    mc_success_grid,
    monte_carlo_success,
    nominal_to_real,
    project_portfolio,
    scenario_to_assumptions,
    scenario_with_defaults,
    spending_curve,
)


def zero_return_assumptions(**overrides):
    assumptions = {
        "current_age": 60,
        "life_expectancy": 65,
        "current_savings": 100_000.0,
        "annual_contribution": 10_000.0,
        "contribution_growth_rate": 0.0,
        "pre_retirement_return": 0.0,
        "post_retirement_return": 0.0,
        "return_volatility": 0.0,
        "annual_expenses": 30_000.0,
        "spending_model": "flat",
        "spending_params": {},
        "social_security_monthly": 0.0,
        "social_security_start_age": 67,
        "pension_monthly": 0.0,
        "pension_start_age": None,
        "target_retirement_age": 62,
        "has_spouse": False,
    }
    assumptions.update(overrides)
    return assumptions


def test_nominal_to_real_uses_fisher_equation():
    assert nominal_to_real(0.10, 0.025) == (1.10 / 1.025) - 1


def test_scenario_to_assumptions_converts_k_and_percent_units():
    scenario = scenario_with_defaults(
        {
            "current_savings": 250,
            "annual_contribution": 15,
            "annual_expenses": 60,
            "inflation_rate": 2.5,
            "pre_retirement_return": 7,
            "post_retirement_return": 5,
            "return_volatility": 12,
            "contribution_growth_rate": 2,
            "social_security_monthly": 1.8,
        }
    )
    assumptions = scenario_to_assumptions(scenario)

    assert assumptions["current_savings"] == 250_000
    assert assumptions["annual_contribution"] == 15_000
    assert assumptions["annual_expenses"] == 60_000
    assert assumptions["social_security_monthly"] == 1_800
    assert assumptions["contribution_growth_rate"] == 0.02
    assert math.isclose(assumptions["pre_retirement_return"], (1.07 / 1.025) - 1)
    assert math.isclose(assumptions["post_retirement_return"], (1.05 / 1.025) - 1)
    assert assumptions["return_volatility"] == 0.12


def test_scenario_defaults_include_future_ui_fields():
    scenario = scenario_with_defaults({})

    for key in DEFAULT_SCENARIO:
        assert key in scenario


def test_project_portfolio_zero_return_baseline():
    projection = project_portfolio(zero_return_assumptions(), retirement_age=62)

    assert projection["balance_end"].tolist() == [
        110_000.0,
        120_000.0,
        90_000.0,
        60_000.0,
        30_000.0,
    ]


def test_contribution_growth_is_real_growth_rate():
    assumptions = zero_return_assumptions(
        life_expectancy=63,
        target_retirement_age=63,
        contribution_growth_rate=0.02,
    )
    projection = project_portfolio(assumptions, retirement_age=63)

    assert projection["contribution"].tolist() == [10_000.0, 10_200.0, 10_404.0]
    assert projection["balance_end"].tolist() == [110_000.0, 120_200.0, 130_604.0]


def test_spending_curve_three_phase_and_taper():
    base = zero_return_assumptions(
        spending_model="three_phase",
        spending_params={
            "slow_go_age": 75,
            "slow_go_pct": 0.8,
            "no_go_age": 85,
            "no_go_pct": 0.6,
        },
    )

    assert spending_curve(100_000, 70, base) == 100_000
    assert spending_curve(100_000, 75, base) == 80_000
    assert spending_curve(100_000, 85, base) == 60_000

    taper = zero_return_assumptions(
        spending_model="taper",
        spending_params={"taper_start_age": 75, "taper_rate": 0.02},
    )
    assert spending_curve(100_000, 74, taper) == 100_000
    assert math.isclose(spending_curve(100_000, 77, taper), 100_000 * 0.98**2)


def test_survivor_does_not_receive_unclaimed_future_spousal_ss():
    assumptions = zero_return_assumptions(
        current_age=60,
        life_expectancy=62,
        current_savings=0.0,
        annual_contribution=0.0,
        annual_expenses=50_000.0,
        social_security_monthly=2_000.0,
        social_security_start_age=70,
        target_retirement_age=60,
        has_spouse=True,
        spouse_current_age=60,
        spouse_life_expectancy=65,
        spouse_retirement_age=60,
        survivor_spending_pct=0.7,
        spouse_ss_monthly=0.0,
        spouse_ss_start_age=70,
    )

    projection = project_portfolio(assumptions, retirement_age=60)

    assert projection.loc[projection["age"] >= 62, "ss_income"].eq(0).all()


def test_find_earliest_retirement_age_returns_first_solvent_age():
    assumptions = zero_return_assumptions(
        current_age=60,
        life_expectancy=65,
        current_savings=60_000,
        annual_contribution=30_000,
        annual_expenses=30_000,
    )

    age, projection = find_earliest_retirement_age(assumptions, range(61, 65))

    assert age == 62
    assert projection is not None
    assert (projection["balance_end"] >= 0).all()


def test_monte_carlo_zero_volatility_is_deterministic():
    assumptions = zero_return_assumptions(
        current_savings=150_000,
        annual_contribution=0,
        target_retirement_age=60,
    )

    rate, balances, paths = monte_carlo_success(
        assumptions, retirement_age=60, n_sims=5, return_paths=True
    )

    assert rate == 1.0
    assert balances == [0.0] * 5
    assert np.all(paths[:, -1] == 0.0)


def test_success_grid_matches_zero_return_threshold():
    assumptions = zero_return_assumptions(
        current_age=60,
        life_expectancy=65,
        annual_contribution=0,
        target_retirement_age=60,
    )

    grid = mc_success_grid(
        assumptions,
        ages=[60],
        balances=[149_999, 150_000, 150_001],
        n_sims=1,
        seed=1,
    )

    assert grid.tolist() == [[0.0], [1.0], [1.0]]


def test_deterministic_summary_reports_depletion_and_retirement_balance():
    summary = deterministic_summary(zero_return_assumptions(), retirement_age=62)

    assert summary.target_retirement_age == 62
    assert summary.balance_at_retirement == 120_000
    assert summary.ending_balance == 30_000
    assert summary.depletion_age is None
