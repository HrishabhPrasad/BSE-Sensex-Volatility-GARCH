## Data Pipeline & Preprocessing

The raw financial data (`BSE Indices.xlsx`) requires significant preprocessing before analysis due to formatting inconsistencies in the source file. 

**Diagnostic Step (`debug_data.py`):
Before running the main analysis, the `debug_data.py` script inspects the raw Excel file structure. As seen in the diagnostic output:
- **Header Offset:** The actual data headers start at **Row 7** (index 6), requiring a `header=6` argument during ingestion.
- **Null Columns:** The first column (`Unnamed: 0`) is empty and must be dropped.
- **Date Alignment:** The primary index dates are located in the second column (`Unnamed: 1`), requiring renaming to `Date`.
- **Data Shape:** The dataset comprises approximately **8,748 records** with 14 raw columns.

**Cleaning Logic Implemented:**
Based on these diagnostics, the main analysis script applies the following transformations:
1. Loads data with `header=6`.
2. Drops the empty `Unnamed: 0` column.
3. Renames `Unnamed: 1` $\rightarrow$ `Date`.
4. Parses the `Date` column to datetime objects for time-series analysis.