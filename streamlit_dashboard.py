import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from arch import arch_model
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BSE Sensex GARCH Volatility Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TITLE & DESCRIPTION ---
st.title("📊 BSE Sensex Volatility Analysis Dashboard")
st.markdown("""
**Interactive GARCH(1,1) Volatility Modeling for BSE Top 30 Stocks**

This dashboard calculates and visualizes historical volatility vs. GARCH-modeled volatility for selected stocks.
""")

# --- TOP 30 BSE SENSEX STOCKS (by market cap/liquidity) ---
BSE_TOP_30 = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "LT": "LT.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "HCLTECH": "HCLTECH.NS",
    "WIPRO": "WIPRO.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "TITAN": "TITAN.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "DRREDDY": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "SBILIFE": "SBILIFE.NS",
    "ITC": "ITC.NS",
    "POWERGRID": "POWERGRID.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "VEDL": "VEDL.NS",
    "SBIN": "SBIN.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
}

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Configuration")

# Stock Ticker Selection
selected_stock_name = st.sidebar.selectbox(
    "Select Stock Ticker:",
    options=list(BSE_TOP_30.keys()),
    index=0
)
ticker_symbol = BSE_TOP_30[selected_stock_name]

# Date Range Selection
st.sidebar.subheader("📅 Date Range")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date:",
        value=datetime.now() - timedelta(days=365*3),
        max_value=datetime.now()
    )
with col2:
    end_date = st.date_input(
        "End Date:",
        value=datetime.now(),
        max_value=datetime.now()
    )

# GARCH Parameters
st.sidebar.subheader("📊 GARCH Model Parameters")
garch_p = st.sidebar.slider("GARCH p (order):", min_value=1, max_value=3, value=1)
garch_q = st.sidebar.slider("GARCH q (order):", min_value=1, max_value=3, value=1)
forecast_horizon = st.sidebar.slider("Forecast Horizon (days):", min_value=1, max_value=30, value=5)

# Rolling Window for Historical Volatility
rolling_window = st.sidebar.slider("Rolling Window (days) for Historical Vol:", min_value=5, max_value=100, value=20)

# --- DATA LOADING ---
st.sidebar.info("⏳ Fetching data... Please wait.")

try:
    # Download data from Yahoo Finance
    data = yf.download(
        ticker_symbol,
        start=start_date,
        end=end_date,
        progress=False,
        show_errors=False
    )
    
    if len(data) == 0:
        st.error(f"❌ No data available for {selected_stock_name}. Try a different stock or date range.")
        st.stop()
    
    # Ensure the dataframe has the required columns
    if isinstance(data.index, pd.MultiIndex):
        data = data[ticker_symbol]
    
    # Clean data
    data = data[['Close']].dropna()
    data.columns = ['close_price']
    
    st.sidebar.success(f"✅ Loaded {len(data)} trading days")
    
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()

# --- DATA PROCESSING ---
# Calculate daily returns
data['returns'] = 100 * data['close_price'].pct_change()
data = data.dropna()

# Remove extreme outliers (data errors)
data_clean = data[(data['returns'] < 20) & (data['returns'] > -20)].copy()

# Calculate historical volatility (rolling standard deviation)
data_clean['hist_volatility'] = data_clean['returns'].rolling(window=rolling_window).std()
data_clean = data_clean.dropna()

# --- GARCH MODEL FITTING ---
if len(data_clean) > 50:
    try:
        model = arch_model(data_clean['returns'], vol='Garch', p=garch_p, q=garch_q)
        results = model.fit(disp='off')
        
        # Get conditional volatility (model's estimate)
        data_clean['garch_volatility'] = results.conditional_volatility
        
        # Forecast future volatility
        forecast = results.forecast(horizon=forecast_horizon)
        forecast_volatility = np.sqrt(forecast.variance.iloc[-1, :].values)
        
        model_fitted = True
    except Exception as e:
        st.warning(f"⚠️ Could not fit GARCH model: {str(e)}")
        model_fitted = False
else:
    st.warning("⚠️ Not enough data to fit GARCH model. Select a longer date range.")
    model_fitted = False

# --- MAIN DASHBOARD LAYOUT ---
# Key Metrics Row
if model_fitted:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Daily Return",
            f"{data_clean['returns'].iloc[-1]:.3f}%"
        )
    
    with col2:
        st.metric(
            "Historical Volatility",
            f"{data_clean['hist_volatility'].iloc[-1]:.3f}%"
        )
    
    with col3:
        st.metric(
            "GARCH Volatility",
            f"{data_clean['garch_volatility'].iloc[-1]:.3f}%"
        )
    
    with col4:
        var_95 = 1.65 * data_clean['garch_volatility'].iloc[-1]
        st.metric(
            "95% VaR",
            f"{var_95:.3f}%",
            delta=f"Downside Risk"
        )

# --- VOLATILITY COMPARISON CHART ---
st.subheader("📈 Volatility Comparison: Historical vs. GARCH Modeled")

if model_fitted:
    fig = go.Figure()
    
    # Historical Volatility
    fig.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean['hist_volatility'],
        mode='lines',
        name='Historical Volatility (Rolling Std)',
        line=dict(color='blue', width=2),
        hovertemplate='<b>Historical Vol</b><br>Date: %{x|%Y-%m-%d}<br>Volatility: %{y:.3f}%<extra></extra>'
    ))
    
    # GARCH Volatility
    fig.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean['garch_volatility'],
        mode='lines',
        name='GARCH Modeled Volatility',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>GARCH Vol</b><br>Date: %{x|%Y-%m-%d}<br>Volatility: %{y:.3f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{selected_stock_name} - Volatility Analysis",
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        height=500,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- RETURNS DISTRIBUTION ---
st.subheader("📊 Daily Returns Distribution")

col1, col2 = st.columns(2)

with col1:
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=data_clean['returns'],
        nbinsx=50,
        name='Daily Returns',
        marker=dict(color='steelblue')
    ))
    
    fig_hist.update_layout(
        title="Returns Distribution",
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency",
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # Statistics Box
    st.write("**Return Statistics**")
    stats_df = pd.DataFrame({
        "Metric": ["Mean", "Std Dev", "Min", "Max", "Skewness", "Kurtosis"],
        "Value": [
            f"{data_clean['returns'].mean():.4f}%",
            f"{data_clean['returns'].std():.4f}%",
            f"{data_clean['returns'].min():.4f}%",
            f"{data_clean['returns'].max():.4f}%",
            f"{data_clean['returns'].skew():.4f}",
            f"{data_clean['returns'].kurtosis():.4f}"
        ]
    })
    st.dataframe(stats_df, hide_index=True, use_container_width=True)

# --- GARCH MODEL SUMMARY ---
if model_fitted:
    st.subheader("📋 GARCH Model Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Model Parameters**")
        st.write(results.summary().tables[1])
    
    with col2:
        st.write("**Forecast**")
        forecast_df = pd.DataFrame({
            "Day": list(range(1, forecast_horizon + 1)),
            "Forecasted Volatility (%)": forecast_volatility
        })
        st.dataframe(forecast_df, hide_index=True, use_container_width=True)

# --- FOOTER ---
st.divider()
st.markdown("""
**Data Source:** Yahoo Finance | **Model:** GARCH(p,q) | **Period:** 1990-2026 (BSE Sensex)

*Disclaimer: This dashboard is for educational purposes only. Historical volatility does not guarantee future results.*
""")
