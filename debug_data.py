import pandas as pd

# --- CONFIGURATION ---
EXCEL_FILE_PATH = r'C:\Users\Hrishabh\Desktop\Python SQL\Indian_Market_Risk_Analysis\BSE Indices.xlsx'

print("--- DIAGNOSTIC MODE ---")
print("1. Reading Excel file with header=6 (Row 7)...")

# We read the file assuming the headers are on Row 7
df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='BSE Indices', header=6)

print(f"2. Raw Shape: {df.shape}")
print("\n3. Here are the COLUMN NAMES Python found:")
print(df.columns.tolist())

print("\n4. Here are the FIRST 5 ROWS of data:")
# We verify what is actually in the first few columns
print(df.iloc[:5, 0:6]) 

print("\n-----------------------")
print("Check the output above:")
print("- Does 'Unnamed: 0' contain the dates?")
print("- Does 'Unnamed: 1' appear empty?")
print("- Do the prices start at Column 2 (Open)?")