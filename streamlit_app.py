# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Import the engine logic from src
from src.market_engine import (
    get_market_data, 
    calculate_basic_metrics, 
    add_technical_indicators, 
    run_forecast,
    run_backtest,
    calculate_volatility
)

# --- PAGE CONFIG (2026 Standards) ---
st.set_page_config(page_title="Stock Performance Engine", layout="wide")

# --- TITLES ---
st.title("📈 Stock Market Performance & Forecasting Engine")
st.markdown("#### *The Story of an Asset: From History to Future*")
st.divider()

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Market Settings")
ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g., AAPL, NVDA, BTC-USD)", value="AAPL")

if st.sidebar.button("Fetch Market Data"):
    # CASCADING RESET: Wipe memory for a clean start on a new ticker
    keys_to_reset = ['stock_df', 'indicators_ready', 'forecast', 'backtest_results']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
            
    data = get_market_data(ticker)
    
    if data is not None:
        st.session_state.stock_df = data
        st.session_state.ticker = ticker
        st.success(f"✅ Ingested data for {ticker}")
    else:
        st.error("❌ Ticker not found. Please use Yahoo Finance symbols.")

# --- PHASE 1: MARKET INGESTION ---
if 'stock_df' in st.session_state:
    st.header("Phase 1: Real-Time Market Ingestion")
    df = st.session_state.stock_df
    metrics = calculate_basic_metrics(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Current {st.session_state.ticker} Price", f"${metrics['current']:.2f}")
    col2.metric("Last Change", f"${metrics['change']:.2f}", f"{metrics['pct']:.2f}%")
    col3.metric("Data Points (2y)", len(df))
    
    with st.expander("🔍 View Raw Market Records"):
        st.dataframe(df.tail(10), width='stretch')

    # --- PHASE 2: TECHNICAL ANALYSIS ---
    st.divider()
    st.header("Phase 2: The Market Pulse")
    
    if st.button("Analyze Trend & Momentum"):
        st.session_state.stock_df = add_technical_indicators(st.session_state.stock_df)
        st.session_state.indicators_ready = True

    if st.session_state.get('indicators_ready'):
        df_ind = st.session_state.stock_df
        
        # Trend Chart
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_ind['Date'], y=df_ind['Close'], name="Close", line=dict(color='white', width=1)))
        fig_trend.add_trace(go.Scatter(x=df_ind['Date'], y=df_ind['SMA_20'], name="20d Trend", line=dict(color='orange')))
        fig_trend.add_trace(go.Scatter(x=df_ind['Date'], y=df_ind['SMA_50'], name="50d Trend", line=dict(color='blue')))
        fig_trend.update_layout(template="plotly_dark", height=500, hovermode="x unified")
        st.plotly_chart(fig_trend, width='stretch')
        
        rsi_val = df_ind['RSI'].iloc[-1]
        st.subheader(f"Momentum Gauge (RSI): {rsi_val:.2f}")
        if rsi_val > 70: st.error("🔥 Overbought: Price may cool down.")
        elif rsi_val < 30: st.success("❄️ Oversold: Potential buy zone.")
        else: st.info("⚖️ Neutral Momentum.")

        # --- PHASE 3: AI FORECAST ---
        st.divider()
        st.header("Phase 3: AI Forward Forecast")
        
        if st.button("🚀 Run AI Prediction"):
            with st.spinner("AI analyzing patterns..."):
                model, forecast = run_forecast(st.session_state.stock_df)
                st.session_state.forecast = forecast

        if 'forecast' in st.session_state:
            fc = st.session_state.forecast
            
            # High-Contrast Forecast Chart
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat_upper'], mode='lines', line=dict(width=0), showlegend=False))
            fig_fc.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat_lower'], mode='lines', line=dict(width=0), 
                                        fill='tonexty', fillcolor='rgba(150, 150, 150, 0.2)', name="Risk Range"))
            fig_fc.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], name="AI Target", line=dict(color='#FFD700', width=3)))
            
            fig_fc.update_layout(template="plotly_dark", height=500, hovermode="x unified")
            st.plotly_chart(fig_fc, width='stretch')
            
            with st.expander("📅 View Prediction Ledger (Next 30 Days)"):
                ledger = fc[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)
                st.dataframe(ledger.set_index('ds'), width='stretch')

            # --- PHASE 4: RISK & VOLATILITY ---
            # Unlocked by Phase 3
            st.divider()
            st.header("Phase 4: Risk & Volatility Assessment")
            vol_score = calculate_volatility(st.session_state.stock_df)
            
            v_col1, v_col2 = st.columns(2)
            v_col1.metric("Annualized Volatility", f"{vol_score:.2f}%")
            with v_col2:
                if vol_score > 40: st.error("⚠️ HIGH RISK")
                elif vol_score > 20: st.warning("⚖️ MODERATE RISK")
                else: st.success("🛡️ LOW RISK")

            # --- PHASE 5: BACKTESTING ---
            # Unlocked by Phase 4
            st.divider()
            st.header("Phase 5: The Reality Check (Backtesting)")
            
            if st.button("⏪ Run 30-Day Backtest"):
                with st.spinner("Testing AI accuracy..."):
                    st.session_state.backtest_results = run_backtest(st.session_state.stock_df)

            if 'backtest_results' in st.session_state:
                res = st.session_state.backtest_results
                acc = 100 - res['Error (%)'].mean()
                st.subheader(f"AI Performance Accuracy: {acc:.2f}%")
                
                fig_bt = go.Figure()
                # Actual in Neon Green
                fig_bt.add_trace(go.Scatter(x=res['ds'], y=res['Actual'], name="REAL Market", 
                                            line=dict(color='#00FF00', width=4), mode='lines+markers'))
                # Prediction in Neon Pink
                fig_bt.add_trace(go.Scatter(x=res['ds'], y=res['yhat'], name="AI Guess", 
                                            line=dict(color='#FF00FF', width=4, dash='dashdot')))
                
                fig_bt.update_layout(template="plotly_dark", height=500, hovermode="x unified")
                st.plotly_chart(fig_bt, width='stretch')
else:
    st.info("Enter a ticker in the sidebar and fetch data to start the market story.")
