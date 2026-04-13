"""
charts.py
─────────
All Plotly figure factories — Deep Space dark theme,
crystalline glow accents, premium typography.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ── Palette ──────────────────────────────────────────────────────────────────
P = {"High": "#10ffc8", "Medium": "#fbbf24", "Low": "#fb7185"}

_BASE = dict(
    paper_bgcolor="rgba(7,18,36,0.95)",
    plot_bgcolor ="rgba(7,18,36,0.0)",
    font         =dict(family="DM Mono, monospace", color="#8ba3be", size=11),
    title_font   =dict(family="Syne, sans-serif",   color="#e8f4fd", size=14),
    legend       =dict(bgcolor="rgba(7,18,36,0.85)", bordercolor="rgba(56,139,253,0.18)",
                       borderwidth=1, font=dict(size=11)),
)
_AX = dict(gridcolor="rgba(56,139,253,0.08)", zerolinecolor="rgba(56,139,253,0.12)",
           linecolor="rgba(56,139,253,0.15)", tickfont=dict(size=10))


def _lay(fig, h=370):
    fig.update_layout(height=h, margin=dict(l=16,r=16,t=48,b=16), **_BASE,
                      xaxis=_AX, yaxis=_AX)
    return fig


# ── Overview ─────────────────────────────────────────────────────────────────

def demand_roi_scatter(df):
    fig = px.scatter(
        df, x="demand_score", y="roi",
        color="priority", color_discrete_map=P,
        size="population", size_max=22,
        hover_name="city",
        hover_data={"state":True,"utilization":":.2f","expansion_cost":True},
        title="Demand Score  ×  ROI — Cluster Landscape",
    )
    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=0.6, color="rgba(255,255,255,0.2)")))
    fig.update_layout(
        height=430, margin=dict(l=16,r=16,t=48,b=16), **_BASE,
        xaxis=dict(title="Demand Score", **_AX),
        yaxis=dict(title="ROI (%)", **_AX),
    )
    return fig


def priority_pie(df):
    c = df["priority"].value_counts().reset_index()
    c.columns = ["priority","count"]
    fig = px.pie(c, names="priority", values="count",
                 color="priority", color_discrete_map=P,
                 title="Priority Breakdown", hole=0.62)
    fig.update_traces(
        textinfo="label+percent", textfont_size=11,
        marker=dict(line=dict(color="rgba(7,18,36,0.9)", width=2)),
    )
    fig.update_layout(height=280, margin=dict(l=10,r=10,t=48,b=10), **_BASE)
    return fig


def cluster_avg_bar(df):
    avg = df.groupby("priority")[["demand_score","roi"]].mean().reset_index()
    fig = px.bar(avg, x="priority", y=["demand_score","roi"], barmode="group",
                 color_discrete_sequence=["#38bdf8","#10ffc8"],
                 title="Avg Metrics by Priority Tier")
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return _lay(fig, 240)


def revenue_bar(df):
    top = df.nlargest(12,"current_revenue")
    fig = px.bar(top, x="city", y=["current_revenue","predicted_revenue"],
                 barmode="group",
                 color_discrete_sequence=["#38bdf8","#10ffc8"],
                 title="Current vs Predicted Revenue — Top 12 Cities")
    fig.update_traces(marker_line_width=0, opacity=0.9)
    fig.update_layout(height=330, margin=dict(l=16,r=16,t=48,b=16), **_BASE,
                      xaxis=dict(tickangle=-35, **_AX), yaxis=_AX)
    return fig


def state_roi_bar(df):
    s = df.groupby("state")["roi"].mean().reset_index().nlargest(12,"roi")
    fig = px.bar(s, x="roi", y="state", orientation="h",
                 color="roi", color_continuous_scale=[[0,"#0d2a4a"],[0.5,"#38bdf8"],[1,"#10ffc8"]],
                 title="Top States — Average ROI")
    fig.update_traces(marker_line_width=0)
    fig.update_layout(height=330, margin=dict(l=16,r=16,t=48,b=16), **_BASE,
                      xaxis=_AX, yaxis=_AX, coloraxis_showscale=False)
    return fig


# ── Map ───────────────────────────────────────────────────────────────────────

def city_map(df, size_col="population"):
    dm = df.dropna(subset=["latitude","longitude"]).copy()
    dm["_sz"] = dm[size_col].clip(lower=0)
    fig = px.scatter_mapbox(
        dm, lat="latitude", lon="longitude",
        color="priority", color_discrete_map=P,
        size="_sz", size_max=20,
        hover_name="city",
        hover_data={"state":True,"demand_score":":.3f","roi":":.1f",
                    "utilization":":.2f","population":":,","_sz":False},
        mapbox_style="carto-darkmatter",
        zoom=4, center={"lat":20.5,"lon":78.9},
        title="City Priority Map — India",
    )
    fig.update_layout(
        height=620, paper_bgcolor="rgba(7,18,36,0.0)", font_color="#8ba3be",
        margin=dict(l=0,r=0,t=44,b=0),
        legend=dict(bgcolor="rgba(7,18,36,0.85)", bordercolor="rgba(56,139,253,0.2)"),
    )
    return fig


# ── Expansion ─────────────────────────────────────────────────────────────────

def opportunity_matrix(df):
    df = df.copy()

    # 🔥 Ensure ALL values are positive
    df["_size"] = df["roi"] - df["roi"].min() + 1

    fig = px.scatter(
        df,
        x="demand_score",
        y="readiness_score",
        color="priority",
        size="_size",   # ✅ IMPORTANT
        size_max=22,
        hover_name="city",
        color_discrete_map=P,
        title="Demand × Readiness Matrix  (bubble = ROI)",
    )

    fig.add_hline(
        y=df["readiness_score"].median(),
        line_dash="dot",
        line_color="rgba(56,189,248,0.35)",
        annotation_text="Median Readiness",
        annotation_font_color="#38bdf8"
    )

    fig.add_vline(
        x=df["demand_score"].median(),
        line_dash="dot",
        line_color="rgba(56,189,248,0.35)",
        annotation_text="Median Demand",
        annotation_font_color="#38bdf8"
    )

    fig.update_traces(
        marker=dict(
            opacity=0.85,
            line=dict(width=0.6, color="rgba(255,255,255,0.2)")
        )
    )

    return _lay(fig, 430)


# ── ML Analysis ───────────────────────────────────────────────────────────────

def elbow_chart(k_range, inertias, silhouettes):
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(
        go.Scatter(x=k_range, y=inertias, name="Inertia",
                   line=dict(color="#38bdf8",width=2.5), mode="lines+markers",
                   marker=dict(size=7, color="#38bdf8",
                               line=dict(width=1.5,color="rgba(255,255,255,0.3)"))),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=k_range, y=silhouettes, name="Silhouette",
                   line=dict(color="#10ffc8",width=2.5), mode="lines+markers",
                   marker=dict(size=7, color="#10ffc8",
                               line=dict(width=1.5,color="rgba(255,255,255,0.3)"))),
        secondary_y=True,
    )
    fig.update_layout(
        height=330, title="Elbow Method — Optimal K Selection",
        **_BASE, margin=dict(l=16,r=16,t=48,b=16),
        xaxis=dict(title="K (clusters)", **_AX),
        yaxis=dict(title="Inertia", **_AX),
        yaxis2=dict(title="Silhouette Score",
                    gridcolor="rgba(56,139,253,0.0)", tickfont=dict(size=10)),
    )
    return fig


def scatter_3d(df):
    fig = px.scatter_3d(
        df, x="demand_score", y="roi", z="population",
        color="priority", color_discrete_map=P,
        hover_name="city", opacity=0.82,
        title="3D Cluster · Demand × ROI × Population",
    )
    fig.update_traces(marker=dict(size=4, line=dict(width=0.3, color="rgba(255,255,255,0.15)")))
    scene_ax = dict(backgroundcolor="rgba(7,18,36,0.8)", gridcolor="rgba(56,189,248,0.08)",
                    linecolor="rgba(56,189,248,0.15)")
    fig.update_layout(
        height=520, **_BASE, margin=dict(l=0,r=0,t=48,b=0),
        scene=dict(xaxis=scene_ax, yaxis=scene_ax, zaxis=scene_ax,
                   bgcolor="rgba(7,18,36,0.0)"),
    )
    return fig


def correlation_heatmap(df):
    cols = ["demand_score","roi","utilization","population","readiness_score",
            "current_revenue","expansion_cost","leads","conversion_rate","arpu"]
    corr = df[cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f",
        color_continuous_scale=[[0,"#0a1e35"],[0.5,"#1a5fa8"],[1,"#06eeff"]],
        title="Feature Correlation Matrix",
    )
    fig.update_traces(textfont_size=9)
    fig.update_layout(height=460, **_BASE, margin=dict(l=16,r=16,t=48,b=16))
    return fig


# ── Scenario ──────────────────────────────────────────────────────────────────

def scenario_dist_bar(df, demand_adj, roi_adj):
    c = df["priority"].value_counts().reset_index()
    c.columns = ["Priority","Cities"]
    fig = px.bar(c, x="Priority", y="Cities", color="Priority",
                 color_discrete_map=P,
                 title=f"Priority Distribution  (Δdemand={demand_adj:+.2f}, ΔROI={roi_adj:+.0f})")
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return _lay(fig, 310)


def scenario_compare_bar(base_counts, scen_counts):
    cmp = pd.concat([base_counts.rename("Baseline"), scen_counts.rename("Scenario")],axis=1).fillna(0).astype(int)
    fig = go.Figure()
    for name, color in [("Baseline","#38bdf8"),("Scenario","#10ffc8")]:
        if name in cmp.columns:
            fig.add_trace(go.Bar(name=name, x=cmp.index, y=cmp[name],
                                 marker_color=color, opacity=0.85, marker_line_width=0))
    fig.update_layout(barmode="group", height=310,
                      title="Baseline vs Scenario — Priority Counts",
                      **_BASE, margin=dict(l=16,r=16,t=48,b=16),
                      xaxis=_AX, yaxis=_AX)
    return fig


def scenario_scatter(df, demand_adj, roi_adj):
    ds = df.copy()
    ds["demand_score"] = (ds["demand_score"] + demand_adj).clip(0)
    ds["roi"]          = ds["roi"] + roi_adj
    fig = px.scatter(
        ds, x="demand_score", y="roi",
        color="priority", color_discrete_map=P,
        hover_name="city", size="population", size_max=20,
        title=f"Scenario View · Adjusted Demand & ROI",
    )
    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=0.6,color="rgba(255,255,255,0.2)")))
    return _lay(fig, 430)
