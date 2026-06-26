# Retirement Planner

A personal retirement planning dashboard. Adjust assumptions with sliders,
review deterministic and Monte Carlo results, inspect retirement-age sweeps,
and save or load scenario JSON files.

[![Launch on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jlconlin/RetirementPlanner/HEAD?urlpath=voila%2Frender%2Fretirement_planner.ipynb)

---

## Features

- **Streamlit dashboard** — grouped assumptions, headline metrics, tabbed
  results, scenario download/upload, and contextual input help
- **Deterministic projection** — year-by-year portfolio balance under constant
  assumed returns, updating live as you adjust inputs
- **Earliest retirement age** — finds the youngest age at which your portfolio
  survives to your life expectancy under average conditions
- **Monte Carlo simulation** — randomised return sequences to estimate the
  probability your plan survives market variability
- **Success rate sweep** — plots success rate across a range of retirement ages
- **Balance &#215; age heatmap** — shows the portfolio balance you need at each
  retirement age to hit a given success rate, in today's dollars
- **Tested calculation engine** — core math lives in `retirement_model.py` and
  is covered by regression tests

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

**Streamlit** (recommended):
```
pip install -r requirements.txt
streamlit run app.py
```

### Optional local AI help

The Help tab can answer questions with [Ollama](https://ollama.com), using a
local model instead of an external chat service. Ollama is optional; the
planner still runs without it, but AI answers are unavailable until Ollama is
installed and running.

1. Install Ollama from the official download page:
   <https://ollama.com/download>

2. Pull a small general-purpose model:
   ```
   ollama pull llama3.2:3b
   ```

3. Confirm the model works:
   ```
   ollama run llama3.2:3b
   ```

4. Leave Ollama running in the background, then start the planner:
   ```
   streamlit run app.py
   ```

The default local Ollama API URL is `http://localhost:11434`. These
environment variables control the integration:

```
AI_HELP_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

Other models can be found in the Ollama model library:
<https://ollama.com/library>

**Jupyter Lab** (editable, code visible):
```
pip install -r requirements.txt
jupyter lab retirement_planner.ipynb
```

**Voilà** (legacy notebook dashboard):
```
pip install -r requirements.txt
voila retirement_planner.ipynb
```

## Testing

```
pytest
```

The tests cover unit conversion, deterministic projections, contribution
growth, spending curves, survivor Social Security behavior, Monte Carlo
baselines, success grids, and summary calculations.

## Running on Binder / iPad

Click the **Launch on Binder** badge above to run the older Voilà notebook
dashboard. The Streamlit app is now the primary local interface.

## Disclaimer

This is a planning aid, not financial advice. The model makes significant
simplifications — no taxes, no per-account modeling, constant real spending,
normal-distribution returns. See [THEORY.md](THEORY.md) for a full discussion
of limitations and suggested extensions.

## License

MIT — see [LICENSE](LICENSE).
