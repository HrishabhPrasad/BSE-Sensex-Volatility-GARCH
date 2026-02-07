## Validated Risk Analysis (Post-Cleaning)

After cleaning the raw dataset to remove data ingestion artifacts (erroneous >50% spikes), the GARCH model was re-run to generate an accurate risk profile.

### 1. Improved Model Performance
The data cleaning process significantly refined the risk metrics, removing artificial volatility bias:
* **Volatility Estimate:** Dropped from `1.82%` (Noisy) $\rightarrow$ `1.14%` (Clean).
* **VaR Estimate:** Dropped from `2.99%` (Noisy) $\rightarrow$ `1.88%` (Clean).

### 2. Final Output
> **95% Value at Risk (VaR):** `1.88%`  
> **Interpretation:** We can estimate with 95% confidence that the BSE Sensex will not decline by more than **1.88%** in the next trading session.

### 3. Historical Visualization
The graph below visualizes the cleaned time series of BSE Sensex daily returns from 1990 to 2026.


**Key Historical Events Captured:**
Unlike the raw data, this validated plot accurately captures major real-world financial events:
* **1992:** Extreme volatility corresponding to the Harshad Mehta Scam.
* **2008:** The Global Financial Crisis market crash.
* **2020:** The sharp, short-term volatility spike caused by the COVID-19 pandemic.

The **Red Dashed Line** represents the modeled VaR threshold. Breaches of this line (blue spikes exceeding the red limit) effectively identify historical "Black Swan" events.