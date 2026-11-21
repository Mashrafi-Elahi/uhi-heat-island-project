# Urban Heat Island Mapping — Remote Sensing & Ground Data

Environmental Science project for **5 CSE students**: combine field temperature surveys, satellite LST/NDVI, GIS heat maps, ML prediction, and an interactive dashboard.

## Quick Start

```powershell
cd uhi-heat-island-project

# Windows: use py launcher if `python` is not on PATH
py -3.14 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 1) Generate demo fused dataset & train model
python scripts/run_pipeline.py

# 2) Start API + dashboard
python backend\app\main.py
# Open http://127.0.0.1:5000
```

**Note:** During Python install, check **"Add python.exe to PATH"** so `python` works in any terminal.

## Team Roles

| Student | Role | Key folders |
|---------|------|-------------|
| 1 | Field data | `field_data/`, `gps_coordinates/` |
| 2 | Remote sensing | `satellite_data/`, `notebooks/`, `scripts/gee_lst_ndvi.js` |
| 3 | GIS | `gis_maps/`, `scripts/gis_interpolation.py` |
| 4 | Data fusion & ML | `scripts/`, `ml_models/` |
| 5 | Dashboard & docs | `frontend/`, `dashboard/`, `documentation/` |

## 8-Week Timeline

| Week | Phase |
|------|-------|
| 1 | Literature survey |
| 2 | Study area & sampling plan |
| 3 | Ground temperature collection |
| 4 | Satellite LST/NDVI (GEE) |
| 5 | GIS heat mapping |
| 6 | Fusion + predictive modeling |
| 7 | Dashboard |
| 8 | Validation & presentation |

## Study Area Setup

Edit `backend/app/config.py`:

- `STUDY_AREA_CENTER` — map center (lat, lon)
- `STUDY_AREA_BOUNDS` — bounding box for GEE export

Default demo area: **Dhaka, Bangladesh** (replace with your city).

## Data Flow

```
Field CSV + GPS  →  fusion  →  ML model  →  predictions GeoJSON
Satellite CSV    ↗              ↓
                            Flask API  →  Leaflet dashboard
```

## Deliverables Checklist

- [ ] Literature review (`documentation/01_literature_review.md`)
- [ ] Sampling plan (`documentation/02_sampling_plan.md`)
- [ ] Field dataset (`field_data/field_measurements.csv`)
- [ ] LST/NDVI maps (`satellite_data/`)
- [ ] GIS heat maps (`gis_maps/`)
- [ ] Trained model (`ml_models/heat_predictor.joblib`)
- [ ] Dashboard (http://127.0.0.1:5000)
- [ ] Presentation (`presentation/`)

## Field Safety

Avoid peak afternoon heat alone; work in pairs; carry water; use sun protection; respect restricted areas.

## Evaluation Alignment

| Criteria | Where demonstrated |
|----------|-------------------|
| Field survey (15) | `field_data/` + observation template |
| Remote sensing (20) | GEE script + `satellite_data/` |
| GIS (20) | `gis_maps/` + interpolation script |
| Predictive modeling (20) | `scripts/train_model.py` + metrics JSON |
| Dashboard (10) | `frontend/` |
| Documentation (15) | `documentation/` + `presentation/` |
