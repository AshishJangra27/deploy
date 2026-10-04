# NiftyScope

An interactive NIFTY 50 history dashboard built with Python, Streamlit, pandas and Plotly.

## Features

- Choose a preset period or set a custom date range.
- Choose Open, High, Low, or Close as the price field for range return and hypothetical P&L; view the selected field or OHLC candles.
- Explore daily and monthly returns, drawdown, rolling annualized volatility and summary metrics.
- Scan for the best historical entry over a chosen holding period (hindsight analysis).
- Compare a historical monthly SIP in the chosen date range and estimate a future SIP from an assumed annual return.
- Select a festival/date and compare the market for a chosen number of trading sessions before and after it.
- Inspect recent observations and download the selected range as CSV.

## Run locally

Python 3.10 or later:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard reads `data.csv` from the project root. `src/public/nifty50.csv` is used as a fallback.

## Deploy

Streamlit requires a Python server, so GitHub Pages cannot host this app. Deploy it with [Streamlit Community Cloud](https://share.streamlit.io/): select this repository, the `main` branch, and `app.py` as the app entry point. Keep `data.csv` in the repository root so the app can load it. GitHub Actions runs a dataset and syntax validation workflow on pushes and pull requests.

## Data

The checked-in dataset snapshot is validated by `scripts/refresh_data.py`. Run `python scripts/refresh_data.py` to validate the local `data.csv`; run `python scripts/refresh_data.py --fetch` to retrieve the upstream dataset. The source directory is `Nifty-50`.

Metric definitions: period return compares the first and last selected close and excludes dividends; daily returns are close-to-close; monthly returns compare first and last available close per calendar month; drawdown is measured from the running peak in the selected window; rolling volatility is based on 21 sessions and annualized with √252.

Historical exploration only, not investment advice. See [PRD.md](PRD.md) for the full product requirements.
