# 📈 Stock Market Performance & Forecasting Engine
### An AI-Driven Market Sentinel for Time-Series Analysis & Predictive Modeling

## 🎯 Project Overview
In the high-volatility world of finance, raw data is noise. This project builds a professional-grade **Quantitative Analysis Dashboard** that transforms real-time market streams into actionable insights. 

Using **Meta's Prophet** model and **Technical Analysis (TA)**, this engine doesn't just show where a stock has been—it utilizes historical seasonality and momentum to forecast where it is going, backed by a rigorous backtesting framework.

## 🏗️ Technical Architecture
This project implements a **State-Aware Cascading Pipeline**:
- **Real-Time Ingestion:** Live API bridge to Yahoo Finance, handling UTC timezone normalization and MultiIndex flattening.
- **Momentum Engine:** Algorithmic calculation of SMA (Simple Moving Averages) and RSI (Relative Strength Index).
- **Predictive Modeling:** Time-Series forecasting using an Additive Model that accounts for non-linear trends and holiday effects.
- **Integrity Logic:** A custom "Cascading Reset" system in Streamlit to ensure data consistency when switching between assets.

## 🛠️ Tech Stack
- **OS:** Ubuntu (LinData VM)
- **Language:** Python 3.12
- **UI Framework:** Streamlit (2026 Interactive "Story" Mode)
- **Time-Series AI:** Prophet (by Meta)
- **Financial APIs:** yfinance, pandas-ta
- **Visualization:** Plotly (High-Contrast Neon Schematics)

## 📈 Key Engineering Features
- **30-Day Forward Forecast:** Generates a golden price target with a 95% confidence interval (Uncertainty Cloud).
- **Automated Backtesting:** A "Reality Check" phase that hides the last 30 days of data to measure AI precision against actual market results.
- **Annualized Volatility Risk:** Standardizes risk by calculating the 20-day rolling standard deviation, annualized across 252 trading days.
- **Interactive Ledger:** A detailed data grid for quantitative review of predicted price targets and risk boundaries.

## 🚀 How to Run
1. **Clone the Repo:** 
   `git clone https://github.com`
2. **Setup Virtual Env:** 
   `python3 -m venv venv && source venv/bin/activate`
3. **Install Dependencies:** 
   `pip install -r requirements.txt`
4. **Launch the Engine:** 
   `streamlit run streamlit_app.py`

---
*Developed as part of a FinTech Portfolio focused on Time-Series Regression and Market Intelligence.*
