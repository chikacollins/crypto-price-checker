import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import ta

st.title("📊 Crypto Signal Dashboard – RSI, MACD, EMA")

try:
    coin = st.text_input("Enter a cryptocurrency symbol (e.g. BTC-USD, ETH-USD, SOL-USD):", value="BTC-USD")
    interval = st.selectbox("Select timeframe", ["1h", "4h", "1d"])
    days = st.slider("Select number of past days to analyze", 5, 90, 30)

    df = yf.download(tickers=coin, period=f"{days}d", interval=interval)

    if df.empty:
        st.warning("⚠️ No data found. Please check the symbol or time interval.")
        st.stop()

    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50).ema_indicator().values.flatten()
    df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200).ema_indicator().values.flatten()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi().values.flatten()

    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd().values.flatten()
    df['SignalLine'] = macd.macd_signal().values.flatten()

    latest = df.iloc[-1]
    signal = "⏸️ No clear signal"

    if latest['RSI'] < 30 and latest['EMA50'] > latest['EMA200']:
        signal = "✅ BUY Signal (Oversold RSI + EMA50 > EMA200)"
    elif latest['RSI'] > 70 and latest['EMA50'] < latest['EMA200']:
        signal = "🔻 SELL Signal (Overbought RSI + EMA50 < EMA200)"

    st.subheader(f"📈 Trade Signal: {signal}")
    st.write(f"**Latest RSI:** {round(latest['RSI'], 2)}")
    st.write(f"**MACD:** {round(latest['MACD'], 4)}")
    st.write(f"**Signal Line:** {round(latest['SignalLine'], 4)}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Candlesticks'
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name='EMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='EMA 200'))

    fig.update_layout(
        title=f"{coin} Price Chart with EMA, RSI, MACD",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
