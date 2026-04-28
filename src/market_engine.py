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

from prophet import Prophet

def run_forecast(df, periods=30):
    """
    Phase 3 Engine: Trains an AI model on historical data 
    to predict the next 30 days of price action.
    """
    # 1. Prepare data for Prophet (Specific naming required)
    train_df = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    
    # 2. Initialize and Train the Model
    # We disable 'yearly_seasonality' to keep it focused on the 2-year trend
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(train_df)
    
    # 3. Create 'Future' dates and Predict
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return model, forecast 

def calculate_volatility(df):
    """
    Calculates the 20-day rolling volatility (Standard Deviation).
    High volatility = Higher Risk.
    """
    # Percentage change of daily prices
    returns = df['Close'].pct_change()
    # Rolling standard deviation of those returns
    volatility = returns.rolling(window=20).std() * (252**0.5) * 100 
    return volatility.iloc[-1]

def run_backtest(df):
    """
    Hides the last 30 days of data, trains the model, 
    and compares the prediction to what actually happened.
    """
    # 1. Split: Hide the last 30 days
    train_data = df[:-30] 
    actual_data = df[-30:]
    
    # 2. Train on the older data
    m = Prophet(daily_seasonality=True)
    m.fit(train_data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}))
    
    # 3. Predict the 30 days we hid
    future = m.make_future_dataframe(periods=30)
    forecast = m.predict(future)
    
    # 4. Compare Prediction (yhat) to Actual (y)
    comparison = forecast[['ds', 'yhat']].tail(30)
    comparison['Actual'] = actual_data['Close'].values
    comparison['Error (%)'] = abs((comparison['Actual'] - comparison['yhat']) / comparison['Actual']) * 100
    
    return comparison
