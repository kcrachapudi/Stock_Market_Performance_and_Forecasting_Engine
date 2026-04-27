# src/market_engine.py
import yfinance as yf
import pandas as pd

def get_market_data(ticker):
    """
    Connects to Yahoo Finance and retrieves 2 years of daily data.
    Ensures columns are flattened for easy access.
    """
    try:
        # We add auto_adjust=True to get 'Clean' Close prices
        df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True)
        
        if df.empty:
            return None
            
        # FIX: Flatten MultiIndex columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        
        # KEY STEP: Remove timezone info for the AI
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

def calculate_basic_metrics(df):
    """
    Extracts the 'Vitals' using the flattened 'Close' column.
    """
    # .item() converts a single-value Series into a standard float
    last_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    
    change = last_price - prev_price
    pct_change = (change / prev_price) * 100
    
    return {
        "current": last_price,
        "change": change,
        "pct": pct_change
    }

def add_technical_indicators(df):
    """
    Phase 2 Logic: Trend and Momentum calculations.
    """
    df_copy = df.copy()
    
    # Calculate 20-day and 50-day moving averages
    df_copy['SMA_20'] = df_copy['Close'].rolling(window=20).mean()
    df_copy['SMA_50'] = df_copy['Close'].rolling(window=50).mean()
    
    # RSI (Momentum) calculation
    delta = df_copy['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_copy['RSI'] = 100 - (100 / (1 + rs))
    
    return df_copy
