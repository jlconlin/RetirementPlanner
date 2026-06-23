# Retirement Planner

A personal, self-contained Jupyter notebook (`retirement_planner.ipynb`) for
projecting retirement savings, finding a sustainable retirement age, and
running Monte Carlo stress tests against market variability.

## Conventions

- **Dollar amounts are in today's dollars.** Expenses, savings, and Social
  Security figures are entered in today's purchasing power.
- **Returns are entered as nominal rates** (what you see on a brokerage
  website). The `w_inflation_rate` widget holds the assumed long-run
  inflation rate; `build_assumptions_from_widgets()` converts nominal →
  real via the Fisher equation before passing values to the projection
  functions. All projected balances are displayed in today's dollars.
- **Age is derived from `birth_year`**, not hardcoded. The assumptions cell
  computes `current_age` from `birth_year` and the current date so the
  notebook stays accurate without manual edits each time it's opened.
- **Single source of truth**: the `assumptions` dict near the top of the
  notebook is the only cell meant to be edited for day-to-day use. Inline
  comments document reasonable ranges (returns/volatility by allocation,
  life expectancy, expense rules of thumb, Social Security claiming
  tradeoffs).
- **Structure** (don't reorder without reason):
  1. Assumptions
  2. Deterministic year-by-year projection
  3. Earliest sustainable retirement age finder
  4. Monte Carlo simulation (success rate + outcome distribution)
  5. Success rate vs. retirement age sweep
  6. Notes & caveats / suggested extensions

## Environment notes

- Python 3 with numpy, pandas, matplotlib. No internet access assumed for
  installing new packages — prefer stdlib or these three libraries.
- This is a planning aid, not financial advice. Avoid adding anything that
  resembles personalized investment recommendations.

## Possible future extensions (see notebook's Notes section)

- Per-account modeling (taxable / traditional / Roth) with tax treatment
- Healthcare cost modeling (separate, higher growth rate, pre-Medicare gap)
- Variable/age-dependent spending curves
- Historical bootstrap sampling instead of normal-distribution Monte Carlo
- One-time events (home sale, inheritance, large purchases)
