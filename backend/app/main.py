"""Flask API for UHI dashboard — Student 5."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parents[1]
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(APP_DIR.parent))

from app.config import (  # noqa: E402
    FIELD_DATA_PATH,
    FUSED_DATA_PATH,
    HEAT_GRID_PATH,
    METRICS_PATH,
    MODEL_PATH,
    PREDICTIONS_PATH,
    SATELLITE_DATA_PATH,
    STUDY_AREA_CENTER,
    STUDY_AREA_NAME,
    STUDY_AREA_ZOOM,
)

app = Flask(
    __name__,
    template_folder=str(FRONTEND),
    static_folder=str(FRONTEND / "static"),
)
CORS(app)


def _read_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _read_csv(path: Path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config")
def api_config():
    return jsonify({
        "study_area": STUDY_AREA_NAME,
        "center": {"lat": STUDY_AREA_CENTER[0], "lon": STUDY_AREA_CENTER[1]},
        "zoom": STUDY_AREA_ZOOM,
    })


@app.route("/api/field-data")
def api_field_data():
    df = _read_csv(FIELD_DATA_PATH)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/satellite-data")
def api_satellite_data():
    df = _read_csv(SATELLITE_DATA_PATH)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/fused-data")
def api_fused_data():
    df = _read_csv(FUSED_DATA_PATH)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/predictions")
def api_predictions():
    return jsonify(_read_json(PREDICTIONS_PATH, {"type": "FeatureCollection", "features": []}))


@app.route("/api/heat-grid")
def api_heat_grid():
    return jsonify(_read_json(HEAT_GRID_PATH, {"heat_points": []}))


@app.route("/api/model-metrics")
def api_model_metrics():
    return jsonify(_read_json(METRICS_PATH, {}))


@app.route("/api/statistics")
def api_statistics():
    field = _read_csv(FIELD_DATA_PATH)
    fused = _read_csv(FUSED_DATA_PATH)
    if field.empty:
        return jsonify({"error": "No field data. Run pipeline first."}), 404

    stats = {
        "avg_air_temp": round(float(field["air_temp_c"].mean()), 2),
        "max_air_temp": round(float(field["air_temp_c"].max()), 2),
        "min_air_temp": round(float(field["air_temp_c"].min()), 2),
        "hottest_location": field.loc[field["air_temp_c"].idxmax(), "location_name"],
        "coolest_location": field.loc[field["air_temp_c"].idxmin(), "location_name"],
        "sample_count": len(field),
    }
    if not fused.empty and "lst_c" in fused.columns:
        stats["avg_lst"] = round(float(fused["lst_c"].mean()), 2)
        stats["avg_ndvi"] = round(float(fused["ndvi"].mean()), 3)
        stats["avg_lst_air_delta"] = round(float(fused["lst_air_delta"].mean()), 2)
        by_zone = fused.groupby("zone_type")["air_temp_c"].mean().round(2)
        stats["temp_by_zone"] = by_zone.to_dict()
        by_time = fused.groupby("time_of_day")["air_temp_c"].mean().round(2)
        stats["temp_by_time"] = by_time.to_dict()
    return jsonify(stats)


@app.route("/api/field-data", methods=["POST"])
def add_field_reading():
    """Add a new field measurement (Student 1 mobile/form use)."""
    payload = request.get_json(force=True)
    required = ["latitude", "longitude", "air_temp_c"]
    if not all(k in payload for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    df = _read_csv(FIELD_DATA_PATH)
    new_id = f"L{len(df) + 1:02d}"
    row = {
        "location_id": payload.get("location_id", new_id),
        "location_name": payload.get("location_name", f"Survey {new_id}"),
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
        "air_temp_c": payload["air_temp_c"],
        "surface_type": payload.get("surface_type", "mixed"),
        "vegetation_cover": payload.get("vegetation_cover", "medium"),
        "traffic_density": payload.get("traffic_density", "medium"),
        "time_of_day": payload.get("time_of_day", "afternoon"),
        "timestamp": payload.get("timestamp", ""),
        "zone_type": payload.get("zone_type", "other"),
        "notes": payload.get("notes", ""),
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    FIELD_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FIELD_DATA_PATH, index=False)
    return jsonify({"ok": True, "location_id": row["location_id"]}), 201


if __name__ == "__main__":
    print(f"UHI Dashboard: http://127.0.0.1:5000")
    print(f"Study area: {STUDY_AREA_NAME}")
    if not MODEL_PATH.exists():
        print("Tip: Run 'python scripts/run_pipeline.py' first for ML & heat maps.")
    app.run(host="127.0.0.1", port=5000, debug=True)
