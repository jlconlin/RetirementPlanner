"""Core retirement planner calculations.

The UI should stay thin. This module owns the assumptions format,
unit conversions, deterministic projections, Monte Carlo runs, and summary
calculations shared by the notebook and Streamlit app.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_SCENARIO: dict[str, Any] = {
    "current_age": 56,
    "life_expectancy": 90,
    "target_retirement_age": 65,
    "current_savings": 250.0,
    "annual_contribution": 15.0,
    "contribution_growth_rate": 2.0,
    "inflation_rate": 2.5,
    "pre_retirement_return": 7.0,
    "post_retirement_return": 5.0,
    "return_volatility": 12.0,
    "annual_expenses": 60.0,
    "spending_model": "flat",
    "slow_go_age": 75,
    "slow_go_pct": 80.0,
    "no_go_age": 85,
    "no_go_pct": 60.0,
    "taper_start_age": 75,
    "taper_rate_pct": 1.5,
    "social_security_monthly": 1.8,
    "social_security_start_age": 67,
    "has_pension": False,
    "pension_monthly": 0.0,
    "pension_start_age": 60,
    "n_sims": 1000,
    "has_spouse": False,
    "spouse_age": 54,
    "spouse_life_expectancy": 92,
    "spouse_retirement_age": 63,
    "survivor_spending_pct": 70.0,
    "spouse_ss_monthly": 1.5,
    "spouse_ss_start_age": 67,
}


@dataclass(frozen=True)
class PlanSummary:
    target_retirement_age: int
    earliest_retirement_age: int | None
    balance_at_retirement: float
    ending_balance: float
    depletion_age: int | None
    monte_carlo_success_rate: float | None = None
    monte_carlo_median_ending_balance: float | None = None
    monte_carlo_p10_ending_balance: float | None = None
    monte_carlo_p90_ending_balance: float | None = None


def nominal_to_real(nominal_rate: float, inflation_rate: float) -> float:
    """Convert nominal annual rate to real annual rate."""
    return (1 + nominal_rate) / (1 + inflation_rate) - 1


def scenario_with_defaults(scenario: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a UI scenario dict with missing keys filled from defaults."""
    merged = DEFAULT_SCENARIO.copy()
    if scenario:
        merged.update(scenario)
    return merged


def scenario_to_assumptions(scenario: dict[str, Any]) -> dict[str, Any]:
    """Convert a user-facing scenario into internal dollar/rate assumptions."""
    s = scenario_with_defaults(scenario)
    inflation = s["inflation_rate"] / 100
    return {
        "current_age": int(s["current_age"]),
        "life_expectancy": int(s["life_expectancy"]),
        "current_savings": float(s["current_savings"]) * 1_000,
        "annual_contribution": float(s["annual_contribution"]) * 1_000,
        "contribution_growth_rate": float(s["contribution_growth_rate"]) / 100,
        "pre_retirement_return": nominal_to_real(
            float(s["pre_retirement_return"]) / 100, inflation
        ),
        "post_retirement_return": nominal_to_real(
            float(s["post_retirement_return"]) / 100, inflation
        ),
        "return_volatility": float(s["return_volatility"]) / 100,
        "annual_expenses": float(s["annual_expenses"]) * 1_000,
        "spending_model": s.get("spending_model", "flat"),
        "spending_params": {
            "slow_go_age": int(s.get("slow_go_age", 75)),
            "slow_go_pct": float(s.get("slow_go_pct", 80.0)) / 100,
            "no_go_age": int(s.get("no_go_age", 85)),
            "no_go_pct": float(s.get("no_go_pct", 60.0)) / 100,
            "taper_start_age": int(s.get("taper_start_age", 75)),
            "taper_rate": float(s.get("taper_rate_pct", 1.5)) / 100,
        },
        "social_security_monthly": float(s["social_security_monthly"]) * 1_000,
        "social_security_start_age": int(s["social_security_start_age"]),
        "pension_monthly": (
            float(s["pension_monthly"]) * 1_000 if s.get("has_pension") else 0
        ),
        "pension_start_age": (
            int(s["pension_start_age"]) if s.get("has_pension") else None
        ),
        "target_retirement_age": int(s["target_retirement_age"]),
        "has_spouse": bool(s.get("has_spouse", False)),
        "spouse_current_age": int(s.get("spouse_age", 54)),
        "spouse_life_expectancy": int(s.get("spouse_life_expectancy", 92)),
        "spouse_retirement_age": int(s.get("spouse_retirement_age", 63)),
        "survivor_spending_pct": float(s.get("survivor_spending_pct", 70.0)) / 100,
        "spouse_ss_monthly": float(s.get("spouse_ss_monthly", 1.5)) * 1_000,
        "spouse_ss_start_age": int(s.get("spouse_ss_start_age", 67)),
    }


def spending_curve(base_expenses: float, age: int, assumptions: dict[str, Any]) -> float:
    """Apply the selected spending model to return age-adjusted expenses."""
    model = assumptions.get("spending_model", "flat")
    params = assumptions.get("spending_params", {})
    if model == "three_phase":
        if age >= params.get("no_go_age", 85):
            return base_expenses * params.get("no_go_pct", 0.60)
        if age >= params.get("slow_go_age", 75):
            return base_expenses * params.get("slow_go_pct", 0.80)
        return base_expenses
    if model == "taper":
        start = params.get("taper_start_age", 75)
        if age >= start:
            return base_expenses * (1 - params.get("taper_rate", 0.015)) ** (
                age - start
            )
        return base_expenses
    return base_expenses


def project_portfolio(
    assumptions: dict[str, Any],
    retirement_age: int,
    return_sequence: list[float] | np.ndarray | None = None,
) -> pd.DataFrame:
    """Simulate the portfolio from current age through the planning horizon."""
    has_spouse = assumptions.get("has_spouse", False)
    self_years = assumptions["life_expectancy"] - assumptions["current_age"]
    if has_spouse:
        spouse_years = (
            assumptions["spouse_life_expectancy"] - assumptions["spouse_current_age"]
        )
        years = max(self_years, spouse_years)
    else:
        spouse_years = 0
        years = self_years

    balance = assumptions["current_savings"]
    contribution = assumptions["annual_contribution"]
    rows: list[dict[str, Any]] = []

    for i in range(years):
        age = assumptions["current_age"] + i

        if has_spouse:
            spouse_age = assumptions["spouse_current_age"] + i
            self_alive = i < self_years
            spouse_alive = i < spouse_years
            if not self_alive and not spouse_alive:
                break
            spouse_retired = spouse_age >= assumptions["spouse_retirement_age"]
        else:
            spouse_age = 0
            self_alive = True
            spouse_alive = False
            spouse_retired = False

        self_retired = age >= retirement_age

        if return_sequence is not None:
            r = return_sequence[i]
        else:
            r = (
                assumptions["post_retirement_return"]
                if (self_retired or spouse_retired)
                else assumptions["pre_retirement_return"]
            )

        if has_spouse:
            self_ss_rate = assumptions["social_security_monthly"] * 12
            spouse_ss_rate = assumptions["spouse_ss_monthly"] * 12
            self_ss_active = (
                self_ss_rate if age >= assumptions["social_security_start_age"] else 0
            )
            spouse_ss_active = (
                spouse_ss_rate
                if spouse_age >= assumptions["spouse_ss_start_age"]
                else 0
            )

            if self_alive and spouse_alive:
                ss_income = self_ss_active + spouse_ss_active
            elif self_alive and not spouse_alive:
                spouse_survivor_ss = (
                    spouse_ss_rate
                    if assumptions["spouse_life_expectancy"]
                    > assumptions["spouse_ss_start_age"]
                    else 0
                )
                ss_income = max(self_ss_active, spouse_survivor_ss)
            elif spouse_alive and not self_alive:
                self_survivor_ss = (
                    self_ss_rate
                    if assumptions["life_expectancy"]
                    > assumptions["social_security_start_age"]
                    else 0
                )
                ss_income = max(spouse_ss_active, self_survivor_ss)
            else:
                ss_income = 0
        else:
            ss_income = (
                assumptions["social_security_monthly"] * 12
                if age >= assumptions["social_security_start_age"]
                else 0
            )

        pension_income = (
            assumptions["pension_monthly"] * 12
            if assumptions["pension_start_age"] is not None
            and age >= assumptions["pension_start_age"]
            else 0
        )

        curve_expenses = spending_curve(assumptions["annual_expenses"], age, assumptions)
        if has_spouse and not (self_alive and spouse_alive):
            effective_expenses = curve_expenses * assumptions["survivor_spending_pct"]
        else:
            effective_expenses = curve_expenses

        balance_start = balance
        in_withdrawal = self_retired or not self_alive
        if in_withdrawal:
            withdrawal = max(effective_expenses - ss_income - pension_income, 0)
            balance -= withdrawal
            contrib_this_year = 0
        else:
            withdrawal = 0
            balance += contribution
            contrib_this_year = contribution
            contribution *= 1 + assumptions["contribution_growth_rate"]

        growth = balance * r
        balance += growth

        rows.append(
            {
                "age": age,
                "retired": self_retired,
                "balance_start": balance_start,
                "contribution": contrib_this_year,
                "ss_income": ss_income,
                "pension_income": pension_income,
                "withdrawal": withdrawal,
                "growth": growth,
                "balance_end": balance,
            }
        )

    return pd.DataFrame(rows)


def find_earliest_retirement_age(
    assumptions: dict[str, Any], age_range: range | None = None
) -> tuple[int | None, pd.DataFrame | None]:
    """Find the earliest age where the deterministic path never depletes."""
    if age_range is None:
        age_range = range(assumptions["current_age"] + 1, assumptions["life_expectancy"])

    for age in age_range:
        df = project_portfolio(assumptions, age)
        if (df["balance_end"] >= 0).all():
            return age, df

    return None, None


def monte_carlo_success(
    assumptions: dict[str, Any],
    retirement_age: int,
    n_sims: int = 1000,
    seed: int = 42,
    return_paths: bool = False,
) -> tuple[float, list[float]] | tuple[float, list[float], np.ndarray]:
    """Run randomized projections for a retirement age."""
    rng = np.random.default_rng(seed)

    self_years = assumptions["life_expectancy"] - assumptions["current_age"]
    if assumptions.get("has_spouse", False):
        spouse_years = (
            assumptions["spouse_life_expectancy"] - assumptions["spouse_current_age"]
        )
        years = max(self_years, spouse_years)
        spouse_ret_age = assumptions["spouse_retirement_age"]
    else:
        years = self_years
        spouse_ret_age = None

    successes = 0
    ending_balances: list[float] = []
    all_paths: list[np.ndarray] | None = [] if return_paths else None

    for _ in range(n_sims):
        returns = []
        for i in range(years):
            age = assumptions["current_age"] + i
            anyone_retired = age >= retirement_age or (
                spouse_ret_age is not None
                and assumptions["spouse_current_age"] + i >= spouse_ret_age
            )
            mean_r = (
                assumptions["post_retirement_return"]
                if anyone_retired
                else assumptions["pre_retirement_return"]
            )
            returns.append(rng.normal(mean_r, assumptions["return_volatility"]))

        df = project_portfolio(assumptions, retirement_age, return_sequence=returns)
        ending_balances.append(df["balance_end"].iloc[-1])
        if (df["balance_end"] >= 0).all():
            successes += 1
        if all_paths is not None:
            all_paths.append(df["balance_end"].values)

    if all_paths is not None:
        return successes / n_sims, ending_balances, np.array(all_paths)
    return successes / n_sims, ending_balances


def mc_success_grid(
    assumptions: dict[str, Any],
    ages: list[int],
    balances: list[float] | np.ndarray,
    n_sims: int = 300,
    seed: int = 42,
    inflation_rate: float = 0.0,
    base_age: int | None = None,
) -> np.ndarray:
    """Return success rates for retirement ages x starting balances."""
    rng = np.random.default_rng(seed)
    grid = np.zeros((len(balances), len(ages)))

    for j, age in enumerate(ages):
        years = assumptions["life_expectancy"] - age
        if years <= 0:
            grid[:, j] = 1.0
            continue

        ret = rng.normal(
            assumptions["post_retirement_return"],
            assumptions["return_volatility"],
            (n_sims, years),
        )

        withdrawals = np.zeros(years)
        for yr in range(years):
            curr_age = age + yr
            ss = (
                assumptions["social_security_monthly"] * 12
                if curr_age >= assumptions["social_security_start_age"]
                else 0
            )
            pension = (
                assumptions["pension_monthly"] * 12
                if assumptions["pension_start_age"] is not None
                and curr_age >= assumptions["pension_start_age"]
                else 0
            )
            withdrawals[yr] = max(
                spending_curve(assumptions["annual_expenses"], curr_age, assumptions)
                - ss
                - pension,
                0,
            )

        if inflation_rate > 0 and base_age is not None:
            real_bals = [b / (1 + inflation_rate) ** (age - base_age) for b in balances]
        else:
            real_bals = balances

        for i, bal in enumerate(real_bals):
            b = np.full(n_sims, float(bal))
            alive = np.ones(n_sims, dtype=bool)
            for yr in range(years):
                b -= withdrawals[yr]
                b *= 1 + ret[:, yr]
                alive &= b >= 0
            grid[i, j] = alive.mean()

    return grid


def deterministic_summary(
    assumptions: dict[str, Any], retirement_age: int | None = None
) -> PlanSummary:
    """Summarize deterministic projection results."""
    target_age = retirement_age or assumptions["target_retirement_age"]
    projection = project_portfolio(assumptions, target_age)
    retired_rows = projection.index[projection["retired"]]
    if len(retired_rows) > 0:
        retire_idx = int(retired_rows[0])
        balance_at_retirement = (
            projection.loc[retire_idx - 1, "balance_end"]
            if retire_idx > 0
            else assumptions["current_savings"]
        )
    else:
        balance_at_retirement = projection["balance_end"].iloc[-1]

    depleted = projection.loc[projection["balance_end"] < 0, "age"]
    depletion_age = int(depleted.iloc[0]) if not depleted.empty else None
    earliest, _ = find_earliest_retirement_age(assumptions)
    return PlanSummary(
        target_retirement_age=target_age,
        earliest_retirement_age=earliest,
        balance_at_retirement=float(balance_at_retirement),
        ending_balance=float(projection["balance_end"].iloc[-1]),
        depletion_age=depletion_age,
    )


def monte_carlo_summary(
    assumptions: dict[str, Any],
    retirement_age: int | None = None,
    n_sims: int = 1000,
    seed: int = 42,
    return_paths: bool = False,
) -> dict[str, Any]:
    """Run Monte Carlo and return common summary statistics."""
    target_age = retirement_age or assumptions["target_retirement_age"]
    result = monte_carlo_success(
        assumptions, target_age, n_sims=n_sims, seed=seed, return_paths=return_paths
    )
    if return_paths:
        rate, balances, paths = result
    else:
        rate, balances = result
        paths = None
    return {
        "success_rate": rate,
        "ending_balances": balances,
        "median_ending_balance": float(np.median(balances)),
        "p10_ending_balance": float(np.percentile(balances, 10)),
        "p90_ending_balance": float(np.percentile(balances, 90)),
        "paths": paths,
    }
