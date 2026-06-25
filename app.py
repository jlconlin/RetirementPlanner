"""Streamlit retirement planner dashboard."""

from __future__ import annotations

import json
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from retirement_model import (
    DEFAULT_SCENARIO,
    deterministic_summary,
    find_earliest_retirement_age,
    mc_success_grid,
    monte_carlo_summary,
    project_portfolio,
    scenario_to_assumptions,
    scenario_with_defaults,
)


st.set_page_config(
    page_title="Retirement Planner",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


HELP_TEXT = {
    "Current age": "Your age today. Projections start from this age.",
    "Life expectancy": "The age through which the plan must remain solvent. Use a conservative planning age, not a median forecast.",
    "Target retirement age": "The age where contributions stop and portfolio withdrawals begin.",
    "Current savings": "Investable assets today, in thousands of today's dollars. Exclude home equity unless you plan to spend it.",
    "Annual contribution": "Total household annual savings into investment accounts, in thousands of today's dollars.",
    "Contribution growth": "Real growth above inflation. Enter 0 if your nominal savings merely keeps pace with inflation.",
    "Inflation": "Used to convert nominal returns into real returns. Dollar inputs remain in today's purchasing power.",
    "Pre-retirement return": "Expected nominal return while working. The model converts it to real return internally.",
    "Post-retirement return": "Expected nominal return after retirement, usually lower due to a more conservative allocation.",
    "Volatility": "Annual return standard deviation used in Monte Carlo simulations.",
    "Annual expenses": "Gross annual retirement spending before Social Security or pension offsets, in today's dollars.",
    "Spending model": "Flat is most conservative. Three-phase and taper reduce real spending later in retirement.",
    "Social Security": "Monthly benefit in today's dollars for the selected claiming age.",
    "Pension": "Monthly defined-benefit pension in today's dollars, if applicable.",
    "Monte Carlo": "Random return simulations. Deterministic results update instantly; Monte Carlo is cached but still heavier.",
}


def fmt_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:,.2f}M"
    return f"{sign}${value / 1_000:,.0f}k"


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def as_display_table(df: pd.DataFrame) -> pd.DataFrame:
    table = df.copy()
    money_cols = [
        "balance_start",
        "contribution",
        "ss_income",
        "pension_income",
        "withdrawal",
        "growth",
        "balance_end",
    ]
    for col in money_cols:
        table[col] = table[col].map(lambda x: round(x / 1_000, 1))
    return table.rename(
        columns={
            "age": "Age",
            "retired": "Retired",
            "balance_start": "Start balance ($k)",
            "contribution": "Contribution ($k)",
            "ss_income": "Social Security ($k)",
            "pension_income": "Pension ($k)",
            "withdrawal": "Withdrawal ($k)",
            "growth": "Growth ($k)",
            "balance_end": "End balance ($k)",
        }
    )


def load_uploaded_scenario() -> dict[str, Any] | None:
    uploaded = st.sidebar.file_uploader("Load scenario", type="json")
    if uploaded is None:
        return None
    try:
        return json.loads(uploaded.getvalue().decode("utf-8"))
    except json.JSONDecodeError as exc:
        st.sidebar.error(f"Could not read scenario: {exc}")
        return None


def init_scenario() -> dict[str, Any]:
    try:
        scenario = st.session_state.get("scenario")
    except Exception:
        scenario = None
    if scenario is None:
        scenario = scenario_with_defaults()
        try:
            st.session_state["scenario"] = scenario
        except Exception:
            pass
    uploaded = load_uploaded_scenario()
    if uploaded is not None:
        scenario = scenario_with_defaults(uploaded)
        try:
            st.session_state["scenario"] = scenario
        except Exception:
            pass
    return scenario.copy()


def scenario_download(scenario: dict[str, Any]) -> None:
    st.sidebar.download_button(
        "Download scenario",
        data=json.dumps(scenario, indent=2),
        file_name="scenario.json",
        mime="application/json",
        use_container_width=True,
    )


def slider_number(
    label: str,
    min_value: int | float,
    max_value: int | float,
    value: int | float,
    step: int | float = 1,
    *,
    key: str,
    help: str | None = None,
    input_min: int | float | None = None,
    input_max: int | float | None = None,
    allow_above_slider: bool = False,
) -> int | float:
    """Render a slider paired with an exact numeric input."""
    slider_value = min(max(value, min_value), max_value)
    slider_col, input_col = st.columns([0.68, 0.32])
    with slider_col:
        slider_result = st.slider(
            label,
            min_value=min_value,
            max_value=max_value,
            value=slider_value,
            step=step,
            help=help,
            key=f"{key}_slider",
        )
    with input_col:
        input_value = (
            value
            if allow_above_slider and value > max_value
            else slider_result
        )
        input_result = st.number_input(
            "Exact",
            min_value=min_value if input_min is None else input_min,
            max_value=(
                input_max
                if input_max is not None
                else None
                if allow_above_slider
                else max_value
            ),
            value=input_value,
            step=step,
            key=f"{key}_input",
            label_visibility="collapsed",
        )
    return input_result


def build_sidebar(scenario: dict[str, Any]) -> dict[str, Any]:
    st.sidebar.title("Assumptions")
    st.sidebar.caption("All dollar amounts are today's dollars unless noted.")

    scenario_name = st.sidebar.text_input(
        "Scenario name", value=str(scenario.get("name", "Personal plan"))
    )

    with st.sidebar.expander("Household", expanded=True):
        current_age = int(slider_number(
            "Current age",
            18,
            90,
            int(scenario["current_age"]),
            key="current_age",
            help=HELP_TEXT["Current age"],
        ))
        life_expectancy = int(slider_number(
            "Life expectancy",
            max(current_age + 1, 70),
            110,
            max(int(scenario["life_expectancy"]), current_age + 1),
            key="life_expectancy",
            help=HELP_TEXT["Life expectancy"],
        ))
        target_retirement_age = int(slider_number(
            "Target retirement age",
            max(current_age + 1, 40),
            min(life_expectancy, 85),
            min(max(int(scenario["target_retirement_age"]), current_age + 1), life_expectancy),
            key="target_retirement_age",
            help=HELP_TEXT["Target retirement age"],
        ))
        has_spouse = st.checkbox(
            "Include spouse", value=bool(scenario.get("has_spouse", False))
        )
        if has_spouse:
            spouse_age = int(slider_number(
                "Spouse age",
                18,
                90,
                int(scenario.get("spouse_age", 54)),
                key="spouse_age",
            ))
            spouse_life_expectancy = int(slider_number(
                "Spouse life expectancy",
                max(spouse_age + 1, 70),
                110,
                max(int(scenario.get("spouse_life_expectancy", 92)), spouse_age + 1),
                key="spouse_life_expectancy",
            ))
            spouse_retirement_age = int(slider_number(
                "Spouse retirement age",
                max(spouse_age + 1, 40),
                min(spouse_life_expectancy, 85),
                min(
                    max(int(scenario.get("spouse_retirement_age", 63)), spouse_age + 1),
                    spouse_life_expectancy,
                ),
                key="spouse_retirement_age",
            ))
            survivor_spending_pct = float(slider_number(
                "Survivor spending %",
                50.0,
                100.0,
                float(scenario.get("survivor_spending_pct", 70.0)),
                step=5.0,
                key="survivor_spending_pct",
            ))
        else:
            spouse_age = scenario.get("spouse_age", DEFAULT_SCENARIO["spouse_age"])
            spouse_life_expectancy = scenario.get(
                "spouse_life_expectancy", DEFAULT_SCENARIO["spouse_life_expectancy"]
            )
            spouse_retirement_age = scenario.get(
                "spouse_retirement_age", DEFAULT_SCENARIO["spouse_retirement_age"]
            )
            survivor_spending_pct = scenario.get(
                "survivor_spending_pct", DEFAULT_SCENARIO["survivor_spending_pct"]
            )

    with st.sidebar.expander("Savings", expanded=True):
        current_savings = float(slider_number(
            "Current savings ($k)",
            0.0,
            10_000.0,
            float(scenario["current_savings"]),
            step=10.0,
            key="current_savings",
            help=HELP_TEXT["Current savings"],
            input_min=0.0,
            allow_above_slider=True,
        ))
        annual_contribution = float(slider_number(
            "Annual contribution ($k)",
            0.0,
            500.0,
            float(scenario["annual_contribution"]),
            step=1.0,
            key="annual_contribution",
            help=HELP_TEXT["Annual contribution"],
            input_min=0.0,
            allow_above_slider=True,
        ))
        contribution_growth_rate = float(slider_number(
            "Contribution growth (real %)",
            0.0,
            10.0,
            float(scenario["contribution_growth_rate"]),
            step=0.25,
            key="contribution_growth_rate",
            help=HELP_TEXT["Contribution growth"],
        ))

    with st.sidebar.expander("Returns", expanded=True):
        inflation_rate = float(slider_number(
            "Inflation rate (%)",
            0.0,
            10.0,
            float(scenario["inflation_rate"]),
            step=0.25,
            key="inflation_rate",
            help=HELP_TEXT["Inflation"],
        ))
        pre_retirement_return = float(slider_number(
            "Pre-retirement return (nominal %)",
            0.0,
            20.0,
            float(scenario["pre_retirement_return"]),
            step=0.25,
            key="pre_retirement_return",
            help=HELP_TEXT["Pre-retirement return"],
        ))
        post_retirement_return = float(slider_number(
            "Post-retirement return (nominal %)",
            0.0,
            15.0,
            float(scenario["post_retirement_return"]),
            step=0.25,
            key="post_retirement_return",
            help=HELP_TEXT["Post-retirement return"],
        ))
        return_volatility = float(slider_number(
            "Return volatility (%)",
            0.0,
            30.0,
            float(scenario["return_volatility"]),
            step=0.5,
            key="return_volatility",
            help=HELP_TEXT["Volatility"],
        ))

    with st.sidebar.expander("Spending", expanded=True):
        annual_expenses = float(slider_number(
            "Annual expenses ($k)",
            0.0,
            500.0,
            float(scenario["annual_expenses"]),
            step=1.0,
            key="annual_expenses",
            help=HELP_TEXT["Annual expenses"],
            input_min=0.0,
            allow_above_slider=True,
        ))
        spending_model = st.radio(
            "Spending model",
            ["flat", "three_phase", "taper"],
            index=["flat", "three_phase", "taper"].index(
                scenario.get("spending_model", "flat")
            ),
            format_func={
                "flat": "Flat",
                "three_phase": "Three-phase",
                "taper": "Annual taper",
            }.get,
            horizontal=True,
            help=HELP_TEXT["Spending model"],
        )
        slow_go_age = scenario.get("slow_go_age", 75)
        slow_go_pct = scenario.get("slow_go_pct", 80.0)
        no_go_age = scenario.get("no_go_age", 85)
        no_go_pct = scenario.get("no_go_pct", 60.0)
        taper_start_age = scenario.get("taper_start_age", 75)
        taper_rate_pct = scenario.get("taper_rate_pct", 1.5)
        if spending_model == "three_phase":
            slow_go_age = int(slider_number("Slow-go starts", 60, 95, int(slow_go_age), key="slow_go_age"))
            slow_go_pct = float(slider_number("Slow-go spending %", 10.0, 100.0, float(slow_go_pct), step=5.0, key="slow_go_pct"))
            no_go_age = int(slider_number("No-go starts", 65, 100, int(no_go_age), key="no_go_age"))
            no_go_pct = float(slider_number("No-go spending %", 10.0, 100.0, float(no_go_pct), step=5.0, key="no_go_pct"))
        elif spending_model == "taper":
            taper_start_age = int(slider_number("Taper starts", 60, 95, int(taper_start_age), key="taper_start_age"))
            taper_rate_pct = float(slider_number("Taper rate (%/yr)", 0.1, 10.0, float(taper_rate_pct), step=0.1, key="taper_rate_pct"))

    with st.sidebar.expander("Income", expanded=True):
        social_security_monthly = float(slider_number(
            "Social Security monthly ($k)",
            0.0,
            10.0,
            float(scenario["social_security_monthly"]),
            step=0.1,
            key="social_security_monthly",
            help=HELP_TEXT["Social Security"],
            input_min=0.0,
            allow_above_slider=True,
        ))
        social_security_start_age = st.radio(
            "Social Security start age",
            [62, 65, 67, 70],
            index=[62, 65, 67, 70].index(int(scenario["social_security_start_age"])),
            horizontal=True,
        )
        if has_spouse:
            spouse_ss_monthly = float(slider_number(
                "Spouse SS monthly ($k)",
                0.0,
                10.0,
                float(scenario.get("spouse_ss_monthly", 1.5)),
                step=0.1,
                key="spouse_ss_monthly",
                input_min=0.0,
                allow_above_slider=True,
            ))
            spouse_ss_start_age = st.radio(
                "Spouse SS start age",
                [62, 65, 67, 70],
                index=[62, 65, 67, 70].index(
                    int(scenario.get("spouse_ss_start_age", 67))
                ),
                horizontal=True,
            )
        else:
            spouse_ss_monthly = scenario.get(
                "spouse_ss_monthly", DEFAULT_SCENARIO["spouse_ss_monthly"]
            )
            spouse_ss_start_age = scenario.get(
                "spouse_ss_start_age", DEFAULT_SCENARIO["spouse_ss_start_age"]
            )

        has_pension = st.checkbox(
            "Include pension", value=bool(scenario.get("has_pension", False))
        )
        if has_pension:
            pension_monthly = float(slider_number(
                "Pension monthly ($k)",
                0.0,
                20.0,
                float(scenario.get("pension_monthly", 0.0)),
                step=0.1,
                key="pension_monthly",
                help=HELP_TEXT["Pension"],
                input_min=0.0,
                allow_above_slider=True,
            ))
            pension_start_age = int(slider_number(
                "Pension start age",
                40,
                85,
                int(scenario.get("pension_start_age", 60)),
                key="pension_start_age",
            ))
        else:
            pension_monthly = scenario.get("pension_monthly", 0.0)
            pension_start_age = scenario.get("pension_start_age", 60)

    with st.sidebar.expander("Simulation", expanded=False):
        n_sims = st.select_slider(
            "Monte Carlo simulations",
            options=[500, 1000, 2000, 5000],
            value=int(scenario.get("n_sims", 1000)),
            help=HELP_TEXT["Monte Carlo"],
        )
        grid_sims = st.select_slider(
            "Grid simulations per cell",
            options=[100, 250, 500, 1000],
            value=250,
        )

    updated = {
        "name": scenario_name,
        "current_age": current_age,
        "life_expectancy": life_expectancy,
        "target_retirement_age": target_retirement_age,
        "current_savings": current_savings,
        "annual_contribution": annual_contribution,
        "contribution_growth_rate": contribution_growth_rate,
        "inflation_rate": inflation_rate,
        "pre_retirement_return": pre_retirement_return,
        "post_retirement_return": post_retirement_return,
        "return_volatility": return_volatility,
        "annual_expenses": annual_expenses,
        "spending_model": spending_model,
        "slow_go_age": slow_go_age,
        "slow_go_pct": slow_go_pct,
        "no_go_age": no_go_age,
        "no_go_pct": no_go_pct,
        "taper_start_age": taper_start_age,
        "taper_rate_pct": taper_rate_pct,
        "social_security_monthly": social_security_monthly,
        "social_security_start_age": social_security_start_age,
        "has_pension": has_pension,
        "pension_monthly": pension_monthly,
        "pension_start_age": pension_start_age,
        "n_sims": n_sims,
        "grid_sims": grid_sims,
        "has_spouse": has_spouse,
        "spouse_age": spouse_age,
        "spouse_life_expectancy": spouse_life_expectancy,
        "spouse_retirement_age": spouse_retirement_age,
        "survivor_spending_pct": survivor_spending_pct,
        "spouse_ss_monthly": spouse_ss_monthly,
        "spouse_ss_start_age": spouse_ss_start_age,
    }
    try:
        st.session_state["scenario"] = updated
    except Exception:
        pass
    scenario_download(updated)
    return updated


@st.cache_data(show_spinner=False)
def cached_monte_carlo(scenario_json: str, n_sims: int) -> dict[str, Any]:
    scenario = json.loads(scenario_json)
    assumptions = scenario_to_assumptions(scenario)
    return monte_carlo_summary(
        assumptions,
        retirement_age=assumptions["target_retirement_age"],
        n_sims=n_sims,
        return_paths=True,
    )


@st.cache_data(show_spinner=False)
def cached_sweep(scenario_json: str) -> pd.DataFrame:
    scenario = json.loads(scenario_json)
    assumptions = scenario_to_assumptions(scenario)
    start = max(assumptions["current_age"] + 1, 50)
    end = min(assumptions["life_expectancy"], 81)
    rows = []
    for age in range(start, end):
        rate, _ = monte_carlo_summary(
            assumptions, retirement_age=age, n_sims=500
        )["success_rate"], None
        rows.append({"retirement_age": age, "success_rate": rate})
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def cached_grid(scenario_json: str, grid_sims: int) -> tuple[list[int], np.ndarray, np.ndarray]:
    scenario = json.loads(scenario_json)
    assumptions = scenario_to_assumptions(scenario)
    ages = list(
        range(
            max(assumptions["current_age"] + 1, 50),
            min(assumptions["life_expectancy"], 81),
            2,
        )
    )
    low = assumptions["current_savings"] * 0.25
    high = max(assumptions["current_savings"] * 8.0, assumptions["annual_expenses"] * 30)
    balances = np.linspace(low, high, 14)
    grid = mc_success_grid(assumptions, ages, balances, n_sims=grid_sims)
    return ages, balances, grid


def projection_chart(projection: pd.DataFrame, scenario: dict[str, Any]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(projection["age"] + 1, projection["balance_end"] / 1_000, linewidth=2.2)
    ax.axhline(0, color="#b91c1c", linewidth=1)
    ax.axvline(
        scenario["target_retirement_age"],
        color="#525252",
        linestyle="--",
        linewidth=1,
        label=f"Retire at {scenario['target_retirement_age']}",
    )
    if scenario.get("has_spouse"):
        ax.axvline(
            scenario["spouse_retirement_age"],
            color="#2563eb",
            linestyle=":",
            linewidth=1.4,
            label=f"Spouse retires at {scenario['spouse_retirement_age']}",
        )
    ax.set_xlabel("Age")
    ax.set_ylabel("Portfolio balance ($k)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def monte_carlo_chart(paths: np.ndarray, scenario: dict[str, Any], success_rate: float) -> plt.Figure:
    ages = np.arange(scenario["current_age"] + 1, scenario["current_age"] + 1 + paths.shape[1])
    success_mask = (paths >= 0).all(axis=1)
    fig, ax = plt.subplots(figsize=(10, 5))

    rng_vis = np.random.default_rng(0)
    plot_count = min(250, len(paths))
    for idx in rng_vis.choice(len(paths), plot_count, replace=False):
        color = "#dc2626" if not success_mask[idx] else "#2563eb"
        ax.plot(ages, paths[idx] / 1_000, color=color, alpha=0.045, linewidth=0.6)

    p10, p25, p50, p75, p90 = np.percentile(paths, [10, 25, 50, 75, 90], axis=0)
    ax.fill_between(ages, p10 / 1_000, p90 / 1_000, color="#bfdbfe", alpha=0.65, label="10-90th pct")
    ax.fill_between(ages, p25 / 1_000, p75 / 1_000, color="#60a5fa", alpha=0.45, label="25-75th pct")
    ax.plot(ages, p50 / 1_000, color="#1e3a8a", linewidth=2.4, label="Median")
    ax.axhline(0, color="#b91c1c", linewidth=1)
    ax.axvline(scenario["target_retirement_age"], color="#525252", linestyle="--", linewidth=1)
    ax.set_title(f"Monte Carlo paths ({success_rate:.1%} success)")
    ax.set_xlabel("Age")
    ax.set_ylabel("Portfolio balance ($k)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def sweep_chart(sweep: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(sweep["retirement_age"], sweep["success_rate"] * 100, marker="o", linewidth=2)
    ax.axhline(90, color="#15803d", linestyle="--", linewidth=1, label="90%")
    ax.axhline(80, color="#c2410c", linestyle="--", linewidth=1, label="80%")
    ax.set_xlabel("Retirement age")
    ax.set_ylabel("Success rate (%)")
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def grid_chart(ages: list[int], balances: np.ndarray, grid: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5.4))
    cf = ax.contourf(
        np.array(ages),
        balances / 1_000,
        grid * 100,
        levels=np.linspace(0, 100, 21),
        cmap="RdYlGn",
        vmin=0,
        vmax=100,
    )
    fig.colorbar(cf, ax=ax, label="Success rate (%)")
    if len(ages) >= 2 and len(balances) >= 2:
        cs = ax.contour(
            np.array(ages),
            balances / 1_000,
            grid * 100,
            levels=[80, 90],
            colors=["#111827", "#111827"],
            linewidths=1.6,
        )
        ax.clabel(cs, fmt="%d%%", fontsize=9)
    ax.set_xlabel("Retirement age")
    ax.set_ylabel("Starting balance ($k, today's dollars)")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return fig


scenario = build_sidebar(init_scenario())
assumptions = scenario_to_assumptions(scenario)
projection = project_portfolio(assumptions, assumptions["target_retirement_age"])
summary = deterministic_summary(assumptions, assumptions["target_retirement_age"])
scenario_json = json.dumps(scenario, sort_keys=True)

st.title("Retirement Planner")
st.caption("A personal planning dashboard in today's dollars.")

with st.spinner("Running Monte Carlo..."):
    mc = cached_monte_carlo(scenario_json, int(scenario["n_sims"]))

metric_cols = st.columns(5)
metric_cols[0].metric("Target retirement", summary.target_retirement_age)
metric_cols[1].metric(
    "Earliest deterministic",
    "None" if summary.earliest_retirement_age is None else summary.earliest_retirement_age,
)
metric_cols[2].metric("Monte Carlo success", fmt_pct(mc["success_rate"]))
metric_cols[3].metric("Balance at retirement", fmt_money(summary.balance_at_retirement))
metric_cols[4].metric(
    "Depletion",
    "No depletion" if summary.depletion_age is None else f"Age {summary.depletion_age}",
)

if summary.depletion_age is not None:
    st.warning(
        f"Deterministic projection depletes at age {summary.depletion_age}. "
        "Try changing retirement age, spending, savings, or income assumptions."
    )
elif mc["success_rate"] < 0.8:
    st.warning(
        "Monte Carlo success is below 80%. The average path may work, but market "
        "sequence risk is material under these assumptions."
    )
else:
    st.success("The plan survives the deterministic horizon and clears the common 80% Monte Carlo threshold.")

overview_tab, mc_tab, sweep_tab, grid_tab, cashflow_tab, assumptions_tab, help_tab = st.tabs(
    [
        "Overview",
        "Monte Carlo",
        "Retirement Age",
        "Required Balance",
        "Cash Flows",
        "Assumptions",
        "Help",
    ]
)

with overview_tab:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Deterministic Projection")
        st.pyplot(projection_chart(projection, scenario), clear_figure=True)
    with right:
        st.subheader("Key Numbers")
        st.write(f"Ending balance: **{fmt_money(summary.ending_balance)}**")
        st.write(f"Median Monte Carlo ending balance: **{fmt_money(mc['median_ending_balance'])}**")
        st.write(f"10th percentile ending balance: **{fmt_money(mc['p10_ending_balance'])}**")
        st.write(f"90th percentile ending balance: **{fmt_money(mc['p90_ending_balance'])}**")
        if summary.earliest_retirement_age is None:
            st.write("No deterministic retirement age in the tested range remains solvent.")
        else:
            st.write(f"Earliest deterministic retirement age: **{summary.earliest_retirement_age}**")

with mc_tab:
    st.subheader("Monte Carlo Simulation")
    st.pyplot(monte_carlo_chart(mc["paths"], scenario, mc["success_rate"]), clear_figure=True)
    stats = pd.DataFrame(
        [
            ["Success rate", fmt_pct(mc["success_rate"])],
            ["Median ending balance", fmt_money(mc["median_ending_balance"])],
            ["10th percentile ending balance", fmt_money(mc["p10_ending_balance"])],
            ["90th percentile ending balance", fmt_money(mc["p90_ending_balance"])],
        ],
        columns=["Metric", "Value"],
    )
    st.dataframe(stats, hide_index=True, use_container_width=True)

with sweep_tab:
    st.subheader("Success Rate by Retirement Age")
    with st.spinner("Running retirement age sweep..."):
        sweep = cached_sweep(scenario_json)
    if sweep.empty:
        st.info("No retirement ages available in the sweep range.")
    else:
        st.pyplot(sweep_chart(sweep), clear_figure=True)
        st.dataframe(
            sweep.assign(success_rate=lambda df: df["success_rate"].map(lambda x: f"{x:.1%}")),
            hide_index=True,
            use_container_width=True,
        )

with grid_tab:
    st.subheader("Required Balance by Age")
    with st.spinner("Running balance grid..."):
        ages, balances, grid = cached_grid(scenario_json, int(scenario["grid_sims"]))
    if not ages:
        st.info("No retirement ages available for the grid.")
    else:
        st.pyplot(grid_chart(ages, balances, grid), clear_figure=True)
        st.caption("Balances are shown in today's dollars.")

with cashflow_tab:
    st.subheader("Year-by-Year Cash Flows")
    st.dataframe(as_display_table(projection), hide_index=True, use_container_width=True)

with assumptions_tab:
    st.subheader("Current Scenario JSON")
    st.json(scenario)
    st.subheader("Internal Assumptions")
    st.json(
        {
            key: (round(value, 6) if isinstance(value, float) else value)
            for key, value in assumptions.items()
            if key != "spending_params"
        }
    )

with help_tab:
    st.subheader("Input Help")
    selected = st.selectbox("Choose an input", sorted(HELP_TEXT))
    st.info(HELP_TEXT[selected])
    st.markdown(
        """
        **Model reminders**

        - Dollar inputs are in today's dollars.
        - Investment return inputs are nominal percentages and are converted to real returns.
        - Contribution growth is a real growth rate above inflation.
        - Survivor Social Security is simplified and should be checked against SSA estimates for final planning.
        - Monte Carlo uses independent normally distributed returns, so historical sequence tools are still useful cross-checks.
        """
    )
