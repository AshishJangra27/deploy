# NiftyScope: 90-Minute Teaching Guide

**Project:** Interactive NIFTY 50 dashboard

**Audience:** Beginner Python/data-visualization learners

**Stack:** Python, Streamlit, pandas, Plotly

**Repository:** [AshishJangra27/deploy](https://github.com/AshishJangra27/deploy)

**App:** `app.py` · **Dataset:** `data.csv`

## Session outcomes

By the end of the session, learners can:

- Describe the problem, dataset, and dashboard solution.
- Explain how Streamlit, pandas, and Plotly work together.
- Interpret the range return, SIP, best-entry, and festival-window calculations.
- Run the app and explain how to deploy it correctly.

## 90-minute agenda

| Time | Activity |
|---|---|
| 0–5 min | Introduce the project and learning goals |
| 5–15 min | Problem statement and solution |
| 15–25 min | Dataset and data-quality tour |
| 25–35 min | Product prompt and PRD |
| 35–60 min | Live dashboard walkthrough |
| 60–70 min | Explain core calculations and assumptions |
| 70–80 min | Run locally and explain deployment |
| 80–88 min | Learner mini-activity |
| 88–90 min | Recap and exit question |

---

## 1. Problem and solution · 5–15 min

### Problem statement

NIFTY 50 history in a CSV is difficult to explore by hand. Learners need to filter dates, compare OHLC values, calculate returns and risk, and inspect event windows without repeatedly writing one-off spreadsheet formulas.

### Solution

NiftyScope turns the daily CSV into an interactive Python dashboard. Users select a date window and OHLC field, then explore charts, hypothetical P&L, historical entry comparisons, SIP calculations, and a festival event study.

Emphasize that this is a learning and historical-exploration project. It is not a trading system or investment advice.

## 2. Dataset tour · 15–25 min

The local file is `data.csv`. It has five columns:

| Column | Meaning |
|---|---|
| `Date` | Trading-session date |
| `Open` | Opening index level |
| `High` | Highest level during that session |
| `Low` | Lowest level during that session |
| `Close` | Closing index level |

Source: [raw NIFTY 50 CSV](https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv). The supplied snapshot covers 3 January 2000 to 26 May 2025; check the file if it has been refreshed.

Ask learners:

1. Why are weekend dates absent? (These are trading sessions, not calendar days.)
2. What OHLC relationships should hold? (`Low ≤ Open/Close ≤ High` and `Low ≤ High`.)
3. Why should duplicate dates and non-numeric prices be checked before charting?

The app reads root `data.csv`, falls back to `src/public/nifty50.csv`, converts types, excludes invalid rows, and sorts chronologically. `scripts/refresh_data.py` validates the data and can explicitly fetch the source with `--fetch`.

## 3. Product prompt and PRD · 25–35 min

Explain the workflow: a prompt helps define scope, the PRD records requirements, and the implementation prompt directs coding work. Review `PRD.md` for the full specification and `prompt.md` / `implement_prompt.md` for the reusable prompts.

### Short PRD prompt

```text
Write a build-ready PRD for NiftyScope, a GFG-inspired NIFTY 50 dashboard. Use Python, Streamlit, pandas, and Plotly with the local Date/Open/High/Low/Close CSV. Specify date filters, OHLC charts, range return/P&L, returns and risk charts, hindsight entry scan, historical and future SIP calculators, and a user-dated festival event study. Include exact formulas, data checks, assumptions, visual palette, user flows, acceptance criteria, limitations, and Streamlit Community Cloud deployment. Mark user-entered festival dates and all hypothetical calculations clearly. Do not claim GitHub Pages can run Streamlit.
```

### Short implementation prompt

```text
Read PRD.md, README.md, prompt.md, and the current repository before coding. Implement the complete PRD in the existing Python/Streamlit project; preserve user changes, validate data and calculations, update documentation, and fix issues. Run applicable checks, inspect the diff, commit, and push the current branch to its configured remote without force-pushing. Report checks and deployment status honestly; GitHub Pages does not host Streamlit.
```

**Teaching point:** prompts are starting instructions, not proof of correctness. Review formulas, assumptions, code, and deployment results.

## 4. Dashboard walkthrough · 35–60 min

Use the app at each step and ask learners what changed.

1. **Period and date range:** select a preset, then adjust the sidebar dates. Range-based metrics update from the selected dates.
2. **Price field:** switch among Close, Open, High, and Low. Explain that range P&L and the entry scan use this selected field.
3. **Chart style:** view the selected-field line or OHLC candles. The chart's bottom range slider zooms that chart; it does not filter the other panels. Use the sidebar date input to update the shared analysis range.
4. **Summary and charts:** inspect range return, hypothetical rupee P&L, close-based volatility and drawdown, daily returns, monthly returns, and recent rows.
5. **Best historical entry:** change the holding period and show the maximum past forward return. Call out “hindsight”—the answer uses future observations from the selected historical range.
6. **SIP calculator:** contrast the historical simulation with the future estimate. Ask what assumptions are different.
7. **Festival study:** select a festival label, enter a date, and change trading-session windows. The chart anchors on the first market session on or after the date and highlights the before/after window.
8. **CSV download:** download the selected main range and inspect the output columns.

### Visual identity

The app uses GFG-inspired green styling and text branding; it does not embed an official GFG logo.

| Use | Color |
|---|---|
| Brand green | `#087F5B` |
| Market up | `#16835D` |
| Market down | `#C2414B` |
| Canvas / sidebar | `#F5F7F6` / `#F0F5F1` |
| Cards | `#FFFFFF` |
| Text / muted text | `#1C2924` / `#68756F` |
| Borders / soft green | `#E2E9E5` / `#E8F4EE` |

Typography is Nunito Sans with a system sans-serif fallback. Cards and charts use light surfaces, subtle borders, and restrained color.

## 5. Core calculations · 60–70 min

Let `P₀` and `P₁` be the first and last selected values of the chosen OHLC field, and `A` be the hypothetical amount:

```text
Range return = (P₁ / P₀) - 1
Hypothetical P&L = A × range return
```

Explain that High or Low observations are not guaranteed fill prices. These hypothetical values exclude costs, taxes, slippage, and dividends.

Other dashboard calculations:

```text
Daily return = (today's close / prior session's close) - 1
Monthly return = (last available close / first available close in month) - 1
Drawdown = close / running close peak in selected range - 1
Annualized volatility = sample standard deviation of daily close returns × √252
```

### Best-entry scan

For a holding period of `n` trading sessions, each eligible date's forward return is `(P[t+n] / P[t]) - 1`. The app reports the highest observed historical result. The final `n` sessions are not eligible. This is hindsight analysis, not a forecast or a “best time” recommendation.

### SIP

- **Historical:** invest the selected monthly amount on the first available session in each month; sum fractional units bought; value units at the final selected price.
- **Future:** for monthly contribution `M`, monthly rate `r` (annual rate ÷ 12), and `n` months, estimate `M × (((1+r)^n - 1) / r)`. If `r=0`, estimate `M × n`. Contributions are assumed at month-end.

Neither SIP view models mutual-fund NAVs, tracking error, expense ratios, tax, inflation, or dividends. Future returns are assumptions, not guarantees.

### Festival window

The user chooses a festival label and date. The first trading session on or after that date is session zero. The app compares the close from the start of the before-window to session zero, from session zero to the end of the after-window, and across the full window. The comparison describes association; it does not establish cause. Dates vary by year and region, so users enter/adjust the date themselves.

## 6. Run and deployment · 70–80 min

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python scripts/refresh_data.py
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

### Hosting lesson

Streamlit requires a Python server. GitHub Pages serves static files and cannot run this app. To publish, connect the repository to Streamlit Community Cloud, choose branch `main`, and set app path to `app.py`. That deployment has **not** been configured in this repository. The GitHub Actions workflow installs dependencies, validates the dataset, and checks Python syntax; it does not deploy or browser-test the app.

## 7. Learner activity and recap · 80–90 min

### Mini-activity · 8 min

In pairs, choose a date window and amount. Calculate the range return and rupee P&L by hand for one chosen OHLC field. Then compare with the dashboard and explain one assumption or limitation.

**Example answer:** if the selected field moves from 20,000 to 22,000, return is 10%. For ₹50,000, hypothetical P&L is ₹5,000 before costs and omitted effects.

### Exit questions · 2 min

1. What is the difference between the sidebar date filter and chart range slider?
2. Why is the “best entry” result hindsight?
3. Where should this Streamlit app be hosted, and why not GitHub Pages?

## Instructor quick reference

| Item | Location / command |
|---|---|
| Product requirements | `PRD.md` |
| Full PRD-generation prompt | `prompt.md` |
| Full implementation prompt | `implement_prompt.md` |
| Streamlit source | `app.py` |
| Dataset | `data.csv` |
| Local run | `streamlit run app.py` |
| Validate/refresh local snapshot | `python scripts/refresh_data.py` |
| Deployment target | Streamlit Community Cloud · `main` · `app.py` |

**Closing message:** We turned historical rows into an interactive learning tool by defining requirements, checking the data, making calculations visible, and explaining what the results cannot tell us.
