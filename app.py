import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Ecommerce Search Demo", layout="wide")

@st.cache_data
def load_data(path: str = "ecommerce_search_logs.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df

df = load_data()

st.title("Ecommerce Search & Relevance Insights")
st.write("Demo dashboard to support Account Executives with search analytics, low-performing query detection, and A/B tuning simulation.")

# ===== KPIs =====
total_searches = len(df)
total_clicks = df["clicked"].sum()
total_purchases = df["purchased"].sum()
total_revenue = df["revenue"].sum()

ctr = total_clicks / total_searches if total_searches else 0
post_click_cr = total_purchases / total_clicks if total_clicks else 0
rps = total_revenue / total_searches if total_searches else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Searches", f"{total_searches}")
k2.metric("CTR", f"{ctr:.2%}")
k3.metric("Conversion Rate (post-click)", f"{post_click_cr:.2%}")
k4.metric("Revenue per Search", f"${rps:,.2f}")

st.markdown("---")

# ===== Query-level aggregation =====
query_grp = (
    df.groupby("normalized_query")
      .agg(
          searches=("normalized_query", "count"),
          clicks=("clicked", "sum"),
          purchases=("purchased", "sum"),
          revenue=("revenue", "sum"),
          no_result_rate=("no_result", "mean")
      )
      .reset_index()
)
query_grp["ctr"] = query_grp["clicks"] / query_grp["searches"]
query_grp["post_click_cr"] = query_grp["purchases"] / query_grp["clicks"].replace(0, np.nan)
query_grp["rps"] = query_grp["revenue"] / query_grp["searches"]

st.subheader("Top Queries by Revenue")
st.dataframe(
    query_grp.sort_values("revenue", ascending=False).head(10),
    use_container_width=True
)

fig = px.scatter(
    query_grp,
    x="searches",
    y="revenue",
    size="clicks",
    hover_name="normalized_query",
    title="Search Volume vs Revenue (bubble size = clicks)"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ===== Low-performing queries =====
st.subheader("High-volume, Low-CTR Queries (Opportunities)")

median_searches = query_grp["searches"].median()
median_ctr = query_grp["ctr"].median()

low_perf = query_grp[
    (query_grp["searches"] >= median_searches) &
    (query_grp["ctr"] < median_ctr)
].copy()

st.write("These queries get a lot of traffic but underperform in engagement:")
st.dataframe(
    low_perf.sort_values(["searches", "ctr"], ascending=[False, True]).head(10),
    use_container_width=True
)

# Simple suggestion engine
st.subheader("Suggested Tuning Actions (Rule-based Demo)")

suggestions = []
for _, row in low_perf.iterrows():
    q = row["normalized_query"]
    sugg = [
        "Review top 10 results and ensure relevance to intent.",
        "Add synonyms and spelling variants.",
        "Boost high-margin or best-selling SKUs.",
        "Improve titles/descriptions and category filters."
    ]
    suggestions.append({
        "query": q,
        "issue": "High volume, low CTR",
        "suggested_actions": "; ".join(sugg)
    })

if suggestions:
    st.dataframe(pd.DataFrame(suggestions), use_container_width=True)
else:
    st.info("No low-performing high-volume queries in this sample.")

st.markdown("---")

# ===== Interactive query deep-dive =====
st.subheader("Interactive Query Deep-Dive")

selected_query = st.selectbox(
    "Select a query to inspect:",
    options=sorted(query_grp["normalized_query"].unique())
)

qstats = query_grp[query_grp["normalized_query"] == selected_query].iloc[0]
st.write(f"**Query:** {selected_query}")
st.write(f"- Searches: {qstats['searches']}")
st.write(f"- CTR: {qstats['ctr']:.2%}")
st.write(f"- Post-click Conversion: {qstats['post_click_cr']:.2%}")
st.write(f"- Revenue per Search: ${qstats['rps']:.2f}")
st.write(f"- No-result rate: {qstats['no_result_rate']:.1%}")

st.write("Suggested next steps for this query:")
st.markdown("""
- Validate that the top-ranked products match the query intent.
- Add query-level synonyms and spelling corrections.
- Boost SKUs with high margin and strong click/purchase history.
- Consider promo banners or badges for top products.
""")

st.markdown("---")

# ===== A/B Simulation =====
st.subheader("A/B Test Simulation: Expected Lift from CTR Improvement")

col1, col2 = st.columns(2)
with col1:
    expected_ctr_lift_pct = st.slider(
        "Expected CTR lift (%) after tuning",
        min_value=5,
        max_value=200,
        value=20,
        step=5
    )
    sample_searches = st.number_input(
        "Sample searches per variant",
        min_value=500,
        max_value=20000,
        value=5000,
        step=500
    )
with col2:
    st.metric("Baseline CTR", f"{ctr:.2%}")
    st.metric("Baseline Post-click CR", f"{post_click_cr:.2%}")

if st.button("Run A/B Simulation"):
    baseline_ctr = ctr
    new_ctr = baseline_ctr * (1 + expected_ctr_lift_pct/100.0)

    control_clicks = int(sample_searches * baseline_ctr)
    variant_clicks = int(sample_searches * new_ctr)

    control_purchases = int(control_clicks * post_click_cr)
    variant_purchases = int(variant_clicks * post_click_cr)

    avg_revenue_per_purchase = total_revenue / total_purchases if total_purchases else 50
    control_revenue = control_purchases * avg_revenue_per_purchase
    variant_revenue = variant_purchases * avg_revenue_per_purchase
    delta_revenue = variant_revenue - control_revenue

    st.write("**Simulation (per variant)**")
    st.write(f"- Control revenue: ${control_revenue:,.2f}")
    st.write(f"- Variant revenue: ${variant_revenue:,.2f}")
    if control_revenue > 0:
        st.write(f"- Estimated revenue lift: ${delta_revenue:,.2f} ({delta_revenue / control_revenue:.2%})")
    else:
        st.write("- Not enough baseline data to estimate lift reliably.")

st.caption("Note: This is a simplified, illustrative simulation for demo purposes (pre-sales conversation).")
