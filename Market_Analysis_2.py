import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from arch import arch_model 

# --- CONFIGURATION ---
DB_PASSWORD = 'Stephen1403!' 

# 1. CONNECT TO SQL
print("1. Connecting to Database...")
# This connects directly to 'bse_indices' (ignoring PopSQL's dropdown!)
connection_str = f'mysql+pymysql://root:{DB_PASSWORD}@127.0.0.1/bse_indices'
engine = create_engine(connection_str)

# 2. FETCH DATA
print("2. Pulling 36 years of Sensex Data...")
query = "SELECT record_date, close_price FROM sensex_data ORDER BY record_date ASC"
df = pd.read_sql(query, engine)

# 3. CALCULATE RETURNS
# We care about % change, not the raw price (80k vs 5k)
# 3. CALCULATE RETURNS
df['returns'] = 100 * df['close_price'].pct_change().dropna()
df = df.dropna()

# --- NEW: DATA CLEANING BLOCK ---
# We verify if data is "Real". If returns are > 20% or < -20%, it's a data error.
print(f"Original Row Count: {len(df)}")
df = df[ (df['returns'] < 20) & (df['returns'] > -20) ]
print(f"Cleaned Row Count: {len(df)} (Removed impossible outliers)")
# -------------------------------

print(f"   Analyzed {len(df)} trading days.")

# 4. THE "WALL STREET" MODEL (GARCH)
print("3. Training GARCH(1,1) Volatility Model...")
model = arch_model(df['returns'], vol='Garch', p=1, q=1)
results = model.fit(disp='off') 

print("\n" + "="*50)
print("       MARKET RISK REPORT (BSE SENSEX)")
print("="*50)

# 5. PREDICT FUTURE RISK
forecast = results.forecast(horizon=1)
next_day_volatility = np.sqrt(forecast.variance.iloc[-1, 0])

# Calculate 95% Value at Risk (VaR)
VaR_95 = 1.65 * next_day_volatility

print(f"Current Market Volatility: {next_day_volatility:.2f}%")
print(f"95% Value at Risk (VaR):   {VaR_95:.2f}%")
print(f"Interpretation: We are 95% confident the Sensex will NOT drop more than {VaR_95:.2f}% tomorrow.")
print("="*50)

# 6. VISUALIZE
plt.figure(figsize=(12, 6))
plt.plot(df['record_date'], df['returns'], color='blue', alpha=0.4, linewidth=0.5)
plt.title('BSE Sensex Daily Returns (1990-2026)', fontsize=14)
plt.ylabel('Daily Return (%)')
plt.axhline(y=VaR_95, color='red', linestyle='--', label=f'95% VaR Limit (-{VaR_95:.2f}%)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()