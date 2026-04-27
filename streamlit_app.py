# streamlit_app.py
import streamlit as st
import pandas as pd
from src.market_engine import get_market_data, calculate_basic_metrics

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stock Performance Engine", layout="wide")

# --- TITLES ---
st.title("📈 Stock Market Performance & Forecasting Engine")
st.markdown("#### *Phase 1: Real-Time Market Ingestion*")
st.divider()

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Market Settings")
ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g., AAPL, TSLA, BTC-USD)", value="AAPL")

# --- PHASE 1: DATA INGESTION ---
if st.sidebar.button("Fetch Market Data"):
    # Clear memory for a new ticker
    if 'stock_df' in st.session_state:
        del st.session_state.stock_df
        
    data = get_market_data(ticker)
    
    if data is not None:
        st.session_state.stock_df = data
        st.session_state.ticker = ticker
        st.success(f"✅ Successfully ingested data for {ticker}")
    else:
        st.error("❌ Ticker not found. Please check the symbol.")

# --- STORY PERSISTENCE ---
if 'stock_df' in st.session_state:
    df = st.session_state.stock_df
    metrics = calculate_basic_metrics(df)
    
    # Display Vitals
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Current {st.session_state.ticker} Price", f"${metrics['current']:.2f}")
    col2.metric("24h Change", f"${metrics['change']:.2f}", f"{metrics['pct']:.2f}%")
    col3.metric("Data Points", len(df))
    
    with st.expander("🔍 View Raw Time-Series Data"):
        st.dataframe(df.tail(10), width='stretch')


import plotly.graph_objects as go
from src.market_engine import add_technical_indicators

# --- PHASE 2: TECHNICAL ANALYSIS ---
st.divider()
st.header("Phase 2: The Market Pulse")

if 'stock_df' in st.session_state:
    if st.button("Analyze Trend & Momentum"):
        st.session_state.stock_df = add_technical_indicators(st.session_state.stock_df)
        st.session_state.indicators_ready = True

    if st.session_state.get('indicators_ready'):
        df = st.session_state.stock_df
        
        # Interactive Plotly Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name="Close Price", line=dict(color='white')))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_20'], name="20d Trend", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name="50d Trend", line=dict(color='blue')))
        
        fig.update_layout(title="Price Trend Analysis", template="plotly_dark", height=500)
        st.plotly_chart(fig, width='stretch')
        
        # RSI Analysis
        rsi_val = df['RSI'].iloc[-1]
        st.subheader(f"Momentum Gauge (RSI): {rsi_val:.2f}")
        if rsi_val > 70: st.error("🔥 Overbought (Price may drop)")
        elif rsi_val < 30: st.success("❄️ Oversold (Potential Buy)")
        else: st.info("⚖️ Neutral Momentum")
