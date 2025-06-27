import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import plotly.graph_objs as go

st.set_page_config(page_title="Crypto Signal Dashboard", layout="wide")
st.title("📊 Crypto Signal Dashboard – RSI, MACD, EMA")

coin = st.text_input("Enter a cryptocurrency symbol (e.g. BTC-USD, ETH-USD, SOL-USD):", value="BTC-USD")
interval = st.selectbox("Select timeframe", ['1h', '1d'], index=0)
days = st.slider("Select number of past days to analyze", 5, 90, 30)

try:
    df = yf.download(coin, period=f"{days}d", interval=interval)
    df.dropna(inplace=True)

    df['EMA50'] = EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close']).rsi()
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['SignalLine'] = macd.macd_signal()

    latest = df.iloc[-1]
    signal = "⏸ No clear signal"
    if latest['RSI'] < 30 and latest['EMA50'] > latest['EMA200']:
        signal = "✅ BUY Signal (Oversold RSI + Bullish EMA)"
    elif latest['RSI'] > 70 and latest['EMA50'] < latest['EMA200']:
        signal = "🔻 SELL Signal (Overbought RSI + Bearish EMA)"

    st.subheader(f"📢 Trade Signal: {signal}")
    st.write(f"**Latest RSI:** {round(latest['RSI'], 2)}")
    st.write(f"**MACD:** {round(latest['MACD'], 4)}")
    st.write(f"**Signal Line:** {round(latest['SignalLine'], 4)}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Candlesticks'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='blue'), name='EMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='red'), name='EMA 200'))

    fig.update_layout(
        title=f"{coin} Price Chart with EMA, RSI, MACD",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")