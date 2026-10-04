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
GREEN, RED, BLUE = "#16835d", "#c2414b", "#1d4ed8"

st.set_page_config(page_title="NiftyScope | NIFTY 50", page_icon="📈", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
.stApp { background:#f5f7fa; font-family:'DM Sans',sans-serif; }
.block-container { max-width:1320px; padding-top:1.5rem; }
[data-testid="stMetric"] { background:white; border:1px solid #e2e8f0; border-radius:14px; padding:16px 18px; }
[data-testid="stMetricLabel"] { color:#657386; }
div[data-testid="stVerticalBlock"] > div:has(> .element-container .ns-title) { margin-bottom:0; }
.ns-title { font-size:2rem; font-weight:700; letter-spacing:-.04em; color:#17212b; margin:0; }
.ns-subtitle { color:#657386; margin:.25rem 0 1.2rem; }
.ns-section { font-size:1.05rem; font-weight:650; color:#17212b; margin:1rem 0 .15rem; }
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


st.markdown('<p class="ns-title">NiftyScope <span style="color:#1d4ed8">/</span> NIFTY 50</p>', unsafe_allow_html=True)
st.markdown('<p class="ns-subtitle">Explore index levels, returns, volatility and drawdowns across market history.</p>', unsafe_allow_html=True)

try:
    raw, data_note = load_data()
except Exception as exc:
    st.error(f"Could not load the NIFTY 50 dataset: {exc}")
    st.stop()

with st.sidebar:
    st.header("Explore")
    preset = st.selectbox("Period", ["Full history", "Last 10 years", "Last 5 years", "Last 3 years", "Last 1 year"])
    chart_type = st.radio("Price view", ["Closing price", "OHLC candles"])
    lengths = {"Last 1 year":252, "Last 3 years":756, "Last 5 years":1260, "Last 10 years":2520}
    start_default = raw.Date.iloc[max(0, len(raw) - lengths.get(preset, len(raw)))]
    date_window = st.date_input("Date range", value=(start_default.date(), raw.Date.iloc[-1].date()), min_value=raw.Date.iloc[0].date(), max_value=raw.Date.iloc[-1].date())
    st.caption(f"Data: {raw.Date.iloc[0]:%d %b %Y} – {raw.Date.iloc[-1]:%d %b %Y} · {len(raw):,} rows")

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
period_return = selected.Close.iloc[-1] / selected.Close.iloc[0] - 1
volatility = selected["Daily return"].std() * math.sqrt(252)
max_dd = selected.Drawdown.min()
trough = selected.loc[selected.Drawdown.idxmin(), "Date"]

st.caption(f"Selected window · {selected.Date.iloc[0]:%d %b %Y} – {selected.Date.iloc[-1]:%d %b %Y} · {len(selected):,} trading sessions")
k = st.columns(5)
k[0].metric("Latest close", f"{selected.Close.iloc[-1]:,.2f}", selected.Date.iloc[-1].strftime("%d %b %Y"))
k[1].metric("Period return", f"{period_return:+.2%}", "Price return · excludes dividends")
k[2].metric("Point change", f"{selected.Close.iloc[-1]-selected.Close.iloc[0]:+,.2f}", "Index points")
k[3].metric("Annualized volatility", f"{volatility:.2%}" if pd.notna(volatility) else "—", "Daily returns · √252")
k[4].metric("Maximum drawdown", f"{max_dd:.2%}", f"Trough · {trough:%d %b %Y}")

st.subheader("Index level")
fig = go.Figure()
if chart_type == "OHLC candles":
    fig.add_trace(go.Candlestick(x=selected.Date, open=selected.Open, high=selected.High, low=selected.Low, close=selected.Close, name="NIFTY 50", increasing_line_color=GREEN, decreasing_line_color=RED))
else:
    fig.add_trace(go.Scatter(x=selected.Date, y=selected.Close, mode="lines", name="Close", line={"color":BLUE,"width":2}, fill="tozeroy", fillcolor="rgba(29,78,216,.07)", hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.2f}</b> points<extra></extra>"))
fig.update_layout(height=400, margin={"l":10,"r":10,"t":10,"b":10}, paper_bgcolor="white", plot_bgcolor="white", hovermode="x unified", xaxis_rangeslider_visible=False, yaxis_title="Index points", font={"color":"#657386"})
st.plotly_chart(fig, use_container_width=True)

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

st.subheader("Recent observations in this range")
table = selected[["Date","Open","High","Low","Close","Daily return"]].tail(20).copy()
table["Date"] = table.Date.dt.strftime("%Y-%m-%d")
table["Daily return"] = (table["Daily return"]*100).round(3)
st.dataframe(table.rename(columns={"Daily return":"Daily return (%)"}), use_container_width=True, hide_index=True)
download = selected[["Date","Open","High","Low","Close"]].to_csv(index=False).encode("utf-8")
st.download_button("Download selected rows as CSV", download, "nifty50-selected-range.csv", "text/csv")
st.divider()
st.caption(f"Data source: [{SOURCE_URL}]({SOURCE_URL}) · {data_note}. Monthly return uses first and last available close per calendar month. Drawdown is measured from the running peak in the selected window. Historical exploration only, not investment advice; index returns exclude dividends.")
