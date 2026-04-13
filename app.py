"""
app.py
------
TeleScope AI - Telecom Network Capacity Planning Dashboard
"""

import pandas as pd
import streamlit as st

import tabs
from advanced_analytics import build_ai_bundle
from data_loader import load_data
from ml_engine import run_clustering
from ui_components import (
    apply_df_filters,
    inject_css,
    render_header,
    render_kpi_cards,
    render_sidebar,
)


st.set_page_config(
    page_title="TeleScope AI | Capacity Planning",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

df_raw = load_data()
controls = render_sidebar(df_raw)

labels, label_map = run_clustering(
    df_raw,
    n_clusters=controls["n_clusters"],
    demand_adj=controls["demand_adj"],
    roi_adj=controls["roi_adj"],
)

df_clustered = df_raw.copy()
df_clustered["priority"] = pd.Series(labels).map(label_map)

df_filtered = apply_df_filters(df_clustered, controls)
ai_bundle = build_ai_bundle(df_filtered)

render_header()
render_kpi_cards(df_filtered, ai_bundle)

(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
    tab6,
    tab7,
    tab8,
    tab9,
) = st.tabs(
    [
        "Overview",
        "Map View",
        "Expansion Targets",
        "ML Analysis",
        "Scenario",
        "Forecasting",
        "Recommendations",
        "Explainability",
        "Data Quality",
    ]
)

with tab1:
    tabs.render_overview(df_filtered)

with tab2:
    tabs.render_map(df_filtered)

with tab3:
    tabs.render_expansion(df_filtered)

with tab4:
    tabs.render_ml_analysis(df_filtered, df_raw)

with tab5:
    tabs.render_scenario(
        df_filtered,
        df_raw,
        controls["demand_adj"],
        controls["roi_adj"],
    )

with tab6:
    tabs.render_forecasting(ai_bundle)

with tab7:
    tabs.render_recommendations(ai_bundle)

with tab8:
    tabs.render_explainability(ai_bundle)

with tab9:
    tabs.render_data_quality(ai_bundle)
