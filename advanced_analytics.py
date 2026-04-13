"""
advanced_analytics.py
---------------------
Forecasting, recommendations, explainability, and data-quality checks.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


NUMERIC_FALLBACK_EXCLUDE = {
    "latitude",
    "longitude",
    "building_id",
}


def _safe_numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == "object":
            try:
                out[col] = pd.to_numeric(out[col])
            except Exception:
                continue
    return out


def _model_features(df: pd.DataFrame, target: str) -> list[str]:
    features = []
    for col in df.columns:
        if col == target:
            continue
        if col in {"city", "state", "priority", "demand_type", "sales_stage"}:
            continue
        if col in NUMERIC_FALLBACK_EXCLUDE:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            features.append(col)
    return features


def _fallback_predictions(frame: pd.DataFrame, target: str) -> pd.DataFrame:
    mean_val = frame[target].mean() if not frame.empty else 0.0
    pred_df = frame[["city", "state"]].copy() if {"city", "state"}.issubset(frame.columns) else pd.DataFrame(index=frame.index)
    pred_df[f"actual_{target}"] = frame[target].values
    pred_df[f"pred_{target}"] = np.full(len(frame), mean_val)
    pred_df[f"uncertainty_{target}"] = 0.0
    return pred_df


def _fit_regressor(df: pd.DataFrame, target: str, random_state: int = 42):
    frame = _safe_numeric_frame(df)
    frame = frame.dropna(subset=[target]).copy()

    features = _model_features(frame, target)
    if not features:
        raise ValueError(f"No usable features found for target '{target}'.")

    X = frame[features].copy()
    y = frame[target].copy()
    X = X.fillna(X.median(numeric_only=True))

    # Handle very small filtered slices gracefully.
    if len(frame) < 12:
        model = RandomForestRegressor(n_estimators=50, random_state=random_state)
        model.fit(X, y)
        pred_df = _fallback_predictions(frame, target)
        metrics = {"mae": float("nan"), "rmse": float("nan"), "r2": float("nan")}
        return model, features, metrics, pred_df

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=random_state,
    )

    model = RandomForestRegressor(
        n_estimators=350,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    pred_test = model.predict(X_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, pred_test)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, pred_test))),
        "r2": float(r2_score(y_test, pred_test)),
    }

    full_pred = model.predict(X)
    tree_preds = np.vstack([tree.predict(X) for tree in model.estimators_])
    full_std = tree_preds.std(axis=0)

    pred_df = frame[["city", "state"]].copy() if {"city", "state"}.issubset(frame.columns) else pd.DataFrame(index=frame.index)
    pred_df[f"actual_{target}"] = y.values
    pred_df[f"pred_{target}"] = full_pred
    pred_df[f"uncertainty_{target}"] = full_std

    return model, features, metrics, pred_df


def _explain_model(model, X: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    method = "Feature Importance"

    try:
        import shap  # optional dependency

        sample = X.sample(min(120, len(X)), random_state=42)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        scores = np.abs(shap_values).mean(axis=0)
        method = "SHAP"
    except Exception:
        scores = model.feature_importances_

    imp = (
        pd.DataFrame({"feature": X.columns, "importance": scores})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    return imp, method


def evaluate_data_quality(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    checks: list[dict] = []

    missing_cells = int(df.isna().sum().sum())
    missing_pct = float((missing_cells / (max(len(df), 1) * max(len(df.columns), 1))) * 100)
    checks.append(
        {
            "check": "Missing Values",
            "status": "Pass" if missing_pct <= 5 else "Warn",
            "affected_rows": int(df.isna().any(axis=1).sum()),
            "details": f"Missing cells: {missing_cells} ({missing_pct:.2f}%).",
        }
    )

    dup = int(df.duplicated().sum())
    checks.append(
        {
            "check": "Duplicate Rows",
            "status": "Pass" if dup == 0 else "Warn",
            "affected_rows": dup,
            "details": f"Duplicate rows found: {dup}.",
        }
    )

    if "utilization" in df.columns:
        bad_util = int(((df["utilization"] < 0) | (df["utilization"] > 1)).sum())
        checks.append(
            {
                "check": "Utilization Range (0-1)",
                "status": "Pass" if bad_util == 0 else "Fail",
                "affected_rows": bad_util,
                "details": "Utilization should stay in [0, 1].",
            }
        )

    if "conversion_rate" in df.columns:
        bad_conv = int(((df["conversion_rate"] < 0) | (df["conversion_rate"] > 1)).sum())
        checks.append(
            {
                "check": "Conversion Range (0-1)",
                "status": "Pass" if bad_conv == 0 else "Fail",
                "affected_rows": bad_conv,
                "details": "Conversion rate should stay in [0, 1].",
            }
        )

    if {"latitude", "longitude"}.issubset(df.columns):
        bad_geo = int(
            (
                (df["latitude"] < -90)
                | (df["latitude"] > 90)
                | (df["longitude"] < -180)
                | (df["longitude"] > 180)
            ).sum()
        )
        checks.append(
            {
                "check": "Geo Coordinates",
                "status": "Pass" if bad_geo == 0 else "Fail",
                "affected_rows": bad_geo,
                "details": "Latitude/Longitude out-of-bounds rows.",
            }
        )

    for col in ["population", "current_revenue", "predicted_revenue", "expansion_cost", "roi"]:
        if col in df.columns:
            bad = int((df[col] < 0).sum())
            checks.append(
                {
                    "check": f"Non-negative {col}",
                    "status": "Pass" if bad == 0 else "Warn",
                    "affected_rows": bad,
                    "details": f"Rows where {col} < 0.",
                }
            )

    check_df = pd.DataFrame(checks)
    passed = int((check_df["status"] == "Pass").sum())
    summary = {
        "score": float(passed / max(len(check_df), 1) * 100),
        "total_checks": int(len(check_df)),
        "passed_checks": passed,
        "warn_fail_checks": int(len(check_df) - passed),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
    }
    return check_df, summary


def build_ai_bundle(df: pd.DataFrame) -> dict:
    if df.empty:
        empty = pd.DataFrame()
        checks, summary = evaluate_data_quality(df)
        return {
            "metrics": empty,
            "predictions": empty,
            "recommendations": empty,
            "importance": empty,
            "importance_method": "Feature Importance",
            "quality_checks": checks,
            "quality_summary": summary,
        }

    roi_model, roi_features, roi_metrics, roi_pred = _fit_regressor(df, "roi")
    _, _, rev_metrics, rev_pred = _fit_regressor(df, "predicted_revenue")

    joined = roi_pred.merge(rev_pred, on=["city", "state"], how="inner")

    base_cols = [
        "city",
        "state",
        "current_revenue",
        "priority",
        "utilization",
        "ports_used",
        "ports_total",
        "fiber_connected",
        "readiness_score",
        "demand_score",
        "leads",
        "conversion_rate",
    ]
    available = [c for c in base_cols if c in df.columns]
    if set(["city", "state"]).issubset(df.columns):
        curr = df[available].copy()
        joined = joined.merge(curr, on=["city", "state"], how="left")

    if "current_revenue" not in joined.columns:
        joined["current_revenue"] = 0.0

    joined["estimated_uplift"] = (joined["pred_predicted_revenue"] - joined["current_revenue"]).clip(lower=0)

    unc_base = joined["uncertainty_predicted_revenue"].median() or 1.0
    joined["confidence"] = (1 - (joined["uncertainty_predicted_revenue"] / (unc_base * 2))).clip(lower=0.35, upper=0.95)

    median_leads = joined["leads"].median() if "leads" in joined.columns else 0

    def choose_action(row):
        util = row.get("utilization", 0.0)
        ports_total = max(row.get("ports_total", 0.0), 1.0)
        ports_used = row.get("ports_used", 0.0)
        demand = row.get("demand_score", 0.0)
        fiber = row.get("fiber_connected", 1)
        readiness = row.get("readiness_score", 0.0)
        conv = row.get("conversion_rate", 0.0)
        leads = row.get("leads", 0.0)

        if (fiber == 0) and (demand >= 0.45):
            return "Deploy fiber backbone"
        if (util >= 0.80) or ((ports_used / ports_total) >= 0.75):
            return "Expand ports and bandwidth"
        if (conv < 0.15) and (leads > median_leads):
            return "Optimize campaigns and sales playbook"
        if readiness < 0.50:
            return "Improve site readiness and equipment"
        return "Bundle plans and targeted upsell"

    joined["recommended_action"] = joined.apply(choose_action, axis=1)

    rec = joined.copy()
    demand_series = rec["demand_score"] if "demand_score" in rec.columns else pd.Series(0, index=rec.index)
    rec["priority_score"] = (
        rec["pred_roi"].rank(pct=True) * 0.35
        + rec["estimated_uplift"].rank(pct=True) * 0.35
        + rec["confidence"].rank(pct=True) * 0.20
        + demand_series.rank(pct=True) * 0.10
    )
    rec = rec.sort_values("priority_score", ascending=False)

    explain_frame = _safe_numeric_frame(df)
    X_explain = explain_frame[roi_features].fillna(explain_frame[roi_features].median(numeric_only=True))
    importance, method = _explain_model(roi_model, X_explain)

    metrics = pd.DataFrame(
        [
            {"model": "ROI Forecast", **roi_metrics},
            {"model": "Revenue Forecast", **rev_metrics},
        ]
    )

    checks, summary = evaluate_data_quality(_safe_numeric_frame(df))

    return {
        "metrics": metrics,
        "predictions": joined.sort_values("estimated_uplift", ascending=False).reset_index(drop=True),
        "recommendations": rec.reset_index(drop=True),
        "importance": importance,
        "importance_method": method,
        "quality_checks": checks,
        "quality_summary": summary,
    }
