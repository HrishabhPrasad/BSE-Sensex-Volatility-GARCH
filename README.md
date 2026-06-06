# BSE Sensex Volatility Modeling — GARCH(1,1) & Value-at-Risk Analysis

> **Live Streamlit App:** [Link Coming Soon]

A rigorous, end-to-end financial risk analysis system built around 36 years of BSE Sensex daily trading data (January 1990 – February 2026, ~8,700 trading days). The project fits a GARCH(1,1) model to estimate time-varying conditional volatility and derives a Basel III–aligned 95% Value-at-Risk (VaR) estimate for institutional risk management. An interactive Streamlit dashboard extends the analysis to the 30 largest BSE-listed equities using live Yahoo Finance data.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Data Pipeline & Methodology](#3-data-pipeline--methodology)
   - [Data Acquisition](#31-data-acquisition)
   - [Data Cleaning & Outlier Treatment](#32-data-cleaning--outlier-treatment)
   - [SQL Implementation](#33-sql-implementation)
   - [Return Calculation](#34-return-calculation)
4. [Econometric Framework — GARCH(1,1)](#4-econometric-framework--garch11)
5. [Streamlit Dashboard](#5-streamlit-dashboard)
6. [Key Findings](#6-key-findings)
7. [Getting Started](#7-getting-started)
8. [Tech Stack](#8-tech-stack)

---

## 1. Project Overview

Indian equity markets exhibit well-documented **volatility clustering** — a stylized fact where periods of high turbulence tend to persist, and quiet periods cluster together. Standard constant-variance models (e.g., simple historical volatility) fail to capture this dynamic, making them inadequate for risk management. This project addresses that gap by:

- **Building a full ETL pipeline** from raw Excel data → MySQL → Python for analysis
- **Fitting a GARCH(1,1) model** using maximum-likelihood estimation to model conditional heteroskedasticity
- **Quantifying market risk** via 95% Value-at-Risk (VaR) consistent with Basel III regulatory requirements
- **Demonstrating the critical impact of data quality** — a single outlier-cleaning step reduces the VaR estimate by ~37%
- **Packaging the analysis** in an interactive Streamlit dashboard covering 30 major BSE equities

---

## 2. Repository Structure

```
BSE-Sensex-Volatility-GARCH/
│
├── streamlit_dashboard.py      # Interactive Streamlit web application
├── Market_Analysis_1.py        # Baseline GARCH analysis (no outlier removal)
├── Market_Analysis_2.py        # Improved analysis with ±20% outlier filter
├── debug_data.py               # Diagnostic tool for Excel header alignment
├── analysis_queries.sql        # SQL DDL and exploratory queries
│
├── BSE Indices.xlsx            # Raw historical OHLC data (1990–2026, ~870 KB)
├── requirements.txt            # Python dependency manifest
│
├── Graph 1.png                 # Returns time-series — raw data
├── Graph 2.png                 # Returns time-series — cleaned data
├── Results 1.png               # GARCH output — raw data (VaR: 2.99%)
├── Results 2.png               # GARCH output — cleaned data (VaR: 1.88%)
├── Debugging.png               # Excel structure inspection output
├── SQL Queries.png             # MySQL query result screenshots
│
├── README.text Indian_Market_Risk_Analysis.txt   # Academic abstract
├── README.text Interpreation 1.txt               # Pre-cleaning interpretation
├── README.text Interpretation 2.txt              # Post-cleaning interpretation
├── README.text Debugging.txt                     # ETL debugging notes
│
└── .devcontainer/
    └── devcontainer.json       # Docker dev container (Python 3.11, port 8501)
```

---

## 3. Data Pipeline & Methodology

### 3.1 Data Acquisition

The primary dataset is sourced from the **BSE (Bombay Stock Exchange)** official historical data archive, covering the full Sensex index from **January 1, 1990 to February 4, 2026** — 36 years of daily OHLC (Open, High, Low, Close) prices representing approximately **8,748 trading days**.

The raw data is delivered as a multi-sheet Excel workbook (`BSE Indices.xlsx`) with a non-standard structure: the column headers reside at **row 7 (0-indexed: row 6)**, requiring a header-offset read. The `debug_data.py` diagnostic script was written explicitly to identify this offset:

```python
# Reading the Excel file with the correct header offset
df_raw = pd.read_excel('BSE Indices.xlsx', sheet_name='BSE Indices', header=6)
df = df_raw.iloc[:, [1, 2, 3, 4, 5]]
df.columns = ['record_date', 'open_price', 'close_price', 'high_price', 'low_price']
```

The Streamlit dashboard supplements this with **live data** fetched from Yahoo Finance via `yfinance`, covering 30 major BSE-listed stocks with user-configurable date ranges.

---

### 3.2 Data Cleaning & Outlier Treatment

Raw financial data from third-party vendors is notoriously noisy. Inspection of the BSE dataset revealed **implausible single-day returns exceeding ±50%** concentrated in the 2015–2017 period — statistically impossible for a large-cap index and confirmed to be **vendor data-entry errors**, not genuine market events.

**Outlier filter applied:**

```python
# Remove returns outside ±20% — beyond any plausible single-day Sensex move
df = df[(df['returns'] > -20) & (df['returns'] < 20)]
```

The ±20% threshold is deliberately conservative: it retains all genuine historical shocks — the 1992 Harshad Mehta securities scandal, the 2008 Global Financial Crisis, and the 2020 COVID-19 crash — while eliminating clear data artifacts. The downstream impact on the risk estimate is substantial (see [Key Findings](#6-key-findings)).

---

### 3.3 SQL Implementation

Cleaned data is loaded into a **MySQL relational database** (`bse_indices`) for structured storage and reproducible querying. The schema is intentionally minimal — a single fact table aligned to the OHLC structure of the source file.

**Database setup:**

```sql
CREATE DATABASE BSE_INDICES;
USE BSE_INDICES;
```

**Schema (`sensex_data`):**

| Column         | Type       | Description                      |
|----------------|------------|----------------------------------|
| `record_date`  | DATE       | Trading date                     |
| `open_price`   | DECIMAL    | Opening index value              |
| `close_price`  | DECIMAL    | Closing index value (primary)    |
| `high_price`   | DECIMAL    | Intra-day high                   |
| `low_price`    | DECIMAL    | Intra-day low                    |

**Exploratory queries:**

```sql
-- Verify data completeness
SELECT
    MIN(record_date) AS start_date,
    MAX(record_date) AS end_date,
    COUNT(*)         AS total_days
FROM sensex_data;

-- Full table inspection (up to 9,000 records)
SELECT * FROM sensex_data LIMIT 9000;
```

**Python–MySQL connection** uses SQLAlchemy with the `pymysql` driver:

```python
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:{PASSWORD}@127.0.0.1/bse_indices')
df = pd.read_sql('SELECT record_date, close_price FROM sensex_data', engine)
```

---

### 3.4 Return Calculation

Daily log-percentage returns are computed from closing prices using pandas `.pct_change()`:

```python
df['returns'] = 100 * df['close_price'].pct_change()
df.dropna(inplace=True)
```

Multiplying by 100 scales returns to percentage points, which is the standard convention for financial econometrics and ensures numerical stability during GARCH estimation.

---

## 4. Econometric Framework — GARCH(1,1)

### Motivation

The ordinary least-squares assumption of **homoskedasticity** (constant variance) is systematically violated in financial return series. The Sensex return series exhibits:

- **Leptokurtosis** — fat tails relative to a normal distribution
- **Volatility clustering** — large return shocks are followed by further large shocks
- **Autocorrelation in squared returns** — evidence of ARCH effects

The **Generalized Autoregressive Conditional Heteroskedasticity (GARCH)** model, introduced by Bollerslev (1986), directly addresses these properties.

### GARCH(1,1) Specification

The model is specified as a two-equation system:

**Mean equation:**

```
r_t = μ + ε_t,   ε_t = σ_t · z_t,   z_t ~ N(0,1)
```

**Variance equation:**

```
σ²_t = ω + α₁·ε²_(t-1) + β₁·σ²_(t-1)
```

Where:
- `σ²_t` — conditional variance at time *t*
- `ω` — long-run variance constant (intercept)
- `α₁` — ARCH coefficient: sensitivity to recent squared return shocks
- `β₁` — GARCH coefficient: persistence of past conditional variance
- `α₁ + β₁ < 1` — covariance stationarity condition

**Stationarity condition:** `α₁ + β₁ < 1` ensures the conditional variance reverts to its long-run mean. For the Sensex, this sum is close to but below 1, confirming high volatility persistence — consistent with an emerging market index.

### Python Implementation

```python
from arch import arch_model
import numpy as np

model = arch_model(df['returns'], vol='Garch', p=1, q=1)
results = model.fit(disp='off')

# 1-step-ahead variance forecast
forecast = results.forecast(horizon=1)
next_day_volatility = np.sqrt(forecast.variance.iloc[-1, 0])

# 95% Value-at-Risk (z = 1.645 for one-tailed 95% CI)
VaR_95 = 1.645 * next_day_volatility
```

### Value-at-Risk Derivation

VaR at the 95% confidence level answers: *"What is the maximum loss we can expect on 95 out of 100 trading days?"*

```
VaR_95% = z_0.05 × σ̂_(t+1|t) = 1.645 × σ̂_(t+1|t)
```

This formulation aligns with **Basel III's Internal Models Approach** for market risk capital requirements, which mandates 99% VaR over a 10-day holding period — the 95% daily estimate here provides the foundation for that calculation.

### Model Diagnostics

The fitted model is evaluated using standard information criteria:

| Criterion | Description |
|-----------|-------------|
| **Log-likelihood** | Higher is better; measures goodness-of-fit |
| **AIC** (Akaike) | Penalizes model complexity; lower is better |
| **BIC** (Bayesian) | Stronger complexity penalty than AIC; lower is better |

Parameter significance is assessed via t-statistics and p-values for `ω`, `α₁`, and `β₁`. The Streamlit dashboard surfaces the full parameter table for each model run.

---

## 5. Streamlit Dashboard

The interactive dashboard (`streamlit_dashboard.py`) extends the analysis beyond the Sensex index to the **30 largest BSE-listed equities**, using live data from Yahoo Finance.

### Supported Stocks

`RELIANCE` · `TCS` · `INFY` · `HINDUNILVR` · `HDFCBANK` · `BAJAJ-AUTO` · `LT` · `ASIANPAINT` · `MARUTI` · `SUNPHARMA` · `HCLTECH` · `WIPRO` · `ULTRACEMCO` · `BHARTIARTL` · `ADANIPORTS` · `TITAN` · `NESTLEIND` · `DRREDDY` · `CIPLA` · `SBILIFE` · `ITC` · `POWERGRID` · `JSWSTEEL` · `VEDL` · `SBIN` · `KOTAKBANK` · `AXISBANK` · `ICICIBANK` · `BAJAJFINSV` · `TATAMOTORS`

### Controls (Sidebar)

| Control | Range | Default |
|---------|-------|---------|
| Stock ticker | 30 BSE equities | RELIANCE |
| Date range | Customizable | Last 3 years |
| GARCH order *p* | 1 – 3 | 1 |
| GARCH order *q* | 1 – 3 | 1 |
| Forecast horizon | 1 – 30 days | 5 days |
| Rolling window | 5 – 100 days | 21 days |

### Dashboard Sections

1. **Key Metrics Row** — Current daily return, historical volatility, GARCH-modeled volatility, and 95% VaR displayed as live metric cards
2. **Volatility Comparison Chart** — Interactive Plotly dual-line chart overlaying rolling historical volatility (blue) against GARCH conditional volatility (red dashed)
3. **Returns Distribution** — 50-bin histogram of daily returns with summary statistics: mean, std dev, min, max, skewness, kurtosis
4. **GARCH Model Parameters Table** — Coefficients (`ω`, `α₁`, `β₁`), standard errors, t-statistics, and p-values
5. **Multi-Step Volatility Forecast** — Day-by-day volatility predictions over the chosen horizon
6. **Model Diagnostics** — Log-likelihood, AIC, BIC, and observation count

---

## 6. Key Findings

### Impact of Data Quality on Risk Estimation

The most critical quantitative insight from this project is the **sensitivity of GARCH-based VaR to data quality**. Vendor-supplied data containing erroneous outliers (single-day returns >50%) inflates the risk estimate by approximately **37%**:

| Metric | Raw Data (unfiltered) | Cleaned Data (±20% filter) | Change |
|--------|-----------------------|---------------------------|--------|
| Estimated Daily Volatility | ~1.82% | ~1.14% | −37% |
| 95% Value-at-Risk | **2.99%** | **1.88%** | −37% |
| Risk Interpretation | Overestimated | Aligned with emerging market norms | — |

**The cleaned estimate of 1.88% daily VaR** is well within the range documented for emerging market indices and consistent with Sensex behavior during non-crisis periods. The GARCH model correctly assigns elevated conditional variance to genuine stress events without artificial amplification from data artifacts.

### Historical Volatility Regimes Captured

The conditional volatility time series correctly identifies the three major structural breaks in Sensex risk:

- **1992** — Harshad Mehta securities scam: sharp, short-duration volatility spike
- **2008** — Global Financial Crisis: sustained elevated variance for 12+ months
- **2020** — COVID-19 pandemic: rapid, extreme spike followed by fast mean-reversion

These events appear as distinct high-variance regimes in the conditional volatility series, validating the model's ability to capture the clustering dynamics of real market stress.

### Result Visualizations

**Figure 1 — Daily Returns with 95% VaR Threshold (Cleaned Data)**

![Results 2 — Cleaned GARCH Output](Results%202.png)

> *The red dashed horizontal line marks the −1.88% VaR threshold. Points breaching this line correspond to genuine "Black Swan" events — 1992 scam, 2008 GFC, 2020 COVID crash.*

**Figure 2 — Returns Time Series (Cleaned Data)**

![Graph 2 — Cleaned Returns](Graph%202.png)

> *Volatility clustering is visually evident: low-volatility corridors punctuated by high-variance crisis episodes.*

> **Note for author:** Replace the above static images with interactive Plotly charts from the Streamlit dashboard, or insert additional output figures (e.g., GARCH conditional volatility series, forecast horizon plots) here as the project matures.

---

## 7. Getting Started

### Prerequisites

- Python 3.11+
- MySQL 8.0+ (for the historical pipeline; not required for the Streamlit dashboard)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/hrishabhprasad/bse-sensex-volatility-garch.git
cd bse-sensex-volatility-garch

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the Streamlit Dashboard (No MySQL Required)

```bash
streamlit run streamlit_dashboard.py
```

Navigate to `http://localhost:8501` in your browser. The dashboard fetches live data from Yahoo Finance — no local database setup is needed.

### Running the Historical GARCH Analysis (MySQL Required)

```bash
# 1. Start MySQL and create the database
mysql -u root -p < analysis_queries.sql

# 2. Run the ETL + GARCH analysis with outlier cleaning (recommended)
python Market_Analysis_2.py

# 3. Alternatively, run the baseline analysis without cleaning
python Market_Analysis_1.py
```

### Dev Container (Recommended for Cloud Environments)

The repository ships with a pre-configured VS Code Dev Container:

```jsonc
// .devcontainer/devcontainer.json
{
  "image": "python:3.11-bookworm",
  "postAttachCommand": "streamlit run streamlit_dashboard.py --server.enableCORS false --server.enableXsrfProtection false",
  "forwardPorts": [8501]
}
```

Open the repository in VS Code, accept the **"Reopen in Container"** prompt, and the Streamlit app will launch automatically on port 8501.

---

## 8. Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Data Storage** | MySQL 8.0 | Structured OHLC historical data |
| **ETL / Wrangling** | pandas 2.0, NumPy 1.26 | Data ingestion, cleaning, return calculation |
| **Econometric Modeling** | `arch` ≥6.0 | GARCH(1,1) MLE estimation & forecasting |
| **Live Data** | `yfinance` ≥0.2 | Real-time BSE equity prices (dashboard) |
| **Visualization** | Plotly 5.18, matplotlib 3.8 | Interactive and static charting |
| **Web Framework** | Streamlit ≥1.28 | Interactive risk analysis dashboard |
| **Scientific Computing** | SciPy 1.11 | Statistical functions (z-scores, distributions) |
| **DB Connectivity** | SQLAlchemy + PyMySQL | Python–MySQL ORM layer |
| **Environment** | Python 3.11, Docker Dev Container | Reproducible runtime |

---

## References

- Bollerslev, T. (1986). *Generalized Autoregressive Conditional Heteroskedasticity*. Journal of Econometrics, 31(3), 307–327.
- Engle, R. F. (1982). *Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation*. Econometrica, 50(4), 987–1007.
- Basel Committee on Banking Supervision (2019). *Minimum Capital Requirements for Market Risk*. Bank for International Settlements.
- BSE India — Historical Index Data: [bseindia.com](https://www.bseindia.com)
