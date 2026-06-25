# Retirement Planner

A self-contained, interactive retirement planning notebook. Adjust your
assumptions in a live sidebar and instantly see how they affect your projected
portfolio balance, earliest retirement age, and Monte Carlo success rate.

[![Launch on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jlconlin/RetirementPlanner/HEAD?urlpath=voila%2Frender%2Fretirement_planner.ipynb)

---

## Features

- **Deterministic projection** — year-by-year portfolio balance under constant
  assumed returns, updating live as you adjust inputs
- **Earliest retirement age** — finds the youngest age at which your portfolio
  survives to your life expectancy under average conditions
- **Monte Carlo simulation** — randomised return sequences to estimate the
  probability your plan survives market variability
- **Success rate sweep** — plots success rate across a range of retirement ages
- **Balance &#215; age heatmap** — shows the portfolio balance you need at each
  retirement age to hit a given success rate, in today's dollars

## Modeling choices

**Everything is in today's dollars (real terms).** Enter expenses, savings,
contributions, and Social Security in today's purchasing power. Contribution
growth is a real growth rate above inflation. Enter rates of return as
*nominal* values — the model converts them to real using your specified
inflation rate via `(1 + nominal) / (1 + inflation) - 1`.

This keeps every dollar amount intuitive: "&#36;60,000/year expenses" always
means &#36;60,000 of today's buying power, no matter how far in the future.

For the full mathematical derivations, justification of every modeling choice,
discussion of limitations, and citations to the academic literature, see
[**THEORY.md**](THEORY.md).

## Running locally

**Jupyter Lab** (editable, code visible):
```
pip install -r requirements.txt
jupyter lab retirement_planner.ipynb
```

**Voilà** (clean dashboard, code hidden):
```
pip install -r requirements.txt
voila retirement_planner.ipynb
```

## Running on Binder / iPad

Click the **Launch on Binder** badge above. Binder builds a container and
serves the notebook as a Voilà dashboard — no local installation required,
works in any browser including iPad Safari. Cold starts take 1–2 minutes if
the image isn't cached.

## Disclaimer

This is a planning aid, not financial advice. The model makes significant
simplifications — no taxes, no per-account modeling, constant real spending,
normal-distribution returns. See [THEORY.md](THEORY.md) for a full discussion
of limitations and suggested extensions.

## License

MIT — see [LICENSE](LICENSE).
