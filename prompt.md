# Reusable PRD Prompt

Copy and use this prompt with an AI assistant:

```text
Write a build-ready Product Requirements Document (PRD) for “NiftyScope,” a GeeksforGeeks-inspired dashboard for exploring NIFTY 50 historical data. Make it self-contained so a developer with no prior context can build the project.

Product and implementation requirements:
- Build the app in Python with Streamlit, pandas, and Plotly. Use a local CSV snapshot with columns Date, Open, High, Low, Close. Source: https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv
- Deploy with Streamlit Community Cloud using root app.py. GitHub Actions should validate dependencies, the dataset, and Python syntax. GitHub Pages is incompatible because it cannot run a Streamlit server.
- Include period presets (1, 3, 5, 10 years, full history), a custom date range, Open/High/Low/Close selection, closing-field line or OHLC candlestick chart, summary metrics, daily/monthly returns, drawdown, rolling volatility, recent rows, and CSV download.
- Range P&L compares the first and last selected OHLC field values and scales that return by a user-entered hypothetical amount. Explain that Open/High/Low are observed values, not guaranteed execution prices.
- Add a hindsight entry scan: find the best historical entry within the selected range for a user-selected holding period in trading sessions; clearly label it as hindsight, not a forecast.
- Add historical SIP simulation (one monthly contribution on the first available session of each month, bought at the selected field and valued at the range end) and a future SIP estimator using duration and an assumed annual return with end-of-month contributions.
- Add a festival event study with festival selection, user-entered date, and adjustable before/after trading-session windows. Anchor on the first market session on or after the date; show before, after, and total close returns; highlight the date/window. Do not imply causation. Festival dates vary by year, so do not claim an automatic calendar unless one is separately sourced and implemented.
- Use a calm, professional, GFG-inspired green palette: primary #087F5B, secondary/up #16835D, down #C2414B, canvas #F5F7F6, sidebar #F0F5F1, white cards, ink #1C2924, muted text #68756F, borders #E2E9E5. Use Nunito Sans with a system sans-serif fallback, generous spacing, subtle cards, responsive columns, and accessible contrast. Treat the GFG identity as inspired styling; do not invent or embed an official logo.
- Validate CSV schema, numeric values, dates, duplicates, and OHLC relationships; sort valid rows by date. Document data freshness, assumptions, limitations, and financial disclaimers.

Organize the PRD with: product summary and goals, target users and jobs, scope and detailed features, exact metric/calculation definitions, data requirements and validation, interaction flows, visual design system, technical architecture and deployment, acceptance criteria, known limitations, out-of-scope items, and future improvements. Distinguish what is implemented from what remains planned. Be specific, concise, and do not promise features that are not in the requirements above.
```
