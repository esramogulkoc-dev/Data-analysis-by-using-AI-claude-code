# Demo Prompts Analysis







## 1. Prompt: Python Environment Setup with UV

I need you to set up my Python environment using uv for data analysis.
Windows Setup (delete macOS section above if using this)

1. First, check if uv is installed by running: uv --version
2. If not installed, install it with PowerShell: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
3. After installation, restart the terminal so uv is available in PATH
4. Create a virtual environment in my current project directory: uv venv
5. Install the required packages: uv pip install pandas openpyxl seaborn matplotlib jupyter
6. Show me how to activate the environment when needed: .venv\Scripts\activate


## 2. Prompt: Update `CLAUDE.md`

After setting up the environment, add the following to my project's `CLAUDE.md` file (create it if it doesn't exist):

## Python Environment

- Always use `uv` for Python package management (not pip directly)
- Always use `uv` for running Python scripts. No exceptions.
- Virtual environment: `.venv` in project root
- Activate before running Python: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- Install packages with: `uv pip install <package>`
- Required packages: pandas, openpyxl, seaborn, matplotlib, jupyter

## Chart Style

When creating charts with matplotlib/seaborn, always apply this configuration at the start of the script:

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'Helvetica Neue', 'Arial', 'sans-serif'],
    'font.size': 11,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#333333',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5,
    'axes.axisbelow': True,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
})

CHART_COLORS = ['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2', '#FF9DA6', '#9D755D', '#BAB0AC']
sns.set_palette(CHART_COLORS)
```

## Verification

After setup is complete, verify everything works by running:

```bash
uv run python -c "import pandas; import openpyxl; import seaborn; import matplotlib; print('All packages installed successfully!')"
```

---

# Retail Analytics Demo

**Dataset:** Online Retail.xlsx (541,909 rows, 8 columns)

## Critical Rules

1. **NEVER** delete return/cancellation rows — flag them with `IsCancellation` column only
2. **GrossRevenue:** calculate from `df_sales` (`IsCancellation=False`)
3. **Returns:** calculate from **FULL df** (all rows) using `abs(ReturnLineTotal)`
4. **NetRevenue** = GrossRevenue - Returns
5. **Always validate:** `df_sales rows + cancellation rows = total rows`

## Column Definitions

| Column | Formula |
|---|---|
| `IsCancellation` | `True` if InvoiceNo starts with 'C' **OR** Quantity < 0 |
| `LineTotal` | Quantity × UnitPrice |
| `GrossLineTotal` | `clip(LineTotal, lower=0)` → max(LineTotal, 0) |
| `ReturnLineTotal` | `clip(LineTotal, upper=0)` → min(LineTotal, 0) |

## Validation Checklist

Run after every analysis step:

- [ ] Row count before and after each filter
- [ ] `sum(GrossLineTotal) + sum(ReturnLineTotal) == sum(LineTotal)`
- [ ] No `NetRevenue > GrossRevenue`
- [ ] No `Return Rate > 100%`
- [ ] No negative AOV
- [ ] Country/product subtotals sum to grand total

## Tech Stack

- **Streamlit** for dashboard
- **Plotly** for charts (use `px.bar` with `orientation='h'`, **NOT** `px.barh`)
- **Pandas** for data processing
- Use **uv** for running scripts

## Known Pitfalls

- `px.barh` does **not** exist in `plotly.express` — use `px.bar(orientation='h')`
- For horizontal bar charts: `x` = numeric value, `y` = category
- `CustomerID` is numeric but should be treated as **category** in charts
- CSV files: check encoding, delimiter, mixed types before analysis

## KPI Calculation Reference

```python
df_sales = df[~df["IsCancellation"]]

gross_revenue   = df_sales["GrossLineTotal"].sum()
total_returns   = abs(df["ReturnLineTotal"].sum())        # FULL df
net_revenue     = gross_revenue - total_returns
total_invoices  = df_sales["InvoiceNo"].nunique()
total_customers = df_sales["CustomerID"].dropna().nunique()
total_products  = df_sales["StockCode"].nunique()
aov             = gross_revenue / total_invoices
return_rate     = total_returns / (gross_revenue + total_returns) * 100
```


## 3. Prompt
I have a retail dataset at @"data/Online Retail.xlsx"

Before you answer anything with numbers:
1. Write Python code that loads the file with pandas
2. Execute it
3. Only then summarize findings from the printed outputs

Rules:
- Do not estimate or infer row counts, date ranges, or totals in chat
- All numbers must come from code execution
- Do not force dayfirst=True for date parsing unless min/max check proves it's needed

Create a data exploration script called explore.py that loads the Online Retail.xlsx file and prints basic information including columns, dtypes, row count, InvoiceDate min/max, first 3 InvoiceDate values, and null counts.


## 4. Prompt: Create a data preparation script called data_prep.py that loads the data, parses InvoiceDate, adds business logic columns (IsCancellation, LineTotal, GrossLineTotal, ReturnLineTotal), and prints data quality summary including cancellation rows, missing CustomerID, UnitPrice <= 0, and financial summaries.
Create a data prep step that DOES NOT delete returns or cancellations.

Requirements:
1. Parse InvoiceDate to datetime - verify min/max after parsing matches Dec 2010 → Dec 2011
2. Add these columns:
   - IsCancellation (True if InvoiceNo starts with 'C' or Quantity < 0)
   - LineTotal = Quantity * UnitPrice
   - GrossLineTotal = max(LineTotal, 0)
   - ReturnLineTotal = min(LineTotal, 0)
3. Print a data quality summary:
   - Total rows
   - Rows flagged as cancellations
   - Rows with missing CustomerID
   - Rows with UnitPrice <= 0
   - Date range confirmed

Do not remove any rows yet - just flag them.

## 5. Prompt: Create a retail analytics dashboard using Streamlit called retail_dashboard.py with tabs for KPIs (metric cards and monthly revenue chart), Top Products (revenue and units sold bars), Sales Over Time (revenue trends with frequency selector), By Country (revenue by country with bars), and QA Checks (data quality metrics and sample invoices).

Parameters (with defaults):
- --top_n 20 (number of top products/customers to show)
- --freq M (time frequency: D/W/M for daily/weekly/monthly)
- --start_date, --end_date (optional date filters)

1. KPIs
   - GrossRevenue, Returns (absolute value), NetRevenue
   - Total Invoices, Total Customers, Total Products
   - Average Order Value
   - Return Rate (%)

2. Top_Products (top N by NetRevenue, grouped by StockCode)
   - StockCode, Description, QuantitySold, GrossRevenue, Returns, NetRevenue, ReturnRate

3. Top_Customers (top N by NetRevenue)
   - CustomerID, Country, NumOrders, GrossRevenue, Returns, NetRevenue, AOV
   - Note: exclude rows with missing CustomerID for this sheet only

4. Sales_Over_Time (resampled by --freq)
   - Period, GrossRevenue, Returns, NetRevenue, NumInvoices

5. Sales_By_Country
   - Country, NumCustomers, NumOrders, GrossRevenue, Returns, NetRevenue, % of Total

6. QA_Checks
   - Row counts at each stage
   - Reconciliation: NetRevenue via sum(LineTotal) vs sum(GrossLineTotal)+sum(ReturnLineTotal)
   - Sample of 5 invoices (seeded for reproducibility) with their line items

Chart requirements:
- Set figure size to (12, 6) for 16:9 aspect ratio
- Add value labels on bar charts
- Include clear titles and axis labels

After building the script:
- Run it with defaults
- Print a preview of KPIs and Top 3 products
- Print how to use the script and what options are available (remember to always use `uv`)
- Open the generated images with charts

## 6. Prompt: Create a PowerPoint presentation script called build_pptx.py using python-pptx that generates a 13-slide presentation with dark tech theme (black background, cyan accents), including title slide, agenda, data overview, KPIs, charts, and conclusion slides.
*
## 7. Prompt: Create a Jupyter notebook called eda_validation.ipynb in the validation folder that includes cells for data exploration (loading file, columns/dtypes, row count, date range, null counts) and data preparation (parsing dates, adding columns, data quality summary).


## 8. Prompt: Create a validation notebook called validation_notebook.ipynb in the validation folder that independently verifies all KPIs using two methods: groupby (Streamlit method) and independent array operations, then creates a comparison table.


## 9. Prompt: Create a validation results markdown file called VALIDATION_RESULTS.md in the validation folder that summarizes the KPI comparison results, logic checks, UnitPrice <= 0 impact analysis, and data integrity status.


## 10. Prompt: Create a README.md file that documents the project with sections for quick start (installing Claude Code, setup, running dashboard), what you get (dashboard tabs and controls), data numbers, and project structure.
