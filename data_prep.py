import pandas as pd

FILE = "Online Retail.xlsx"

print("Loading file...")
df = pd.read_excel(FILE, engine="openpyxl")

# 1. Parse InvoiceDate - already datetime64 from openpyxl, ensure it's correct
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

date_min = df["InvoiceDate"].min()
date_max = df["InvoiceDate"].max()
assert date_min.year == 2010 and date_min.month == 12, f"Unexpected min date: {date_min}"
assert date_max.year == 2011 and date_max.month == 12, f"Unexpected max date: {date_max}"
print(f"Date range verified: {date_min} to {date_max}")

# 2. Add flag and value columns
df["IsCancellation"] = df["InvoiceNo"].astype(str).str.startswith("C") | (df["Quantity"] < 0)
df["LineTotal"]      = df["Quantity"] * df["UnitPrice"]
df["GrossLineTotal"] = df["LineTotal"].clip(lower=0)
df["ReturnLineTotal"] = df["LineTotal"].clip(upper=0)

# 3. Data quality summary
total_rows          = len(df)
cancellation_rows   = df["IsCancellation"].sum()
missing_customer    = df["CustomerID"].isna().sum()
zero_or_neg_price   = (df["UnitPrice"] <= 0).sum()

print("\n--- Data Quality Summary ---")
print(f"Total rows            : {total_rows:>10,}")
print(f"Cancellation rows     : {cancellation_rows:>10,}  ({cancellation_rows/total_rows*100:.2f}%)")
print(f"Missing CustomerID    : {missing_customer:>10,}  ({missing_customer/total_rows*100:.2f}%)")
print(f"UnitPrice <= 0        : {zero_or_neg_price:>10,}  ({zero_or_neg_price/total_rows*100:.2f}%)")
print(f"Date range confirmed  :  {date_min.date()} to {date_max.date()}")

print("\n--- LineTotal sanity check ---")
print(f"GrossLineTotal  sum   : £{df['GrossLineTotal'].sum():>15,.2f}")
print(f"ReturnLineTotal sum   : £{df['ReturnLineTotal'].sum():>15,.2f}")
print(f"Net LineTotal   sum   : £{df['LineTotal'].sum():>15,.2f}")

print("\n--- IsCancellation breakdown ---")
print(f"  Starts with 'C'     : {df['InvoiceNo'].astype(str).str.startswith('C').sum():>10,}")
print(f"  Quantity < 0        : {(df['Quantity'] < 0).sum():>10,}")
print(f"  Either flag (union) : {cancellation_rows:>10,}")
