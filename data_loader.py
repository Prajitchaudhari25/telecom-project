"""
data_loader.py
──────────────
CSV loading, cleaning, feature prep.
"""

import pandas as pd
import numpy as np
import streamlit as st
import os

# ✅ REMOVE LOCAL PATH (important)
DATA_FILE = "final_telecomdataset.csv"

FEATURE_COLS = ["demand_score", "roi", "utilization", "population"]

NUMERIC_COLS = [
    "demand_score","roi","utilization","population","readiness_score",
    "current_revenue","predicted_revenue","expansion_cost","leads",
    "conversion_rate","arpu","bandwidth_capacity","used_bandwidth",
    "ports_total","ports_used",
]


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load dataset safely (works locally + Streamlit Cloud)
    """

    # ✅ SAFE PATH (important fix)
    path = os.path.join(os.path.dirname(__file__), DATA_FILE)

    # ✅ Load CSV
    df = pd.read_csv(path)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # ── HANDLE NUMERIC NULLS ─────────────────────────────
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # ── HANDLE CATEGORICAL NULLS ─────────────────────────
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    # ── IMPORTANT FIXES (YOUR BUGS) ──────────────────────

    # Fix negative ROI (causing Plotly crash)
    if "roi" in df.columns:
        df["roi"] = df["roi"].clip(lower=0)

    # Ensure demand_score safe
    if "demand_score" in df.columns:
        df["demand_score"] = df["demand_score"].clip(lower=0)

    # Ensure utilization safe
    if "utilization" in df.columns:
        df["utilization"] = df["utilization"].clip(lower=0)

    return df