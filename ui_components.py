"""
ui_components.py
----------------
UI primitives and styling for TeleScope AI.
"""

import pandas as pd
import streamlit as st


def inject_css():
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">

<style>
:root {
  --bg: #041018;
  --bg2: #0b1f2e;
  --panel: #0d2235;
  --panel-soft: #102a41;
  --line: rgba(100, 180, 255, 0.20);
  --text: #eaf6ff;
  --muted: #a9c3d8;
  --accent: #38bdf8;
  --accent2: #10b981;
  --warn: #f59e0b;
}

html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 18% 10%, rgba(56,189,248,0.12), transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(16,185,129,0.10), transparent 40%),
    linear-gradient(160deg, var(--bg) 0%, var(--bg2) 75%);
  color: var(--text) !important;
  font-family: 'Manrope', sans-serif !important;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #091827 0%, #081423 100%) !important;
  border-right: 1px solid var(--line) !important;
}

[data-testid="block-container"] { padding-top: 1.2rem; }

.dash-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 4px 20px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
}
.dash-logo {
  width: 54px; height: 54px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
  background: linear-gradient(145deg, rgba(56,189,248,0.20), rgba(14,165,233,0.10));
  border: 1px solid rgba(56,189,248,0.35);
}
.dash-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.9rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text);
}
.dash-sub {
  font-family: 'DM Mono', monospace;
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--muted);
  margin-top: 2px;
}
.live-pill {
  font-family: 'DM Mono', monospace;
  font-size: 0.66rem;
  color: #a7f3d0;
  border: 1px solid rgba(16,185,129,0.35);
  border-radius: 999px;
  padding: 6px 10px;
  background: rgba(16,185,129,0.08);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(170px, 1fr));
  gap: 12px;
  margin: 4px 0 22px;
}
@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(2, minmax(160px, 1fr)); }
}
@media (max-width: 700px) {
  .kpi-grid { grid-template-columns: 1fr; }
}

.kpi-card {
  background: linear-gradient(170deg, var(--panel) 0%, var(--panel-soft) 100%);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px 14px 12px;
}
.kpi-row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.kpi-label {
  font-size: 0.68rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-family: 'DM Mono', monospace;
}
.kpi-ico { font-size: 1.1rem; opacity: 0.9; }
.kpi-value {
  margin-top: 8px;
  font-family: 'Syne', sans-serif;
  font-size: 1.45rem;
  line-height: 1.1;
  color: #f0fbff;
}
.kpi-hint {
  margin-top: 3px;
  color: var(--muted);
  font-size: 0.73rem;
}
.kpi-card.good .kpi-value { color: #8ef6d0; }
.kpi-card.warn .kpi-value { color: #fde68a; }

.s-head {
  display: flex; align-items: center; gap: 9px;
  font-family: 'Syne', sans-serif;
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text);
  margin: 14px 0 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--line);
}

.insight-card {
  background: linear-gradient(145deg, #0d2133, #0f2940);
  border: 1px solid var(--line);
  border-left: 4px solid var(--accent);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
  color: #c6deee;
  line-height: 1.6;
}
.insight-card.g { border-left-color: var(--accent2); }
.insight-card.a { border-left-color: var(--warn); }
.insight-card strong { color: #d9f3ff; }

.mini-title {
  font-family: 'Syne', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #7dd3fc;
  margin-bottom: 10px;
}
.mini-title-alt { color: #86efac; }

.chip-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.stat-chip {
  background: rgba(8, 27, 42, 0.95);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 8px 11px;
  min-width: 120px;
  text-align: center;
  font-size: 0.7rem;
  color: var(--muted);
}
.stat-chip .val {
  display: block;
  font-family: 'Syne', sans-serif;
  font-size: 1.05rem;
  color: #e2f5ff;
}

.scen-panel {
  background: linear-gradient(145deg, rgba(56,189,248,0.14), rgba(16,185,129,0.08));
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
  color: #d7edff;
  font-size: 0.82rem;
}

.stTabs [data-baseweb="tab-list"] {
  background: rgba(9, 24, 38, 0.9) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  padding: 3px !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--muted) !important;
  font-family: 'Manrope', sans-serif !important;
  font-size: 0.83rem !important;
  font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(145deg, rgba(56,189,248,0.20), rgba(16,185,129,0.16)) !important;
  color: #dff6ff !important;
  border-radius: 8px !important;
}

.stSelectbox label, .stMultiSelect label, .stSlider label {
  color: #b6cde0 !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.66rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.11em !important;
}

div[data-testid="stDataFrame"] > div {
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  overflow: hidden;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_sidebar(df: pd.DataFrame) -> dict:
    with st.sidebar:
        st.markdown(
            """
<div style="text-align:center;padding:14px 0 10px;">
  <div style="font-size:1.8rem;">📡</div>
  <div style="font-family:'Syne',sans-serif;font-weight:700;color:#eaf6ff;">TeleScope AI</div>
  <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#9db8cf;letter-spacing:0.08em;">CAPACITY PLANNING</div>
</div>
<hr style="border-color:rgba(125,211,252,0.25);">
""",
            unsafe_allow_html=True,
        )

        all_states = sorted(df["state"].dropna().unique())
        selected_states = st.multiselect("State", all_states, default=all_states)

        all_cities = sorted(df["city"].dropna().unique())
        selected_cities = st.multiselect("City", all_cities, placeholder="All cities")

        selected_priority = st.multiselect(
            "Priority Tier",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
        )

        st.markdown("<hr style='border-color:rgba(125,211,252,0.25);'>", unsafe_allow_html=True)

        n_clusters = st.slider("Cluster Count", 2, 6, 3)
        demand_adj = st.slider("Demand Score Delta", -0.3, 0.3, 0.0, 0.01, format="%.2f")
        roi_adj = st.slider("ROI Delta", -50.0, 50.0, 0.0, 1.0, format="%.0f")

        st.markdown(
            """
<div style="text-align:center;padding:8px 0 4px;">
  <div class="live-pill">LIVE ANALYSIS</div>
  <div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:#8db1c9;margin-top:6px;line-height:1.6;">
    Dynamic clustering and scenario simulation
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    return {
        "selected_states": selected_states,
        "selected_cities": selected_cities,
        "selected_priority": selected_priority,
        "n_clusters": n_clusters,
        "demand_adj": demand_adj,
        "roi_adj": roi_adj,
    }


def render_header():
    st.markdown(
        """
<div class="dash-header">
  <div class="dash-logo">📡</div>
  <div style="flex:1;">
    <div class="dash-title">TeleScope AI</div>
    <div class="dash-sub">Network Capacity Planning Intelligence Dashboard</div>
  </div>
  <div class="live-pill">System Active</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kpi_cards(df: pd.DataFrame, ai_bundle: dict | None = None):
    total = int(df["city"].nunique()) if "city" in df.columns else len(df)
    high = int((df["priority"] == "High").sum()) if "priority" in df.columns else 0
    avg_roi = float(df["roi"].mean()) if "roi" in df.columns and not df.empty else 0.0
    avg_dem = float(df["demand_score"].mean()) if "demand_score" in df.columns and not df.empty else 0.0
    rev = float(df["current_revenue"].sum() / 1e6) if "current_revenue" in df.columns else 0.0
    util = float(df["utilization"].mean() * 100) if "utilization" in df.columns and not df.empty else 0.0

    uplift = 0.0
    quality = 0.0
    if ai_bundle:
        pred = ai_bundle.get("predictions", pd.DataFrame())
        q = ai_bundle.get("quality_summary", {})
        if not pred.empty and "estimated_uplift" in pred.columns:
            uplift = float(pred["estimated_uplift"].sum() / 1e6)
        quality = float(q.get("score", 0.0))

    cards = [
        ("Coverage", f"{total:,}", "Cities", "🗺️", ""),
        ("Priority", f"{high:,}", "High-priority cities", "🚀", "good"),
        ("Average ROI", f"{avg_roi:.1f}%", "Expected return", "📈", "warn"),
        ("Demand", f"{avg_dem:.3f}", "Average demand score", "📊", ""),
        ("Revenue", f"₹{rev:.1f}M", "Current revenue", "💰", "good"),
        ("Utilization", f"{util:.1f}%", "Network load", "⚡", ""),
        ("Forecast Uplift", f"₹{uplift:.1f}M", "Model-estimated gain", "🤖", "good"),
        ("Data Quality", f"{quality:.1f}%", "Quality check score", "✅", "warn"),
    ]

    html = ["<div class='kpi-grid'>"]
    for label, value, hint, icon, tone in cards:
        cls = f"kpi-card {tone}".strip()
        html.append(
            f"<div class='{cls}'>"
            f"<div class='kpi-row-top'><div class='kpi-label'>{label}</div><div class='kpi-ico'>{icon}</div></div>"
            f"<div class='kpi-value'>{value}</div>"
            f"<div class='kpi-hint'>{hint}</div>"
            f"</div>"
        )
    html.append("</div>")

    st.markdown("".join(html), unsafe_allow_html=True)


def section_header(emoji: str, title: str):
    st.markdown(f"<div class='s-head'><span>{emoji}</span>{title}</div>", unsafe_allow_html=True)


def insight_card(html: str, variant: str = ""):
    cls = {"green": "g", "amber": "a", "": ""}.get(variant, "")
    st.markdown(f"<div class='insight-card {cls}'>{html}</div>", unsafe_allow_html=True)


def style_priority(val: str) -> str:
    p = {
        "High": "background:#053428;color:#86efac;border-radius:6px;padding:2px 9px;font-size:0.72rem;font-weight:600;",
        "Medium": "background:#3a2908;color:#fcd34d;border-radius:6px;padding:2px 9px;font-size:0.72rem;font-weight:600;",
        "Low": "background:#3f1721;color:#fda4af;border-radius:6px;padding:2px 9px;font-size:0.72rem;font-weight:600;",
    }
    return p.get(val, "")


def apply_df_filters(df: pd.DataFrame, controls: dict) -> pd.DataFrame:
    f = df.copy()
    if controls["selected_states"]:
        f = f[f["state"].isin(controls["selected_states"])]
    if controls["selected_cities"]:
        f = f[f["city"].isin(controls["selected_cities"])]
    if controls["selected_priority"]:
        f = f[f["priority"].isin(controls["selected_priority"])]
    return f
