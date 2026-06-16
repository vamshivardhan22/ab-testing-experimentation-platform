import math
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path("data/marketing_ab.csv")

st.set_page_config(page_title="A/B Testing Platform", layout="wide")


@st.cache_data
def load_experiment():
    return pd.read_csv(DATA_PATH)


def z_test(control_success, control_total, treatment_success, treatment_total):
    p1 = control_success / control_total
    p2 = treatment_success / treatment_total
    pooled = (control_success + treatment_success) / (control_total + treatment_total)
    se = math.sqrt(pooled * (1 - pooled) * (1 / control_total + 1 / treatment_total))
    z = (p2 - p1) / se if se else 0
    p_value = math.erfc(abs(z) / math.sqrt(2))
    diff = p2 - p1
    ci_low = diff - 1.96 * se
    ci_high = diff + 1.96 * se
    return p1, p2, z, p_value, diff, ci_low, ci_high


def summarize(data):
    summary = data.groupby("variant").agg(
        users=("user_id", "count"),
        conversions=("converted", "sum"),
        avg_ads=("total_ads", "mean"),
        median_ads=("total_ads", "median"),
    ).reset_index()
    summary["conversion_rate"] = summary["conversions"] / summary["users"]
    return summary


data = load_experiment()
conn = sqlite3.connect(":memory:")
data.to_sql("experiment", conn, index=False, if_exists="replace")

st.title("A/B Testing & Experimentation Platform")
st.caption(
    "Real marketing A/B test analysis comparing ad exposure against public service announcement exposure."
)

with st.sidebar:
    st.header("Experiment Filters")
    days = st.multiselect("Most ads day", sorted(data["most_ads_day"].unique()), default=sorted(data["most_ads_day"].unique()))
    hours = st.slider("Most ads hour range", 0, 23, (0, 23))
    min_ads = st.number_input("Minimum ads seen", min_value=0, value=0, step=1)

filtered = data[
    data["most_ads_day"].isin(days)
    & data["most_ads_hour"].between(hours[0], hours[1])
    & (data["total_ads"] >= min_ads)
]

summary = summarize(filtered)
control = summary[summary["variant"] == "Public Service Announcement"].iloc[0]
treatment = summary[summary["variant"] == "Ad Campaign"].iloc[0]
p1, p2, z, p_value, diff, ci_low, ci_high = z_test(
    int(control["conversions"]),
    int(control["users"]),
    int(treatment["conversions"]),
    int(treatment["users"]),
)
relative_lift = diff / p1 if p1 else 0
incremental_conversions = diff * int(treatment["users"])

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Users", f"{len(filtered):,}")
k2.metric("Control CVR", f"{p1:.2%}")
k3.metric("Ad CVR", f"{p2:.2%}")
k4.metric("Relative Lift", f"{relative_lift:.2%}")
k5.metric("p-value", f"{p_value:.4f}")
k6.metric("Incremental Conversions", f"{incremental_conversions:,.0f}")

tab_summary, tab_stats, tab_segments, tab_sql = st.tabs(
    ["Executive Summary", "Statistical Test", "Segments", "SQL"]
)

with tab_summary:
    st.subheader("Variant Performance")
    st.dataframe(summary, width="stretch", hide_index=True)
    chart_data = summary[["variant", "conversion_rate"]].copy()
    st.bar_chart(chart_data, x="variant", y="conversion_rate", height=320)

    if p_value < 0.05 and p2 > p1:
        st.success("Decision: The ad campaign significantly improves conversion versus PSA exposure.")
    elif p_value < 0.05:
        st.error("Decision: The ad campaign significantly underperforms the PSA control.")
    else:
        st.warning("Decision: Continue testing. The selected slice is not statistically significant.")

with tab_stats:
    st.subheader("Two-Proportion Z-Test")
    st.markdown(
        f"""
        **Null hypothesis:** ad campaign and PSA control have equal conversion rates.

        **Alternative hypothesis:** ad campaign conversion rate is different from PSA control.

        - z-score: `{z:.3f}`
        - p-value: `{p_value:.4f}`
        - absolute lift: `{diff:.3%}`
        - 95% confidence interval: `{ci_low:.3%}` to `{ci_high:.3%}`
        """
    )

with tab_segments:
    st.subheader("Conversion by Day")
    by_day = filtered.groupby(["most_ads_day", "variant"], as_index=False).agg(
        users=("user_id", "count"),
        conversion_rate=("converted", "mean"),
        avg_ads=("total_ads", "mean"),
    )
    st.dataframe(by_day, width="stretch", hide_index=True)

    st.subheader("Conversion by Hour")
    by_hour = filtered.groupby(["most_ads_hour", "variant"], as_index=False).agg(
        users=("user_id", "count"),
        conversion_rate=("converted", "mean"),
    )
    st.line_chart(by_hour, x="most_ads_hour", y="conversion_rate", color="variant", height=330)

with tab_sql:
    st.subheader("SQL Experiment Queries")
    st.code(Path("sql/experiment_queries.sql").read_text(encoding="utf-8"), language="sql")
    st.subheader("SQLite Result")
    result = pd.read_sql_query(
        """
        SELECT variant,
               COUNT(*) AS users,
               ROUND(100.0 * AVG(converted), 2) AS conversion_rate,
               ROUND(AVG(total_ads), 2) AS avg_ads
        FROM experiment
        GROUP BY variant
        """,
        conn,
    )
    st.dataframe(result, width="stretch", hide_index=True)
