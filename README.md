# Retirement Planner

A personal retirement planning dashboard. Adjust assumptions with sliders,
review deterministic and Monte Carlo results, inspect retirement-age sweeps,
and save or load scenario JSON files.

[![Open App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://retirementplanner.conlin.io)

---

## Features

- **Streamlit dashboard** — grouped assumptions, headline metrics, tabbed
  results, scenario download/upload, contextual input help, and optional local
  AI help
- **Deterministic projection** — year-by-year portfolio balance under constant
  assumed returns, updating live as you adjust inputs
- **Earliest retirement age** — finds the youngest age at which your portfolio
  survives to your life expectancy under average conditions
- **Monte Carlo simulation** — randomised return sequences to estimate the
  probability your plan survives market variability
- **Success rate sweep** — plots success rate across a range of retirement ages
- **Balance &#215; age heatmap** — shows the portfolio balance you need at each
  retirement age to hit a given success rate, in today's dollars
- **Methodology tab** — renders the methodology notes from `METHODOLOGY.md` inside the
  app
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
[**METHODOLOGY.md**](METHODOLOGY.md).

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
AI_HELP_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

Other models can be found in the Ollama model library:
<https://ollama.com/library>

## Deploying / sharing

The app is designed to run as a Streamlit app with `app.py` as the entry point.
To publish it on Streamlit Community Cloud, connect the GitHub repository and
choose:

```
app.py
```

as the main file. Streamlit Community Cloud handles the Python environment from
`requirements.txt`.

Optional local AI help uses Ollama. On a hosted Streamlit deployment, AI help
is hidden by default because local Ollama is not reachable from the hosted app.
Set `AI_HELP_ENABLED=false` explicitly to hide it on any host. Set
`AI_HELP_ENABLED=true` only if `OLLAMA_BASE_URL` points to an Ollama service
reachable from the deployed app.

For hosts that require an explicit start command and provide a `$PORT`
environment variable, use:

```
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## Testing

```
pytest
```

The tests cover unit conversion, deterministic projections, contribution
growth, spending curves, survivor Social Security behavior, Monte Carlo
baselines, success grids, and summary calculations.

## Disclaimer

This is a planning aid, not financial advice. The model makes significant
simplifications — no taxes, no per-account modeling, constant real spending,
normal-distribution returns. See [METHODOLOGY.md](METHODOLOGY.md) for a full discussion
of limitations and suggested extensions.

## License

MIT — see [LICENSE](LICENSE).
