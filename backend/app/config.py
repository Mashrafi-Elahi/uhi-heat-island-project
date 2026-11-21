"""Project configuration — update for your study city."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Demo: Dhaka, Bangladesh — change to your campus/city
STUDY_AREA_NAME = "Dhaka Metropolitan Area"
STUDY_AREA_CENTER = (23.8103, 90.4125)  # lat, lon
STUDY_AREA_BOUNDS = {
    "west": 90.35,
    "south": 23.75,
    "east": 90.48,
    "north": 23.88,
}
STUDY_AREA_ZOOM = 13

FIELD_DATA_PATH = PROJECT_ROOT / "field_data" / "field_measurements.csv"
SATELLITE_DATA_PATH = PROJECT_ROOT / "satellite_data" / "satellite_points.csv"
FUSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "fused_dataset.csv"
PREDICTIONS_PATH = PROJECT_ROOT / "data" / "exports" / "heat_predictions.geojson"
MODEL_PATH = PROJECT_ROOT / "ml_models" / "heat_predictor.joblib"
METRICS_PATH = PROJECT_ROOT / "ml_models" / "model_metrics.json"
HEAT_GRID_PATH = PROJECT_ROOT / "gis_maps" / "heat_grid.json"
