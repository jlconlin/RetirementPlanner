# Retirement Planner — Theory & Methodology

This document describes the mathematical foundations of the retirement planner, justifies the modeling choices made, and provides references to the academic and professional literature that supports them. It also records the limitations baked into the model and suggests directions for future extension.

---

## Table of Contents

1. [Input Parameter Reference](#1-input-parameter-reference)
2. [Modeling in Real (Inflation-Adjusted) Terms](#2-modeling-in-real-inflation-adjusted-terms)
3. [The Accumulation Phase](#3-the-accumulation-phase)
4. [The Retirement and Drawdown Phase](#4-the-retirement-and-drawdown-phase)
5. [Income Offsets: Social Security and Pensions](#5-income-offsets-social-security-and-pensions)
6. [Deterministic vs. Stochastic Modeling](#6-deterministic-vs-stochastic-modeling)
7. [Monte Carlo Simulation](#7-monte-carlo-simulation)
8. [Sequence-of-Returns Risk](#8-sequence-of-returns-risk)
9. [Safe Withdrawal Rates and the 4% Rule](#9-safe-withdrawal-rates-and-the-4-rule)
10. [The Balance × Age Success-Rate Grid](#10-the-balance--age-success-rate-grid)
11. [Limitations and Simplifications](#11-limitations-and-simplifications)
12. [Suggested Extensions](#12-suggested-extensions)
13. [References](#13-references)
14. [Acknowledgements](#14-acknowledgements)

---

## 1. Input Parameter Reference

This section describes every input parameter in the dashboard, gives recommended ranges, and explains how to calibrate each one to your situation. All dollar figures are in **today's dollars** (real terms); all return and growth rates are entered as **nominal** percentages.

### Quick Reference

| Parameter | Default | Typical Range | Section |
|---|---|---|---|
| Current age | 56 | 20–75 | 1.1 |
| Target retirement age | 65 | 50–75 | 1.1 |
| Life expectancy | 90 | 80–100 | 1.1 |
| Current savings ($k) | 250 | 0–10,000+ | 1.2 |
| Annual contribution ($k) | 15 | 0–150 | 1.2 |
| Contribution growth (%) | 2.0 | 0–5 | 1.2 |
| Inflation (%) | 2.5 | 2.0–4.0 | 1.3 |
| Pre-ret. nominal return (%) | 7.0 | 5–12 | 1.3 |
| Post-ret. nominal return (%) | 5.0 | 3–8 | 1.3 |
| Return volatility σ (%) | 12.0 | 5–20 | 1.3 |
| Annual expenses ($k) | 60 | 20–250 | 1.4 |
| SS monthly ($k) | 1.8 | 0–4.5 | 1.4 |
| SS start age | 67 | 62–70 | 1.4 |
| Pension monthly ($k) | 0 | 0–10+ | 1.4 |

---

### 1.1 Personal Timeline

**Current age**
Range: 18–90. Your age right now. This sets the starting point of the simulation; all projections run from current age to life expectancy.

**Target retirement age**
Range: 40–80. The age at which you plan to stop making contributions and begin drawing from the portfolio. The deterministic projection marks this age with a vertical dashed line. The Monte Carlo sweep shows how success rate varies as this age changes.

Conventional retirement ages and their implications:

| Age | Significance |
|---|---|
| 55 | Earliest penalty-free 401(k) access under "Rule of 55" |
| 59½ | Penalty-free IRA and 401(k) withdrawals begin |
| 62 | Earliest Social Security claiming age |
| 65 | Medicare eligibility begins |
| 67 | Full Retirement Age (FRA) for those born 1960+ |
| 70 | Maximum Social Security benefit (8%/year delayed credit) |

**Life expectancy**
Range: 70–110. The age to which your portfolio must last. Use a conservative (longer) estimate rather than a median forecast: running out of money at 95 is catastrophic, while dying with a surplus is not.

| Planning scenario | Suggested value |
|---|---|
| Median US male life expectancy at 65 | 84 |
| Median US female life expectancy at 65 | 87 |
| 90th-percentile longevity (top 10% live past…) | 95–99 |
| Couples: probability at least one survives to 90 | ~50% |
| Conservative individual planning target | 90–95 |

Source: Social Security Administration actuarial life tables [7].

---

### 1.2 Savings and Contributions

**Current savings ($k)**
The combined value of all investable assets today — 401(k), IRA, Roth IRA, taxable brokerage accounts, etc. — expressed in thousands of dollars. Do not include home equity, vehicles, or illiquid assets unless you plan to convert them to investable assets before retirement.

**Annual contribution ($k)**
The total amount added to the portfolio each year across all accounts, in thousands. Include both your own contributions and any employer match. If contributions vary year to year, use your best estimate of the near-term average.

2025 contribution limits (approximate):

| Account type | Annual limit |
|---|---|
| 401(k) / 403(b) employee contribution | $23,500 |
| 401(k) catch-up (age 50–59, 64+) | +$7,500 |
| 401(k) catch-up (age 60–63, SECURE 2.0) | +$11,250 |
| IRA (traditional or Roth) | $7,000 |
| IRA catch-up (age 50+) | +$1,000 |

**Contribution growth (%)**
The annual nominal rate at which your contribution grows. A value of 2% means annual savings increase 2% per year in nominal terms; at 2.5% inflation this represents roughly −0.5% real growth (essentially flat).

| Scenario | Suggested value |
|---|---|
| Fixed dollar amount year over year | 0% |
| Savings grow with inflation only | 2–3% (match your inflation assumption) |
| Modest salary growth with rising savings rate | 2–4% |
| Aggressive career growth / rapidly increasing savings | 4–6% |

---

### 1.3 Returns and Inflation

**Inflation (%)**
The expected long-run annual rate of price-level increase. This parameter converts nominal returns to real returns via the Fisher equation (Section 2). It does **not** directly inflate any dollar amounts in the model — all dollar inputs remain in today's purchasing power.

| Scenario | Suggested value |
|---|---|
| US Federal Reserve long-run target | 2.0% |
| US historical average (1990–2024, CPI) | ~2.8% |
| Conservative / elevated-inflation planning | 3.0–4.0% |

**Pre-retirement nominal return (%)**
The expected annual nominal return on your portfolio during the accumulation phase. Enter the figure quoted by your brokerage or index fund provider — not an inflation-adjusted number.

The appropriate value depends on your asset allocation:

| Asset allocation | Historical nominal return (approx., 1926–2023) |
|---|---|
| 100% US large-cap equities | 10–11% |
| 80% equities / 20% bonds | 9–10% |
| 60% equities / 40% bonds | 8–9% |
| 40% equities / 60% bonds | 6–8% |
| 100% intermediate bonds | 4–6% |

Source: Ibbotson/Morningstar SBBI data [5]. Forward-looking estimates from Vanguard and other providers tend to be 0.5–1.5% lower, reflecting current valuations [6]. The default of 7% is a deliberately conservative forward-looking estimate for an equity-heavy pre-retirement portfolio.

**Post-retirement nominal return (%)**
The expected annual nominal return after retirement. Most retirees shift toward a more conservative allocation to reduce sequence-of-returns risk (Section 8), so this value is typically lower than the pre-retirement return.

| Post-retirement allocation | Historical nominal return (approx.) |
|---|---|
| 80% equities / 20% bonds | 9–10% |
| 60% equities / 40% bonds | 8–9% |
| 40% equities / 60% bonds | 6–8% |
| 20% equities / 80% bonds | 5–7% |

A 60/40 balanced portfolio has historically returned roughly 8–9% nominally. The default of 5% is conservative, reflecting a moderate-to-conservative allocation and lower forward-looking return expectations.

**Return volatility σ (%)**
The annualised standard deviation of portfolio returns. This controls the spread of the Monte Carlo simulation: higher σ produces more variation in outcomes, increasing the probability of both very good and very bad results. Section 7 provides a detailed mathematical treatment; the calibration table is reproduced here for convenience:

| Asset class / allocation | Approximate σ |
|---|---|
| 100% US equities | 15–20% |
| 70% equities / 30% bonds | 11–14% |
| 50% equities / 50% bonds | 8–11% |
| 100% bonds (intermediate) | 5–8% |

The default σ = 12% corresponds roughly to a 60–70% equity portfolio. A more conservative post-retirement portfolio might use σ = 8–10%.

With σ = 12% and a 4.4% real mean return, approximately 68% of simulated annual returns fall between −7.6% and +16.4%, and approximately 95% fall between −19.6% and +28.4%.

---

### 1.4 Spending and Income

**Annual expenses ($k)**
Total annual living costs in today's purchasing power, in thousands. This is the gross spending target — the total amount needed to cover all living expenses regardless of income source. Social Security and pension income reduce the required portfolio withdrawal (see Section 4), but the expense figure itself should reflect your actual anticipated lifestyle cost.

Rules of thumb and benchmarks:

| Guideline | Typical value |
|---|---|
| Standard "replacement rate" target | 70–80% of pre-retirement gross income |
| 4% rule implied portfolio size | 25× annual expenses |
| Median US household spending in retirement (BLS, 2023) | ~$52,000/yr |
| Include: healthcare, travel, housing, food, taxes on withdrawals | — |

Consider that expenses in early "go-go" retirement years often exceed later years, and that healthcare costs tend to rise substantially after 75.

**Social Security monthly ($k)**
Your expected monthly Social Security retirement benefit for the claiming age you select, in thousands of today's dollars. The most reliable source is your personalised estimate at [ssa.gov/myaccount](https://ssa.gov/myaccount).

Approximate monthly benefit ranges at Full Retirement Age (age 67), in 2024 dollars:

| Career earnings level | Approx. monthly benefit at FRA |
|---|---|
| Low earner (~$30k/yr average) | $0.8–1.2k |
| Average earner (~$60k/yr average) | $1.5–2.2k |
| High earner (~$120k/yr average) | $2.5–3.5k |
| Maximum benefit (2024) | ~$3.8k |

**Social Security start age**
The age at which you begin claiming Social Security. Benefits are permanently adjusted based on when you claim relative to your Full Retirement Age (FRA):

| Claiming age | Effect vs. FRA (born 1960+) |
|---|---|
| 62 (earliest possible) | −25 to −30% |
| 65 | −13% |
| 67 (Full Retirement Age) | 100% of PIA (no adjustment) |
| 70 (latest) | +24% (+8%/year delay credit after FRA) |

The break-even age for delaying from 67 to 70 is approximately 82–83: if you live past that age, delaying produces higher lifetime benefits [8]. For conservative (long-horizon) planning, age 67 or 70 is typically preferred. Enter the benefit amount in the widget that corresponds to your chosen claiming age — the ssa.gov estimate tool shows your benefit at each claiming age.

**Pension monthly ($k)**
If you have a defined-benefit pension, enter the expected monthly benefit in today's dollars (thousands) and the age at which it begins. Toggle the pension on with the "Has pension" button. The benefit is treated symmetrically with Social Security: it reduces the net withdrawal from the portfolio beginning at the specified start age.

---

## 2. Modeling in Real (Inflation-Adjusted) Terms

All quantities in this model — portfolio balances, contributions, expenses, Social Security benefits — are expressed in **today's dollars** (real terms). This is a deliberate design choice that significantly simplifies the model while keeping every number intuitive.

### The Fisher Equation

The relationship between nominal returns, real returns, and inflation is given by the **Fisher equation** [1]:

$$1 + r_{\text{real}} = \frac{1 + r_{\text{nominal}}}{1 + r_{\text{inflation}}}$$

or equivalently:

$$r_{\text{real}} = \frac{1 + r_{\text{nominal}}}{1 + r_{\text{inflation}}} - 1$$

where:

- $r_{\text{nominal}}$ is the **nominal rate of return** — the raw percentage gain on an investment as reported by a brokerage or index fund, before any adjustment for inflation. For example, if a portfolio grows from $100,000 to $107,000 in a year, $r_{\text{nominal}} = 0.07$ (7%).

- $r_{\text{inflation}}$ is the **inflation rate** — the annual rate at which the general price level rises, eroding purchasing power. In the United States this is typically measured by the Consumer Price Index (CPI). A value of $r_{\text{inflation}} = 0.025$ represents 2.5% annual inflation.

- $r_{\text{real}}$ is the **real rate of return** — the inflation-adjusted return, representing the actual increase in purchasing power. If a portfolio earns 7% nominally while inflation runs at 2.5%, the real return is $(1.07 / 1.025) - 1 \approx 4.39\%$, meaning the portfolio's purchasing power grew by about 4.39%.

For small values of $r$, this is well approximated by the simpler linear form:

$$r_{\text{real}} \approx r_{\text{nominal}} - r_{\text{inflation}}$$

The model accepts **nominal** return inputs from the user (because these are the figures most commonly quoted by brokerages and financial media) and converts them to real returns internally using the exact Fisher formula before any simulation.

### Why Real Terms?

A model running in **nominal terms** must track inflation separately and apply it to every future cash flow — expenses, Social Security benefits, and contributions all need to be inflated year by year. The resulting numbers (e.g., "$312,000/year expenses in 2055") are difficult to reason about.

A model running in **real terms** avoids this entirely. Every number retains its present-day purchasing power, regardless of when it occurs in the future. A projected balance of $2,000,000 means $2,000,000 of today's buying power. Annual expenses of $60,000 means what $60,000 buys today — always.

This approach is standard in long-horizon financial planning [2, 3] and is consistent with how Social Security Administration benefit estimates are reported (in today's dollars, using the "wage-indexed" methodology).

The **one exception** in this model is the Balance × Age success-rate grid (Section 10), which displays the Y-axis in *nominal* dollars so that users can compare directly to their brokerage account statements.

---

## 3. The Accumulation Phase

During the working years (age < retirement age), the portfolio grows through investment returns and regular contributions.

### Portfolio Dynamics

Let $B_t$ denote the portfolio balance at the **end** of year $t$ (i.e., at age $t + 1$), $C_t$ the contribution made during year $t$, and $r_{\text{pre}}$ the real annual return during the accumulation phase.

$$B_t = (B_{t-1} + C_t)(1 + r_{\text{pre}})$$

where $B_0 = B_{\text{initial}}$ is the starting portfolio value (current savings).

This formulation applies the contribution at the **beginning** of the year and then compounds the entire balance for the year — a conservative approximation relative to mid-year contributions.

### Contribution Growth

Contributions are assumed to grow at a constant real annual rate $g$ (reflecting expected real wage growth and increasing savings rates):

$$C_t = C_0 \cdot (1 + g)^t$$

A typical value for $g$ is 1–3%, reflecting long-run real wage growth in the United States, which has averaged approximately 1.5–2% per year historically [4].

### Pre-Retirement Return Assumption

The model uses a single blended pre-retirement real return $r_{\text{pre}}$. Historically, a diversified equity portfolio (e.g., a broad US index fund) has returned approximately 10% per year in nominal terms [5], corresponding to roughly 7% real at 3% inflation, or 7.5% real at 2.5% inflation. A blended portfolio with bonds would be lower. The appropriate value depends heavily on the user's asset allocation; the model exposes this as a user input rather than hard-coding an assumption.

---

## 4. The Retirement and Drawdown Phase

Once retired (age ≥ retirement age), contributions cease and the portfolio funds living expenses.

### Net Withdrawal

The annual net withdrawal $W_t$ is the shortfall between desired spending and income from other sources:

$$W_t = \max(E - SS_t - P_t, \; 0)$$

where:
- $E$ is the annual real expense target (constant in real terms)
- $SS_t$ is Social Security income in year $t$ (zero before claiming age)
- $P_t$ is pension income in year $t$ (zero before pension start age)

The $\max(\cdot, 0)$ ensures that if Social Security and pension income exceed desired spending, the portfolio is not drawn upon (excess income is implicitly saved or spent, but the model does not grow the portfolio with it).

### Portfolio Dynamics in Retirement

$$B_t = (B_{t-1} - W_t)(1 + r_{\text{post}})$$

The withdrawal is taken at the **beginning** of the year and the remaining balance earns the post-retirement return $r_{\text{post}}$ for the year.

### Post-Retirement Return Assumption

Retirees typically shift toward a more conservative asset allocation — increasing bond exposure to reduce sequence-of-returns risk (see Section 8). This lower expected return is captured by $r_{\text{post}} < r_{\text{pre}}$. A common target allocation for a 65-year-old might be 50–60% equities / 40–50% bonds, historically returning around 5–7% nominal, or 2.5–4.5% real at 2.5% inflation [5, 6].

---

## 5. Income Offsets: Social Security and Pensions

### Social Security

Social Security retirement benefits are a function of the recipient's earnings history and claiming age. The Social Security Administration computes a **Primary Insurance Amount** (PIA) based on the highest 35 years of wage-indexed earnings. The actual monthly benefit then depends on when the recipient claims relative to their **Full Retirement Age** (FRA), which is 67 for anyone born in 1960 or later [7]:

| Claiming age | Effect on benefit |
|---|---|
| 62 (earliest) | Reduced ~25–30% vs. FRA |
| 67 (FRA) | 100% of PIA |
| 70 (latest) | Increased ~24% vs. FRA (8%/year delayed credit) |

The break-even age for delayed claiming (67 vs. 70) is approximately 82–83, meaning those who expect to live past that age generally benefit from delaying [8]. The model takes the monthly benefit as a user input for the chosen claiming age; the Social Security Administration provides personalised estimates at [ssa.gov/myaccount](https://ssa.gov/myaccount).

All Social Security amounts in the model are in **today's dollars**. In reality, benefits are adjusted annually by the **Cost-of-Living Adjustment** (COLA), which approximately tracks CPI-W. In a real-terms model, this adjustment is implicit: a constant real benefit is equivalent to a CPI-adjusted nominal benefit.

### Pension Income

Pension income is treated symmetrically with Social Security: a constant real annual amount (monthly benefit × 12) is subtracted from the required withdrawal beginning at a user-specified start age. Users without a pension set this to zero.

---

## 6. Deterministic vs. Stochastic Modeling

The model provides both a **deterministic** projection (Sections 3–5) and a **Monte Carlo** simulation (Section 7). They serve different purposes.

The deterministic model uses constant assumed returns and answers: *"Does my plan work under average conditions?"*

The Monte Carlo model uses randomised return sequences and answers: *"How often does my plan survive across the range of markets I might actually encounter?"*

Neither is sufficient alone. The deterministic model is fast, intuitive, and useful for exploring how parameters affect the plan. The stochastic model is essential for understanding risk, because retirement outcomes are dominated not by average returns but by the **order** in which returns arrive — a phenomenon called sequence-of-returns risk (Section 8).

---

## 7. Monte Carlo Simulation

### Return Model

In each simulation, the annual real return in year $t$ is drawn independently from a normal distribution:

$$r_t \sim \mathcal{N}(\mu, \sigma^2)$$

where:
- $\mu = r_{\text{pre}}$ or $r_{\text{post}}$ (depending on whether the person is retired in year $t$)
- $\sigma$ is the **annualised return volatility** (standard deviation of annual returns), a user input

#### What does $\sigma$ mean in practice?

Under a normal distribution, approximately 68% of annual returns will fall within one standard deviation of the mean ($\mu \pm \sigma$), and approximately 95% will fall within two standard deviations ($\mu \pm 2\sigma$).

With $\sigma = 0.12$ (12%) and, say, $\mu = 0.044$ (4.4% real return):

| Probability | Annual return range |
|---|---|
| ~68% of years | −7.6% to +16.4% |
| ~95% of years | −19.6% to +28.4% |
| ~2.5% of years | worse than −19.6% |
| ~2.5% of years | better than +28.4% |

In plain terms: with $\sigma = 0.12$, roughly one year in six will see the portfolio lose more than 7.6% in real terms, and roughly one year in forty will lose more than 19.6%. This is broadly consistent with the historical behaviour of a diversified equity-heavy portfolio [5].

**Calibrating $\sigma$ to your asset allocation:**

Historical annualised volatility (nominal, which is close to real) has been approximately [5]:

| Asset class / allocation | Approximate $\sigma$ |
|---|---|
| 100% US equities | 15–20% |
| 70% equities / 30% bonds | 11–14% |
| 50% equities / 50% bonds | 8–11% |
| 100% bonds (intermediate) | 5–8% |

The default value of 12% in this model corresponds roughly to a 60–70% equity portfolio — a common pre-retirement allocation. A more conservative post-retirement allocation might use 8–10%.

The normal distribution is the standard assumption in academic finance dating to Markowitz's foundational portfolio theory paper [9], and it provides a tractable analytical framework. The model uses NumPy's default pseudorandom number generator (PCG64), seeded for reproducibility.

### Success Rate

After running $N$ independent simulations, the success rate is:

$$\text{Success Rate} = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}\!\left[\min_{t \in [t_0, T]} B_t^{(i)} \geq 0\right]$$

where $\mathbf{1}[\cdot]$ is the indicator function, $t_0$ is the retirement year, and $T$ is the life expectancy year. A simulation "succeeds" if the portfolio never reaches zero over the entire retirement horizon.

### Choosing $N$

The standard error of a proportion estimated from $N$ Bernoulli trials is $\sqrt{p(1-p)/N}$. For a success rate near 85%:

| $N$ | Standard error |
|---|---|
| 500 | ±1.6% |
| 1,000 | ±1.1% |
| 2,000 | ±0.8% |
| 5,000 | ±0.5% |

For planning purposes, ±1–2% precision is generally adequate; 1,000 simulations is a reasonable default. The Balance × Age grid uses 500 simulations per cell as a speed compromise.

### Limitations of the Normal Return Model

The assumption that annual returns are **independently and identically distributed (i.i.d.) normal** is convenient but imperfect:

1. **Fat tails**: Empirical return distributions have heavier tails than a normal distribution — large losses occur more frequently than the model predicts [10]. This means the model may underestimate the probability of catastrophic outcomes.
2. **Serial correlation**: Returns exhibit mild negative autocorrelation at annual horizons (mean reversion) and positive autocorrelation at shorter horizons (momentum), which the i.i.d. assumption ignores.
3. **Regime changes**: Markets periodically shift between high- and low-return regimes (e.g., bull markets, financial crises) that are not well-captured by a single fixed distribution.

An alternative approach — **historical bootstrap sampling** — resamples actual historical annual returns (e.g., from Shiller's dataset [11]), capturing fat tails and some autocorrelation structure. This is a suggested extension (Section 12).

---

## 8. Sequence-of-Returns Risk

Perhaps the most important insight from stochastic retirement modeling is that **the order of returns matters enormously**, even when the average return is identical.

Consider two retirees who both experience the same set of annual returns over 30 years, but in reverse order. The retiree who encounters poor returns early (just after retiring, when the portfolio is largest) is forced to sell assets at depressed prices to fund expenses. This permanently impairs the portfolio; subsequent good returns apply to a smaller base and cannot fully compensate. The retiree who experiences the same poor returns late (when the portfolio is smaller) is much less affected.

This asymmetry — called **sequence-of-returns risk** — is the primary reason why a deterministic projection using average returns is not sufficient for retirement planning [12]. A plan that "works on average" can fail in a surprisingly large fraction of scenarios if early retirement years happen to be poor market environments.

Sequence risk is most acute in the years immediately **before and after** retirement, because this is when the portfolio is at its peak size. This is why the model uses a higher return volatility $\sigma$ to stress-test the plan, and why a 90%+ success rate (rather than 50%) is the typical planning target.

---

## 9. Safe Withdrawal Rates and the 4% Rule

### Bengen (1994)

The landmark study of retirement withdrawal rates was published by financial planner William Bengen in 1994 [13]. Bengen analysed historical US market data (stocks and intermediate-term government bonds) from 1926 onward and asked: *What is the highest constant-dollar withdrawal rate that would have survived every historical 30-year retirement period?*

His answer was approximately **4% of initial portfolio value per year** — a figure now universally known as the "4% rule." Critically, Bengen showed that higher withdrawal rates failed in a significant number of historical scenarios, including retirements beginning in the late 1960s (which suffered both poor equity returns and high inflation).

### The Trinity Study

Cooley, Hubbard, and Walz (1998) extended Bengen's analysis using a portfolio success framework across multiple asset allocations and withdrawal rates [14]. Their key findings:

- A 4% withdrawal rate had a 95–100% historical success rate for 30-year retirements with a 50–75% equity allocation
- Higher withdrawal rates (5–6%) succeeded in 70–80% of scenarios
- Success rates declined substantially for longer planning horizons (e.g., 40 years)

### Relationship to This Model

This model does not implement the 4% rule directly — it allows the user to specify any expense level and uses Monte Carlo simulation to compute the resulting success rate. However, as a rough calibration check: a portfolio of 25× annual expenses at a 4% real post-retirement return and 12% volatility, with a 30-year horizon and no Social Security, should produce a success rate consistent with the historical literature.

The **safe withdrawal rate** implied by the model is:

$$\text{SWR} = \frac{W_{\text{net}}}{B_{\text{retirement}}}$$

where $W_{\text{net}}$ is the net annual withdrawal (after SS and pension offsets) and $B_{\text{retirement}}$ is the portfolio balance at retirement. Users can read this ratio off the output and compare it to the 4% benchmark.

### Caveats on the 4% Rule

The 4% rule was derived from **US historical data** during a period of exceptional equity market performance. Several researchers have argued that forward-looking safe withdrawal rates may be lower (3.0–3.5%) given current valuations [15, 16]. The model makes no assumptions about whether future returns will resemble historical ones — users supply their own return assumptions and can explore the sensitivity themselves.

---

## 10. The Balance × Age Success-Rate Grid

### Motivation

The deterministic projection and Monte Carlo sweep both take **retirement age** as an input and compute outcomes. But a user approaching retirement faces a different question: *"Given my current account balance — which I can look up right now — can I retire at my target age?"*

The Balance × Age grid answers this directly. It sweeps a two-dimensional grid of (retirement age, portfolio balance at retirement) pairs, computes the Monte Carlo success rate for each cell, and displays the result as a heatmap. The user finds their projected account balance on the Y-axis, their target retirement age on the X-axis, and reads off the success probability.

### Nominal Dollar Y-Axis

The Y-axis of the heatmap is in **nominal dollars** — the value your brokerage account will actually display at retirement — rather than today's dollars. This is the one place in the model where nominal values appear, and it is deliberate.

The conversion from nominal to real is:

$$B_{\text{real}} = \frac{B_{\text{nominal}}}{(1 + r_{\text{inflation}})^{T - t_0}}$$

where $T - t_0$ is the number of years until retirement. The simulation internally uses $B_{\text{real}}$ for all calculations; the nominal label is purely for readability.

### Interpreting the Contours

The heatmap overlays contour lines at 80% and 90% success rates. These thresholds are conventional targets in financial planning [13, 14]:

- **90%+**: Conservative; appropriate if you have few fallback options (no pension, no ability to return to work, no other assets)
- **80–90%**: Moderate; appropriate for most retirees with some spending flexibility
- **Below 80%**: Aggressive; plan should include contingency strategies

---

## 11. Limitations and Simplifications

The following simplifications are built into the current model. Each is a candidate for future extension.

### Taxes

The model treats `annual_expenses` as the amount needed **after tax**. It does not model:

- Required Minimum Distributions (RMDs) from traditional IRA/401(k) accounts
- The tax treatment of Roth vs. traditional withdrawals
- Capital gains taxes on taxable account withdrawals
- The impact of provisional income on Social Security benefit taxation

For a more accurate model, accounts should be segregated by tax treatment and a withdrawal sequencing strategy should be specified [17].

### Single Pooled Portfolio

All assets are modeled as a single balance with a single return assumption. In reality, most households hold assets across taxable accounts, traditional tax-deferred accounts, and Roth accounts, each with different effective returns (due to tax treatment) and different optimal withdrawal sequences. A multi-bucket model would provide greater accuracy [18].

### Constant Real Spending

Annual expenses are held constant in real terms throughout retirement. In practice, spending tends to follow a "smile" pattern: higher in the active early retirement years ("go-go years"), declining through middle retirement, and sometimes rising again in late retirement due to healthcare costs [19].

### Normal Return Distribution

As discussed in Section 7, the i.i.d. normal return model understates tail risk. Historical return distributions exhibit:

- **Negative skew**: Large losses are more common than large gains of the same magnitude
- **Excess kurtosis**: Extreme events ("fat tails") occur more often than the normal distribution predicts [10]

### Healthcare Costs

Healthcare spending typically grows faster than general inflation, particularly for the pre-Medicare gap (ages 60–64) and long-term care. This is not modeled separately.

### One-Time Cash Flows

The model does not accommodate one-time events such as home sale proceeds, inheritances, or large purchases (e.g., a new vehicle, major renovation). These can be approximated by adjusting the starting balance, but the interface does not expose this directly.

---

## 12. Suggested Extensions

The following extensions would improve model accuracy without compromising the self-contained, dependency-light design philosophy:

- **Per-account modeling**: Separate taxable, traditional, and Roth balances with appropriate tax treatment and withdrawal ordering (e.g., taxable first, Roth last)
- **Healthcare cost module**: A separate expense category with a higher growth rate (historically ~4–6% nominal) [20]
- **Age-dependent spending**: A spending curve parameterised by age (e.g., a piecewise linear function or the Blanchett "smile" model [19])
- **Historical bootstrap sampling**: Resample from actual historical annual return sequences (e.g., Shiller data [11]) to capture fat tails and avoid distributional assumptions
- **Social Security optimisation**: Model both spouses and optimise the joint claiming strategy
- **Dynamic withdrawal strategies**: Model guardrail or floor-and-ceiling strategies that reduce withdrawals in poor market years [21]
- **Roth conversion analysis**: Model strategic Roth conversions during early low-income retirement years

---

## 13. References

[1] Fisher, I. (1930). *The Theory of Interest*. Macmillan. The original derivation of the relationship between nominal and real interest rates.

[2] Bodie, Z., Kane, A., & Marcus, A. J. (2023). *Investments* (13th ed.). McGraw-Hill. Standard graduate finance textbook; real-terms retirement planning discussed in Part 5.

[3] Pfau, W. D. (2017). *How Much Can I Spend in Retirement? A Guide to Investment-Based Retirement Income Strategies*. Retirement Researcher Media.

[4] Bureau of Labor Statistics. (2024). *Real Earnings — Historical Data*. U.S. Department of Labor. https://www.bls.gov/ces/data/

[5] Ibbotson Associates / Morningstar. (2024). *Stocks, Bonds, Bills, and Inflation (SBBI) Yearbook*. Annual compendium of US asset class returns since 1926.

[6] Vanguard. (2024). *Vanguard's Economic and Market Outlook*. Annual forward-looking return estimates by asset class.

[7] Social Security Administration. (2024). *Retirement Benefits*. SSA Publication No. 05-10035. https://www.ssa.gov/pubs/EN-05-10035.pdf

[8] Meyer, W., & Reichenstein, W. (2012). "Social Security: When to Start Benefits and How to Minimize Longevity Risk." *Journal of Financial Planning*, 25(3), 49–59.

[9] Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77–91. Foundational paper establishing mean-variance optimization and the normal distribution model for asset returns.

[10] Mandelbrot, B., & Hudson, R. L. (2004). *The (Mis)Behavior of Markets: A Fractal View of Risk, Ruin, and Reward*. Basic Books. Accessible treatment of fat-tailed return distributions.

[11] Shiller, R. J. (2024). *Online Data*. Yale University. http://www.econ.yale.edu/~shiller/data.htm. Long-run US equity and bond return data with CAPE ratio; widely used for historical simulation studies.

[12] Kitces, M. E. (2014). "Managing Sequence of Return Risk with Bucket Strategies vs. a Systematic Withdrawal Approach." *Kitces.com*. https://www.kitces.com/blog/managing-sequence-of-return-risk-with-bucket-strategies-vs-a-systematic-withdrawal-approach/

[13] Bengen, W. P. (1994). "Determining Withdrawal Rates Using Historical Data." *Journal of Financial Planning*, 7(4), 171–180. The original paper establishing the 4% safe withdrawal rate.

[14] Cooley, P. L., Hubbard, C. M., & Walz, D. T. (1998). "Retirement Savings: Choosing a Withdrawal Rate That Is Sustainable." *AAII Journal*, 20(2), 16–21. The "Trinity Study"; systematic analysis of withdrawal rates across asset allocations and time horizons.

[15] Pfau, W. D. (2012). "Capital Market Expectations, Asset Allocation, and Safe Withdrawal Rates." *Journal of Financial Planning*, 25(1), 36–43. Argues that lower expected future returns imply safe withdrawal rates of 3.0–3.5%.

[16] Blanchett, D., Finke, M., & Pfau, W. D. (2013). "Low Bond Yields and Safe Portfolio Withdrawal Rates." *Journal of Wealth Management*, 16(2), 55–62.

[17] Horan, S. M. (2006). "Withdrawal Location with Progressive Tax Rates." *Financial Analysts Journal*, 62(6), 77–87. Analysis of optimal withdrawal sequencing across account types.

[18] Daryanani, G. (2008). "Opportunistic Rebalancing: A New Paradigm for Wealth Managers." *Journal of Financial Planning*, 21(1), 48–61.

[19] Blanchett, D. M. (2014). "Exploring the Retirement Consumption Puzzle." *Journal of Financial Planning*, 27(5), 34–42. Empirical analysis of the "retirement spending smile."

[20] Employee Benefit Research Institute. (2024). *Savings Medicare Beneficiaries Need for Health Expenses: Some Couples Could Need as Much as $413,000*. EBRI Issue Brief No. 586.

[21] Guyton, J. T., & Klinger, W. J. (2006). "Decision Rules and Maximum Initial Withdrawal Rates." *Journal of Financial Planning*, 19(3), 48–58. The "guardrails" dynamic withdrawal strategy.

---

## 14. Acknowledgements

This retirement planner and its accompanying theoretical documentation were developed with substantial assistance from **Claude** (Anthropic, 2025–2026), a large language model AI assistant. Claude contributed to the design of the interactive widget dashboard, the mathematical formulations, the Monte Carlo vectorisation, and the drafting of this document.

The use of AI in this project is consistent with the spirit of the tool itself: leveraging available technology to make rigorous quantitative analysis accessible to individuals without a specialised finance or programming background. All modeling decisions, parameter choices, and interpretations remain the responsibility of the human author.

Users who wish to verify, critique, or extend the model are encouraged to inspect the source code directly in `retirement_planner.ipynb`, which is intentionally kept short, readable, and dependency-light.

> *This document and the accompanying notebook are provided for educational and planning purposes only. Nothing here constitutes personalised financial, tax, or investment advice. Consult a qualified financial professional before making retirement planning decisions.*
