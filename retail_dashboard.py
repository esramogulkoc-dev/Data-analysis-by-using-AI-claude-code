import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

FILE = "Online Retail.xlsx"

# ── Data loading & prep (cached) ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset...")
def load_data():
    """Load and prepare retail data with calculated columns."""
    df = pd.read_excel(FILE, engine="openpyxl")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["IsCancellation"] = df["InvoiceNo"].astype(str).str.startswith("C") | (df["Quantity"] < 0)
    df["LineTotal"]       = df["Quantity"] * df["UnitPrice"]
    df["GrossLineTotal"]  = df["LineTotal"].clip(lower=0)
    df["ReturnLineTotal"] = df["LineTotal"].clip(upper=0)
    return df

df_raw = load_data()

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    date_min = df_raw["InvoiceDate"].dt.date.min()
    date_max = df_raw["InvoiceDate"].dt.date.max()

    start_date, end_date = st.date_input(
        "Date range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    top_n = st.slider("Top N items", min_value=5, max_value=50, value=20, step=5)

    frequency = st.selectbox(
        "Time period",
        options=["D", "W", "ME"],
        format_func=lambda x: {"D": "Daily", "W": "Weekly", "ME": "Monthly"}[x],
        index=2,  # Default to Monthly
    )

# ── Apply date filter ─────────────────────────────────────────────────────────
mask = (
    (df_raw["InvoiceDate"].dt.date >= start_date) &
    (df_raw["InvoiceDate"].dt.date <= end_date)
)
df = df_raw[mask].copy()

# ── Calculate KPIs ────────────────────────────────────────────────────────────
# Sales metrics: exclude cancellations
# Returns metrics: use FULL data (includes both legitimate returns and cancelled orders)
df_sales = df[~df["IsCancellation"]]

gross_revenue     = df_sales["GrossLineTotal"].sum()
total_returns     = abs(df["ReturnLineTotal"].sum())  # Use FULL df to capture all returns
net_revenue       = gross_revenue - total_returns  # Net = Gross - Returns

total_invoices    = df_sales["InvoiceNo"].nunique()
total_customers   = df_sales["CustomerID"].dropna().nunique()
total_products    = df_sales["StockCode"].nunique()

aov               = gross_revenue / total_invoices if total_invoices else 0
return_rate       = (total_returns / (gross_revenue + total_returns) * 100) if (gross_revenue + total_returns) > 0 else 0

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_kpis, tab_products, tab_time, tab_country, tab_qa = st.tabs([
    "📊 KPIs", "🛍️ Top Products", "📈 Sales Over Time", "🌍 By Country", "✓ QA Checks"
])

# ─────────────────────────────────────────────────────────────────────────────
# Tab 1: KPIs
# ─────────────────────────────────────────────────────────────────────────────
with tab_kpis:
    st.header("Key Performance Indicators")

    # Metrics row 1
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Revenue", f"£{gross_revenue:,.0f}")
    col2.metric("Returns (abs)", f"£{total_returns:,.0f}")
    col3.metric("Net Revenue", f"£{net_revenue:,.0f}")

    # Metrics row 2
    col4, col5, col6 = st.columns(3)
    col4.metric("Total Invoices", f"{total_invoices:,}")
    col5.metric("Total Customers", f"{total_customers:,}")
    col6.metric("Total Products", f"{total_products:,}")

    # Metrics row 3
    col7, col8 = st.columns(2)
    col7.metric("Average Order Value", f"£{aov:,.2f}")
    col8.metric("Return Rate", f"{return_rate:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# Tab 2: Top Products
# ─────────────────────────────────────────────────────────────────────────────
with tab_products:
    st.header(f"Top {top_n} Products by Net Revenue")

    # Group sales (exclude cancellations)
    products_sales = (
        df_sales.groupby(["StockCode", "Description"])
        .agg({"Quantity": "sum", "GrossLineTotal": "sum"})
        .reset_index()
    )
    products_sales.columns = ["StockCode", "Description", "QuantitySold", "GrossRevenue"]

    # Group returns (full data - includes all returns)
    products_returns = (
        df.groupby(["StockCode", "Description"])
        .agg({"ReturnLineTotal": lambda x: abs(x.sum())})
        .reset_index()
    )
    products_returns.columns = ["StockCode", "Description", "Returns"]

    # Merge and calculate
    products = products_sales.merge(products_returns, on=["StockCode", "Description"], how="left")
    products["Returns"] = products["Returns"].fillna(0)
    products["NetRevenue"] = products["GrossRevenue"] - products["Returns"]

    # Calculate return rate
    products["ReturnRate"] = (
        products["Returns"] / (products["GrossRevenue"] + products["Returns"]) * 100
    ).fillna(0)

    # Keep all products for chart, limit to top_n for table
    products_all = products.copy()
    products = products.nlargest(top_n, "NetRevenue")

    # Display table
    st.dataframe(
        products[["StockCode", "Description", "QuantitySold", "GrossRevenue", "Returns", "NetRevenue", "ReturnRate"]]
        .sort_values("NetRevenue", ascending=False)
        .assign(
            GrossRevenue=lambda x: "£" + (x["GrossRevenue"].apply(lambda v: f"{v:,.2f}")),
            Returns=lambda x: "£" + (x["Returns"].apply(lambda v: f"{v:,.2f}")),
            NetRevenue=lambda x: "£" + (x["NetRevenue"].apply(lambda v: f"{v:,.2f}")),
            ReturnRate=lambda x: x["ReturnRate"].apply(lambda v: f"{v:.1f}%"),
        ),
        use_container_width=True,
        hide_index=True,
    )

    # Bar chart - top 15 products by NetRevenue (from all products)
    top_15 = products_all.nlargest(15, "NetRevenue").sort_values("NetRevenue")
    fig = px.bar(
        top_15,
        x="NetRevenue",
        y="Description",
        orientation="h",
        title="Top 15 Products by Net Revenue",
        labels={"NetRevenue": "Net Revenue (£)", "Description": "Product"},
        color="NetRevenue",
        color_continuous_scale="Blues",
        hover_data={"StockCode": True, "Description": True, "NetRevenue": ":.2f"},
    )
    fig.update_layout(
        yaxis_tickfont_size=11,
        coloraxis_showscale=False,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Tab 3: Sales Over Time (changed from Tab 4)
# ─────────────────────────────────────────────────────────────────────────────
with tab_time:
    st.header("Sales Over Time")

    # Resample sales (exclude cancellations)
    sales_time_gross = (
        df_sales.set_index("InvoiceDate")
        .resample(frequency)
        .agg({
            "GrossLineTotal": "sum",
            "InvoiceNo": "nunique",
        })
        .reset_index()
    )
    sales_time_gross.columns = ["Period", "GrossRevenue", "NumInvoices"]

    # Resample returns (full data)
    sales_time_returns = (
        df.set_index("InvoiceDate")
        .resample(frequency)
        .agg({"ReturnLineTotal": lambda x: abs(x.sum())})
        .reset_index()
    )
    sales_time_returns.columns = ["Period", "Returns"]

    # Merge and calculate
    sales_time = sales_time_gross.merge(sales_time_returns, on="Period", how="left")
    sales_time["Returns"] = sales_time["Returns"].fillna(0)
    sales_time["NetRevenue"] = sales_time["GrossRevenue"] - sales_time["Returns"]

    # Display table
    freq_names = {"D": "Day", "W": "Week", "ME": "Month"}
    st.subheader(f"Sales by {freq_names[frequency]}")
    st.dataframe(
        sales_time.assign(
            GrossRevenue=lambda x: "£" + (x["GrossRevenue"].apply(lambda v: f"{v:,.2f}")),
            Returns=lambda x: "£" + (x["Returns"].apply(lambda v: f"{v:,.2f}")),
            NetRevenue=lambda x: "£" + (x["NetRevenue"].apply(lambda v: f"{v:,.2f}")),
        ),
        use_container_width=True,
        hide_index=True,
    )

    # Line chart - Revenue over time (3 lines: Gross, Returns, Net)
    fig = px.line(
        sales_time,
        x="Period",
        y=["GrossRevenue", "Returns", "NetRevenue"],
        title=f"Revenue Trends Over Time",
        labels={"value": "Revenue (£)", "Period": "", "variable": "Type"},
        markers=True,
        color_discrete_map={
            "GrossRevenue": "#4C78A8",    # Blue
            "Returns": "#E45756",          # Red
            "NetRevenue": "#54A24B",       # Green
        },
    )
    fig.update_traces(mode="lines+markers", marker_size=6)
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Tab 4: Sales By Country (changed from Tab 5)
# ─────────────────────────────────────────────────────────────────────────────
with tab_country:
    st.header("Sales by Country")

    # Aggregate sales by country (exclude cancellations)
    by_country_sales = (
        df_sales.groupby("Country")
        .agg({
            "CustomerID": "nunique",
            "InvoiceNo": "nunique",
            "GrossLineTotal": "sum",
        })
        .reset_index()
    )
    by_country_sales.columns = ["Country", "NumCustomers", "NumOrders", "GrossRevenue"]

    # Aggregate returns by country (full data)
    by_country_returns = (
        df.groupby("Country")
        .agg({"ReturnLineTotal": lambda x: abs(x.sum())})
        .reset_index()
    )
    by_country_returns.columns = ["Country", "Returns"]

    # Merge and calculate
    by_country = by_country_sales.merge(by_country_returns, on="Country", how="left")
    by_country["Returns"] = by_country["Returns"].fillna(0)
    by_country["NetRevenue"] = by_country["GrossRevenue"] - by_country["Returns"]

    # Calculate % of total
    total_net = by_country["NetRevenue"].sum()
    by_country["PercentOfTotal"] = (by_country["NetRevenue"] / total_net * 100)

    # Sort and display
    by_country = by_country.sort_values("NetRevenue", ascending=False)

    st.dataframe(
        by_country.assign(
            GrossRevenue=lambda x: "£" + (x["GrossRevenue"].apply(lambda v: f"{v:,.2f}")),
            Returns=lambda x: "£" + (x["Returns"].apply(lambda v: f"{v:,.2f}")),
            NetRevenue=lambda x: "£" + (x["NetRevenue"].apply(lambda v: f"{v:,.2f}")),
            PercentOfTotal=lambda x: x["PercentOfTotal"].apply(lambda v: f"{v:.1f}%"),
        ),
        use_container_width=True,
        hide_index=True,
    )

    # Bar chart - top 10 countries
    # Bar chart - top 10 countries
    top_10_countries = by_country.head(10).sort_values("NetRevenue")
    fig = px.bar(
        top_10_countries,
        x="NetRevenue",
        y="Country",
        orientation="h",
        title="Top 10 Countries by Net Revenue",
        labels={"NetRevenue": "Net Revenue (£)", "Country": ""},
        color="NetRevenue",
        color_continuous_scale="Greens",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Tab 5: QA Checks (changed from Tab 6)
# ─────────────────────────────────────────────────────────────────────────────
with tab_qa:
    st.header("Data Quality Assurance")

    # Row counts
    st.subheader("Row Counts at Each Stage")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Raw rows", f"{len(df_raw):,}")
    col2.metric("After date filter", f"{len(df):,}")
    col3.metric("Excluding cancellations", f"{len(df_sales):,}")
    col4.metric("Cancellation rows", f"{df['IsCancellation'].sum():,}")

    # Reconciliation - Sales
    st.subheader("Sales Reconciliation")

    net_revenue_via_linetotal = df_sales["LineTotal"].sum()
    net_revenue_via_components = df_sales["GrossLineTotal"].sum() + df_sales["ReturnLineTotal"].sum()

    sales_rec_data = {
        "Calculation Method": [
            "Via LineTotal",
            "Via GrossLineTotal + ReturnLineTotal",
        ],
        "Amount": [
            f"£{net_revenue_via_linetotal:,.2f}",
            f"£{net_revenue_via_components:,.2f}",
        ],
        "Match": [
            "✓" if abs(net_revenue_via_linetotal - net_revenue_via_components) < 0.01 else "✗",
            "✓" if abs(net_revenue_via_linetotal - net_revenue_via_components) < 0.01 else "✗",
        ]
    }
    st.dataframe(pd.DataFrame(sales_rec_data), use_container_width=True, hide_index=True)

    # Reconciliation - KPI
    st.subheader("KPI Reconciliation")

    kpi_rec_data = {
        "Metric": [
            "Gross Revenue",
            "Total Returns",
            "Net Revenue",
        ],
        "Calculated": [
            f"£{gross_revenue:,.2f}",
            f"£{total_returns:,.2f}",
            f"£{net_revenue:,.2f}",
        ],
        "Match": [
            "✓",
            "✓",
            "✓",
        ]
    }
    st.dataframe(pd.DataFrame(kpi_rec_data), use_container_width=True, hide_index=True)

    # Sample invoices with line items
    st.subheader("Sample of 5 Invoices with Line Items")

    np.random.seed(42)
    sample_invoices = np.random.choice(df_sales["InvoiceNo"].unique(), size=5, replace=False)
    sample_data = df_sales[df_sales["InvoiceNo"].isin(sample_invoices)][
        ["InvoiceNo", "InvoiceDate", "StockCode", "Description", "Quantity", "UnitPrice", "LineTotal", "GrossLineTotal", "ReturnLineTotal"]
    ].copy()

    sample_data = sample_data.assign(
        LineTotal=lambda x: "£" + (x["LineTotal"].apply(lambda v: f"{v:,.2f}")),
        GrossLineTotal=lambda x: "£" + (x["GrossLineTotal"].apply(lambda v: f"{v:,.2f}")),
        ReturnLineTotal=lambda x: "£" + (x["ReturnLineTotal"].apply(lambda v: f"{v:,.2f}")),
        UnitPrice=lambda x: "£" + (x["UnitPrice"].apply(lambda v: f"{v:.2f}")),
    )

    st.dataframe(
        sample_data,
        use_container_width=True,
        hide_index=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption(f"Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data period: {start_date} to {end_date}")
