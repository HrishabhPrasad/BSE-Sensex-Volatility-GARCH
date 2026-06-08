import streamlit as st
import pandas as pd
import numpy as np
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

selected_stock_name = st.sidebar.selectbox(
    "Select Stock Ticker:",
    options=list(BSE_TOP_30.keys()),
    index=0
)
ticker_symbol = BSE_TOP_30[selected_stock_name]

st.sidebar.subheader("📅 Date Range")
yesterday = datetime.now() - timedelta(days=1)
start_date = st.sidebar.date_input(
    "Start Date:",
    value=datetime.now() - timedelta(days=365 * 3),
    max_value=yesterday
)
end_date = st.sidebar.date_input(
    "End Date:",
    value=yesterday,
    max_value=yesterday
)

st.sidebar.subheader("📊 GARCH Model Parameters")
garch_p = st.sidebar.slider("GARCH p (order):", min_value=1, max_value=3, value=1)
garch_q = st.sidebar.slider("GARCH q (order):", min_value=1, max_value=3, value=1)
forecast_horizon = st.sidebar.slider("Forecast Horizon (days):", min_value=1, max_value=30, value=5)
rolling_window = st.sidebar.slider("Rolling Window (days) for Historical Vol:", min_value=5, max_value=100, value=20)

# --- DATA LOADING ---
# Raises on empty so failed fetches are never cached — forces a fresh attempt next run.
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    # Flatten MultiIndex columns returned by newer yfinance versions
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    if len(data) == 0:
        raise ValueError("empty")
    return data[['Close']].dropna()

status = st.sidebar.empty()
status.info("⏳ Fetching data...")

if st.sidebar.button("🔄 Refresh Data"):
    load_data.clear()

try:
    data = load_data(ticker_symbol, start_date, end_date)
    data.columns = ['close_price']
    status.success(f"✅ Loaded {len(data)} trading days")

except ValueError:
    st.error(
        f"❌ Yahoo Finance returned no data for **{selected_stock_name}** "
        f"({start_date} → {end_date}). "
        f"This is usually a temporary Yahoo Finance issue — click **🔄 Refresh Data** in the sidebar to retry."
    )
    st.stop()

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()

# --- DATA PROCESSING ---
data['returns'] = 100 * data['close_price'].pct_change()
data = data.dropna()

data_clean = data[(data['returns'] < 20) & (data['returns'] > -20)].copy()
data_clean['hist_volatility'] = data_clean['returns'].rolling(window=rolling_window).std()
data_clean = data_clean.dropna()

# --- GARCH MODEL FITTING ---
model_fitted = False
if len(data_clean) > 50:
    try:
        model = arch_model(data_clean['returns'], vol='Garch', p=garch_p, q=garch_q)
        results = model.fit(disp='off')
        data_clean['garch_volatility'] = results.conditional_volatility
        forecast = results.forecast(horizon=forecast_horizon)
        forecast_volatility = np.sqrt(forecast.variance.iloc[-1, :].values)
        model_fitted = True
    except Exception as e:
        st.warning(f"⚠️ Could not fit GARCH model: {str(e)}")
else:
    st.warning("⚠️ Not enough data to fit GARCH model. Select a longer date range.")

# --- KEY METRICS ROW ---
if model_fitted:
    col1, col2, col3, col4 = st.columns(4)
    current_return = data_clean['returns'].iloc[-1]
    garch_vol = data_clean['garch_volatility'].iloc[-1]
    var_95 = 1.645 * garch_vol

    with col1:
        st.metric("Current Daily Return", f"{current_return:.3f}%")
    with col2:
        st.metric("Historical Volatility", f"{data_clean['hist_volatility'].iloc[-1]:.3f}%")
    with col3:
        st.metric("GARCH Volatility", f"{garch_vol:.3f}%")
    with col4:
        st.metric(
            "95% Value-at-Risk",
            f"{var_95:.3f}%",
            delta=f"-{var_95:.3f}% max expected loss",
            delta_color="inverse"
        )

# --- VOLATILITY COMPARISON CHART ---
st.subheader("📈 Volatility Comparison: Historical vs. GARCH Modeled")

if model_fitted:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean['hist_volatility'],
        mode='lines',
        name='Historical Volatility (Rolling Std)',
        line=dict(color='blue', width=2),
        hovertemplate='<b>Historical Vol</b><br>Date: %{x|%Y-%m-%d}<br>Volatility: %{y:.3f}%<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=data_clean.index,
        y=data_clean['garch_volatility'],
        mode='lines',
        name='GARCH Modeled Volatility',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>GARCH Vol</b><br>Date: %{x|%Y-%m-%d}<br>Volatility: %{y:.3f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f"{selected_stock_name} — Volatility Analysis",
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
        params_df = pd.DataFrame({
            "Parameter": list(results.params.index),
            "Value": [f"{v:.6f}" for v in results.params.values],
            "Std Error": [f"{v:.6f}" for v in results.std_err.values],
            "T-Stat": [f"{v:.4f}" for v in results.tvalues.values],
            "P-Value": [f"{v:.4f}" for v in results.pvalues.values]
        })
        st.dataframe(params_df, hide_index=True, use_container_width=True)

    with col2:
        st.write("**Volatility Forecast**")
        forecast_df = pd.DataFrame({
            "Day": list(range(1, forecast_horizon + 1)),
            "Forecasted Volatility (%)": [f"{v:.4f}" for v in forecast_volatility]
        })
        st.dataframe(forecast_df, hide_index=True, use_container_width=True)

    st.write("**Model Diagnostics**")
    diag_df = pd.DataFrame({
        "Metric": ["Log Likelihood", "AIC", "BIC", "Observations"],
        "Value": [
            f"{results.loglikelihood:.2f}",
            f"{results.aic:.2f}",
            f"{results.bic:.2f}",
            f"{len(data_clean)}"
        ]
    })
    st.dataframe(diag_df, hide_index=True, use_container_width=True)

# --- FOOTER ---
st.divider()
st.markdown(f"""
**Data Source:** Yahoo Finance via `yfinance` | **Model:** GARCH({garch_p},{garch_q}) | **Period:** {start_date} to {end_date}

*Disclaimer: This dashboard is for educational purposes only. Historical volatility does not guarantee future results.*
""")
