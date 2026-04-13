"""
tabs.py (FINAL FIXED VERSION)
"""

import pandas as pd
import plotly.express as px
import streamlit as st

import charts
import insights as ins
from ui_components import insight_card, section_header


# ───────────────── OVERVIEW ─────────────────
def render_overview(df):
    col_l, col_r = st.columns([2.1, 1])

    with col_l:
        st.plotly_chart(charts.demand_roi_scatter(df), use_container_width=True)

    with col_r:
        st.plotly_chart(charts.priority_pie(df), use_container_width=True)
        st.plotly_chart(charts.cluster_avg_bar(df), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.revenue_bar(df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.state_roi_bar(df), use_container_width=True)

    section_header("💡", "Auto Insights")

    for variant, html in ins.generate_insights(df):
        insight_card(html, variant)


# ───────────────── MAP ─────────────────
def render_map(df):
    section_header("🗺️", "Geographic Map")

    size_col = st.selectbox(
        "Bubble size",
        ["population", "roi", "demand_score"]
    )

    st.plotly_chart(
        charts.city_map(df, size_col),
        use_container_width=True
    )

    section_header("📊", "State Summary")

    summary = ins.get_state_summary(df)
    st.dataframe(summary, use_container_width=True)


# ───────────────── EXPANSION ─────────────────
def render_expansion(df):
    section_header("🚀", "Expansion Targets")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Top 10 by ROI")
        roi_tbl = ins.get_top_expansion_targets(df, 10)
        st.dataframe(roi_tbl, use_container_width=True)

    with c2:
        st.markdown("### Top 10 by Demand")
        dem_tbl = ins.get_top_demand_cities(df, 10)
        st.dataframe(dem_tbl, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ✅ FIXED (correct arguments)
    section_header("🔥", "Opportunity Matrix")

    st.plotly_chart(
        charts.opportunity_matrix(df),
        use_container_width=True
    )


# ───────────────── ML ANALYSIS ─────────────────
def render_ml_analysis(df, df_raw):
    from ml_engine import compute_elbow

    section_header("🔬", "ML Analysis")

    k_range, inertias, silhouettes = compute_elbow(df_raw)

    st.plotly_chart(
        charts.elbow_chart(k_range, inertias, silhouettes),
        use_container_width=True
    )

    st.plotly_chart(
        charts.scatter_3d(df),
        use_container_width=True
    )

    st.plotly_chart(
        charts.correlation_heatmap(df),
        use_container_width=True
    )


# ───────────────── SCENARIO ─────────────────
def render_scenario(df, df_raw, demand_adj, roi_adj):
    section_header("🎛️", "Scenario Analysis")

    st.markdown(
        f"Demand Adjustment: {demand_adj:+.2f} | ROI Adjustment: {roi_adj:+.0f}"
    )

    st.plotly_chart(
        charts.scenario_dist_bar(df, demand_adj, roi_adj),
        use_container_width=True
    )

    st.plotly_chart(
        charts.scenario_scatter(df, demand_adj, roi_adj),
        use_container_width=True
    )


# ───────────────── FORECASTING ─────────────────
def render_forecasting(ai_bundle):
    section_header("📉", "Forecasting")

    preds = ai_bundle.get("predictions", pd.DataFrame())

    if preds.empty:
        st.warning("No predictions available")
        return

    st.dataframe(preds, use_container_width=True)


# ───────────────── RECOMMENDATIONS ─────────────────
def render_recommendations(ai_bundle):
    section_header("🧠", "Recommendations")

    rec = ai_bundle.get("recommendations", pd.DataFrame())

    if rec.empty:
        st.warning("No recommendations available")
        return

    st.dataframe(rec, use_container_width=True)


# ───────────────── EXPLAINABILITY ─────────────────
def render_explainability(ai_bundle):
    section_header("🔍", "Explainability")

    imp = ai_bundle.get("importance", pd.DataFrame())

    if imp.empty:
        st.warning("No explainability data")
        return

    fig = px.bar(
        imp.sort_values("importance"),
        x="importance",
        y="feature",
        orientation="h",
        title="Feature Importance"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(imp, use_container_width=True)


# ───────────────── DATA QUALITY ─────────────────
def render_data_quality(ai_bundle):
    section_header("✅", "Data Quality")

    checks = ai_bundle.get("quality_checks", pd.DataFrame())

    if checks.empty:
        st.warning("No quality data available")
        return

    st.dataframe(checks, use_container_width=True)