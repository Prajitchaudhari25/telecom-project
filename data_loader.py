"""
data_loader.py
──────────────
CSV loading, cleaning, feature prep.
"""

import pandas as pd
import numpy as np
import streamlit as st

DATA_PATH = r"C:\Users\Prajit\Desktop\networkproj\final_telecom_dataset (1).csv"
FEATURE_COLS = ["demand_score", "roi", "utilization", "population"]

NUMERIC_COLS = [
    "demand_score","roi","utilization","population","readiness_score",
    "current_revenue","predicted_revenue","expansion_cost","leads",
    "conversion_rate","arpu","bandwidth_capacity","used_bandwidth",
    "ports_total","ports_used",
]


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)
    for col in df.select_dtypes(include="object").columns:
        if df[col].isnull().any():
            df[col].fillna(df[col].mode()[0], inplace=True)
    return df
