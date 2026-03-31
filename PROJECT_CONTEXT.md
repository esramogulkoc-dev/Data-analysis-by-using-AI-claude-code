# Project Context — Retail Analytics Dashboard

**Project Name:** Tech Talk Demo — Retail Analytics with Claude Code
**Created:** 2026-03-31
**Status:** Complete — Ready for live demo

---

## 1. Data Source

### Dataset: Online Retail.xlsx
- **Location:** Project root — `Online Retail.xlsx`
- **Rows:** 541,909 transactions
- **Date range:** December 1, 2010 — December 9, 2011
- **Source:** UK Online Retail dataset (e-commerce transactions)

### Columns (8 total)
```
InvoiceNo      [object]   — transaction ID (some start with 'C' = cancellations)
StockCode      [object]   — product SKU
Description    [object]   — product name (1,454 nulls)
Quantity       [int64]    — units ordered (negative values = returns)
InvoiceDate    [datetime] — transaction timestamp
UnitPrice      [float64]  — price per unit (2,517 rows with price <= 0)
CustomerID     [float64]  — unique customer ID (135,080 nulls = 24.93%)
Country        [str]      — customer shipping country
```

---

## 2. Data Transformations

### Created in: `data_prep.py`
**Process:** Load → Clean → Flag → Calculate → Summarize

#### Step 1: Parse InvoiceDate
```
Verified date range: 2010-12-01 to 2011-12-09
Type: datetime64[us]
```

#### Step 2: Add Business Logic Columns
```python
df["IsCancellation"]    # True if InvoiceNo starts with 'C' OR Quantity < 0
df["LineTotal"]         # Quantity × UnitPrice
df["GrossLineTotal"]    # max(LineTotal, 0) — sales only, no returns
df["ReturnLineTotal"]   # min(LineTotal, 0) — returns only, negative values
```

#### Step 3: Data Quality Flags (no rows deleted)
- **Total rows:** 541,909 (100%)
- **Cancellation rows:** 10,624 (1.96%)
  - Starts with 'C': 9,288
  - Quantity < 0: 10,624 (union = full set)
- **Missing CustomerID:** 135,080 (24.93%)
- **UnitPrice <= 0:** 2,517 (0.46%)
- **Missing Description:** 1,454 (0.27%)

#### Step 4: Financial Summary
- **Gross revenue (sales only):** £10,666,684.54
- **Total returns:** −£918,936.61
- **Net revenue:** £9,747,747.93

---

## 3. KPIs Calculated (for Dashboard)

Created in: `retail_dashboard.py`

### Primary Metrics (Metric Cards)
1. **Gross Revenue** — sum(GrossLineTotal) when exclude_cancellations=True
2. **Orders** — count(distinct InvoiceNo)
3. **Unique Customers** — count(distinct CustomerID, dropna)
4. **Average Order Value** — Gross Revenue / Orders
5. **Items Sold** — sum(Quantity) where Quantity > 0
6. **Total Returns** — sum(ReturnLineTotal) always included
7. **Cancellation Rows** — count(IsCancellation=True)

### Filter Controls (Sidebar)
- **Date range picker:** min(InvoiceDate) to max(InvoiceDate)
- **Top N slider:** 5–50 (products, customers, countries)
- **Frequency selector:** D/W/ME (daily/weekly/monthly)
- **Exclude cancellations toggle:** True/False (affects all charts except QA)

---

## 4. Dashboard Tabs & Visualizations

### Tab 1: KPIs
- **7 metric cards** at top
- **Monthly revenue area chart** (Plotly)
  - Brown color scheme: #4C78A8 (cyan)
  - Hover shows exact revenue per month

### Tab 2: Top Products
- **Bar chart (horizontal)** — revenue by product (Top N)
  - Color scale: Blues gradient
- **Bar chart (horizontal)** — units sold by product (Top N)
  - Color scale: Oranges gradient

### Tab 3: Top Customers
- **Bar chart (horizontal)** — revenue by CustomerID (Top N)
  - Color scale: Greens gradient
- **Bar chart (horizontal)** — order count by CustomerID (Top N)
  - Color scale: Purples gradient

### Tab 4: Sales Trend
- **Line chart with markers** — daily/weekly/monthly revenue
  - Frequency controlled by sidebar selector
  - Color: #4C78A8 (cyan)
- **Bar chart** — order count per period
  - Color: #F58518 (orange)

### Tab 5: By Country
- **Choropleth map** — global revenue distribution
  - Blue scale: low to high revenue
- **Top N countries bar chart** — horizontal
  - Sorted by revenue descending
- **Pie chart** — top N countries (ex-UK for clarity)
  - Reason: UK dominates, pie would be unreadable
- **Full table** — all countries, revenue & order count

### Tab 6: QA Checks
- **5 quality metrics** (count + %)
  - Total rows (filtered)
  - Cancellation rows
  - Missing CustomerID
  - UnitPrice <= 0
  - Missing Description
- **Cancellations over time** — monthly bar chart
  - Red color (#E45756)
- **Rows with UnitPrice <= 0** — raw data table (top 50)

---

## 5. Chart Configuration

All charts use project standard from `CLAUDE.md`:

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

---

## 6. File Structure

```
tech-talk-demo-project/
├── .venv/                              # Virtual environment (Python 3.14.2)
│   └── Scripts/python.exe              # Main Python executable
│
├── CLAUDE.md                           # Project instructions for Claude Code
├── Online Retail.xlsx                  # Raw data (541,909 rows)
│
├── explore.py                          # Step 1: Data exploration
│   └── Output: columns, dtypes, nulls, date range verification
│
├── data_prep.py                        # Step 2: Data cleaning & transformation
│   └── Output: adds IsCancellation, LineTotal, GrossLineTotal, ReturnLineTotal
│   └── Prints: data quality summary
│
├── retail_dashboard.py                 # Step 3: Live Streamlit application
│   └── 6 tabs: KPIs, Products, Customers, Trend, Country, QA
│   └── Interactive charts (Plotly): bar, line, area, choropleth, pie
│   └── Sidebar controls: date range, Top N, frequency, cancellation toggle
│   └── Run: uv run streamlit run retail_dashboard.py
│
├── build_pptx.py                       # PowerPoint generation (separate from data work)
├── output/                             # Output folder
│   ├── Claude_Code_Tech_Talk_v4.pptx  # Presentation slides (13 slides + notes)
│   └── gamma_prompt.txt                # Gamma.app template
│
└── PROJECT_CONTEXT.md                  # This file
```

---

## 7. Python Dependencies

**Package manager:** uv (not pip)

Required packages (in `.venv`):
- **pandas** — data manipulation, groupby aggregations
- **openpyxl** — read Excel files
- **seaborn** — chart styling
- **matplotlib** — chart configuration (not directly used in dashboard)
- **jupyter** — notebook support
- **streamlit** — web app framework
- **plotly** — interactive charts (bar, line, area, choropleth, pie)

Total: 109 packages installed (includes all dependencies)

---

## 8. Run Instructions

### 1. Setup (one-time)
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Install packages (if needed)
uv pip install pandas openpyxl seaborn matplotlib jupyter streamlit plotly
```

### 2. Explore Data
```bash
# Windows
uv run --python .venv/Scripts/python.exe explore.py

# Output: columns, dtypes, row count, InvoiceDate min/max
```

### 3. Prepare Data
```bash
# Windows
uv run --python .venv/Scripts/python.exe data_prep.py

# Output: data quality summary, LineTotal calculations, cancellation flags
```

### 4. Launch Dashboard
```bash
# Windows
uv run streamlit run retail_dashboard.py

# Output: Streamlit server runs at http://localhost:8501
```

---

## 9. Key Numbers Summary

| Metric | Value |
|---|---|
| Total rows loaded | 541,909 |
| Date range | Dec 1, 2010 – Dec 9, 2011 |
| Gross revenue (sales) | £10,666,684.54 |
| Total returns | −£918,936.61 |
| Net revenue | £9,747,747.93 |
| Unique customers | ~4,372 (excluding nulls) |
| Unique products | 4,070 |
| Cancellation rows | 10,624 (1.96%) |
| Missing CustomerID | 135,080 (24.93%) |
| UnitPrice <= 0 | 2,517 (0.46%) |

---

## 10. Design Decisions

### Why No Rows Deleted
- Cancellations and returns flagged but retained
- Audit trail preserved for business review
- QA tab surfaces anomalies—doesn't hide them

### Why /plan and /clear Strategy
- Context window management for large datasets
- Split into 3 scripts (explore → prep → dashboard)
- Each script can run independently

### Why Plotly Over Matplotlib
- Interactive hover: users see exact values
- Choropleth map: geospatial insights
- Responsive design: works on desktop & mobile

### Why 6 Dashboard Tabs
- KPIs: executive summary (what happened?)
- Products/Customers: business drill-down (who and what?)
- Trend: temporal analysis (when?)
- Country: geographic split (where?)
- QA: data quality (are we confident?)

---

## 11. How Claude Code Built This

**Total session time:** ~1 session
**Prompts given (natural language only):**

1. "Load the Excel file, flag cancellations without deleting them, add LineTotal, GrossLineTotal, and ReturnLineTotal columns, then print a data quality summary."
2. "Create a Streamlit dashboard with 6 tabs: KPIs, Top Products, Top Customers, Sales Trend, By Country, QA Checks. Use Plotly for charts. Include sidebar controls for date range, top_n slider (5-50), frequency toggle (D/W/M), and exclude_cancellations checkbox."
3. Error fixes: "The ReturnLineTotal is showing all negative values mixed with positives. Filter it to show only negative values."

**What Claude Code did autonomously:**
- Read project files and CLAUDE.md
- Wrote explore.py, data_prep.py, retail_dashboard.py
- Ran each script to verify output
- Fixed errors (Unicode codec, Plotly layout issues)
- Created reusable, production-ready code

---

## 12. Notes for Next Steps

### If Extending This Project
- Add cohort analysis (customer acquisition date → retention curves)
- Add forecasting (monthly revenue trend + forecast)
- Add download export (CSV, Excel of selected data)
- Add authentication (limit access to specific countries/products)

### If Reusing the Pattern
- This project is fully reusable
- Swap `Online Retail.xlsx` for any other dataset
- Adapt `data_prep.py` column transforms to your schema
- Update dashboard tabs to match your KPIs
- All done with `/plan` → context engineering → tool selection

---

**Last updated:** 2026-03-31
**Claude Code session:** 1
**Status:** Ready for tech talk live demo
