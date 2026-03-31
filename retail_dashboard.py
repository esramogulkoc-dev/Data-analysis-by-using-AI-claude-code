import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Dashboard",
    page_icon="🛒",
    layout="wide",
)

FILE = "Online Retail.xlsx"

# ── Data loading & prep (cached) ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset...")
def load_data():
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
    st.title("Controls")

    date_min = df_raw["InvoiceDate"].dt.date.min()
    date_max = df_raw["InvoiceDate"].dt.date.max()
    date_range = st.date_input(
        "Date range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    top_n = st.slider("Top N", min_value=5, max_value=50, value=10, step=5)

    freq = st.selectbox(
        "Sales trend frequency",
        options=["D", "W", "ME"],
        format_func=lambda x: {"D": "Daily", "W": "Weekly", "ME": "Monthly"}[x],
        index=2,
    )

    exclude_cancellations = st.checkbox("Exclude cancellations from charts", value=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_min, date_max

mask = (
    (df_raw["InvoiceDate"].dt.date >= start_date) &
    (df_raw["InvoiceDate"].dt.date <= end_date)
)
df = df_raw[mask].copy()

df_sales = df[~df["IsCancellation"]] if exclude_cancellations else df

# ── KPI calculations ──────────────────────────────────────────────────────────
total_revenue     = df_sales["GrossLineTotal"].sum()
total_orders      = df_sales["InvoiceNo"].nunique()
total_customers   = df_sales["CustomerID"].dropna().nunique()
total_items       = df_sales["Quantity"][df_sales["Quantity"] > 0].sum()
aov               = total_revenue / total_orders if total_orders else 0
total_returns     = df["ReturnLineTotal"].sum()  # always show returns
cancellation_rows = df["IsCancellation"].sum()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_kpi, tab_products, tab_customers, tab_trend, tab_country, tab_qa = st.tabs([
    "KPIs", "Top Products", "Top Customers", "Sales Trend", "By Country", "QA Checks"
])

# ── Tab: KPIs ─────────────────────────────────────────────────────────────────
with tab_kpi:
    st.header("Key Performance Indicators")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Gross Revenue",    f"£{total_revenue:,.0f}")
    c2.metric("Orders",           f"{total_orders:,}")
    c3.metric("Unique Customers", f"{total_customers:,}")
    c4.metric("Avg Order Value",  f"£{aov:,.2f}")
    c5.metric("Items Sold",       f"{total_items:,.0f}")

    c6, c7 = st.columns(2)
    c6.metric("Total Returns",       f"£{total_returns:,.0f}")
    c7.metric("Cancellation Rows",   f"{cancellation_rows:,}")

    st.divider()

    # Revenue over time (monthly) as area chart
    rev_trend = (
        df_sales.set_index("InvoiceDate")["GrossLineTotal"]
        .resample("ME")
        .sum()
        .reset_index()
    )
    rev_trend.columns = ["Month", "Revenue"]
    fig = px.area(
        rev_trend, x="Month", y="Revenue",
        title="Monthly Revenue Overview",
        labels={"Revenue": "Revenue (£)", "Month": ""},
        color_discrete_sequence=["#4C78A8"],
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# ── Tab: Top Products ─────────────────────────────────────────────────────────
with tab_products:
    st.header(f"Top {top_n} Products")

    top_products = (
        df_sales.groupby("Description")["GrossLineTotal"]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values("GrossLineTotal")
    )
    top_products.columns = ["Product", "Revenue"]

    fig = px.bar(
        top_products, x="Revenue", y="Product",
        orientation="h",
        title=f"Top {top_n} Products by Revenue",
        labels={"Revenue": "Revenue (£)", "Product": ""},
        color="Revenue",
        color_continuous_scale="Blues",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_tickfont_size=11)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Top {top_n} Products by Units Sold")
    top_units = (
        df_sales[df_sales["Quantity"] > 0]
        .groupby("Description")["Quantity"]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values("Quantity")
    )
    top_units.columns = ["Product", "Units"]
    fig2 = px.bar(
        top_units, x="Units", y="Product",
        orientation="h",
        labels={"Units": "Units Sold", "Product": ""},
        color="Units",
        color_continuous_scale="Oranges",
    )
    fig2.update_layout(coloraxis_showscale=False, yaxis_tickfont_size=11)
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab: Top Customers ────────────────────────────────────────────────────────
with tab_customers:
    st.header(f"Top {top_n} Customers")

    df_known = df_sales.dropna(subset=["CustomerID"])
    df_known = df_known.copy()
    df_known["CustomerID"] = df_known["CustomerID"].astype(int).astype(str)

    top_customers = (
        df_known.groupby("CustomerID")["GrossLineTotal"]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values("GrossLineTotal")
    )
    top_customers.columns = ["CustomerID", "Revenue"]

    fig = px.bar(
        top_customers, x="Revenue", y="CustomerID",
        orientation="h",
        title=f"Top {top_n} Customers by Revenue",
        labels={"Revenue": "Revenue (£)", "CustomerID": "Customer ID"},
        color="Revenue",
        color_continuous_scale="Greens",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Top {top_n} Customers by Order Count")
    top_orders = (
        df_known.groupby("CustomerID")["InvoiceNo"]
        .nunique()
        .nlargest(top_n)
        .reset_index()
        .sort_values("InvoiceNo")
    )
    top_orders.columns = ["CustomerID", "Orders"]
    fig2 = px.bar(
        top_orders, x="Orders", y="CustomerID",
        orientation="h",
        labels={"Orders": "Number of Orders", "CustomerID": "Customer ID"},
        color="Orders",
        color_continuous_scale="Purples",
    )
    fig2.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab: Sales Trend ──────────────────────────────────────────────────────────
with tab_trend:
    freq_label = {"D": "Daily", "W": "Weekly", "ME": "Monthly"}[freq]
    st.header(f"{freq_label} Sales Trend")

    trend = (
        df_sales.set_index("InvoiceDate")["GrossLineTotal"]
        .resample(freq)
        .sum()
        .reset_index()
    )
    trend.columns = ["Date", "Revenue"]

    fig = px.line(
        trend, x="Date", y="Revenue",
        title=f"{freq_label} Revenue",
        labels={"Revenue": "Revenue (£)", "Date": ""},
        color_discrete_sequence=["#4C78A8"],
    )
    fig.update_traces(mode="lines+markers", marker_size=4)
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # Orders trend
    orders_trend = (
        df_sales.set_index("InvoiceDate")["InvoiceNo"]
        .resample(freq)
        .nunique()
        .reset_index()
    )
    orders_trend.columns = ["Date", "Orders"]

    fig2 = px.bar(
        orders_trend, x="Date", y="Orders",
        title=f"{freq_label} Order Count",
        labels={"Orders": "Number of Orders", "Date": ""},
        color_discrete_sequence=["#F58518"],
    )
    fig2.update_layout(hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab: By Country ───────────────────────────────────────────────────────────
with tab_country:
    st.header("Sales by Country")

    by_country = (
        df_sales.groupby("Country")
        .agg(Revenue=("GrossLineTotal", "sum"), Orders=("InvoiceNo", "nunique"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    # Choropleth map
    fig_map = px.choropleth(
        by_country,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        hover_data={"Orders": True, "Revenue": ":,.0f"},
        title="Revenue by Country",
        color_continuous_scale="Blues",
    )
    fig_map.update_layout(geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.bar(
            by_country.head(top_n).sort_values("Revenue"),
            x="Revenue", y="Country",
            orientation="h",
            title=f"Top {top_n} Countries by Revenue",
            labels={"Revenue": "Revenue (£)"},
            color="Revenue",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Exclude UK for pie to show other countries clearly
        no_uk = by_country[by_country["Country"] != "United Kingdom"].head(top_n)
        fig_pie = px.pie(
            no_uk, values="Revenue", names="Country",
            title=f"Revenue Share (ex-UK, Top {top_n})",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Full Country Table")
    by_country["Revenue"] = by_country["Revenue"].map("£{:,.2f}".format)
    st.dataframe(by_country, use_container_width=True, hide_index=True)

# ── Tab: QA Checks ────────────────────────────────────────────────────────────
with tab_qa:
    st.header("Data Quality Checks")

    total_rows      = len(df)
    cancel_rows     = int(df["IsCancellation"].sum())
    missing_cid     = int(df["CustomerID"].isna().sum())
    zero_price_rows = int((df["UnitPrice"] <= 0).sum())
    missing_desc    = int(df["Description"].isna().sum())

    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Total Rows (filtered)", f"{total_rows:,}")
    q2.metric("Cancellation Rows",     f"{cancel_rows:,}",  f"{cancel_rows/total_rows*100:.1f}%")
    q3.metric("Missing CustomerID",    f"{missing_cid:,}",  f"{missing_cid/total_rows*100:.1f}%")
    q4.metric("UnitPrice <= 0",        f"{zero_price_rows:,}", f"{zero_price_rows/total_rows*100:.2f}%")
    q5.metric("Missing Description",   f"{missing_desc:,}", f"{missing_desc/total_rows*100:.2f}%")

    st.divider()

    st.subheader("Cancellations Over Time")
    cancel_trend = (
        df[df["IsCancellation"]]
        .set_index("InvoiceDate")["InvoiceNo"]
        .resample("ME")
        .count()
        .reset_index()
    )
    cancel_trend.columns = ["Month", "Cancellations"]
    fig = px.bar(
        cancel_trend, x="Month", y="Cancellations",
        title="Monthly Cancellation Row Count",
        color_discrete_sequence=["#E45756"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rows with UnitPrice <= 0")
    st.dataframe(
        df[df["UnitPrice"] <= 0][["InvoiceNo", "StockCode", "Description", "Quantity", "UnitPrice", "InvoiceDate"]].head(50),
        use_container_width=True,
        hide_index=True,
    )
