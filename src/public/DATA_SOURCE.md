# Data source

- Dataset: NIFTY 50 daily index OHLC history
- Repository file: <https://github.com/AshishJangra27/datasets/blob/main/Nifty-50/data.csv>
- Raw CSV: <https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv>
- Schema: `Date`, `Open`, `High`, `Low`, `Close`
- Snapshot policy: fetch the public CSV during the GitHub Pages build and validate it before export. Local maintainers can refresh it with `python scripts/refresh_data.py`.
- Attribution/licensing: confirm and retain any upstream license and attribution requirements before publishing the bundled copy.

The originally supplied link used `Nifty50` as the folder name; the repository path is `Nifty-50`.
