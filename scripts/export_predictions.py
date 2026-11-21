"""Export GeoJSON predictions and grid forecast for dashboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import (  # noqa: E402
    FUSED_DATA_PATH,
    MODEL_PATH,
    PREDICTIONS_PATH,
    STUDY_AREA_BOUNDS,
)

FEATURE_COLS = [
    "latitude", "longitude", "ndvi", "lst_c", "built_up_density",
    "surface_code", "vegetation_code", "traffic_code", "time_code",
]


def predict_points(df: pd.DataFrame, bundle: dict) -> pd.DataFrame:
    X = df[FEATURE_COLS].values
    model = bundle["model"]
    if bundle.get("scaler"):
        X = bundle["scaler"].transform(X)
    df = df.copy()
    df["predicted_temp_c"] = model.predict(X)
    df["heat_risk"] = pd.cut(
        df["predicted_temp_c"],
        bins=[-np.inf, 30, 33, np.inf],
        labels=["low", "medium", "high"],
    )
    return df


def to_geojson(df: pd.DataFrame) -> dict:
    features = []
    for _, row in df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["longitude"]), float(row["latitude"])],
            },
            "properties": {
                "location_id": row["location_id"],
                "location_name": row.get("location_name", ""),
                "air_temp_c": float(row["air_temp_c"]),
                "predicted_temp_c": float(row["predicted_temp_c"]),
                "lst_c": float(row["lst_c"]),
                "ndvi": float(row["ndvi"]),
                "zone_type": row.get("zone_type", ""),
                "heat_risk": str(row["heat_risk"]),
            },
        })
    return {"type": "FeatureCollection", "features": features}


def export_forecast_grid(bundle: dict, n: int = 12) -> list[dict]:
    """Simple grid forecast using mean NDVI/LST from fused data."""
    df = pd.read_csv(FUSED_DATA_PATH)
    lat = np.linspace(STUDY_AREA_BOUNDS["south"], STUDY_AREA_BOUNDS["north"], n)
    lon = np.linspace(STUDY_AREA_BOUNDS["west"], STUDY_AREA_BOUNDS["east"], n)
    mean_ndvi = df["ndvi"].mean()
    mean_lst = df["lst_c"].mean()
    mean_built = df["built_up_density"].mean()

    rows = []
    for la in lat:
        for lo in lon:
            rows.append({
                "latitude": la,
                "longitude": lo,
                "ndvi": mean_ndvi,
                "lst_c": mean_lst,
                "built_up_density": mean_built,
                "surface_code": 2,
                "vegetation_code": 2,
                "traffic_code": 2,
                "time_code": 2,
            })
    grid_df = pd.DataFrame(rows)
    grid_df["predicted_temp_c"] = bundle["model"].predict(grid_df[FEATURE_COLS].values)
    return grid_df.to_dict(orient="records")


if __name__ == "__main__":
    bundle = joblib.load(MODEL_PATH)
    df = pd.read_csv(FUSED_DATA_PATH)
    pred = predict_points(df, bundle)
    geo = to_geojson(pred)
    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREDICTIONS_PATH.write_text(json.dumps(geo), encoding="utf-8")
    print(f"Exported {len(geo['features'])} features -> {PREDICTIONS_PATH}")
