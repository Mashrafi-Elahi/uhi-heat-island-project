"""Run full UHI data pipeline: fusion -> ML -> GIS -> exports."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from data_fusion import fuse_datasets
from train_model import train_and_evaluate
from gis_interpolation import build_heat_grid
from export_predictions import predict_points, to_geojson
import pandas as pd
import json
import joblib

sys.path.insert(0, str(ROOT / "backend"))
from app.config import FUSED_DATA_PATH, MODEL_PATH, PREDICTIONS_PATH, METRICS_PATH


def main():
    print("=== UHI Pipeline ===")
    fused = fuse_datasets()
    print(f"[1/4] Fusion: {len(fused)} records")

    metrics = train_and_evaluate(fused)
    print(f"[2/4] Model: {metrics['selected_model']} (see {METRICS_PATH})")

    build_heat_grid(fused)
    print("[3/4] GIS heat grid generated")

    bundle = joblib.load(MODEL_PATH)
    pred = predict_points(fused, bundle)
    geo = to_geojson(pred)
    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREDICTIONS_PATH.write_text(json.dumps(geo), encoding="utf-8")
    print(f"[4/4] GeoJSON predictions -> {PREDICTIONS_PATH}")
    print("=== Done. Start server: python backend/app/main.py ===")


if __name__ == "__main__":
    main()
