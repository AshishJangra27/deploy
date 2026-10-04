# NIFTY 50 Interactive Market Dashboard — Product Requirements Document

> **Implementation update (4 October 2026):** The project owner later requested a Streamlit implementation. This overrides the original static GitHub Pages/marimo deployment architecture below. The current app entry point is root `app.py`; deployment is through Streamlit Community Cloud. GitHub Pages cannot execute the Streamlit server.

**Status:** Product and implementation brief  
**Version:** 1.0  
**Date:** 4 October 2026  
**Working name:** NiftyScope

## 1. Product summary

NiftyScope is a responsive, browser-based dashboard for exploring the long-run daily performance and risk of the NIFTY 50 index. It turns daily OHLC index data into an approachable, interactive experience for learners and market observers: users can choose a time range, inspect prices and returns, compare periods, and understand drawdowns and volatility without needing a local Python installation.

The project is an educational data-visualization product, not a trading terminal. It will be built primarily in Python and published as a static site on GitHub Pages. The deployed dashboard must not depend on a running Python server, paid data service, login, or API key.

## 2. User problem and opportunity

Raw historical price rows are difficult to interpret. A useful dashboard should let a visitor answer questions such as:

- How did the index move over a selected period?
- What was the return over that period, and how did it compare with another period?
- When were the largest drawdowns and most volatile stretches?
- How often did daily or monthly returns fall into different ranges?
- What do the open, high, low, and close fields mean?

The experience should keep the main trend legible while making the calculations and data limits visible.

## 3. Goals and non-goals

### Goals

1. Deliver a polished, responsive, interactive NIFTY 50 historical-data dashboard.
2. Make the dataset’s dates, OHLC fields, return calculations, and limitations transparent.
3. Keep the deployment compatible with GitHub Pages static hosting.
4. Keep implementation and analytical transformations in Python wherever practical, with minimal custom JavaScript and no custom C code.
5. Make the site usable on desktop, tablet, and mobile, including keyboard interaction and clear chart labels.
6. Provide a reproducible workflow for updating the bundled dataset and publishing the site.

### Non-goals for the first release

- Intraday streaming prices, brokerage integration, alerts, account features, or order placement.
- Constituents, sector breakdowns, or constituent-level comparisons: this file is index OHLC only.
- Forecasts or investment recommendations.
- A server-backed API, database, user accounts, or collection of personal data.
- Promising live/current prices or automatic daily data refresh when the source is a historical CSV.

## 4. Users and primary use cases

### Primary audience

- Students learning time-series and financial-market analysis.
- Curious investors who want to explore index history, not execute trades.
- Developers and data-science learners looking for a readable Python visualization project.

### Core user journeys

1. **Quick overview:** Open the dashboard, see the covered date range and latest included close, then scan return and drawdown summary cards.
2. **Explore a period:** Choose a preset or custom date interval; charts and summary statistics update together.
3. **Inspect a move:** Hover/focus a chart point to read the date and OHLC values; zoom or reset the view.
4. **Understand risk:** Open the drawdown or rolling-volatility view, see how the selected period compares with its own prior peak, and read a concise definition.
5. **Download and verify:** Download the data currently used by the page and follow a direct link to the source CSV.

## 5. Dataset and data contract

### Verified source

- Source repository: `https://github.com/AshishJangra27/datasets`
- Correct raw CSV URL: `https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv`
- The originally supplied URL uses `Nifty50` in the path. The repository folder is `Nifty-50`; use the corrected path above.
- The file has 6,315 lines including the header (6,314 observations), 258 KB at the time inspected, and columns `Date, Open, High, Low, Close`.
- The earliest visible observation is 2000-01-03. The final date must be derived from the checked-in dataset at build/update time and shown in the interface; do not hard-code “today” or imply coverage through today.
- Data source was inspected on 4 October 2026. Recheck the repository before implementation and each data refresh.

### Field meanings

| Field | Type | Meaning | Dashboard use |
|---|---|---|---|
| `Date` | Date | Trading session date | X-axis, date filter, aggregation key |
| `Open` | Decimal | Index opening level | OHLC detail and optional candlestick view |
| `High` | Decimal | Session high | OHLC detail and optional candlestick view |
| `Low` | Decimal | Session low | OHLC detail and optional candlestick view |
| `Close` | Decimal | Session closing level | Main price series and return calculations |

There is no volume, ticker/constituent, turnover, dividend, or macroeconomic field in this dataset. Do not show volume charts or imply stock-level constituent analysis.

### Ingestion and validation requirements

- Bundle a versioned copy of the CSV with the site so Pages deployment does not depend on browser cross-origin access to `raw.githubusercontent.com`.
- Keep the source URL and data attribution beside the data refresh instructions.
- Parse `Date` as a date and OHLC values as finite numeric values.
- Sort ascending by date; detect duplicate dates, missing values, non-numeric values, and invalid OHLC relationships (`High` below open/close, `Low` above open/close, or `Low > High`). Report validation problems during the build/update process.
- Do not silently fabricate, interpolate, or forward-fill observed price data. If rows must be excluded due to invalid fields, expose the excluded-row count and document why.
- Confirm the dataset is chronological and that `Close` is positive before calculating percentage/log returns.
- Display source, date coverage, last data refresh/check date, and row count in the dashboard’s About/Data panel.
- Provide a clear loading state and recoverable error message if the browser cannot load or parse the bundled data.

## 6. Product scope and features

### P0 — first release

#### A. Overview and controls

- Dashboard title, short explanation, data coverage badge, and source link.
- Date-range presets: 1Y, 3Y, 5Y, 10Y, all time, plus custom start/end dates.
- Preset ranges clamp to available dates and display the actual selected start and end.
- One consistent filter state drives all charts and KPIs.
- Reset-to-default control and accessible labels for controls.

#### B. Summary cards

- Latest close in the selected period.
- Period price return: `(last close / first close - 1) × 100`.
- Period absolute point change.
- Annualized volatility estimate for the selected daily returns.
- Maximum drawdown in the selected interval.

Each card includes units, period context, and a concise tooltip or caption explaining the definition. Do not label a point change as an investment return.

#### C. Main price chart

- Default to a clean closing-price line chart with date on x-axis and index points on y-axis.
- Tooltip shows date, close, open, high, low, and period-to-date return where available.
- Range selector/brush, zoom, pan, and reset controls on desktop; sensible touch-friendly behavior on mobile.
- Optional OHLC candlestick mode as a chart toggle if it remains legible and accessible; line mode remains the default.
- Do not normalize prices unless the user explicitly switches to a clearly labeled indexed comparison view.

#### D. Returns view

- Daily percentage return series, based on consecutive available closes.
- Monthly return bars calculated from the first and last available close in each calendar month.
- Positive and negative values use color plus sign/position; color is not the only signal.
- Optional return-distribution histogram with clearly labeled binning and count/proportion toggle.

#### E. Risk view

- Drawdown series: `close / running maximum close - 1`, scoped to selected period. Explain that the first selected observation establishes the initial peak.
- Rolling annualized volatility, default 21 trading observations: standard deviation of daily simple returns multiplied by `sqrt(252)` and 100. Clearly indicate the rolling window and annualization convention.
- Maximum drawdown and its trough date for the selected period.
- Explain that historical volatility/drawdown describe past data and are not forecasts.

#### F. Data table and export

- Paginated or virtualized data table for the selected date range, sorted by date, with search not required for first release.
- Download selected-range rows as CSV.
- Download the source CSV or reset to full dataset.
- Format dates consistently (`DD MMM YYYY` in display, ISO `YYYY-MM-DD` in exports) and numeric values to a sensible number of decimals without modifying raw downloads.

#### G. About, definitions, and disclosure

- Collapsible methodology panel defining price return, daily return, monthly return, rolling volatility, and drawdown.
- Cite and link the source dataset; show the included data range and latest observation date.
- Short educational-use notice: historical data only; no investment advice; no guarantee of completeness or accuracy; verify decisions with authoritative sources.

### P1 — follow-up enhancements

- Compare two selected date ranges by rebasing each to 100, with explicit labeling that this compares percentage movement rather than index points.
- Calendar heatmap of monthly returns.
- Best/worst trading sessions and best/worst months for the current selection.
- Bookmarkable URL query parameters for date range and chart tab, if supported cleanly by the selected framework.
- Light/dark theme toggle with persisted preference.
- Small “market timeline” annotations for user-curated historical milestones, only after sources and neutral descriptions are reviewed.

## 7. Metrics and acceptance criteria

### Product success signals

- A first-time visitor can locate the date range and understand what dataset is loaded without reading documentation.
- A visitor can change the range and see the price, return, risk, and KPI views respond coherently.
- The dashboard can be loaded from a GitHub Pages URL with no backend service.
- The same input data and selected range always produce the same figures.

### Release acceptance criteria

1. Every displayed data date is within the bundled CSV’s actual coverage, and the displayed latest observation equals the maximum parsed date.
2. The site has no dependency on a Python server at runtime and no external secret/API key.
3. Range controls affect all dependent summaries and visualizations consistently.
4. Return, monthly aggregation, volatility, and drawdown definitions match the formulas in this document.
5. Invalid/missing data is surfaced through validation or a user-visible error state; it is never silently presented as valid.
6. CSV export contains the selected observations and stable column names.
7. Core content remains understandable on narrow mobile screens; charts and controls do not require hover alone.
8. Charts include titles/axis labels, readable tooltips, and a non-color cue for gains/losses.
9. The page has a visible data-source link and historical-data disclosure.
10. GitHub Pages build/deployment succeeds from the documented workflow, and a clean clone can reproduce the static site.

## 8. Information architecture and layout

### Single-page structure

1. **Top bar:** NiftyScope wordmark, Overview / Returns / Risk / Data navigation, theme control (P1), About link.
2. **Intro row:** title, purpose sentence, “Historical data through {latest date}” badge, source link.
3. **Filter rail:** preset range buttons and custom date inputs, with reset.
4. **KPI row:** five summary cards.
5. **Primary panel:** large closing-price chart with chart-type toggle and range selection.
6. **Analysis grid:** returns chart, drawdown chart, rolling volatility chart.
7. **Data panel:** selected-range table and downloads.
8. **Methodology/footer:** definitions, source, coverage, refresh/check date, disclaimer.

On mobile, use a single column, horizontally scrollable or wrapping range presets, compact KPI cards, and charts stacked in the same story order. Avoid dense sidebars and tiny controls.

## 9. Visual design system

### Art direction

Minimal financial research desk: neutral paper-like canvas, crisp typography, restrained color, generous spacing, subtle dividers, and charts as the visual focus. Avoid gradients, skeuomorphic trading widgets, blinking live-price cues, and decorative market noise.

### Color palette

| Token | Hex | Use |
|---|---|---|
| `canvas` | `#F5F7FA` | Page background |
| `surface` | `#FFFFFF` | Cards and chart panels |
| `ink` | `#17212B` | Primary text |
| `muted` | `#657386` | Supporting text and labels |
| `line` | `#E2E8F0` | Borders, gridlines, separators |
| `brand` | `#1D4ED8` | Primary action, selected state, main price line |
| `brand-soft` | `#DBEAFE` | Selection/range highlight |
| `positive` | `#16835D` | Positive return / up candle |
| `negative` | `#C2414B` | Negative return / down candle |
| `neutral` | `#8A6A16` | Caution and context badges |
| `focus` | `#7C3AED` | Visible keyboard focus ring |

Positive/negative colors are paired with plus/minus signs, line direction, and labels. Keep contrast strong enough for text and control states; validate contrast during implementation. In dark mode (P1), define equivalent tokens instead of inverting colors mechanically.

### Typography

- **Primary:** `Inter` (self-hosted or via a dependable static asset), with `system-ui`, `-apple-system`, `Segoe UI`, sans-serif fallback.
- **Numerals:** tabular numerals for KPI values and tables (`font-variant-numeric: tabular-nums`).
- Use a restrained scale: 12–13 px labels, 14–16 px body, 20–24 px section titles, 30–36 px page title, 28–36 px KPI values.
- Avoid light font weights for chart labels; preserve readability at mobile sizes.

### UI and UX design approach

- Use **Material Design 3 principles** selectively for clear hierarchy, accessible touch targets, focus states, and predictable controls; do not import a heavy component system solely for appearance.
- Use **WCAG 2.2 AA** as the accessibility target: keyboard-operable controls, visible focus, meaningful headings, sufficient contrast, text labels, responsive reflow, and no color-only encoding.
- Follow progressive disclosure: keep the overview calm; put formulas and full data details in clearly named panels.
- Ensure consistent selection state across charts, cards, and exports.
- Use plain language and explain financial terms at first use.
- Respect reduced-motion preferences; avoid animation that obscures data.
- Provide loading, empty-range, no-data, and parse-error states.

## 10. Technical architecture and deployment

### Recommended architecture

This must be a static site because GitHub Pages serves static files and does not run a persistent Python app server. Keep the application logic in Python using **marimo exported as a WebAssembly (Pyodide) app**, with Python data processing and interactive controls running in the visitor’s browser. Use a supported Python plotting library such as **Plotly** for interactive charts; use **pandas** only if the bundled runtime size and load time remain acceptable. Prefer Python standard library for small parsing/aggregation tasks when practical. Avoid hand-written C extensions and custom JavaScript; a small amount of framework glue is acceptable only where the browser runtime requires it.

Do not use Streamlit, Dash server mode, Flask, FastAPI, or any approach that expects a persistent Python process on GitHub Pages. Before committing to a specific export/runtime path, verify current marimo static export capabilities and package compatibility in a short prototype; the application must still publish as static assets and load without a server.

### Suggested repository layout

```text
proj/
├── PRD.md
├── README.md
├── pyproject.toml
├── data/
│   ├── nifty50.csv                 # versioned deployment copy
│   └── DATA_SOURCE.md              # source URL, license/attribution notes, refresh date
├── src/
│   ├── app.py                      # marimo application and view composition
│   ├── data.py                     # loading, validation, calculations
│   └── charts.py                   # reusable chart configuration
├── scripts/
│   └── refresh_data.py             # controlled download + validation workflow
└── .github/workflows/
    └── pages.yml                   # build/export and Pages deployment
```

Names may adapt to the framework’s required structure, but keep data validation, calculations, presentation, and deployment steps separable and readable.

### Python libraries and implementation constraints

- **marimo:** Python-first reactive UI/notebook authoring and static/WebAssembly deployment candidate.
- **pandas:** optional CSV/date handling and period aggregation; use only if supported in the chosen WebAssembly environment.
- **Plotly:** interactive line/candlestick and analytical charts if its integration works reliably in the static export.
- **Python standard library:** `csv`, `datetime`, `statistics`, and `math` for fallback parsing and calculations.
- Keep dependencies pinned and minimal. Avoid a custom backend and unnecessary frontend framework.
- No custom C code. Avoid libraries that require native extensions unavailable to the browser runtime unless their supported WebAssembly wheels are verified.
- Build must emit a static directory suitable for GitHub Pages.

### GitHub Pages deployment

- Use GitHub Actions to install pinned dependencies, validate the dataset, export/build the static app, and publish the generated artifact to GitHub Pages.
- Select one publishing strategy and document it: GitHub Actions artifact deployment is preferred; do not mix it with branch-folder publishing.
- Configure the app’s base path so project-site URLs under `/<repository>/` work (not only a root custom domain).
- Avoid absolute `/assets/...` paths unless base-path-aware.
- Bundle data and required assets in the Pages artifact; use HTTPS for any external font/CDN resource and provide local/system fallbacks.
- Add a README with local authoring/preview instructions, data refresh procedure, deployment setup, and known limitations.
- Keep GitHub Pages build logs free of leaked tokens; use no secret for the read-only public CSV source.

## 11. Data calculations and definitions

Let observations be sorted by trading date and let `C_t` be the closing level on observation `t`.

- **Point change:** `C_last - C_first`.
- **Period price return:** `(C_last / C_first - 1) × 100%`.
- **Daily simple return:** `(C_t / C_(t-1) - 1) × 100%` for consecutive available observations. Never insert non-trading calendar dates.
- **Monthly return:** `(last available close in month / first available close in month - 1) × 100%`. State that the period uses available sessions.
- **Running peak:** cumulative maximum of close within the displayed calculation scope.
- **Drawdown:** `(C_t / running_peak_t - 1) × 100%`.
- **Maximum drawdown:** minimum drawdown in the selected interval. Its peak can precede the trough; define whether the selected window’s first close is the initial peak.
- **Rolling annualized volatility:** sample standard deviation of the last 21 daily simple returns multiplied by `sqrt(252) × 100%`. Suppress values until a full window exists. Label window and annualization assumption.
- **Optional indexed comparison:** each series rebased to 100 at the first in-range close, `C_t / C_first × 100`.

Do not label a return calculated only from index closes as total shareholder return: dividends are not present. Use consistent precision and avoid implying precision beyond the source.

## 12. Accessibility, privacy, and reliability

- All controls work by keyboard; charts provide a textual summary or accessible data table alternative for essential information.
- Do not rely exclusively on hover; provide click/focus tooltips where supported and a table alternative.
- Use semantic headings, labels, button names, and status messages; maintain logical focus order.
- No account, analytics tracker, or personal data collection is required for v1. If optional analytics are added later, disclose them and keep them privacy-conscious.
- Static data and client-side calculations should work without sending selected ranges to a service.
- Fail gracefully if the charting runtime cannot initialize; show a plain message and link/download to the CSV.

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| User-provided URL path is incorrect | Use verified `Nifty-50` path and record correction in README/data metadata. |
| Source CSV changes or becomes unavailable | Bundle a validated snapshot; refresh explicitly and show coverage/refresh date. |
| Python WebAssembly package compatibility changes | Prototype marimo export and chart/runtime dependencies early; pin versions and keep standard-library fallback for parsing/calculations. |
| WebAssembly startup or bundle is too large | Keep dependencies lean, show loading progress, and consider generated static chart data/HTML if runtime performance misses target. |
| GitHub Pages base path breaks assets | Test both project-site base path and local export paths in CI/preview. |
| Long history overwhelms chart or mobile browser | Aggregate only for display at wide ranges if necessary while retaining source rows for detail/export; disclose aggregation behavior. |
| OHLC data is mistaken for tradable constituent data | Name the series as the NIFTY 50 index and explain what the dataset contains. |
| Historical metrics are interpreted as predictions | Add methodology and educational-use disclosure near the dashboard. |

## 14. Delivery plan

1. **Repository and source setup:** inspect project instructions, verify exact source and terms, store source metadata, create pinned Python project environment.
2. **Static runtime prototype:** prove that the chosen Python UI exports to static assets, runs without a server on GitHub Pages, and supports required dependencies.
3. **Data pipeline:** implement CSV validation and tested calculation functions; bundle a known dataset snapshot.
4. **Core dashboard:** build range controls, KPIs, main price chart, returns and risk views, table, download, methodology panel.
5. **Responsive/accessibility pass:** verify keyboard behavior, mobile layout, chart alternatives, labels, contrast, and reduced motion.
6. **Deployment:** configure Pages via GitHub Actions, base path, build artifact, and README instructions.
7. **Release verification:** validate calculations against hand-checkable sample rows, exercise data errors, verify CSV exports, and check deployed URL and refresh workflow.

## 15. Open decisions for implementation

- Confirm whether the corrected `Nifty-50/data.csv` is the intended source and review its license/attribution requirements before redistribution.
- Prototype marimo’s current static/WebAssembly export and Plotly integration against GitHub Pages project subpaths. If the combination is not reliable, choose a Python-generated static artifact pipeline and document which interactions remain possible client-side.
- Decide whether candlesticks belong in v1 after mobile and accessibility checks; the closing-price line chart is mandatory.
- Decide whether data refresh is manual by maintainer or scheduled. Any scheduled refresh must validate the new data before publishing and retain a reproducible snapshot.

## 16. Source reference

- [Dataset file on GitHub](https://github.com/AshishJangra27/datasets/blob/main/Nifty-50/data.csv)
- [Corrected raw CSV URL](https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv)
