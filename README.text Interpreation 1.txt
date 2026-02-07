## Results & Visualization

### 1. Risk Forecasting (GARCH Model Output)
The model analyzed historical volatility to predict potential losses for the next trading day. 

> **Current Market Volatility:** `1.82%`  
> **95% Value at Risk (VaR):** `2.99%`

**Interpretation:** Based on current market conditions, we can say with **95% confidence** that the BSE Sensex will not drop more than **2.99%** in a single day. This metric helps institutional investors set stop-loss limits and capital reserves.

### 2. Historical Return Analysis (1990-2026)
The graph below visualizes the daily returns of the Sensex over 36 years.


* **Blue Series:** Represents daily percentage changes. Notice the "volatility clustering" (periods where the graph gets wider), which confirms that market volatility is not constant but comes in waves—justifying the use of a GARCH model over simple standard deviation.
* **Red Line (VaR):** The calculated threshold. Returns dipping below this line represent the rare "tail events" (market crashes) that occur less than 5% of the time.

---
**Data Quality Note:**
You may notice extreme outliers in the graph between 2015-2017 (spikes >50%). These represent artifacts/errors in the raw source dataset, as the Sensex has historically never moved by such magnitudes in a single day. In a production environment, an additional cleaning layer would be added to filter these anomalies.