# NiftyScope

NiftyScope is a Python-first interactive dashboard for exploring daily NIFTY 50 index history. Its charts, calculations, date controls, and CSV download run in Python in the browser through marimo WebAssembly; GitHub Pages only serves static files.

## Features

- Filter by a 1, 3, 5, or 10-year window, or full history, then refine the dates with the range slider.
- View the index close or OHLC candles, daily and monthly returns, drawdown, and rolling annualized volatility.
- Inspect summary metrics and recent rows; download all observations in the selected window.
- Read the metric definitions, source, data coverage, and historical-data disclosure in the page.

## Run locally

Python 3.11 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/refresh_data.py
python -m marimo edit src/app.py
```

To preview the same static WebAssembly export used by Pages:

```bash
python -m marimo export html-wasm src/app.py -o dist --mode run
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Serve over HTTP; opening `index.html` as a `file://` URL can block browser data/runtime loading.

## Data refresh

The refresh script checks the root `data.csv` column schema, dates, duplicates, finite positive values, and OHLC relationships, then copies the validated snapshot to `src/public/nifty50.csv`. That file is included in the exported site and is read locally by the browser app. The default workflow uses this checked-in snapshot for a reproducible deployment; it does not depend on a network fetch during publishing.

```bash
python scripts/refresh_data.py
```

To explicitly refresh from the upstream source, use `python scripts/refresh_data.py --fetch`. The supplied URL had a path typo: the source folder is `Nifty-50`, not `Nifty50`. The script uses the corrected [raw CSV URL](https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv). Review the dataset license/attribution terms before redistributing a refreshed copy.

## GitHub Pages

1. Push this project to a GitHub repository on the `main` branch.
2. In repository **Settings → Pages → Build and deployment**, choose **GitHub Actions** as the source.
3. Push to `main` or run **Build and deploy NiftyScope** from the Actions tab.
4. The workflow validates `data.csv`, exports `src/app.py` as WebAssembly-powered static HTML, and publishes `dist/` to Pages.

The export uses relative assets, so it is intended to work at both a root domain and a project-site path (`/<repository>/`). If dependencies are changed, update both `requirements.txt` and the dependency versions in `src/app.py` and verify the WebAssembly export.

## Definitions

- **Period price return:** last selected close divided by first selected close, minus one. It excludes dividends.
- **Daily return:** change between consecutive available closes.
- **Monthly return:** last available close divided by first available close in each calendar month, minus one.
- **Drawdown:** selected close divided by its running peak within the selected window, minus one.
- **Rolling volatility:** sample standard deviation of the latest 21 daily returns, annualized by multiplying by √252.

This project is for historical exploration and education, not investment advice. See [PRD.md](PRD.md) for full product, design, and delivery requirements.
