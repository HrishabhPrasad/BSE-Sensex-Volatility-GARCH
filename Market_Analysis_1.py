import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION ---
DB_PASSWORD = '****'
EXCEL_FILE_PATH = r'C:\Users\Hrishabh\Desktop\Python SQL\Indian_Market_Risk_Analysis\BSE Indices.xlsx'

print("1. Reading Excel file...")
# header=6 means we take the headers from Row 7
df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='BSE Indices', header=6)

print("2. Cleaning Data...")

# FIX: We select columns [1, 2, 3, 4, 5]
# 1 = Date (Was mistakenly looking at 0 before)
# 2 = Open
# 3 = Close
# 4 = High
# 5 = Low
df_sensex = df.iloc[:, [1, 2, 3, 4, 5]].copy()

# Rename columns
df_sensex.columns = ['record_date', 'open_price', 'close_price', 'high_price', 'low_price']

# Format Date
df_sensex['record_date'] = pd.to_datetime(df_sensex['record_date'])
df_sensex = df_sensex.dropna()

print(f"   Prepared {len(df_sensex)} rows of data.")

# 3. LOAD into SQL
print("3. Connecting to MySQL...")
connection_str = f'mysql+pymysql://root:{DB_PASSWORD}@127.0.0.1/bse_indices'
engine = create_engine(connection_str)

print("4. Pushing data to SQL...")
df_sensex.to_sql('sensex_data', con=engine, if_exists='replace', index=False)

print("Success! Data loaded. Go check PopSQL.")




















import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from arch import arch_model 

# --- CONFIGURATION ---
DB_PASSWORD = '****' 

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
df['returns'] = 100 * df['close_price'].pct_change().dropna()
df = df.dropna() 

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