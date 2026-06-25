# Validating Results Against External Calculators

This notebook uses normally-distributed Monte Carlo simulation to estimate
retirement success rates. Two well-known free calculators — **FIRECalc** and
**cFIREsim** — use a different methodology (historical sequences) that serves
as a useful cross-check. This document explains the differences and walks
through how to set up a comparable scenario in each.

---

## Methodological Differences

| | This notebook | FIRECalc / cFIREsim |
|---|---|---|
| **Return model** | Each year drawn independently from a normal distribution | Actual historical annual returns, used in sequence |
| **Data source** | User-specified mean and volatility | Shiller U.S. market data, ~1871–present |
| **Sequence risk** | Captured probabilistically via many simulations | Captured directly — every historical sequence is tested |
| **Fat tails / crashes** | Underweighted (normal distribution assumption) | Captured — e.g. 1929, 1966, 2000, 2008 sequences appear |
| **Inflation** | User-specified constant rate subtracted from nominal return | Embedded in historical real-return data |
| **Dollar amounts** | Today's dollars (real terms) | Today's dollars (real terms) |

### Why historical sequences matter

In a normal-distribution simulation, each year's return is drawn
independently. In reality, bad years cluster: a bear market that starts the
year you retire can permanently impair a portfolio even if average long-run
returns are fine. This is called **sequence-of-returns risk**.

Historical-sequence calculators expose your plan to every bad run that
actually occurred — the 1966 retiree who faced 15 years of stagflation, the
2000 retiree who hit two crashes in a decade. Normal-distribution Monte Carlo
can reproduce *some* bad sequences by chance, but it does not guarantee that
the historically worst sequences appear with the right frequency.

**Practical implication:** For stock-heavy portfolios, historical-sequence
calculators typically report *lower* success rates than normal-distribution
Monte Carlo. If your notebook shows a higher success rate than FIRECalc or
cFIREsim, that is expected and does not indicate a bug — it reflects the
methodology difference. A large gap (more than ~15 percentage points) is
worth investigating.

---

## FIRECalc

**URL:** https://firecalc.com

FIRECalc is intentionally simple. It tests your plan against every historical
30-year (or custom-length) period in the Shiller dataset and reports how many
survived.

### Setting up a comparable scenario

1. **Spending:** Enter your **annual expenses minus Social Security income**
   (FIRECalc calls this "spending" and treats it as the net portfolio
   withdrawal). In today's dollars.
2. **Portfolio:** Enter your current savings in dollars.
3. **Years:** Set to `life_expectancy − current_age`.
4. Leave the default portfolio allocation (75% stocks / 25% bonds) unless
   you want to match your own allocation — FIRECalc lets you adjust this
   under the "Your Portfolio" tab.
5. Under **"Other Income/Spending"** you can add Social Security as income
   starting at your claiming age. This is cleaner than netting it out of
   spending in step 1 if your SS start age differs from retirement age.
6. Run and note the **success percentage**.

### Limitations of FIRECalc for comparison

- No spouse modeling (single portfolio only)
- Spending is constant in real terms (matches this notebook's assumption)
- Cannot model pre-retirement contribution phase — start from your projected
  balance *at retirement*, not today's balance

---

## cFIREsim

**URL:** https://cfiresim.com

cFIREsim uses the same Shiller historical dataset but offers far more inputs,
making it the closer comparison to this notebook.

### Setting up a comparable scenario

Work through the cFIREsim input panels in order:

**Simulation Settings**
- Start year: current calendar year
- End year: `current_year + (life_expectancy − current_age)`
- Portfolio: your current savings

**Spending**
- Annual spending: your `annual_expenses` in today's dollars
- Spending model: *Inflation-adjusted* (matches this notebook)

**Income**
- Add a Social Security entry: set the annual amount
  (`social_security_monthly × 12`) and the start year
  (`current_year + (social_security_start_age − current_age)`)
- If modeling a spouse, add a second SS entry for the spouse

**Contributions** *(if comparing pre-retirement phase)*
- Add an annual contribution entry with your `annual_contribution` amount,
  ending in the year you retire

**Portfolio**
- Set stock/bond allocation to match your assumptions
- cFIREsim uses historical U.S. stock and bond returns, so the implied real
  return will vary by period — you cannot directly set a mean return

Run the simulation and note the **success rate** (percentage of historical
cycles where portfolio survived to the end year).

### Limitations of cFIREsim for comparison

- Spouse modeling is approximate; this notebook includes a simplified survivor
  benefit rule, but cFIREsim generally requires separate income entries
- Historical data is U.S.-centric; international diversification is not
  separately modeled
- The implied average real return from historical data (~5–7% for stocks,
  ~1–2% for bonds) may differ from your assumptions in this notebook

---

## Interpreting the Comparison

### What to expect

| Scenario | Typical relationship |
|---|---|
| Stock-heavy, long horizon | cFIREsim/FIRECalc success rate **lower** than this notebook |
| Bond-heavy, short horizon | Results closer together |
| High withdrawal rate (>4%) | Larger divergence — sequence risk matters more |
| Low withdrawal rate (<3%) | Results often similar; plan is robust under both methods |

### Green flags (models roughly agree)

- Success rates within ~10 percentage points of each other
- Both show the same "cliff" age — the retirement age where success rate
  drops sharply — within a year or two
- Earliest sustainable retirement age from this notebook falls within the
  range that cFIREsim shows ≥80% success

### Yellow flags (worth investigating)

- This notebook shows >15 percentage points higher success than cFIREsim
  with the same inputs — your plan may be more fragile than it appears
- This notebook shows *lower* success than cFIREsim — check that you have
  entered real (inflation-adjusted) returns, not nominal, in the
  `pre_retirement_return` / `post_retirement_return` fields

  > **Note:** As of the current version, this notebook accepts **nominal**
  > returns and subtracts inflation internally. If you previously saved a
  > scenario with real returns entered directly, reload it and verify the
  > values look right after the switch.

### Red flags (model likely has an error)

- Success rates differ by more than 25–30 percentage points with identical
  inputs — recheck that spending, portfolio, SS income, and horizon are
  truly equivalent between the tools

---

## Quick Sanity Checks (No External Tool Required)

Before comparing to external calculators, verify the notebook's internal
logic with these manual checks:

**1. Zero-return baseline**
Set `pre_retirement_return` and `post_retirement_return` both equal to the
inflation rate (so real return = 0%). The deterministic projection should show
the portfolio declining by exactly `annual_expenses − ss_income − pension` per
year in retirement. If it doesn't, there is a bug.

**2. Infinite-return baseline**
Set returns very high (e.g. 20% nominal). The portfolio should grow rapidly
and the earliest retirement age should equal `current_age + 1`. If not,
check the contribution/withdrawal logic.

**3. Conversion check**
The stats panel displays:
```
Returns:  pre-ret X.X% nominal → Y.YY% real  (inflation Z.Z%)
```
Verify manually: `(1 + X/100) / (1 + Z/100) − 1 = Y`. For example,
10% nominal at 2.5% inflation → `(1.10 / 1.025) − 1 = 0.0732 = 7.32%`.
