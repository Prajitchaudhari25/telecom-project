"""
ml_engine.py
────────────
KMeans clustering, elbow/silhouette, cluster-to-priority mapping.
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from data_loader import FEATURE_COLS


def run_clustering(df, n_clusters=3, demand_adj=0.0, roi_adj=0.0):
    df_ml = df[FEATURE_COLS].copy()
    df_ml["demand_score"] = (df_ml["demand_score"] + demand_adj).clip(lower=0)
    df_ml["roi"] = df_ml["roi"] + roi_adj

    scaler = StandardScaler()
    X = scaler.fit_transform(df_ml)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    centers = pd.DataFrame(scaler.inverse_transform(km.cluster_centers_), columns=FEATURE_COLS)
    roi_range = centers["roi"].abs().max() or 1.0
    rank = centers["demand_score"] + centers["roi"] / roi_range
    sorted_c = rank.argsort().iloc[::-1].values

    names = ["High", "Medium", "Low"]
    label_map = {int(sorted_c[i]): names[min(i, len(names)-1)] for i in range(len(sorted_c))}
    return labels, label_map


@st.cache_data
def compute_elbow(df):
    X = StandardScaler().fit_transform(df[FEATURE_COLS])
    k_range, inertias, silhouettes = [], [], []
    for k in range(2, 9):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X)
        k_range.append(k)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X, km.labels_))
    return k_range, inertias, silhouettes


def get_cluster_stats(df):
    return (
        df.groupby("priority")
        .agg(
            count=("city","count"),
            avg_demand=("demand_score","mean"),
            avg_roi=("roi","mean"),
            avg_util=("utilization","mean"),
            avg_pop=("population","mean"),
            avg_revenue=("current_revenue","mean"),
            avg_readiness=("readiness_score","mean"),
        )
        .reset_index()
    )
