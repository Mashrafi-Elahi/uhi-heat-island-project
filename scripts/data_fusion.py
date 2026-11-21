"""Merge ground field data with satellite LST/NDVI at each location."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import FIELD_DATA_PATH, FUSED_DATA_PATH, SATELLITE_DATA_PATH  # noqa: E402

SURFACE_MAP = {"concrete": 1, "asphalt": 2, "grass": 3, "water": 4, "mixed": 5}
VEG_MAP = {"low": 1, "medium": 2, "high": 3}
TRAFFIC_MAP = {"low": 1, "medium": 2, "high": 3}
TIME_MAP = {"morning": 1, "afternoon": 2, "evening": 3}


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["surface_code"] = out["surface_type"].str.lower().map(SURFACE_MAP).fillna(0)
    out["vegetation_code"] = out["vegetation_cover"].str.lower().map(VEG_MAP).fillna(0)
    out["traffic_code"] = out["traffic_density"].str.lower().map(TRAFFIC_MAP).fillna(0)
    out["time_code"] = out["time_of_day"].str.lower().map(TIME_MAP).fillna(0)
    return out


def fuse_datasets(
    field_path: Path = FIELD_DATA_PATH,
    satellite_path: Path = SATELLITE_DATA_PATH,
    output_path: Path = FUSED_DATA_PATH,
) -> pd.DataFrame:
    field = pd.read_csv(field_path)
    sat = pd.read_csv(satellite_path)

    merged = field.merge(
        sat[["location_id", "lst_c", "ndvi", "built_up_density", "land_cover"]],
        on="location_id",
        how="inner",
    )
    merged["lst_air_delta"] = merged["lst_c"] - merged["air_temp_c"]
    merged = encode_categoricals(merged)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    return merged


if __name__ == "__main__":
    result = fuse_datasets()
    print(f"Fused {len(result)} records -> {FUSED_DATA_PATH}")
