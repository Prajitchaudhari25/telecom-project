"""
tabs.py
-------
One render_* function per dashboard tab.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

import charts
import insights as ins
from ui_components import insight_card, section_header, style_priority


def render_overview(df: pd.DataFrame):
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

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("💡", "Auto-Generated Business Insights")

    for variant, html in ins.generate_insights(df):
        insight_card(html, variant)


def render_map(df: pd.DataFrame):
    section_header("🗺️", "Geographic Priority Map")

    size_col = st.selectbox(
        "Bubble size by",
        ["population", "roi", "demand_score", "current_revenue"],
    )
    st.plotly_chart(charts.city_map(df, size_col), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📊", "State-Level Summary")

    summary = ins.get_state_summary(df)
    display = summary[["state", "cities", "high_priority", "avg_roi_fmt", "avg_demand_fmt", "total_revenue_fmt"]]
    display = display.rename(
        columns={
            "avg_roi_fmt": "Avg ROI",
            "avg_demand_fmt": "Avg Demand",
            "total_revenue_fmt": "Total Revenue",
            "cities": "Cities",
            "high_priority": "High Priority",
            "state": "State",
        }
    )
    st.dataframe(display, use_container_width=True, height=320)


def render_expansion(df: pd.DataFrame):
    section_header("🚀", "Top Expansion Targets")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            "<div class='mini-title'>Top 10 by ROI</div>",
            unsafe_allow_html=True,
        )
        roi_tbl = ins.get_top_expansion_targets(df, 10)
        st.dataframe(
            roi_tbl.style.map(style_priority, subset=["priority"]).format(
                {
                    "roi": "{:.1f}%",
                    "demand_score": "{:.3f}",
                    "expansion_cost": "₹{:,.0f}",
                    "population": "{:,}",
                    "readiness_score": "{:.2f}",
                }
            ),
            use_container_width=True,
            height=370,
        )

    with c2:
        st.markdown(
            "<div class='mini-title mini-title-alt'>Top 10 by Demand Score</div>",
            unsafe_allow_html=True,
        )
        dem_tbl = ins.get_top_demand_cities(df, 10)
        st.dataframe(
            dem_tbl.style.map(style_priority, subset=["priority"]).format(
                {
                    "demand_score": "{:.3f}",
                    "roi": "{:.1f}%",
                    "readiness_score": "{:.2f}",
                    "leads": "{:,}",
                }
            ),
            use_container_width=True,
            height=370,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("💎", "High-Priority Regions - Full Detail")
    detail = ins.get_high_priority_detail(df)
    st.dataframe(
        detail.style.format(
            {
                "demand_score": "{:.3f}",
                "roi": "{:.1f}%",
                "utilization": "{:.2f}",
                "population": "{:,}",
                "current_revenue": "₹{:,.0f}",
                "predicted_revenue": "₹{:,.0f}",
                "expansion_cost": "₹{:,.0f}",
                "readiness_score": "{:.2f}",
                "conversion_rate": "{:.2f}",
            }
        ),
        use_container_width=True,
        height=400,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🔥", "Opportunity Matrix - Demand vs Readiness")
    st.plotly_chart(charts.opportunity_matrix(df), use_container_width=True)


def render_ml_analysis(df: pd.DataFrame, df_raw: pd.DataFrame):
    from ml_engine import compute_elbow, get_cluster_stats

    section_header("🔬", "Cluster Analysis and ML Insights")

    c1, c2 = st.columns([1.1, 1])
    with c1:
        k_range, inertias, silhouettes = compute_elbow(df_raw)
        st.plotly_chart(charts.elbow_chart(k_range, inertias, silhouettes), use_container_width=True)

    with c2:
        st.markdown("<div class='mini-title'>Cluster Summary</div>", unsafe_allow_html=True)
        stats = get_cluster_stats(df)
        st.dataframe(
            stats.style.format(
                {
                    "avg_demand": "{:.4f}",
                    "avg_roi": "{:.1f}",
                    "avg_util": "{:.4f}",
                    "avg_pop": "{:,.0f}",
                    "avg_revenue": "₹{:,.0f}",
                    "avg_readiness": "{:.2f}",
                }
            ),
            use_container_width=True,
            height=220,
        )

        h = df[df["priority"] == "High"]
        h_roi = h["roi"].mean() if not h.empty else 0.0
        h_dem = h["demand_score"].mean() if not h.empty else 0.0
        st.markdown(
            f"<div class='chip-row'>"
            f"<div class='stat-chip'><span class='val'>{len(h)}</span>High Cities</div>"
            f"<div class='stat-chip'><span class='val'>{h_roi:.1f}%</span>High Avg ROI</div>"
            f"<div class='stat-chip'><span class='val'>{h_dem:.3f}</span>High Avg Demand</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🌐", "3D Cluster Visualisation")
    st.plotly_chart(charts.scatter_3d(df), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🔗", "Feature Correlation Matrix")
    st.plotly_chart(charts.correlation_heatmap(df), use_container_width=True)


def render_scenario(df: pd.DataFrame, df_raw: pd.DataFrame, demand_adj: float, roi_adj: float):
    from ml_engine import run_clustering

    section_header("🎛️", "Scenario Modelling")

    st.markdown(
        f"<div class='scen-panel'>"
        f"Active Adjustments: Demand Score Delta <strong>{demand_adj:+.2f}</strong> | "
        f"ROI Delta <strong>{roi_adj:+.0f}</strong><br>"
        f"Clustering re-runs live with adjusted values."
        f"</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(
            charts.scenario_dist_bar(df, demand_adj, roi_adj),
            use_container_width=True,
        )

    with c2:
        base_labels, base_map = run_clustering(df_raw, len(set(df["priority"].unique())), 0, 0)
        base_priorities = pd.Series(base_labels).map(base_map)
        df_base = df_raw.copy()
        df_base["priority"] = base_priorities.values

        base_counts = df_base["priority"].value_counts()
        scen_counts = df["priority"].value_counts()

        st.plotly_chart(
            charts.scenario_compare_bar(base_counts, scen_counts),
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🔄", "Cities That Changed Priority")

    changed = ins.get_changed_priorities(df_base, df)
    if changed.empty:
        st.success("No priority changes under current scenario adjustments.")
    else:
        st.dataframe(
            changed.style.map(style_priority, subset=["baseline_priority", "scenario_priority"]),
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📈", "Scenario Demand vs ROI Landscape")
    st.plotly_chart(charts.scenario_scatter(df, demand_adj, roi_adj), use_container_width=True)


def render_forecasting(ai_bundle: dict):
    section_header("📉", "Forecasting Models")

    metrics = ai_bundle.get("metrics", pd.DataFrame())
    preds = ai_bundle.get("predictions", pd.DataFrame())

    if metrics.empty or preds.empty:
        st.info("Not enough rows in current filter to compute reliable forecasts.")
        return

    c1, c2, c3 = st.columns(3)
    roi_row = metrics.loc[metrics["model"] == "ROI Forecast"].head(1)
    rev_row = metrics.loc[metrics["model"] == "Revenue Forecast"].head(1)

    roi_r2 = float(roi_row["r2"].iloc[0]) if not roi_row.empty else float("nan")
    rev_rmse = float(rev_row["rmse"].iloc[0]) if not rev_row.empty else float("nan")
    roi_mae = float(roi_row["mae"].iloc[0]) if not roi_row.empty else float("nan")

    c1.metric("ROI Forecast R2", "N/A" if pd.isna(roi_r2) else f"{roi_r2:.3f}")
    c2.metric("Revenue RMSE", "N/A" if pd.isna(rev_rmse) else f"₹{rev_rmse:,.0f}")
    c3.metric("ROI MAE", "N/A" if pd.isna(roi_mae) else f"{roi_mae:.2f}")

    left, right = st.columns(2)
    with left:
        fig_roi = px.scatter(
            preds,
            x="actual_roi",
            y="pred_roi",
            hover_data=["city", "state"],
            title="ROI: Actual vs Predicted",
            color="confidence",
            color_continuous_scale=["#1d4ed8", "#06b6d4", "#10b981"],
        )
        st.plotly_chart(fig_roi, use_container_width=True)

    with right:
        fig_rev = px.scatter(
            preds,
            x="actual_predicted_revenue",
            y="pred_predicted_revenue",
            hover_data=["city", "state"],
            title="Revenue: Actual vs Predicted",
            color="confidence",
            color_continuous_scale=["#1d4ed8", "#06b6d4", "#10b981"],
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(
        preds[
            [
                "city",
                "state",
                "actual_roi",
                "pred_roi",
                "actual_predicted_revenue",
                "pred_predicted_revenue",
                "estimated_uplift",
                "confidence",
            ]
        ].sort_values("estimated_uplift", ascending=False),
        use_container_width=True,
        height=340,
    )


def render_recommendations(ai_bundle: dict):
    section_header("🧠", "Action Recommendations")

    rec = ai_bundle.get("recommendations", pd.DataFrame())
    if rec.empty:
        st.info("No recommendations available for the current filter.")
        return

    top_rec = rec[
        [
            "city",
            "state",
            "priority",
            "recommended_action",
            "pred_roi",
            "estimated_uplift",
            "confidence",
            "priority_score",
        ]
    ].head(25)

    st.dataframe(
        top_rec.style.map(style_priority, subset=["priority"]).format(
            {
                "pred_roi": "{:.1f}%",
                "estimated_uplift": "₹{:,.0f}",
                "confidence": "{:.0%}",
                "priority_score": "{:.3f}",
            }
        ),
        use_container_width=True,
        height=430,
    )

    action_counts = rec["recommended_action"].value_counts().reset_index()
    action_counts.columns = ["action", "count"]
    fig = px.bar(
        action_counts,
        x="count",
        y="action",
        orientation="h",
        color="count",
        color_continuous_scale=["#1d4ed8", "#10b981"],
        title="Recommendation Mix",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_explainability(ai_bundle: dict):
    method = ai_bundle.get("importance_method", "Feature Importance")
    section_header("🔍", f"Explainability ({method})")

    imp = ai_bundle.get("importance", pd.DataFrame())
    if imp.empty:
        st.info("Feature importance is not available for the current filter.")
        return

    top_imp = imp.head(15)
    fig = px.bar(
        top_imp.sort_values("importance"),
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale=["#2563eb", "#14b8a6"],
        title="Top Drivers of ROI Forecast",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_imp, use_container_width=True, height=320)


def render_data_quality(ai_bundle: dict):
    section_header("✅", "Data Quality Checks")

    summary = ai_bundle.get("quality_summary", {})
    checks = ai_bundle.get("quality_checks", pd.DataFrame())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quality Score", f"{summary.get('score', 0):.1f}%")
    c2.metric("Checks", f"{summary.get('total_checks', 0)}")
    c3.metric("Passed", f"{summary.get('passed_checks', 0)}")
    c4.metric("Warn/Fail", f"{summary.get('warn_fail_checks', 0)}")

    if checks.empty:
        st.info("No quality checks available.")
        return

    status_order = pd.CategoricalDtype(categories=["Pass", "Warn", "Fail"], ordered=True)
    checks = checks.copy()
    checks["status"] = checks["status"].astype(status_order)
    checks = checks.sort_values("status")

    st.dataframe(checks, use_container_width=True, height=360)

    status_counts = checks["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(
        status_counts,
        names="status",
        values="count",
        color="status",
        color_discrete_map={"Pass": "#10b981", "Warn": "#f59e0b", "Fail": "#ef4444"},
        hole=0.55,
        title="Data Quality Status Mix",
    )
    st.plotly_chart(fig, use_container_width=True)