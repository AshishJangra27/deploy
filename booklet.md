# NiftyScope Teaching Booklet

## A guided build of an interactive NIFTY 50 dashboard

**Audience:** students, instructors, beginner Python developers, and project-based learning groups

**Project stack:** Python · Streamlit · pandas · Plotly

**Repository:** `https://github.com/AshishJangra27/deploy`

**App entry point:** `app.py`

**Dataset:** `data.csv`

**Companion documents:** `PRD.md`, `prompt.md`, `implement_prompt.md`, and `README.md`

---

## 1. How to use this booklet

This booklet is a teaching plan and a project walkthrough. It explains why the project exists, how to use the dataset, how the PRD and implementation prompts fit together, how the dashboard works, how to run it, how to deploy it, and how to lead exercises.

The instructor can teach it as one long workshop or split it into two sessions:

1. **Product and data:** problem definition, dataset, requirements, and visual design.
2. **Build and explain:** Python app, calculations, validation, interaction, deployment, and extensions.

The project is an educational market-data exploration tool. It is not a trading system and does not provide investment advice.

## 2. Learning outcomes

By the end, learners should be able to:

- Explain the problem the dashboard is designed to solve.
- Read a daily OHLC CSV and describe what each column means.
- Turn a broad idea into a scoped, testable PRD using a reusable prompt.
- Explain the roles of Streamlit, pandas, and Plotly in a small Python dashboard.
- Describe how date filters affect metrics and visualizations.
- Explain range return, hypothetical P&L, daily and monthly returns, drawdown, volatility, a hindsight entry scan, SIP calculations, and an event window.
- Identify assumptions and limitations in financial calculations.
- Run the app locally, understand the CI workflow, and explain the correct hosting target.
- Extend the project without confusing historical analysis with forecasts or advice.

## 3. Suggested class plan

This is a flexible plan for a 2.5–3 hour session. Allow more time if learners are new to Python or Git.

| Time | Topic | Teaching activity |
|---:|---|---|
| 10 min | Opening question | Ask how someone would compare two historical market periods using a CSV. |
| 15 min | Problem statement | Identify the audience, task, constraints, and why a dashboard helps. |
| 20 min | Dataset tour | Inspect the columns, dates, OHLC relationships, and missing data risks. |
| 20 min | PRD prompt | Read the reusable PRD prompt and critique the resulting requirements. |
| 15 min | Architecture | Trace CSV → pandas → Streamlit controls/calculations → Plotly outputs. |
| 35 min | Feature walkthrough | Demonstrate date selection, OHLC view, return/risk, entry scan, SIP, and festival study. |
| 15 min | Validation and limitations | Discuss unusual input, hindsight, data quality, and non-causal event comparisons. |
| 15 min | Run and deployment | Start locally; explain GitHub Actions and Streamlit Community Cloud. |
| 20 min | Learner activity | Change one feature or calculate a metric independently. |
| 10 min | Wrap-up | Review learning outcomes and assign an extension. |

### Materials

- A computer with Python 3.10 or later and Git.
- The project repository cloned locally, or a copy of the project files.
- Internet access to install Python packages and, if desired, open the upstream CSV source.
- A spreadsheet or calculator for checking a small sample calculation by hand.

## 4. Problem statement

### The problem

Historical index data is often presented as rows of dates and prices. A learner may be able to open a CSV but still find it difficult to answer practical exploration questions:

- How did the index move over a chosen period?
- Did that interval produce a positive or negative price return?
- How do Open, High, Low, and Close compare?
- How large were drawdowns or volatility during that period?
- How would a fixed monthly contribution have behaved over the selected historical data?
- What market movement occurred in a chosen number of trading sessions around a festival date?

Answering these questions manually requires repeated filtering, calculations, and chart creation. Results are also easy to misinterpret if assumptions are hidden.

### Product problem statement

Build a small, Python-first web dashboard that lets learners explore the provided NIFTY 50 OHLC history through date and price-field controls, clear charts, transparent calculations, and downloadable selected data. Keep the app simple to run, document its assumptions, and avoid implying that historical results predict future performance.

### Who benefits

- **Students:** learn data analysis and interactive Python app design.
- **Researchers and analysts:** quickly inspect selected historical windows.
- **New investors:** understand hypothetical calculations and their limitations.
- **Instructors:** teach data validation, visualization, product requirements, and responsible presentation together.

## 5. Proposed solution and scope

NiftyScope is a Streamlit dashboard. pandas reads and transforms the CSV. Plotly renders interactive charts. Streamlit provides the sidebar inputs, layout, tables, metrics, and download control.

### What the current app does

- Selects a period preset and a custom start/end date range.
- Lets the user choose Close, Open, High, or Low for price-field analysis.
- Shows a line for the selected price field or an OHLC candlestick chart.
- Calculates selected-range return and a rupee P&L scaled by a hypothetical starting amount.
- Shows daily returns, monthly returns, drawdown, annualized volatility, and recent rows.
- Scans for the best historical entry date over a chosen holding period.
- Calculates a historical monthly SIP over the selected range and an assumed-return future SIP estimate.
- Compares market closes around a selected festival name and user-entered event date.
- Highlights the selected festival date when it falls inside the main chart's selected range.
- Downloads the selected date range as CSV.

### What the app does not do

- It does not provide live or intraday data.
- It does not calculate a forecast or recommend a trade.
- It does not provide total-return or dividend-adjusted performance.
- It does not maintain a sourced automatic festival calendar; the date is selected by the user.
- The Plotly range slider zooms the main chart only. The sidebar date picker controls the range used by all range-based metrics.
- It is not currently deployed as a Streamlit Community Cloud app. GitHub Actions validates the repository but does not publish a Streamlit server.
- GitHub Pages cannot run the Streamlit Python server. A previous static Pages site, if still visible, is not the current Streamlit app.

## 6. Dataset guide

### Location and source

- Local file expected by the app: project-root `data.csv`.
- Fallback file: `src/public/nifty50.csv`.
- Upstream CSV: [NIFTY 50 dataset](https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv).
- In this repository, the supplied snapshot contains daily data from **3 January 2000 through 26 May 2025**. Re-check the file before teaching if the snapshot has since been refreshed.

### Columns

| Column | Meaning | Example question |
|---|---|---|
| `Date` | Trading-session date | What was the index close on a date? |
| `Open` | Opening index level | How does the opening level compare with the close? |
| `High` | Highest index level recorded for the session | How far did the index rise intraday? |
| `Low` | Lowest index level recorded for the session | How far did it fall intraday? |
| `Close` | Closing index level | What was the final index level for the session? |

For a valid OHLC row, `Low` should not exceed `Open` or `Close`; `High` should not be below either; and `Low` must not exceed `High`. Dates should be parseable and unique. Prices should be numeric and positive.

### Instructor demonstration

Open `data.csv` in a spreadsheet or text editor and ask learners:

1. Is each row a trading day or a calendar day?
2. Why are there gaps between some dates?
3. Why can the High be greater than the Close?
4. Which columns are needed for a line chart? Which are needed for candles?
5. What could go wrong if a date or price were blank, repeated, or incorrectly typed?

Emphasize that missing weekend dates are expected for a trading-session dataset. They should not automatically be filled as if trades occurred.

## 7. Prompts used in the project workflow

The repository contains two reusable prompts. The first creates a requirements document; the second tells an AI coding agent how to implement that document.

### 7.1 PRD generation prompt (`prompt.md`)

Use this when teaching product definition or regenerating the PRD for this project:

```text
Write a build-ready Product Requirements Document (PRD) for “NiftyScope,” a GeeksforGeeks-inspired dashboard for exploring NIFTY 50 historical data. Make it self-contained so a developer with no prior context can build the project.

Product and implementation requirements:
- Build the app in Python with Streamlit, pandas, and Plotly. Use a local CSV snapshot with columns Date, Open, High, Low, Close. Source: https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv
- Deploy with Streamlit Community Cloud using root app.py. GitHub Actions should validate dependencies, the dataset, and Python syntax. GitHub Pages is incompatible because it cannot run a Streamlit server.
- Include period presets (1, 3, 5, 10 years, full history), a custom date range, Open/High/Low/Close selection, selected-field line or OHLC candlestick chart, summary metrics, daily/monthly returns, drawdown, rolling volatility, recent rows, and CSV download.
- Range P&L compares the first and last selected OHLC field values and scales that return by a user-entered hypothetical amount. Explain that Open/High/Low are observed values, not guaranteed execution prices.
- Add a hindsight entry scan: find the best historical entry within the selected range for a user-selected holding period in trading sessions; clearly label it as hindsight, not a forecast.
- Add historical SIP simulation (one monthly contribution on the first available session of each month, bought at the selected field and valued at the range end) and a future SIP estimator using duration and an assumed annual return with end-of-month contributions.
- Add a festival event study with festival selection, user-entered date, and adjustable before/after trading-session windows. Anchor on the first market session on or after the date; show before, after, and total close returns; highlight the date/window. Do not imply causation. Festival dates vary by year, so do not claim an automatic calendar unless one is separately sourced and implemented.
- Use a calm, professional, GFG-inspired green palette: primary #087F5B, secondary/up #16835D, down #C2414B, canvas #F5F7F6, sidebar #F0F5F1, white cards, ink #1C2924, muted text #68756F, borders #E2E9E5. Use Nunito Sans with a system sans-serif fallback, generous spacing, subtle cards, responsive columns, and accessible contrast. Treat the GFG identity as inspired styling; do not invent or embed an official logo.
- Validate CSV schema, numeric values, dates, duplicates, and OHLC relationships; sort valid rows by date. Document data freshness, assumptions, limitations, and financial disclaimers.

Organize the PRD with: product summary and goals, target users and jobs, scope and detailed features, exact metric/calculation definitions, data requirements and validation, interaction flows, visual design system, technical architecture and deployment, acceptance criteria, known limitations, out-of-scope items, and future improvements. Distinguish what is implemented from what remains planned. Be specific, concise, and do not promise features that are not in the requirements above.
```

### 7.2 Implementation prompt (`implement_prompt.md`)

Use this after reviewing the PRD when asking an AI coding agent to work in the repository:

```text
Implement this project from its Product Requirements Document.

1. Read all of `PRD.md`, `README.md`, `prompt.md`, and the existing source/configuration before editing. Treat `PRD.md` as the functional and visual specification; treat other repository files as project context. If the PRD conflicts with the current code, follow the PRD and update the documentation to match the result.
2. Inspect the repository state, branch, and configured Git remotes. Preserve existing user changes. Do not reset, force-push, or overwrite unrelated work.
3. Build the complete project described in the PRD. Keep the specified Python/Streamlit/pandas/Plotly stack, data source and schema, calculations, controls, visual system, and disclaimers. Do not silently omit features or replace them with mockups. Keep feature behavior and assumptions explicit in the UI.
4. Run the applicable checks and validation described by the PRD and repository workflow. Validate the local data snapshot and verify important calculations and app startup when the environment allows. Fix issues found. If a dependency, credential, service, or deployment setting blocks verification, state the concrete blocker and finish all independent work.
5. Update `README.md` and other project documentation when implementation or setup changes. Ensure deployment instructions match the actual runtime. Streamlit needs a Python host; do not claim that GitHub Pages runs it. Configure or verify Streamlit Community Cloud only when account access and required authorization are available.
6. Review the final diff for correctness, accidental files, secrets, and whitespace errors. Commit the completed work with a concise message, then push the current working branch to its configured remote (normally `origin`). Do not force-push. If pushing is blocked by missing access or credentials, leave the commit intact and report the exact action the user must take.
7. In the final response, summarize what was built, list checks and their outcomes, give the commit and push status, and clearly state any feature, runtime, or deployment limitation that remains. Never claim successful deployment without confirming the app is live and usable.

Work through the implementation end to end. Do not stop after proposing a plan or generating code snippets; modify the repository, validate the result, and push it when repository access permits.
```

### Teaching note about prompts

AI-generated requirements and code need review. Ask learners to confirm that the PRD describes the real user goal, that every formula is clear, that assumptions are visible, that the selected technology can run on the stated host, and that claimed deployment status has been verified.

## 8. Product requirements and calculation lessons

### 8.1 Range return and hypothetical P&L

Let `P₀` be the first selected observation of the chosen OHLC field, `P₁` its final selected observation, and `A` a hypothetical amount:

```text
range_return = (P₁ / P₀) - 1
hypothetical_pnl = A × range_return
hypothetical_ending_value = A × (1 + range_return)
```

Example for teaching only: if a price rises from 100 to 110, the price return is 10%. If the hypothetical amount is ₹1,000, the arithmetic P&L is ₹100 and ending value is ₹1,100. Real-world costs and execution are not included.

Point out that the app can use Open, High, or Low as the selected observation. A High-to-High range is not the same as a realistic strategy that could have bought and sold at both intraday highs. It is a comparison of data fields.

### 8.2 Daily returns

For close `Cₜ` and previous available trading-session close `Cₜ₋₁`:

```text
daily_returnₜ = (Cₜ / Cₜ₋₁) - 1
```

The first selected row has no prior selected close, so its daily return is missing. The app starts this calculation inside the selected window.

### 8.3 Monthly returns

Group selected observations by calendar month. For first available close `C_first` and last available close `C_last` in the month:

```text
monthly_return = (C_last / C_first) - 1
```

This is first-to-last available close within each month. It is not necessarily the return from the prior month's final close.

### 8.4 Drawdown

At each selected session, compare the close to the highest close so far in the selected window:

```text
running_peakₜ = max(C₀, C₁, …, Cₜ)
drawdownₜ = (Cₜ / running_peakₜ) - 1
maximum_drawdown = minimum(drawdownₜ)
```

Because the peak is calculated within the current selected range, changing the start date can change the drawdown path.

### 8.5 Annualized volatility

The app uses the sample standard deviation `s` of close-to-close daily returns and annualizes it with 252 assumed trading sessions:

```text
annualized_volatility = s × √252
```

The dashboard's rolling volatility uses a 21-session rolling sample standard deviation and multiplies by `√252 × 100` to display a percentage. Annualization is a convention, not a prediction.

### 8.6 Best historical entry scan

For selected-field price `Pₜ` and a holding period of `n` trading sessions:

```text
forward_returnₜ = (Pₜ₊ₙ / Pₜ) - 1
best_entry = eligible t with the largest forward_returnₜ
```

The last `n` rows cannot be starting points because the selected window does not contain their full future holding period. This scan searches historical data with hindsight. It does not tell a learner when to invest now.

### 8.7 Historical SIP simulation

The app selects the first available trading session in every calendar month inside the selected date window. For monthly contribution `M` and selected-field price `Pᵢ` at each monthly purchase:

```text
units_bought = Σ (M / Pᵢ)
total_invested = M × number_of_monthly_purchases
ending_value = units_bought × final_selected_field_price
historical_pnl = ending_value - total_invested
```

This simplified simulation assumes fractional units and does not include fund fees, taxes, dividends, NAV tracking, or actual mutual-fund transaction rules.

### 8.8 Future SIP estimate

For end-of-month contributions `M`, number of months `n`, and assumed monthly rate `r` (annual percentage divided by 12 and 100):

```text
future_value = M × (((1 + r)ⁿ - 1) / r), when r ≠ 0
future_value = M × n, when r = 0
```

This is a scenario calculator. It assumes a constant rate and does not predict actual performance. Learners should compare multiple rates and durations to see how sensitive the estimate is.

### 8.9 Festival study

The user chooses a festival label, calendar date, `b` sessions before, and `a` sessions after. The event anchor is the first dataset session on or after the chosen date. Let `C₀` be the anchor close, `C₋b` the first close in the before window, and `C₊a` the final close in the after window:

```text
before_return = (C₀ / C₋b) - 1
after_return = (C₊a / C₀) - 1
full_window_return = (C₊a / C₋b) - 1
relative_close_at_session_k = (Cₖ / C₀) - 1
```

Sessions are trading sessions, not calendar days. An event study describes what happened around selected dates; it cannot establish that the festival caused the movement.

## 9. Technical architecture walkthrough

### Data flow

```text
data.csv
   ↓
load_data() — parse, convert, validate, sort, cache
   ↓
sidebar controls — date range, OHLC field, amount, holding period, festival
   ↓
pandas — calculate returns, monthly groups, drawdown, volatility, SIP and event slices
   ↓
Plotly — interactive charts
   ↓
Streamlit — render metrics, charts, table, controls, and CSV download
```

### Project files

| File | Role |
|---|---|
| `app.py` | Streamlit page, controls, data transformations, calculations, charts, and outputs. |
| `data.csv` | Primary local OHLC dataset. |
| `src/public/nifty50.csv` | Validated fallback copy created by the refresh script. |
| `scripts/refresh_data.py` | Checks schema and value relationships; copies the local CSV or fetches upstream when `--fetch` is passed. |
| `requirements.txt` | Python package requirements: Streamlit, pandas, Plotly. |
| `.github/workflows/streamlit.yml` | Installs dependencies, runs the dataset validation script, and checks Python syntax on pushes and pull requests. |
| `PRD.md` | Current product and implementation specification. |
| `prompt.md` | Reusable prompt for generating the PRD. |
| `implement_prompt.md` | Reusable prompt for implementing the PRD. |
| `booklet.md` | This teaching guide. |
| `README.md` | Quick start and deployment notes. |

### What CI proves

The GitHub Actions workflow verifies that dependencies install in its environment, the dataset validation/refresh step completes, and Python files compile. It does not launch the Streamlit UI, test browser interactions, or deploy the app to Streamlit Community Cloud.

## 10. Hands-on setup

### Clone the repository

```bash
git clone https://github.com/AshishJangra27/deploy.git
cd deploy
```

### Create an environment and install packages

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Validate data and launch

```bash
python scripts/refresh_data.py
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Open it in a browser. Stop the server with `Ctrl+C` in the terminal.

### Explore the app as a class

1. Change the period preset and compare how much history is selected.
2. Choose a custom date interval and identify the selected-session count.
3. Change the price field between Close, Open, High, and Low. Explain why P&L changes.
4. Switch to candlesticks and identify the four OHLC values in one candle.
5. Change the hypothetical starting amount. Check that the percentage return remains the same while rupee P&L scales.
6. Increase the best-entry holding period. Notice that fewer dates remain eligible.
7. Compare historical and future SIP tabs. Separate observed historical inputs from assumed future returns.
8. Pick a festival date and vary the session windows. Note that the anchor can move to the next trading day when the date is not a session.
9. Download the selected range and open the CSV to inspect what was exported.

## 11. Data refresh and governance

To validate the checked-in local snapshot and rebuild the fallback copy:

```bash
python scripts/refresh_data.py
```

To fetch from the upstream raw CSV explicitly:

```bash
python scripts/refresh_data.py --fetch
```

Before committing a refreshed dataset, inspect its date range, row count, schema, and upstream source. Confirm that redistribution is permitted by the source's licensing/usage terms. The app currently reports the CSV filename and number of excluded rows; it does not automatically fetch data during normal use.

## 12. Deployment lesson

### Why not GitHub Pages?

GitHub Pages serves static files. Streamlit runs a Python server process, so putting `app.py` on Pages does not make the app run. The old marimo static-export approach and the current Streamlit server approach are different architectures.

### Streamlit Community Cloud path

To publish the current app, an owner with access to the repository should:

1. Sign in to Streamlit Community Cloud.
2. Create a new app and connect `AshishJangra27/deploy`.
3. Select the `main` branch.
4. Set the app file path to `app.py`.
5. Deploy, then test the public app in a browser.

The repository's GitHub Actions workflow is validation only. Do not tell learners that CI has deployed the Streamlit app. A successful CI run is not a successful live-site check.

## 13. Troubleshooting guide

| Symptom | Likely cause | Teaching/debugging step |
|---|---|---|
| `FileNotFoundError` | `data.csv` is absent from the project root and fallback path. | Check the current working folder and filenames. |
| CSV schema error | Column names or order do not match the required OHLC schema. | Inspect `frame.columns`; map source columns explicitly only after confirming meaning. |
| Empty selected range | Chosen dates contain no rows or are reversed/outside the data coverage. | Widen the date window and compare it with the dataset's first/last dates. |
| Not enough observations for entry scan | Range contains fewer sessions than the selected holding period plus a future endpoint. | Widen the date range or reduce the session horizon. |
| Festival window warning | The event is too near the beginning/end of available data for the chosen before/after interval. | Select an earlier/later event date within data coverage or reduce the intervals. |
| Streamlit command not found | Virtual environment is inactive or dependencies were not installed there. | Activate `.venv`; reinstall from `requirements.txt`. |
| GitHub Pages shows an old dashboard | Pages may still serve an earlier static artifact. | Explain that it is not the Streamlit runtime; use Community Cloud for the current app. |
| Community Cloud build fails | Missing file, unsupported Python/package setup, or service configuration issue. | Read the deployment log, fix the specific issue, redeploy, and verify the rendered app. |
| `pip` cannot find compatible packages | A local package mirror/index may be stale or restrict versions. | Inspect pip's configured index and Python version; retry only with an approved, trusted package index. |

## 14. Classroom exercises

### Exercise A — Validate a row

Given `Open=100`, `High=110`, `Low=95`, `Close=105`, is the OHLC row structurally valid? Change one value so it becomes invalid and explain which rule it violates.

**Expected discussion:** valid as given. `High=102` would violate `High >= max(Open, Close)`. `Low=101` would violate `Low <= min(Open, Close)` and `Low <= High`.

### Exercise B — Calculate a range return

A selected price field starts at 20,000 and ends at 22,000. The hypothetical amount is ₹50,000. Calculate the return, hypothetical profit, and ending value.

**Expected:** return = 10%; P&L = ₹5,000; ending value = ₹55,000 before costs and other omitted effects.

### Exercise C — Compare a SIP with a lump sum

Use the same selected date window and amount. Compare a one-time hypothetical investment with the app's historical monthly SIP. Explain why the results can differ.

**Expected discussion:** purchase dates and entry prices differ. The SIP buys multiple units at different dates; the lump sum is exposed to the entire amount from the start. Neither result includes costs or dividends.

### Exercise D — Change the festival window

Study the same selected event with 5, 10, and 20 trading sessions before and after. How do the before, after, and total returns change? Does this prove that the festival caused the movement?

**Expected:** window returns may change as endpoints change; no causal claim can be inferred from this descriptive comparison alone.

### Exercise E — Design a test case

Write one test/check for a short date range and one for a boundary case. Examples: one row selected; fewer sessions than the requested holding period; festival date at the dataset boundary; zero or negative OHLC input.

**Expected discussion:** define the input, expected behavior/message, and the calculation or UI output that proves the behavior.

## 15. Assessment rubric

| Area | Strong evidence |
|---|---|
| Problem framing | Explains the user, task, and why an interactive dashboard helps. |
| Data literacy | Describes OHLC, date gaps, validation, and source limitations. |
| Calculation accuracy | Can independently verify at least two displayed metrics. |
| Interaction reasoning | Explains which controls update calculations and which only zoom the chart. |
| Responsible communication | Labels hypothetical, hindsight, and assumed-rate results clearly. |
| Technical understanding | Traces data from CSV through pandas and Plotly to Streamlit output. |
| Deployment clarity | Distinguishes CI validation from live deployment and Pages from Streamlit hosting. |

## 16. Suggested extensions

- Add a separate point-change metric and define exactly which OHLC field it uses.
- Add an interactive graph selection that updates the shared date filter, while preserving a keyboard-accessible date input.
- Provide an explicitly sourced and versioned festival calendar, with the source and date convention documented.
- Add unit tests for formulas and edge cases, then add browser tests for controls and downloads.
- Add dividend-adjusted or total-return data only after selecting an appropriate licensed source.
- Add a comparison mode for two user-selected historical windows.
- Add a return-distribution or calendar heatmap while documenting how partial months are treated.

## 17. Instructor closing script

“We started with a CSV and a user question. We inspected the data before plotting it, wrote down what the dashboard should do, chose Python tools that fit the hosting requirement, and made the calculations visible. We also separated historical description from prediction. The finished project is useful because its controls, assumptions, and limits are understandable—not because it claims to tell us what the market will do next.”

---

## Quick reference

- **PRD:** `PRD.md`
- **PRD-writing prompt:** `prompt.md`
- **Implementation prompt:** `implement_prompt.md`
- **Current Streamlit app:** `app.py`
- **Dataset:** `data.csv`
- **Run locally:** `streamlit run app.py`
- **Validate local data:** `python scripts/refresh_data.py`
- **Deployment target:** Streamlit Community Cloud, `main`, `app.py`
- **Current repository CI:** dataset validation and Python syntax check; no app deployment
