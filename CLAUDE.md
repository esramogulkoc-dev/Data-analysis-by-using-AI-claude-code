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
