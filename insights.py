"""
insights.py
───────────
Business logic: expansion targets, state summaries, auto insights.
"""

import pandas as pd


def get_top_expansion_targets(df, n=10):
    return (
        df[df["priority"] == "High"]
        .nlargest(n, "roi")[[
            "city", "state", "priority", "roi", "demand_score",
            "expansion_cost", "population", "readiness_score"
        ]]
        .reset_index(drop=True)
    )


def get_top_demand_cities(df, n=10):
    return (
        df.nlargest(n, "demand_score")[[
            "city", "state", "priority", "demand_score",
            "roi", "readiness_score", "leads"
        ]]
        .reset_index(drop=True)
    )


def get_high_priority_detail(df):
    cols = [
        "city", "state", "demand_score", "roi", "utilization", "population",
        "current_revenue", "predicted_revenue", "expansion_cost",
        "readiness_score", "fiber_connected", "leads", "conversion_rate"
    ]

    return (
        df[df["priority"] == "High"]
        .sort_values("roi", ascending=False)[cols]
        .reset_index(drop=True)
    )


def get_state_summary(df):
    s = (
        df.groupby("state")
        .agg(
            cities=("city", "nunique"),
            high_priority=("priority", lambda x: (x == "High").sum()),
            avg_roi=("roi", "mean"),
            avg_demand=("demand_score", "mean"),
            total_revenue=("current_revenue", "sum"),
        )
        .reset_index()
        .sort_values("avg_roi", ascending=False)
    )

    s["total_revenue_fmt"] = s["total_revenue"].apply(lambda x: f"₹{x/1e6:.1f}M")
    s["avg_roi_fmt"] = s["avg_roi"].apply(lambda x: f"{x:.1f}%")
    s["avg_demand_fmt"] = s["avg_demand"].apply(lambda x: f"{x:.3f}")

    return s


# ✅ FIXED FUNCTION (IMPORTANT)
def get_changed_priorities(df_base, df_scenario):
    base = df_base[["city", "state", "priority"]].rename(
        columns={"priority": "baseline_priority"}
    )

    scen = df_scenario[["city", "state", "priority"]].rename(
        columns={"priority": "scenario_priority"}
    )

    # Merge properly instead of assigning
    merged = base.merge(
        scen,
        on=["city", "state"],
        how="left"
    )

    # Only keep changed rows
    changed = merged[
        merged["baseline_priority"] != merged["scenario_priority"]
    ]

    return changed.reset_index(drop=True)


def generate_insights(df):
    high_df = df[df["priority"] == "High"]
    low_df = df[df["priority"] == "Low"]

    # Best city
    best = high_df.nlargest(1, "roi")
    best_city = best["city"].values[0] if not best.empty else "N/A"
    best_roi = best["roi"].values[0] if not best.empty else 0

    # High demand but low utilization
    unmet = df[df["demand_score"] > df["demand_score"].quantile(0.75)]
    top_unmet = unmet.nsmallest(3, "utilization")["city"].tolist()

    # No fiber but high demand
    underserved = df[
        (df["demand_score"] > 0.4)
        & (df.get("fiber_connected", pd.Series(1)) == 0)
    ]

    # Revenue growth
    rev_growth = 0.0
    if not high_df.empty and high_df["current_revenue"].sum() > 0:
        rev_growth = (
            high_df["predicted_revenue"].sum()
            / high_df["current_revenue"].sum()
            - 1
        ) * 100

    # Best state
    top_state = df.groupby("state")["roi"].mean().idxmax()

    return [
        (
            "green",
            f"🏆 <strong>Best City for Expansion:</strong> <strong>{best_city}</strong> — "
            f"ROI of <strong>{best_roi:.1f}%</strong> with high demand. Prioritise fibre deployment here.",
        ),

        (
            "",
            f"⚡ <strong>Quick-Win Upgrades:</strong> "
            f"{', '.join(top_unmet) or 'N/A'} show high demand + under-utilised infrastructure — "
            "fast-return capacity upgrades await.",
        ),

        (
            "amber",
            f"📶 <strong>Greenfield Opportunity:</strong> <strong>{len(underserved)}</strong> cities "
            "have high demand but zero fibre — significant un-monetised market.",
        ),

        (
            "",
            f"💸 <strong>Low-Priority Review:</strong> <strong>{len(low_df)}</strong> low-priority cities "
            f"hold ₹{low_df['current_revenue'].sum()/1e6:.1f}M — consider cost optimisation or reallocation.",
        ),

        (
            "green",
            f"📈 <strong>Revenue Growth Forecast:</strong> High-priority cities project "
            f"<strong>{rev_growth:.1f}%</strong> revenue growth — reinforce with targeted campaigns.",
        ),

        (
            "",
            f"🗺️ <strong>Top Performing State:</strong> <strong>{top_state}</strong> leads on average ROI — "
            "use as replication template for expansion.",
        ),
    ]