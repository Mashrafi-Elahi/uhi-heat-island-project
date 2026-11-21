"""Train temperature prediction models and export metrics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import FUSED_DATA_PATH, METRICS_PATH, MODEL_PATH  # noqa: E402

FEATURE_COLS = [
    "latitude",
    "longitude",
    "ndvi",
    "lst_c",
    "built_up_density",
    "surface_code",
    "vegetation_code",
    "traffic_code",
    "time_code",
]
TARGET = "air_temp_c"


def train_and_evaluate(df: pd.DataFrame) -> dict:
    X = df[FEATURE_COLS].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=100, max_depth=6, random_state=42
        ),
    }

    best_name = None
    best_model = None
    best_rmse = float("inf")
    report = {"models": {}, "feature_columns": FEATURE_COLS, "target": TARGET}

    for name, model in models.items():
        if name == "linear_regression":
            model.fit(X_train_s, y_train)
            preds = model.predict(X_test_s)
            fitted = model
            bundle_scaler = scaler
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            fitted = model
            bundle_scaler = None

        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = float(mean_absolute_error(y_test, preds))
        r2 = float(r2_score(y_test, preds))
        n_cv = min(5, len(y))
        if n_cv >= 2:
            X_cv = scaler.fit_transform(X) if name == "linear_regression" else X
            cv = cross_val_score(model, X_cv, y, cv=n_cv, scoring="r2")
        else:
            cv = np.array([r2])

        report["models"][name] = {
            "rmse": round(rmse, 3),
            "mae": round(mae, 3),
            "r2": round(r2, 3),
            "cv_r2_mean": round(float(np.mean(cv)), 3) if len(cv) else None,
        }
        if rmse < best_rmse:
            best_rmse = rmse
            best_name = name
            best_model = fitted

    bundle = {
        "model_name": best_name,
        "model": best_model,
        "scaler": bundle_scaler if best_name == "linear_regression" else None,
        "features": FEATURE_COLS,
    }
    report["selected_model"] = best_name
    report["n_samples"] = len(df)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    data = pd.read_csv(FUSED_DATA_PATH)
    metrics = train_and_evaluate(data)
    print(json.dumps(metrics, indent=2))
