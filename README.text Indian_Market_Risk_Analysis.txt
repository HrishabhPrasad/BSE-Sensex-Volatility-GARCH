# A GARCH Analysis of the BSE Sensex (1990–2026)


## Abstract
This study investigates the volatility dynamics of the Bombay Stock Exchange (BSE) Sensex over a 36-year horizon. By establishing an automated ETL (Extract-Transform-Load) pipeline between **Python** and **SQL**, the project analyzes daily log-returns to quantify market risk.

The core objective was to model time-varying variance using a **GARCH(1,1)** framework and estimate the **95% Value-at-Risk (VaR)** for regulatory compliance (Basel III standards). The study further highlights the critical importance of data hygiene by demonstrating how structural data anomalies (outliers >20σ) can inflate risk estimates by over 60%.

## Methodology

1. Data Engineering (The Pipeline)
* **Data Warehousing:** Constructed a relational database (`bse_indices`) using **MySQL** to house 8,700+ trading days of OHLC data.
* **Automation:** Developed a Python script to extract raw data, normalize formats, and load it into the SQL warehouse, ensuring a reproducible workflow.

2. Statistical Preprocessing & Robustness Checks
* **Stationarity:** Log-returns were calculated to ensure the time series satisfied the stationarity condition required for GARCH modeling.
* **Anomaly Detection:** Initial exploratory analysis revealed non-stochastic outliers (returns > ±20%) in 2015 and 2017 attributed to vendor data entry errors.
* **Correction:** A statistical filter was applied to censor these artifacts. This correction reduced the VaR estimate from an erroneous **2.99%** to a robust **1.88%**.

3. Econometric Modeling
* **Model Selection:** A **GARCH(1,1)** (Generalized Autoregressive Conditional Heteroskedasticity) model was selected to capture "volatility clustering"—the phenomenon where large market shocks are followed by further large shocks (e.g., the 2008 Financial Crisis and 2020 COVID-19 Pandemic).
* **Risk Forecasting:** The conditional variance ($\sigma^2_t$) was forecasted one step ahead to derive the Value-at-Risk (VaR).

## Key Findings

| Metric | Raw Data (Uncleaned) | Cleaned Data (Robust) |
| :--- | :--- | :--- |
| **Daily Volatility** | High Distortion | **1.14%** |
| **95% VaR** | 2.99% | **1.88%** |
| **Interpretation** | **Overestimated Risk** | **Aligned with Emerging Market Norms** |

> *Conclusion:* The automated cleaning pipeline proved essential. The adjusted VaR of 1.88% accurately reflects the Sensex's risk profile, balancing market sensitivity with stability.
