"""NiftyScope: a Python-first, static-deployable NIFTY 50 dashboard."""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo==0.24.0",
#   "pandas==2.2.3",
#   "plotly==6.1.2",
# ]
# [tool.marimo.opengraph]
# title = "NiftyScope | NIFTY 50 explorer"
# description = "Explore NIFTY 50 index levels, returns, volatility, and drawdowns."
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full")


@app.cell
def _():
    import math

    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import marimo as mo

    return go, make_subplots, math, mo, pd


@app.cell
def _(mo, pd):
    data_path = mo.notebook_location() / "public" / "nifty50.csv"
    if not data_path.exists():
        raise FileNotFoundError(
            "The bundled NIFTY 50 data file is missing. Run "
            "python scripts/refresh_data.py before opening or exporting the app."
        )

    raw = pd.read_csv(data_path, parse_dates=["Date"])
    expected = ["Date", "Open", "High", "Low", "Close"]
    if list(raw.columns) != expected:
        raise ValueError(f"Expected CSV columns {expected}; found {list(raw.columns)}")

    for _column in expected[1:]:
        raw[_column] = pd.to_numeric(raw[_column], errors="coerce")
    invalid = raw[expected[1:]].isna().any(axis=1) | raw["Date"].isna()
    invalid |= (raw["Close"] <= 0) | (raw["Low"] > raw["High"])
    invalid |= (raw["High"] < raw[["Open", "Close"]].max(axis=1))
    invalid |= (raw["Low"] > raw[["Open", "Close"]].min(axis=1))
    invalid |= raw["Date"].duplicated(keep="last")
    invalid_count = int(invalid.sum())
    raw = raw.loc[~invalid].drop_duplicates(subset="Date", keep="last")
    raw = raw.sort_values("Date").reset_index(drop=True)
    if raw.empty:
        raise ValueError("The dataset has no valid observations after validation.")

    source = "https://github.com/AshishJangra27/datasets/blob/main/Nifty-50/data.csv"
    return invalid_count, raw, source


@app.cell
def _(mo, raw):
    date_options = {
        "Last 1 year": 252,
        "Last 3 years": 756,
        "Last 5 years": 1260,
        "Last 10 years": 2520,
        "Full history": len(raw),
    }
    period = mo.ui.dropdown(
        options=list(date_options), value="Full history", label="Period"
    )
    chart_kind = mo.ui.dropdown(
        options=["Closing price", "OHLC candles"],
        value="Closing price",
        label="Price view",
    )
    return chart_kind, date_options, period


@app.cell
def _(date_options, mo, period, raw):
    row_count = max(2, min(int(date_options[period.value]), len(raw)))
    initial = [len(raw) - row_count, len(raw) - 1]
    date_range = mo.ui.range_slider(
        start=0,
        stop=len(raw) - 1,
        step=1,
        value=initial,
        debounce=True,
        full_width=True,
        label="Drag the handles to refine the date range",
    )
    return date_range,


@app.cell
def _(date_range, math, raw):
    _lo, _hi = sorted(int(v) for v in date_range.value)
    selected = raw.iloc[_lo : _hi + 1].copy().reset_index(drop=True)
    selected["Daily return"] = selected["Close"].pct_change()
    selected["Running peak"] = selected["Close"].cummax()
    selected["Drawdown"] = selected["Close"] / selected["Running peak"] - 1
    selected["Rolling volatility"] = (
        selected["Daily return"].rolling(21).std(ddof=1) * math.sqrt(252) * 100
    )
    selected["Month"] = selected["Date"].dt.to_period("M")
    monthly = selected.groupby("Month", sort=True).agg(
        first_close=("Close", "first"), last_close=("Close", "last")
    )
    monthly["Return"] = (monthly["last_close"] / monthly["first_close"] - 1) * 100
    monthly = monthly.reset_index()
    monthly["Month"] = monthly["Month"].astype(str)
    period_return = selected["Close"].iloc[-1] / selected["Close"].iloc[0] - 1
    point_change = selected["Close"].iloc[-1] - selected["Close"].iloc[0]
    daily_vol = selected["Daily return"].std(ddof=1) * math.sqrt(252)
    max_drawdown = float(selected["Drawdown"].min())
    trough_date = selected.loc[selected["Drawdown"].idxmin(), "Date"]
    return (
        daily_vol,
        max_drawdown,
        monthly,
        period_return,
        point_change,
        selected,
        trough_date,
    )


@app.cell
def _(chart_kind, date_range, invalid_count, mo, period, raw, selected, source):
    _lo, _hi = sorted(int(v) for v in date_range.value)
    _start = selected["Date"].iloc[0].strftime("%d %b %Y")
    _end = selected["Date"].iloc[-1].strftime("%d %b %Y")
    _latest = raw["Date"].iloc[-1].strftime("%d %b %Y")
    _css = r"""
    <style>
    :root { --canvas:#f5f7fa; --surface:#fff; --ink:#17212b; --muted:#657386;
      --line:#e2e8f0; --brand:#1d4ed8; --green:#16835d; --red:#c2414b; }
    body { background:var(--canvas)!important; }
    .nifty-page { max-width:1280px; margin:0 auto; color:var(--ink);
      font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
    .nifty-page * { box-sizing:border-box; }
    .ns-top { display:flex; justify-content:space-between; align-items:center; gap:20px;
      padding:12px 2px 22px; border-bottom:1px solid var(--line); }
    .ns-brand { display:flex; align-items:center; gap:11px; font-weight:750; letter-spacing:-.03em; }
    .ns-mark { display:grid; place-items:center; width:34px; height:34px; border-radius:11px;
      background:#1d4ed8; color:#fff; font-size:16px; }
    .ns-caption,.ns-muted { color:var(--muted); font-size:13px; }
    .ns-status { color:#35506a; background:#eaf1f8; border:1px solid #dce6f0;
      padding:8px 12px; border-radius:999px; font-size:12px; }
    .ns-intro { padding:26px 0 18px; }
    .ns-eyebrow { color:var(--brand); font-size:11px; text-transform:uppercase;
      letter-spacing:.12em; font-weight:700; }
    .ns-intro h1 { font-size:32px; letter-spacing:-.045em; line-height:1.15; margin:8px 0; }
    .ns-intro p { margin:0; color:var(--muted); max-width:680px; font-size:14px; }
    .ns-filter { background:var(--surface); border:1px solid var(--line); border-radius:14px;
      padding:16px 18px; margin-bottom:16px; }
    .ns-filter-head { display:flex; justify-content:space-between; gap:16px; align-items:center;
      margin-bottom:8px; }
    .ns-range { font-size:13px; font-weight:650; font-variant-numeric:tabular-nums; }
    .ns-kpis { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; margin:14px 0; }
    .ns-card,.ns-panel { background:var(--surface); border:1px solid var(--line); border-radius:14px; }
    .ns-card { padding:16px; min-height:102px; }
    .ns-label { font-size:12px; color:var(--muted); margin-bottom:12px; }
    .ns-value { font-size:22px; line-height:1.1; letter-spacing:-.035em; font-weight:700;
      font-variant-numeric:tabular-nums; }
    .ns-positive { color:var(--green); } .ns-negative { color:var(--red); }
    .ns-sub { margin-top:7px; color:var(--muted); font-size:11px; }
    .ns-panel { padding:15px 17px 9px; margin:13px 0; }
    .ns-panel h2 { font-size:15px; letter-spacing:-.015em; margin:3px 0 2px; }
    .ns-panel p { font-size:12px; color:var(--muted); margin:4px 0 8px; }
    .ns-grid { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
    .ns-data-head { display:flex; align-items:center; justify-content:space-between; gap:12px; }
    .ns-footer { color:var(--muted); font-size:12px; padding:18px 3px 36px; line-height:1.7; }
    .ns-footer a { color:var(--brand); }
    @media(max-width:850px) { .ns-kpis { grid-template-columns:repeat(3,minmax(0,1fr)); } }
    @media(max-width:600px) { .nifty-page { padding:0 3px; } .ns-top { align-items:flex-start; }
      .ns-status { max-width:150px; text-align:center; } .ns-intro h1 { font-size:27px; }
      .ns-kpis { grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
      .ns-card { padding:13px; min-height:92px; } .ns-value { font-size:19px; }
      .ns-grid { grid-template-columns:1fr; } .ns-filter-head { align-items:flex-start; flex-direction:column; } }
    </style>
    """
    _header = mo.Html(f"""
      <div class="ns-top"><div class="ns-brand"><span class="ns-mark">N</span>
        <span>NiftyScope <span class="ns-caption">/ market history</span></span></div>
        <span class="ns-status">Historical data through {_latest}</span></div>
      <div class="ns-intro"><div class="ns-eyebrow">India · NIFTY 50 index</div>
        <h1>Read the market, over time.</h1>
        <p>Explore more than two decades of daily index levels, returns and drawdowns.
        Choose a period, then move the range handles to inspect any stretch of history.</p></div>
    """)
    _foot = mo.Html(f"""
      <div class="ns-footer"><b>Data &amp; methodology</b><br>
      Daily index OHLC data · {len(raw):,} rows · {raw['Date'].iloc[0].strftime('%d %b %Y')} to {_latest}.
      Price return uses first and last close; annualized volatility uses daily returns × √252;
      maximum drawdown is measured from the running peak within the selected window.
      {f'{invalid_count} invalid row(s) were excluded.' if invalid_count else ''}<br>
      Source: <a href="{source}" target="_blank" rel="noreferrer">dataset on GitHub</a>.
      Historical data is educational context, not investment advice. Index close returns exclude dividends.</div>
    """)
    _period_cls = "ns-positive" if selected["Close"].iloc[-1] >= selected["Close"].iloc[0] else "ns-negative"
    return _css, _foot, _header, _period_cls


@app.cell
def _(daily_vol, max_drawdown, mo, pd, period_return, period_cls, point_change, selected, trough_date):
    _close = selected["Close"].iloc[-1]
    _cards = [
        ("Latest close", f"{_close:,.2f}", selected["Date"].iloc[-1].strftime("%d %b %Y"), ""),
        ("Period return", f"{period_return:+.2%}", "Close-to-close · price return", period_cls),
        ("Point change", f"{point_change:+,.2f}", "Index points", period_cls),
        ("Annualized volatility", f"{daily_vol:.2%}" if pd.notna(daily_vol) else "—", "Daily returns · 252 sessions", ""),
        ("Maximum drawdown", f"{max_drawdown:.2%}", f"Trough · {trough_date.strftime('%d %b %Y')}", "ns-negative"),
    ]
    _kpis = mo.Html('<div class="nifty-page ns-kpis">' + "".join(
        f'<div class="ns-card"><div class="ns-label">{_label}</div>'
        f'<div class="ns-value {_class}">{_value}</div><div class="ns-sub">{_sub}</div></div>'
        for _label, _value, _sub, _class in _cards
    ) + "</div>")
    return (_kpis,)


@app.cell
def _(chart_kind, go, make_subplots, mo, selected):
    _main = make_subplots(specs=[[{"secondary_y": True}]])
    if chart_kind.value == "OHLC candles":
        _main.add_trace(go.Candlestick(
            x=selected["Date"], open=selected["Open"], high=selected["High"],
            low=selected["Low"], close=selected["Close"], name="NIFTY 50",
            increasing_line_color="#16835d", decreasing_line_color="#c2414b",
        ), secondary_y=False)
    else:
        _main.add_trace(go.Scatter(
            x=selected["Date"], y=selected["Close"], mode="lines", name="Close",
            line={"color":"#1d4ed8", "width":2},
            fill="tozeroy", fillcolor="rgba(29,78,216,.07)",
            hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.2f}</b> points<extra></extra>",
        ), secondary_y=False)
    _main.update_layout(
        height=390, margin={"l":50,"r":18,"t":22,"b":35},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family":"Inter, system-ui, sans-serif","color":"#657386","size":11},
        showlegend=False, hovermode="x unified", xaxis_rangeslider_visible=False,
        xaxis={"showgrid":False,"title":""},
        yaxis={"title":"Index points","gridcolor":"#edf1f5","fixedrange":False},
    )
    _main_panel = mo.Html('<div class="ns-panel"><h2>Index level</h2>'
        '<p>Daily open, high, low and close. Drag the range above to change the selected window.</p></div>')
    return _main, _main_panel


@app.cell
def _(go, make_subplots, mo, monthly, selected):
    _daily = make_subplots(specs=[[{"secondary_y":False}]])
    _daily.add_trace(go.Bar(
        x=selected["Date"], y=selected["Daily return"] * 100,
        marker_color=["#16835d" if _v >= 0 else "#c2414b" for _v in selected["Daily return"].fillna(0)],
        name="Daily return", hovertemplate="%{x|%d %b %Y}<br>%{y:+.2f}%<extra></extra>",
    ))
    _daily.update_layout(height=255, margin={"l":42,"r":8,"t":5,"b":32},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family":"Inter, system-ui, sans-serif","color":"#657386","size":10},
        showlegend=False, xaxis={"showgrid":False},
        yaxis={"title":"Daily %","gridcolor":"#edf1f5","zerolinecolor":"#cbd5e1"})
    _monthly = go.Figure(go.Bar(
        x=monthly["Month"], y=monthly["Return"],
        marker_color=["#16835d" if _v >= 0 else "#c2414b" for _v in monthly["Return"]],
        hovertemplate="%{x}<br>%{y:+.2f}%<extra></extra>",
    ))
    _monthly.update_layout(height=255, margin={"l":42,"r":8,"t":5,"b":32},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family":"Inter, system-ui, sans-serif","color":"#657386","size":10},
        showlegend=False, xaxis={"showgrid":False,"tickangle":-30},
        yaxis={"title":"Monthly %","gridcolor":"#edf1f5","zerolinecolor":"#cbd5e1"})
    return _daily, _monthly


@app.cell
def _(go, mo, selected):
    _risk = go.Figure()
    _risk.add_trace(go.Scatter(
        x=selected["Date"], y=selected["Drawdown"] * 100, name="Drawdown",
        mode="lines", line={"color":"#c2414b","width":1.5},
        fill="tozeroy", fillcolor="rgba(194,65,75,.10)",
        hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}% from peak<extra></extra>",
    ))
    _risk.update_layout(height=250, margin={"l":46,"r":12,"t":8,"b":34},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family":"Inter, system-ui, sans-serif","color":"#657386","size":10},
        showlegend=False, xaxis={"showgrid":False},
        yaxis={"title":"Drawdown %","gridcolor":"#edf1f5"})
    _vol = go.Figure(go.Scatter(
        x=selected["Date"], y=selected["Rolling volatility"], name="21-session volatility",
        mode="lines", line={"color":"#7c3aed","width":1.7},
        hovertemplate="%{x|%d %b %Y}<br>%{y:.1f}% annualized<extra></extra>",
    ))
    _vol.update_layout(height=250, margin={"l":46,"r":12,"t":8,"b":34},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family":"Inter, system-ui, sans-serif","color":"#657386","size":10},
        showlegend=False, xaxis={"showgrid":False},
        yaxis={"title":"Annualized %","gridcolor":"#edf1f5"})
    return _risk, _vol


@app.cell
def _(_css, _daily, _foot, _header, _kpis, _main, _main_panel, _monthly, _risk, _vol, chart_kind, date_range, mo, period, raw, selected):
    _table = mo.ui.table(selected[["Date","Open","High","Low","Close","Daily return"]].tail(20).assign(
        Date=lambda _d: _d["Date"].dt.strftime("%Y-%m-%d"),
        **{"Daily return":lambda _d: (_d["Daily return"] * 100).round(3)},
    ).rename(columns={"Daily return":"Daily return (%)"}))
    _download = mo.download(
        data=selected[["Date","Open","High","Low","Close"]].to_csv(index=False).encode("utf-8"),
        filename="nifty50-selected-range.csv", mimetype="text/csv", label="Download selected rows",
    )
    _top = mo.hstack([period, chart_kind], justify="start", gap=1)
    _range = mo.vstack([_top, date_range])
    _selected_label = mo.Html(
        f'<div class="ns-filter"><span class="ns-label">SELECTED WINDOW</span> '
        f'<span class="ns-range">{selected["Date"].iloc[0].strftime("%d %b %Y")} — '
        f'{selected["Date"].iloc[-1].strftime("%d %b %Y")}</span> '
        f'<span class="ns-caption">{len(selected):,} trading sessions</span></div>'
    )
    _price_card = mo.vstack([_main_panel, _main])
    _daily_card = mo.vstack([
        mo.Html('<div class="ns-panel"><h2>Daily returns</h2><p>Close-to-close changes across available sessions.</p></div>'),
        _daily,
    ])
    _monthly_card = mo.vstack([
        mo.Html('<div class="ns-panel"><h2>Monthly returns</h2><p>First-to-last available close in each month.</p></div>'),
        _monthly,
    ])
    _returns_charts = mo.hstack([_daily_card, _monthly_card], widths="equal")
    _drawdown_card = mo.vstack([
        mo.Html('<div class="ns-panel"><h2>Drawdown from peak</h2><p>Distance below the running close peak in this window.</p></div>'),
        _risk,
    ])
    _vol_card = mo.vstack([
        mo.Html('<div class="ns-panel"><h2>Rolling volatility</h2><p>21 sessions, annualized with √252.</p></div>'),
        _vol,
    ])
    _risk_charts = mo.hstack([_drawdown_card, _vol_card], widths="equal")
    _table_head = mo.Html('<div class="ns-panel"><h2>Recent observations in this range</h2>'
        '<p>Latest 20 selected sessions shown; download includes the full selected range.</p></div>')
    mo.vstack([
        mo.Html(_css),
        _header,
        _selected_label,
        _range,
        _kpis,
        _price_card,
        _returns_charts, _risk_charts,
        _table_head, _table, _download,
        mo.Html(f'<div class="ns-footer">Source CSV snapshot: {len(raw):,} validated rows · selected: {len(selected):,} rows.</div>'),
        _foot,
    ])
    return


if __name__ == "__main__":
    app.run()
