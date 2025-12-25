import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Live Stock Dashboard",
    page_icon="📊",
    layout="wide"
)

# ------------------ AUTO REFRESH ------------------
st_autorefresh(interval=30_000, key="datarefresh")  # refresh every 30 seconds

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.metric-label {
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>📈 Live Stock Market Dashboard</h1>",
    unsafe_allow_html=True
)

# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙️ Dashboard Controls")

ticker = st.sidebar.text_input("Stock Symbol", "AAPL")
period = st.sidebar.selectbox(
    "Time Range",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
)

show_ma = st.sidebar.checkbox("Show Moving Averages", True)

# ------------------ LOAD DATA ------------------
@st.cache_data(ttl=30)
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval="5m")
    return df

data = load_data(ticker, period)

if data.empty:
    st.error("❌ Invalid stock symbol")
    st.stop()

# ------------------ METRICS ------------------
latest = data.iloc[-1]
previous = data.iloc[-2]

price_change = latest["Close"] - previous["Close"]
percent_change = (price_change / previous["Close"]) * 100

color = "green" if price_change > 0 else "red"
arrow = "▲" if price_change > 0 else "▼"

col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Current Price",
    f"${latest['Close']:.2f}",
    f"{arrow} {percent_change:.2f}%"
)

col2.metric(
    "📊 Volume",
    f"{int(latest['Volume']):,}"
)

col3.metric(
    "📈 High / Low",
    f"${latest['High']:.2f} / ${latest['Low']:.2f}"
)

# ------------------ INDICATORS ------------------
data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()

# ------------------ CANDLESTICK CHART ------------------
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Price"
))

if show_ma:
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["MA20"],
        line=dict(color="#00BFFF", width=2),
        name="MA 20"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["MA50"],
        line=dict(color="#FF5733", width=2),
        name="MA 50"
    ))

fig.update_layout(
    height=550,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    title=f"{ticker} Live Price Chart",
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ VOLUME CHART ------------------
st.subheader("🔵 Trading Volume")

volume_fig = go.Figure()
volume_fig.add_trace(go.Bar(
    x=data.index,
    y=data["Volume"],
    marker_color="#7FDBFF"
))

volume_fig.update_layout(
    height=250,
    template="plotly_dark"
)

st.plotly_chart(volume_fig, use_container_width=True)

# ------------------ DATA TABLE ------------------
with st.expander("📄 View Live Data Table"):
    st.dataframe(data.tail(15))
