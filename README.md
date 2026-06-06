# BSE Sensex Volatility — GARCH(1,1) & Value-at-Risk

36 years of BSE Sensex daily data (Jan 1990 – Feb 2026, ~8,700 trading days) modeled with GARCH(1,1) to estimate conditional volatility and a Basel III–aligned 95% Value-at-Risk.

---

## What I Built

- **ETL Pipeline** — Parsed a non-standard BSE Excel file (headers at row 7), loaded OHLC data into MySQL, and queried it via SQLAlchemy in Python
- **Data Cleaning** — Identified and removed vendor data-entry errors (returns >±20%) that were inflating risk estimates by 37%
- **GARCH(1,1) Model** — Fitted using MLE via the `arch` library to capture volatility clustering in Indian equity returns
- **Risk Metric** — Derived a 95% VaR of **1.88%** per day on cleaned data, down from a distorted 2.99% on raw data

---

## Key Findings

| Metric | Raw Data | Cleaned Data |
|--------|----------|--------------|
| Daily Volatility | ~1.82% | ~1.14% |
| 95% VaR | 2.99% | **1.88%** |

The GARCH model correctly flags three major volatility regimes — the **1992 Harshad Mehta scam**, the **2008 Global Financial Crisis**, and the **2020 COVID-19 crash** — validating the model's capture of real market stress without artificial noise.

**Figure — Daily Returns with 95% VaR Threshold (Cleaned Data)**
![GARCH Results](Results%202.png)

---

## How to Run

```bash
git clone https://github.com/hrishabhprasad/bse-sensex-volatility-garch.git
cd bse-sensex-volatility-garch
pip install -r requirements.txt

# Run baseline analysis
python Market_Analysis_1.py

# Run with outlier cleaning (recommended)
python Market_Analysis_2.py
```

MySQL must be running with a `bse_indices` database loaded from `BSE Indices.xlsx`.

---

## Tech Stack

`Python 3.11` · `pandas` · `NumPy` · `arch` (GARCH) · `MySQL` · `SQLAlchemy` · `matplotlib`

---

## Streamlit Dashboard

Built an interactive dashboard the following day — select any of the 30 major BSE stocks, configure GARCH(p,q) parameters, and view live volatility forecasts and VaR estimates.

```bash
streamlit run streamlit_dashboard.py
```

> **Live App:** [Link Coming Soon]
