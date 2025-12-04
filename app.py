# app.py

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st

# ------------- App config -------------
st.set_page_config(
    page_title="Ecommerce Search Demo",
    page_icon="🛒",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "ecommerce_search_logs.csv"


# ------------- Synthetic data generator -------------
def generate_synthetic_data(n_rows: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    now = datetime.utcnow()
    timestamps = [now - timedelta(minutes=int(m)) for m in rng.integers(0, 60 * 24 * 30, size=n_rows)]

    queries = [
        "running shoes",
        "wireless headphones",
        "laptop bag",
        "phone charger",
        "coffee mug",
        "office chair",
        "gaming keyboard",
        "baby stroller",
        "winter jacket",
        "smartwatch",
    ]
    countries = ["Canada", "USA", "UK", "Germany", "India", "Brazil"]
    devices = ["mobile", "desktop", "tablet"]

    data = {
        "timestamp": timestamps,
        "session_id": rng.integers(10000, 99999, size=n_rows),
        "user_id": rng.integers(1, 500, size=n_rows),
        "query": rng.choice(queries, size=n_rows),
        "n_results": rng.integers(0, 50, size=n_rows),
        "clicked": rng.choice([0, 1], size=n_rows, p=[0.3, 0.7]),
        "dwell_time_sec": rng.gamma(shape=2.0, scale=15.0, size=n_rows),
        "added_to_cart": rng.choice([0, 1], size=n_rows, p=[0.75, 0.25]),
        "purchased": rng.choice([0, 1], size=n_rows, p=[0.9, 0.1]),
        "country": rng.choice(countries, size=n_rows),
        "device": rng.choice(devices, size=n_rows),
    }

    df = pd.DataFrame(data)
    return df


# ------------- Data loader with EmptyDataError handling -------------
@st.cache_data
def load_data() -> pd.DataFrame:
    # 1) If file doesn't exist or is zero bytes -> generate and save
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        st.warning(
            "No ecommerce_search_logs.csv data found or file is empty. "
            "Generating synthetic dataset for the demo."
        )
        df_gen = generate_synthetic_data()
        df_gen.to_csv(CSV_PATH, index=False)
        return df_gen

    # 2) Try reading existing file, handle empty/invalid data
    try:
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    except pd.errors.EmptyDataError:
        st.warning(
            "Existing ecommerce_search_logs.csv is empty. "
            "Generating synthetic dataset for the demo."
        )
        df = generate_synthetic_data()
        df.to_csv(CSV_PATH, index=False)
    except Exception as e:
        st.error(f"Error reading ecommerce_search_logs.csv: {e}")
        st.info("Generating a fresh synthetic dataset instead.")
        df = generate_synthetic_data()
        df.to_csv(CSV_PATH, index=False)

    return df


# ------------- Main app -------------
st.title("🛒 Ecommerce Search Analytics Demo")

st.caption(
    "Synthetic demo dashboard for analyzing on-site search behaviour: queries, clicks, "
    "conversions and traffic patterns."
)

df = load_data()

if df.empty:
    st.error("Dataset is empty even after generation. Please check file permissions.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

country_filter = st.sidebar.multiselect(
    "Country",
    options=sorted(df["country"].dropna().unique().tolist()),
    default=[],
)

device_filter = st.sidebar.multiselect(
    "Device",
    options=sorted(df["device"].dropna().unique().tolist()),
    default=[],
)

query_search = st.sidebar.text_input(
    "Search term contains",
    placeholder="e.g. shoes, headphones",
)

# Apply filters
mask = (
    (df["timestamp"].dt.date >= start_date)
    & (df["timestamp"].dt.date <= end_date)
)

if country_filter:
    mask &= df["country"].isin(country_filter)

if device_filter:
    mask &= df["device"].isin(device_filter)

if query_search.strip():
    mask &= df["query"].str.contains(query_search.strip(), case=False, na=False)

df_filt = df[mask].copy()

st.subheader("Summary metrics")

col1, col2, col3, col4 = st.columns(4)

total_searches = len(df_filt)
click_through_rate = (df_filt["clicked"].mean() * 100) if total_searches else 0
add_to_cart_rate = (df_filt["added_to_cart"].mean() * 100) if total_searches else 0
purchase_rate = (df_filt["purchased"].mean() * 100) if total_searches else 0

with col1:
    st.metric("Total searches", f"{total_searches:,}")
with col2:
    st.metric("Click-through rate", f"{click_through_rate:.1f}%")
with col3:
    st.metric("Add-to-cart rate", f"{add_to_cart_rate:.1f}%")
with col4:
    st.metric("Purchase rate", f"{purchase_rate:.1f}%")

st.markdown("---")

# Top queries
st.subheader("Top search queries")

top_n = st.slider("Show top N queries", min_value=5, max_value=30, value=10, step=1)

top_queries = (
    df_filt.groupby("query")
    .agg(
        searches=("query", "count"),
        ctr=("clicked", "mean"),
        purchases=("purchased", "sum"),
    )
    .sort_values("searches", ascending=False)
    .head(top_n)
)

st.dataframe(
    top_queries.assign(
        ctr=lambda x: (x["ctr"] * 100).round(1)
    ).rename(columns={"ctr": "ctr_%"}),
    use_container_width=True,
)

# Time series
st.subheader("Searches over time")

ts = (
    df_filt.set_index("timestamp")
    .resample("D")
    .agg(
        searches=("query", "count"),
        ctr=("clicked", "mean"),
        purchases=("purchased", "sum"),
    )
)

if not ts.empty:
    st.line_chart(ts[["searches"]])
else:
    st.info("No data available for the selected filters / date range.")

st.markdown("---")

st.subheader("Raw filtered data preview")
st.dataframe(df_filt.head(200), use_container_width=True)
