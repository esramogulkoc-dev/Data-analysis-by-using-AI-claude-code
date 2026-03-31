import pandas as pd

FILE = "Online Retail.xlsx"

print("Loading file...")
df = pd.read_excel(FILE, engine="openpyxl")

print("\n--- Columns & dtypes ---")
print(df.dtypes)

print(f"\n--- Row count ---")
print(f"Rows: {len(df):,}")

print("\n--- InvoiceDate min/max (raw, before any parsing) ---")
print(f"dtype : {df['InvoiceDate'].dtype}")
print(f"min   : {df['InvoiceDate'].min()}")
print(f"max   : {df['InvoiceDate'].max()}")

print("\n--- First 3 InvoiceDate values (to inspect format) ---")
print(df['InvoiceDate'].head(3).tolist())

print("\n--- Null counts ---")
print(df.isnull().sum())
