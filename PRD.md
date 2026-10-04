# NiftyScope — Product Requirements Document

**Version:** 2.0
**Status:** Reflects the Streamlit implementation in `app.py`
**Updated:** 4 October 2026
**Product:** GeeksforGeeks-inspired NIFTY 50 market-history explorer

## 1. Product summary

NiftyScope is an interactive dashboard for exploring historical daily NIFTY 50 OHLC data. Users can choose a date window and price field, inspect return and risk charts, compare hypothetical outcomes, calculate historical or assumption-based SIP values, and study market movement around a selected festival date.

The application is implemented in Python with Streamlit, pandas, and Plotly. The current dashboard source is the root-level `app.py`. It reads a local CSV snapshot and does not request live market data.

## 2. Product goals

- Make long-run NIFTY 50 data easier to explore through responsive controls and interactive charts.
- Let users see how a chosen date range and OHLC price field affect hypothetical price returns and rupee P&L.
- Provide descriptive historical tools for entry-date comparison, monthly SIP simulation, and festival-window analysis.
- Keep calculations and their assumptions visible so users can understand what each result represents.
- Keep the interface calm, legible, mobile-aware, and aligned with a GeeksforGeeks-inspired green identity.

## 3. Users and primary jobs

### Learner or student

Explore how the index behaved over time, compare periods, and learn how returns, volatility, drawdown, and recurring contributions are calculated.

### Market-history researcher

Select a specific interval, compare OHLC fields, inspect daily or monthly changes, and examine market movement around a chosen event date.

### First-time investor

Explore hypothetical SIP outcomes under historical data or a user-entered future return assumption, with the calculation caveats displayed alongside the result.

## 4. Scope and current implementation

All features below are implemented in the current Streamlit app unless called out in **Known limitations**.

### 4.1 Dashboard controls

- Period preset: Full history, last 10 years, 5 years, 3 years, or 1 year.
- Custom start and end date input.
- Price field for range return and entry scan: Close, Open, High, or Low.
- Price chart style: selected price field or OHLC candlesticks.
- Hypothetical starting amount for range P&L and entry-scan outcome.
- Holding period for entry scan, in trading sessions (5–252).
- Festival selector: Diwali, Holi, Eid al-Fitr, Ganesh Chaturthi, Christmas, or custom event.
- Editable festival date and independently selectable before/after windows (1–60 trading sessions each).
- SIP monthly contribution input.

The dashboard date input filters the data used by range-based metrics and analyses. The Plotly range slider zooms the main price chart; dragging that chart slider does not change the sidebar date selection or recalculate the other panels.

### 4.2 Summary metrics and range P&L

The header reports the latest selected price-field value, selected-range return, hypothetical P&L on the chosen starting amount, annualized volatility based on close-to-close returns, and maximum close-based drawdown.

For the selected OHLC field `P`, first selected observation `P₀`, last selected observation `P₁`, and hypothetical starting amount `A`:

- **Range return:** `P₁ / P₀ − 1`
- **Hypothetical P&L:** `A × (P₁ / P₀ − 1)`
- **Point change:** the selected field’s end value minus its start value (shown through the return and chart context; not a transaction ledger).

The selected field is a historical price observation. Open, High, and Low are not represented as guaranteed executable prices. The hypothetical calculation omits fees, taxes, slippage, dividends, and position sizing rules.

### 4.3 Charts

- **Index level:** line chart for the selected OHLC field, or candlesticks showing Open, High, Low, and Close. The chart has hover details and a Plotly date-range zoom slider.
- **Daily returns:** close-to-close percentage changes; positive and negative sessions use subdued green and red.
- **Monthly returns:** first available close to last available close per calendar month.
- **Drawdown:** close relative to the running close peak in the selected date window.
- **Rolling volatility:** rolling 21-session sample standard deviation of close returns, annualized by √252.
- **Best-entry scan:** forward return from every eligible selected-field observation to the observation `n` trading sessions later. The highest historical outcome is marked on the chart.
- **Festival study:** close movement around the first available trading session on or after the user-selected festival date, indexed by trading sessions from the event.

### 4.4 Best historical entry scan

The user selects a date range, OHLC field, and holding-period length. For each eligible date `t`, the app calculates `P[t+n] / P[t] − 1` and highlights the maximum observed outcome. It reports the selected historical entry date, forward return, and hypothetical value of the starting amount at the horizon.

This is a hindsight comparison. It is not a prediction, a forward-looking signal, or an investment recommendation. Entry prices are the selected daily OHLC observations and exclude trading frictions.

### 4.5 SIP calculator

The calculator has two modes:

**Historical SIP**

- Uses the selected date range and OHLC price field.
- Simulates one contribution on the first available trading session of each calendar month.
- Buys fractional index units at the selected OHLC field.
- Values accumulated units at the final selected field value.
- Shows number of contributions, total invested, ending value, and historical P&L.

**Future SIP estimate**

- User enters duration in years and an assumed annual return.
- Contributions occur at the end of each month.
- The app converts the annual rate to a monthly equivalent and estimates future value using the ordinary annuity formula. At a zero rate, value equals total contributions.
- Results are hypothetical and exclude fees, taxes, inflation, and changes in the assumed rate.

Neither mode models a mutual fund, tracking error, dividends, expense ratios, tax treatment, or actual fund NAVs. The underlying NIFTY 50 price index itself is not directly investable.

### 4.6 Festival event study

Users select an event label, enter or adjust its calendar date, and choose the number of trading sessions before and after it. The dashboard:

- Uses the first dataset trading session on or after the entered date as the event reference session.
- Reports the close return from the beginning of the before-window to the reference session, from the reference session to the end of the after-window, and across the full window.
- Plots close changes relative to the event-session close, shades the before and after regions, and marks the event on the main price chart when its calendar date falls inside the selected main window.
- Shows a helpful message if the selected event does not have enough surrounding data.

Festival dates can vary by year and region. The event name does not supply a validated year-by-year calendar; users must choose the date they want to study. The chart is descriptive and does not attribute market movement to the festival.

### 4.7 Data table and export

- Shows the most recent 20 observations inside the selected date window.
- Allows download of all selected-window Date, Open, High, Low, and Close values as CSV.

## 5. Data requirements and processing

### Source and format

- Local source: `data.csv` at the repository root.
- Fallback: `src/public/nifty50.csv`.
- Expected columns in order: `Date`, `Open`, `High`, `Low`, `Close`.
- Dates are parsed as timestamps; OHLC values are converted to numeric.
- Upstream dataset location: `https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv`.

### Validation in the app

The app excludes rows containing missing or non-numeric OHLC values, missing dates, non-positive Close values, invalid High/Low relationships, or duplicate dates. Remaining rows are sorted chronologically. `scripts/refresh_data.py` performs a stricter dataset validation before copying the checked-in snapshot to the fallback path.

### Data freshness

The app loads the checked-in snapshot at startup and caches it with Streamlit's data cache. It does not fetch new values automatically. Refreshing the dataset requires an explicit run of `python scripts/refresh_data.py --fetch`, a review of the updated data, and a commit/publish.

## 6. Visual design and interaction

### Brand direction

Use a **GeeksforGeeks-inspired** green identity with a quiet, professional financial-dashboard style. The current interface uses the GeeksforGeeks name as a text label; it does not embed an official logo asset.

### Current palette

| Use | Color |
|---|---|
| Primary brand green | `#087F5B` |
| Market up / secondary green | `#16835D` |
| Market down | `#C2414B` |
| Canvas | `#F5F7F6` |
| Sidebar | `#F0F5F1` |
| Surface / cards | `#FFFFFF` |
| Main text | `#1C2924` |
| Muted text | `#68756F` |
| Borders | `#E2E9E5` |
| Soft green surface | `#E8F4EE` |
| Festival accent | `#E6A23C` |

Use green and red for market direction, neutral gray-green for most labels and axes, and amber only to call attention to the selected event. Avoid large saturated backgrounds and excessive shadows.

### Typography and layout

- Current typeface: Nunito Sans, with a system sans-serif fallback.
- Wide, centered Streamlit layout with a maximum content width around 1320px.
- Sidebar groups exploration controls and festival settings.
- Metrics use white cards, fine borders, and subtle shadows.
- Charts use white surfaces, restrained grid lines, concise labels, and hover details.
- Two-column chart groups collapse through Streamlit's responsive layout on narrow screens.

## 7. Technical architecture

| Layer | Current implementation |
|---|---|
| App framework | Streamlit (`app.py`) |
| Data processing | pandas |
| Charts | Plotly Graph Objects |
| Data source | Local checked-in CSV snapshot |
| Dependency manifest | `requirements.txt` |
| Data refresh/validation | `scripts/refresh_data.py` |
| CI | `.github/workflows/streamlit.yml` installs dependencies, validates the data snapshot, and checks Python syntax |

The Streamlit Community Cloud deployment target should point to the `main` branch and root `app.py`. **This deployment is not configured by the repository workflow.** The current GitHub Actions workflow validates the project; it does not publish a Streamlit app. GitHub Pages cannot execute the Streamlit Python server. Any old Pages deployment is a separate static artifact and is not the current Streamlit application.

### Project structure

```text
.
├── app.py
├── data.csv
├── requirements.txt
├── PRD.md
├── README.md
├── scripts/
│   └── refresh_data.py
├── src/public/nifty50.csv       # validated fallback snapshot
└── .github/workflows/
    └── streamlit.yml            # validation only
```

## 8. Acceptance criteria and current status

| Requirement | Status |
|---|---|
| Run locally with `streamlit run app.py` | Implemented |
| Period presets and custom date range | Implemented |
| Open, High, Low, Close selection and OHLC candle view | Implemented |
| Range return and hypothetical rupee P&L | Implemented |
| Daily/monthly return, drawdown, volatility, and recent rows | Implemented |
| Best historical entry scan for selected holding period | Implemented |
| Historical monthly SIP and assumption-based future SIP | Implemented |
| Festival event date, event highlighting, and before/after window | Implemented with user-entered date |
| CSV download for selected main range | Implemented |
| GFG-inspired subdued visual style | Implemented |
| Dataset and Python syntax validation in GitHub Actions | Implemented |
| Public Streamlit Community Cloud deployment | Not configured yet |
| Direct selection/brush on graph recalculates all metrics | Not implemented; use the sidebar date range |
| Automatically populated festival calendars by year | Not implemented; festival date is user-entered |

## 9. Known limitations and safeguards

- The source is a historical OHLC index series, not adjusted total-return data. It does not include dividends.
- An OHLC field is a daily observation, not a guaranteed transaction price. Hypothetical P&L and historical entry scans omit fees, taxes, slippage, and execution constraints.
- A “best entry” result is selected using future observations inside the chosen historical window. It is therefore hindsight analysis and must remain labeled as such.
- Future SIP output is a scenario based on a fixed user-entered rate, not an expected or guaranteed outcome.
- Festival event windows are calendar-date inputs anchored to trading sessions. An event association is not evidence of causality.
- The current CI workflow does not include automated application-level or browser-interaction tests.
- Public deployment requires configuring Streamlit Community Cloud separately; GitHub Pages is not a compatible runtime.

## 10. Out of scope

- Personalized financial advice, trade recommendations, or market forecasts.
- Live or intraday data feeds, accounts, or broker integrations.
- Dividend-adjusted index performance, mutual-fund NAV data, or fund expense modeling.
- Automatic festival calendar ingestion or causal/event-attribution claims.
- Server-side persistence of user settings or uploaded datasets.

## 11. Future improvements

1. Configure and verify the public Streamlit Community Cloud deployment.
2. Add automated calculation checks and browser-level interaction coverage.
3. Consider a sourced, versioned festival calendar so a user can choose both festival and year without manually entering the date.
4. Consider a selection-capable chart interaction that updates the date filter and all range-based metrics directly from a graph gesture.
5. Add explicit dividend-adjusted or total-return data only when an appropriate licensed source is available.
