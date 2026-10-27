import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="NYC Airbnb Market Analysis",
    page_icon="🏙️",
    layout="wide",
)

# ---------- Connection (cached so we don't reconnect on every interaction) ----------
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(**st.secrets["snowflake"])

@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        df = cur.fetch_pandas_all()
    finally:
        cur.close()
    # Snowflake returns UPPERCASE column names by default; keep them
    return df

# ---------- Load data ----------
@st.cache_data(ttl=600)
def load_neighbourhoods() -> pd.DataFrame:
    return run_query("""
        select * from AIRBNB_PORTFOLIO.ANALYTICS.FCT_NEIGHBOURHOOD_SUMMARY
    """)

@st.cache_data(ttl=600)
def load_room_types() -> pd.DataFrame:
    return run_query("""
        select * from AIRBNB_PORTFOLIO.ANALYTICS.FCT_LISTINGS_BY_ROOM_TYPE
    """)

df_neigh = load_neighbourhoods()
df_room  = load_room_types()

# ---------- Header ----------
st.title("🏙️ NYC Airbnb Market Analysis")
st.markdown(
    "End-to-end analytics pipeline: **Snowflake** + **dbt** + **Streamlit**. "
    "Source: Inside Airbnb (NYC) — 30,259 listings, price outliers (>$2,000/night) excluded."
)

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
boroughs = ["All"] + sorted(df_neigh["BOROUGH"].unique().tolist())
selected_borough = st.sidebar.selectbox("Borough", boroughs)

if selected_borough != "All":
    df_neigh_filtered = df_neigh[df_neigh["BOROUGH"] == selected_borough]
    df_room_filtered = df_room[df_room["BOROUGH"] == selected_borough]
else:
    df_neigh_filtered = df_neigh
    df_room_filtered = df_room

# ---------- KPI row ----------
col1, col2, col3, col4 = st.columns(4)
#col1.metric("Neighbourhoods", f"{len(df_neigh_filtered):,}")
col1.metric("Neighbourhoods (≥10 listings)", f"{len(df_neigh_filtered):,}")
col2.metric(
    "Total listings",
    f"{int(df_neigh_filtered['LISTING_COUNT'].sum()):,}",
)
col3.metric(
    "Median price (all)",
    f"${df_neigh_filtered['MEDIAN_PRICE'].median():,.0f}",
)
col4.metric(
    "Avg review rating",
    f"{df_neigh_filtered['AVG_REVIEW_RATING'].mean():.2f} / 5",
)

st.divider()

# ---------- Chart 1: Top neighbourhoods by median price ----------
st.subheader(f"Top 15 Neighbourhoods by Median Price (of {len(df_neigh_filtered)})")
top15 = df_neigh_filtered.nlargest(15, "MEDIAN_PRICE")
fig1 = px.bar(
    top15.sort_values("MEDIAN_PRICE"),
    x="MEDIAN_PRICE",
    y="NEIGHBOURHOOD",
    color="BOROUGH",
    orientation="h",
    text="MEDIAN_PRICE",
    labels={"MEDIAN_PRICE": "Median price (USD)", "NEIGHBOURHOOD": ""},
)
fig1.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
fig1.update_layout(height=500, showlegend=True)
st.plotly_chart(fig1, use_container_width=True)

# ---------- Chart 1b: Distribution by borough ----------
st.subheader("Neighbourhood Distribution by Borough")
fig1b = px.box(
    df_neigh_filtered,
    x="BOROUGH",
    y="MEDIAN_PRICE",
    color="BOROUGH",
    points="all",
    hover_name="NEIGHBOURHOOD",
    labels={"MEDIAN_PRICE": "Median neighbourhood price (USD)", "BOROUGH": ""},
)
fig1b.update_layout(height=450, showlegend=False)
st.plotly_chart(fig1b, use_container_width=True)

st.caption(
    "Each dot is one neighbourhood. Box shows the interquartile range (25th–75th percentile); "
    "line inside is the median of neighbourhood medians. This reveals spread within boroughs."
)

# ---------- Chart 2: Price vs revenue scatter ----------
st.subheader("Median Price vs. Median Annual Revenue")
fig2 = px.scatter(
    df_neigh_filtered,
    x="MEDIAN_PRICE",
    y="MEDIAN_ANNUAL_REVENUE",
    size="LISTING_COUNT",
    color="BOROUGH",
    hover_name="NEIGHBOURHOOD",
    labels={
        "MEDIAN_PRICE": "Median nightly price (USD)",
        "MEDIAN_ANNUAL_REVENUE": "Median annual revenue (USD)",
    },
)
fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "Bubble size = number of listings in neighbourhood. "
    "Neighbourhoods with high price but low revenue may indicate seasonal or underperforming markets."
)

# ---------- Chart 3: Room type breakdown ----------
st.subheader("Room Type Mix by Borough")
fig3 = px.bar(
    df_room_filtered,
    x="BOROUGH",
    y="LISTING_COUNT",
    color="ROOM_TYPE",
    barmode="group",
    labels={"LISTING_COUNT": "Listings", "BOROUGH": ""},
)
fig3.update_layout(height=450)
st.plotly_chart(fig3, use_container_width=True)

# ---------- Data table ----------
with st.expander("📊 View underlying neighbourhood data"):
    st.dataframe(
        df_neigh_filtered.sort_values("MEDIAN_PRICE", ascending=False),
        use_container_width=True,
    )

st.divider()
st.caption(
    "Built as a portfolio project. Data pipeline: Snowflake → dbt (staging → intermediate → marts) → Streamlit. "
    "Excludes price outliers (>$2,000/night) and neighbourhoods with <10 priced listings."
)