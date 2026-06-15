import math
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from scripts.seed_data import OUTPUT, main as seed_data


st.set_page_config(page_title="A/B Testing Platform", layout="wide")


def ensure_data():
    if not OUTPUT.exists():
        seed_data()
    return pd.read_csv(OUTPUT, parse_dates=["visit_date"])


def z_test(control_success, control_total, treatment_success, treatment_total):
    p1 = control_success / control_total
    p2 = treatment_success / treatment_total
    pooled = (control_success + treatment_success) / (control_total + treatment_total)
    se = math.sqrt(pooled * (1 - pooled) * (1 / control_total + 1 / treatment_total))
    z = (p2 - p1) / se if se else 0
    p_value = math.erfc(abs(z) / math.sqrt(2))
    ci_low = (p2 - p1) - 1.96 * se
    ci_high = (p2 - p1) + 1.96 * se
    return p1, p2, z, p_value, ci_low, ci_high


def money(value):
    return f"${value:,.0f}"


data = ensure_data()
conn = sqlite3.connect(":memory:")
data.to_sql("experiment", conn, index=False, if_exists="replace")

st.title("A/B Testing & Experimentation Platform")
st.caption("Landing page experiment analysis with CTR, conversion, revenue impact, and statistical significance.")

with st.sidebar:
    st.header("Experiment Filters")
    devices = st.multiselect("Device", sorted(data["device"].unique()), default=sorted(data["device"].unique()))
    sources = st.multiselect("Traffic source", sorted(data["traffic_source"].unique()), default=sorted(data["traffic_source"].unique()))
    metric = st.selectbox("Primary metric", ["converted", "clicked"])

filtered = data[data["device"].isin(devices) & data["traffic_source"].isin(sources)]
summary = filtered.groupby("variant").agg(
    visitors=("visitor_id", "count"),
    clicks=("clicked", "sum"),
    conversions=("converted", "sum"),
    revenue=("revenue", "sum"),
).reset_index()
summary["ctr"] = summary["clicks"] / summary["visitors"]
summary["conversion_rate"] = summary["conversions"] / summary["visitors"]
summary["revenue_per_visitor"] = summary["revenue"] / summary["visitors"]

control = summary[summary["variant"] == "Old Landing Page"].iloc[0]
treatment = summary[summary["variant"] == "New Landing Page"].iloc[0]
success_col = "conversions" if metric == "converted" else "clicks"
p1, p2, z, p_value, ci_low, ci_high = z_test(
    int(control[success_col]),
    int(control["visitors"]),
    int(treatment[success_col]),
    int(treatment["visitors"]),
)

lift = (p2 - p1) / p1 if p1 else 0
revenue_lift = treatment["revenue_per_visitor"] - control["revenue_per_visitor"]
projected_monthly_visitors = 120000
projected_impact = revenue_lift * projected_monthly_visitors

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Control Rate", f"{p1:.2%}")
k2.metric("Treatment Rate", f"{p2:.2%}")
k3.metric("Lift", f"{lift:.2%}")
k4.metric("p-value", f"{p_value:.4f}")
k5.metric("Monthly Impact", money(projected_impact))

tab_summary, tab_stats, tab_segments, tab_sql = st.tabs(["Executive Summary", "Statistics", "Segments", "SQL"])

with tab_summary:
    st.subheader("Variant Performance")
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.bar_chart(summary, x="variant", y=["conversion_rate", "ctr"], height=320)

    if p_value < 0.05 and p2 > p1:
        st.success("Decision: Ship the new landing page. It improves the selected metric with statistical significance.")
    elif p_value < 0.05:
        st.error("Decision: Keep the old landing page. The treatment underperforms with statistical significance.")
    else:
        st.warning("Decision: Keep testing. The observed difference is not statistically significant yet.")

with tab_stats:
    st.subheader("Hypothesis Test")
    st.markdown(
        f"""
        **Null hypothesis:** old and new landing pages have the same {metric} rate.

        **Alternative hypothesis:** the new landing page changes the {metric} rate.

        - z-score: `{z:.3f}`
        - p-value: `{p_value:.4f}`
        - 95% confidence interval for lift in percentage points: `{ci_low:.2%}` to `{ci_high:.2%}`
        """
    )

with tab_segments:
    st.subheader("Conversion by Segment")
    segment = filtered.groupby(["traffic_source", "variant"], as_index=False).agg(
        visitors=("visitor_id", "count"),
        conversion_rate=("converted", "mean"),
        revenue_per_visitor=("revenue", "mean"),
    )
    st.dataframe(segment, use_container_width=True, hide_index=True)

with tab_sql:
    st.subheader("SQL Experiment Queries")
    st.code(Path("sql/experiment_queries.sql").read_text(encoding="utf-8"), language="sql")
    st.subheader("SQLite Result")
    result = pd.read_sql_query(
        """
        SELECT variant, COUNT(*) AS visitors, ROUND(100.0 * AVG(converted), 2) AS conversion_rate,
               ROUND(AVG(revenue), 2) AS revenue_per_visitor
        FROM experiment
        GROUP BY variant
        """,
        conn,
    )
    st.dataframe(result, use_container_width=True, hide_index=True)
