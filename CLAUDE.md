# Retirement Planner

A personal, self-contained Jupyter notebook (`retirement_planner.ipynb`) for
projecting retirement savings, finding a sustainable retirement age, and
running Monte Carlo stress tests against market variability.

## Conventions

- **All dollar amounts are in today's dollars (real terms).** Returns,
  expenses, savings, and Social Security figures should all be entered as
  inflation-adjusted (real) values. Do not introduce a separate inflation
  rate unless the whole model is reworked to be nominal.
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
