"""NiftyScope: an interactive Streamlit dashboard for NIFTY 50 history."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_CANDIDATES = (ROOT / "data.csv", ROOT / "src" / "public" / "nifty50.csv")
SOURCE_URL = "https://github.com/AshishJangra27/datasets/blob/main/Nifty-50/data.csv"
GREEN, RED, DARK_GREEN = "#16835d", "#c2414b", "#087f5b"
PALETTE = {"canvas": "#f5f7f6", "surface": "#ffffff", "ink": "#1c2924", "muted": "#68756f", "line": "#e2e9e5", "brand": "#087f5b", "brand_soft": "#e8f4ee"}

st.set_page_config(page_title="NiftyScope | NIFTY 50", page_icon="📈", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;500;600;700;800&display=swap');
.stApp { background:#f5f7f6; font-family:'Nunito Sans',sans-serif; color:#1c2924; }
.block-container { max-width:1320px; padding-top:1.5rem; }
[data-testid="stMetric"] { background:white; border:1px solid #e2e9e5; border-radius:14px; padding:16px 18px; box-shadow:0 2px 10px rgba(20,60,42,.035); }
[data-testid="stMetricLabel"] { color:#68756f; }
div[data-testid="stVerticalBlock"] > div:has(> .element-container .ns-title) { margin-bottom:0; }
.ns-title { font-size:2rem; font-weight:800; letter-spacing:-.04em; color:#1c2924; margin:0; }
.ns-subtitle { color:#68756f; margin:.25rem 0 1.2rem; }
.ns-pill { display:inline-block; background:#e8f4ee; color:#087f5b; border:1px solid #cce7d8; padding:3px 9px; border-radius:99px; font-size:.72rem; font-weight:700; letter-spacing:.04em; }
div[data-testid="stSidebar"] { background:#f0f5f1; }
button[kind="primary"] { background:#087f5b; border-color:#087f5b; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading NIFTY 50 history…")
def load_data() -> tuple[pd.DataFrame, str]:
    path = next((candidate for candidate in DATA_CANDIDATES if candidate.exists()), None)
    if path is None:
        raise FileNotFoundError("Place data.csv in the project root, then reload the app.")
    frame = pd.read_csv(path, parse_dates=["Date"])
    expected = ["Date", "Open", "High", "Low", "Close"]
    if list(frame.columns) != expected:
        raise ValueError(f"Expected columns: {', '.join(expected)}")
    for col in expected[1:]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    invalid = frame[expected[1:]].isna().any(axis=1) | frame.Date.isna()
    invalid |= (frame.Close <= 0) | (frame.Low > frame.High)
    invalid |= frame.High < frame[["Open", "Close"]].max(axis=1)
    invalid |= frame.Low > frame[["Open", "Close"]].min(axis=1)
    invalid |= frame.Date.duplicated(keep="last")
    removed = int(invalid.sum())
    frame = frame.loc[~invalid].drop_duplicates("Date", keep="last")
    return frame.sort_values("Date").reset_index(drop=True), f"{path.name} · {removed:,} invalid rows excluded"


st.markdown('<span class="ns-pill">GEEKSFORGEEKS · MARKET DATA PROJECT</span><p class="ns-title">NiftyScope <span style="color:#087f5b">/</span> NIFTY 50</p>', unsafe_allow_html=True)
st.markdown('<p class="ns-subtitle">Explore index levels, returns, volatility and drawdowns across market history.</p>', unsafe_allow_html=True)

try:
    raw, data_note = load_data()
except Exception as exc:
    st.error(f"Could not load the NIFTY 50 dataset: {exc}")
    st.stop()

with st.sidebar:
    st.markdown("### 🟢 GeeksforGeeks")
    st.caption("NIFTY 50 interactive explorer")
    st.divider()
    st.header("Explore")
    preset = st.selectbox("Period", ["Full history", "Last 10 years", "Last 5 years", "Last 3 years", "Last 1 year"])
    price_field = st.selectbox("Price field for P&L", ["Close", "Open", "High", "Low"], help="P&L and entry-date analysis use this OHLC field. Open/High/Low are illustrative price observations, not guaranteed execution prices.")
    chart_type = st.radio("Chart style", ["Selected price field", "OHLC candles"])
    investment_amount = st.number_input("Hypothetical amount (₹)", min_value=100, max_value=100_000_000, value=100_000, step=10_000)
    holding_sessions = st.slider("Holding period for best-entry scan (sessions)", 5, 252, 21)
    lengths = {"Last 1 year":252, "Last 3 years":756, "Last 5 years":1260, "Last 10 years":2520}
    start_default = raw.Date.iloc[max(0, len(raw) - lengths.get(preset, len(raw)))]
    date_window = st.date_input("Date range", value=(start_default.date(), raw.Date.iloc[-1].date()), min_value=raw.Date.iloc[0].date(), max_value=raw.Date.iloc[-1].date())
    st.divider()
    st.subheader("Festival event study")
    festival = st.selectbox("Festival", ["Diwali", "Holi", "Eid al-Fitr", "Ganesh Chaturthi", "Christmas", "Custom event"])
    suggested_event_dates = {"Diwali": pd.Timestamp("2024-11-01"), "Holi": pd.Timestamp("2024-03-25"), "Eid al-Fitr": pd.Timestamp("2024-04-11"), "Ganesh Chaturthi": pd.Timestamp("2024-09-07"), "Christmas": pd.Timestamp("2024-12-25"), "Custom event": raw.Date.iloc[-1]}
    event_default = min(max(suggested_event_dates[festival].date(), raw.Date.iloc[0].date()), raw.Date.iloc[-1].date())
    festival_date = st.date_input("Festival date", value=event_default, min_value=raw.Date.iloc[0].date(), max_value=raw.Date.iloc[-1].date(), key="festival_date")
    festival_before = st.slider("Sessions before", 1, 60, 10, key="festival_before")
    festival_after = st.slider("Sessions after", 1, 60, 10, key="festival_after")
    st.caption(f"Data: {raw.Date.iloc[0]:%d %b %Y} – {raw.Date.iloc[-1]:%d %b %Y} · {len(raw):,} rows")

festival_ts = pd.Timestamp(festival_date)
if not isinstance(date_window, (tuple, list)) or len(date_window) != 2:
    st.info("Choose a start and end date to view the dashboard.")
    st.stop()
start, end = pd.Timestamp(date_window[0]), pd.Timestamp(date_window[1])
selected = raw.loc[raw.Date.between(start, end)].copy().reset_index(drop=True)
if selected.empty:
    st.warning("No trading sessions fall inside that date range.")
    st.stop()

selected["Daily return"] = selected.Close.pct_change()
selected["Running peak"] = selected.Close.cummax()
selected["Drawdown"] = selected.Close / selected["Running peak"] - 1
selected["Rolling volatility"] = selected["Daily return"].rolling(21).std() * math.sqrt(252) * 100
selected["Month"] = selected.Date.dt.to_period("M")
monthly = selected.groupby("Month", as_index=False).agg(
    first=("Close", "first"), last=("Close", "last")
)
monthly["Month"] = monthly.Month.astype(str)
monthly["Return"] = (monthly["last"] / monthly["first"] - 1) * 100
period_return = selected[price_field].iloc[-1] / selected[price_field].iloc[0] - 1
period_profit = investment_amount * period_return
volatility = selected["Daily return"].std() * math.sqrt(252)
max_dd = selected.Drawdown.min()
trough = selected.loc[selected.Drawdown.idxmin(), "Date"]

st.caption(f"Selected window · {selected.Date.iloc[0]:%d %b %Y} – {selected.Date.iloc[-1]:%d %b %Y} · {len(selected):,} trading sessions")
k = st.columns(5)
k[0].metric(f"Latest {price_field.lower()}", f"{selected[price_field].iloc[-1]:,.2f}", selected.Date.iloc[-1].strftime("%d %b %Y"))
k[1].metric("Selected-range return", f"{period_return:+.2%}", f"{price_field}: first to last")
k[2].metric("Hypothetical P&L", f"₹{period_profit:+,.0f}", f"On ₹{investment_amount:,.0f} invested")
k[3].metric("Annualized volatility", f"{volatility:.2%}" if pd.notna(volatility) else "—", "Close returns · √252")
k[4].metric("Maximum drawdown", f"{max_dd:.2%}", f"Trough · {trough:%d %b %Y}")

st.subheader("Index level")
fig = go.Figure()
if chart_type == "OHLC candles":
    fig.add_trace(go.Candlestick(x=selected.Date, open=selected.Open, high=selected.High, low=selected.Low, close=selected.Close, name="NIFTY 50", increasing_line_color=GREEN, decreasing_line_color=RED))
else:
    fig.add_trace(go.Scatter(x=selected.Date, y=selected[price_field], mode="lines", name=price_field, line={"color":DARK_GREEN,"width":2}, fill="tozeroy", fillcolor="rgba(8,127,91,.07)", hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.2f}</b> points<extra></extra>"))
fig.update_layout(height=400, margin={"l":10,"r":10,"t":10,"b":10}, paper_bgcolor="white", plot_bgcolor="white", hovermode="x unified", xaxis_rangeslider_visible=True, yaxis_title="Index points", font={"color":PALETTE["muted"]})
if start <= festival_ts <= end:
    fig.add_vline(x=festival_ts, line_dash="dot", line_color="#e6a23c", annotation_text=festival, annotation_position="top left")
st.plotly_chart(fig, use_container_width=True)
st.caption("Adjust the date range in the sidebar to recalculate all range-based metrics. Drag the chart's lower range slider to zoom the price view.")

left, right = st.columns(2)
with left:
    st.subheader("Daily returns")
    daily = go.Figure(go.Bar(x=selected.Date, y=selected["Daily return"]*100, marker_color=[GREEN if v >= 0 else RED for v in selected["Daily return"].fillna(0)], hovertemplate="%{x|%d %b %Y}<br>%{y:+.2f}%<extra></extra>"))
    daily.update_layout(height=290, margin={"l":5,"r":5,"t":5,"b":5}, paper_bgcolor="white", plot_bgcolor="white", yaxis_title="Daily %", showlegend=False)
    st.plotly_chart(daily, use_container_width=True)
with right:
    st.subheader("Monthly returns")
    month_fig = go.Figure(go.Bar(x=monthly.Month, y=monthly.Return, marker_color=[GREEN if v >= 0 else RED for v in monthly.Return], hovertemplate="%{x}<br>%{y:+.2f}%<extra></extra>"))
    month_fig.update_layout(height=290, margin={"l":5,"r":5,"t":5,"b":5}, paper_bgcolor="white", plot_bgcolor="white", yaxis_title="Monthly %", showlegend=False, xaxis_tickangle=-35)
    st.plotly_chart(month_fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Drawdown from peak")
    dd = go.Figure(go.Scatter(x=selected.Date, y=selected.Drawdown*100, mode="lines", line={"color":RED}, fill="tozeroy", fillcolor="rgba(194,65,75,.10)", hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}% from peak<extra></extra>"))
    dd.update_layout(height=280, margin={"l":5,"r":5,"t":5,"b":5}, paper_bgcolor="white", plot_bgcolor="white", yaxis_title="Drawdown %")
    st.plotly_chart(dd, use_container_width=True)
with right:
    st.subheader("Rolling volatility")
    vol = go.Figure(go.Scatter(x=selected.Date, y=selected["Rolling volatility"], mode="lines", line={"color":"#7c3aed"}, hovertemplate="%{x|%d %b %Y}<br>%{y:.1f}% annualized<extra></extra>"))
    vol.update_layout(height=280, margin={"l":5,"r":5,"t":5,"b":5}, paper_bgcolor="white", plot_bgcolor="white", yaxis_title="Annualized %")
    st.plotly_chart(vol, use_container_width=True)

st.subheader("Best historical entry in this window")
st.caption(f"Hindsight scan: compares every eligible {price_field.lower()} with the price {holding_sessions} trading sessions later. It cannot identify future best times.")
entry_prices = selected[price_field].astype(float)
entry_returns = entry_prices.shift(-holding_sessions) / entry_prices - 1
eligible_returns = entry_returns.iloc[:-holding_sessions] if len(entry_returns) > holding_sessions else pd.Series(dtype=float)
if eligible_returns.empty or eligible_returns.notna().sum() == 0:
    st.info(f"Select more than {holding_sessions} trading sessions to calculate a best historical entry.")
else:
    best_idx = int(eligible_returns.idxmax())
    best_return = float(eligible_returns.loc[best_idx])
    best_cols = st.columns(3)
    best_cols[0].metric("Best entry date (hindsight)", selected.Date.iloc[best_idx].strftime("%d %b %Y"))
    best_cols[1].metric(f"Return after {holding_sessions} sessions", f"{best_return:+.2%}")
    best_cols[2].metric("Illustrative outcome", f"₹{investment_amount * (1 + best_return):,.0f}", f"from ₹{investment_amount:,.0f}")
    scan = pd.DataFrame({"Date": selected.Date.iloc[:len(eligible_returns)], "Forward return": eligible_returns.to_numpy() * 100})
    scan_fig = go.Figure(go.Scatter(x=scan.Date, y=scan["Forward return"], mode="lines", line={"color":DARK_GREEN,"width":1.6}, name="Forward return"))
    scan_fig.add_trace(go.Scatter(x=[selected.Date.iloc[best_idx]], y=[best_return * 100], mode="markers", marker={"size":11,"color":"#e6a23c","line":{"color":"white","width":2}}, name="Best historical entry", hovertemplate="Best entry · %{x|%d %b %Y}<br>%{y:+.2f}%<extra></extra>"))
    scan_fig.update_layout(height=260, margin={"l":10,"r":10,"t":10,"b":10}, paper_bgcolor="white", plot_bgcolor="white", xaxis_title="Potential entry date", yaxis_title=f"Return after {holding_sessions} sessions (%)", hovermode="x unified", font={"color":PALETTE["muted"]})
    st.plotly_chart(scan_fig, use_container_width=True)

st.subheader("SIP calculator")
st.caption("Compare a historical monthly SIP across the selected data window, or estimate a future SIP using an assumed annual return. Neither includes fees, taxes or dividends.")
sip_amount = st.number_input("Monthly investment (₹)", min_value=100, max_value=10_000_000, value=5_000, step=500, key="sip_amount")
historical_tab, future_tab = st.tabs(["Historical SIP", "Future SIP estimate"])
with historical_tab:
    monthly_buys = selected.assign(_month=selected.Date.dt.to_period("M")).groupby("_month", sort=True).head(1)
    units_bought = float((sip_amount / monthly_buys[price_field]).sum())
    historical_invested = sip_amount * len(monthly_buys)
    historical_value = units_bought * float(selected[price_field].iloc[-1])
    historical_profit = historical_value - historical_invested
    hcols = st.columns(4)
    hcols[0].metric("Monthly investments", f"{len(monthly_buys):,}")
    hcols[1].metric("Total invested", f"₹{historical_invested:,.0f}")
    hcols[2].metric("Value at window end", f"₹{historical_value:,.0f}")
    hcols[3].metric("Historical P&L", f"₹{historical_profit:+,.0f}", f"{historical_profit / historical_invested:+.2%}" if historical_invested else "")
    st.caption(f"Model: one contribution on the first available trading session each month, buying at {price_field}; valued at the selected window's final {price_field}.")
with future_tab:
    fcols = st.columns(2)
    years = fcols[0].number_input("Investment duration (years)", min_value=1, max_value=50, value=10, step=1, key="sip_years")
    annual_rate = fcols[1].number_input("Assumed annual return (%)", min_value=-50.0, max_value=100.0, value=12.0, step=0.5, key="sip_rate")
    months = int(years * 12)
    monthly_rate = annual_rate / 1200
    if abs(monthly_rate) < 1e-12:
        future_value = sip_amount * months
    else:
        future_value = sip_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    contributed = sip_amount * months
    future_cols = st.columns(3)
    future_cols[0].metric("Total contributions", f"₹{contributed:,.0f}")
    future_cols[1].metric("Estimated value", f"₹{future_value:,.0f}")
    future_cols[2].metric("Estimated growth", f"₹{future_value-contributed:+,.0f}")
    st.caption("Estimate assumes end-of-month contributions and a constant monthly equivalent of the annual rate; actual returns vary and can be negative.")

st.subheader(f"{festival} market-window study")
event_ix = int(raw.Date.searchsorted(festival_ts, side="left"))
if event_ix >= len(raw) or event_ix - festival_before < 0 or event_ix + festival_after >= len(raw):
    st.info("The chosen festival date does not have enough surrounding trading sessions in the available dataset. Choose another date or smaller before/after windows.")
else:
    event_slice = raw.iloc[event_ix-festival_before:event_ix+festival_after+1].copy().reset_index(drop=True)
    event_slice["Sessions from festival"] = range(-festival_before, festival_after + 1)
    event_anchor_date = event_slice.Date.iloc[festival_before]
    event_anchor = float(event_slice["Close"].iloc[festival_before])
    event_slice["Change from event close (%)"] = (event_slice.Close / event_anchor - 1) * 100
    pre_change = event_anchor / float(event_slice.Close.iloc[0]) - 1
    post_change = float(event_slice.Close.iloc[-1]) / event_anchor - 1
    event_metrics = st.columns(3)
    event_metrics[0].metric(f"{festival_before} sessions before → event", f"{pre_change:+.2%}")
    event_metrics[1].metric(f"Event → {festival_after} sessions after", f"{post_change:+.2%}")
    event_metrics[2].metric("Full before/after window", f"{(float(event_slice.Close.iloc[-1])/float(event_slice.Close.iloc[0])-1):+.2%}")
    event_fig = go.Figure(go.Scatter(x=event_slice["Sessions from festival"], y=event_slice["Change from event close (%)"], mode="lines+markers", line={"color":DARK_GREEN,"width":2}, marker={"size":5}, hovertemplate="Session %{x:+d}<br>%{y:+.2f}% vs event close<extra></extra>"))
    event_fig.add_vrect(x0=-festival_before, x1=0, fillcolor="rgba(8,127,91,.07)", line_width=0, layer="below")
    event_fig.add_vrect(x0=0, x1=festival_after, fillcolor="rgba(230,162,60,.08)", line_width=0, layer="below")
    event_fig.add_vline(x=0, line_dash="dash", line_color="#68756f")
    event_fig.update_layout(height=310, margin={"l":10,"r":10,"t":10,"b":10}, paper_bgcolor="white", plot_bgcolor="white", xaxis_title="Trading sessions relative to festival date", yaxis_title="Close change vs event session (%)", font={"color":PALETTE["muted"]})
    st.plotly_chart(event_fig, use_container_width=True)
    st.caption(f"Festival date selected: {festival_ts:%d %b %Y}. Reference market session: {event_anchor_date:%d %b %Y} (first session on/after the event date). Window is measured in trading sessions, not calendar days.")
    st.caption("Festival dates are user-selected because observances vary by year and region. This is a descriptive historical comparison, not evidence that a festival caused price changes.")

st.subheader("Recent observations in this range")
table = selected[["Date","Open","High","Low","Close","Daily return"]].tail(20).copy()
table["Date"] = table.Date.dt.strftime("%Y-%m-%d")
table["Daily return"] = (table["Daily return"]*100).round(3)
st.dataframe(table.rename(columns={"Daily return":"Daily return (%)"}), use_container_width=True, hide_index=True)
download = selected[["Date","Open","High","Low","Close"]].to_csv(index=False).encode("utf-8")
st.download_button("Download selected rows as CSV", download, "nifty50-selected-range.csv", "text/csv")
st.divider()
st.caption(f"Data source: [{SOURCE_URL}]({SOURCE_URL}) · {data_note}. Monthly return uses first and last available close per calendar month. Drawdown is measured from the running peak in the selected window. Historical exploration only, not investment advice; index returns exclude dividends.")
