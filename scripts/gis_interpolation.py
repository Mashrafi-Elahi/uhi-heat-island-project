"""Spatial interpolation grid for heat map visualization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import griddata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import FUSED_DATA_PATH, HEAT_GRID_PATH, STUDY_AREA_BOUNDS  # noqa: E402


def build_heat_grid(
    df: pd.DataFrame,
    value_col: str = "air_temp_c",
    resolution: int = 40,
) -> dict:
    lats = df["latitude"].values
    lons = df["longitude"].values
    vals = df[value_col].values

    lat_lin = np.linspace(STUDY_AREA_BOUNDS["south"], STUDY_AREA_BOUNDS["north"], resolution)
    lon_lin = np.linspace(STUDY_AREA_BOUNDS["west"], STUDY_AREA_BOUNDS["east"], resolution)
    lon_grid, lat_grid = np.meshgrid(lon_lin, lat_lin)

    interp = griddata(
        (lons, lats), vals, (lon_grid, lat_grid), method="cubic", fill_value=np.nanmean(vals)
    )

    # Leaflet heat layer expects [lat, lon, intensity]
    heat_points = []
    vmin, vmax = float(np.nanmin(interp)), float(np.nanmax(interp))
    for i in range(resolution):
        for j in range(resolution):
            intensity = (interp[i, j] - vmin) / (vmax - vmin + 1e-6)
            heat_points.append([float(lat_grid[i, j]), float(lon_grid[i, j]), float(intensity)])

    payload = {
        "bounds": STUDY_AREA_BOUNDS,
        "value_col": value_col,
        "min_temp": vmin,
        "max_temp": vmax,
        "heat_points": heat_points,
    }
    HEAT_GRID_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEAT_GRID_PATH.write_text(json.dumps(payload), encoding="utf-8")
    return payload


if __name__ == "__main__":
    data = pd.read_csv(FUSED_DATA_PATH)
    grid = build_heat_grid(data)
    print(f"Heat grid: {len(grid['heat_points'])} points -> {HEAT_GRID_PATH}")
