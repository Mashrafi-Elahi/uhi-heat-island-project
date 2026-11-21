# Literature Review — Urban Heat Island (Week 1)

## 1. Urban Heat Island (UHI)

**Definition:** Urban areas are systematically warmer than surrounding rural land, especially at night.

**Causes:**
- Low albedo surfaces (asphalt, concrete) absorb solar radiation
- Reduced evapotranspiration due to less vegetation
- Anthropogenic heat (traffic, AC, industry)
- Urban canyon geometry trapping longwave radiation

**Effects:**
- Higher cooling energy demand
- Heat-related health risks
- Reduced thermal comfort and productivity

## 2. Remote Sensing for UHI

| Index / Product | Satellite | Purpose |
|-----------------|-----------|---------|
| LST | Landsat 8/9 (Band 10) | Surface temperature distribution |
| NDVI | Sentinel-2 (B8, B4) | Vegetation density / cooling potential |
| MODIS LST | MODIS | Regional temperature trends |

**Key concept:** LST measures *surface* temperature; field sensors measure *air* temperature. Expect offset (often LST > air temp on sunny afternoons).

## 3. GIS & Spatial Analysis

- **Point sampling:** GPS-tagged field measurements
- **Interpolation:** IDW, kriging, or cubic grid (used in `scripts/gis_interpolation.py`)
- **Hotspot analysis:** Kernel density or Getis-Ord Gi*

## 4. Data Fusion & ML

Combining ground truth with satellite-derived features improves spatial prediction where field samples are sparse.

**Features used in this project:**
- NDVI (vegetation cooling)
- LST (radiative surface heating)
- Built-up density
- Surface type, traffic, time of day

**Models:** Linear Regression (baseline), Random Forest (nonlinear), optional XGBoost for extension.

## 5. References (expand for submission)

1. Oke, T.R. (1982). The energetic basis of the urban heat island.
2. Voogt, J.A., Oke, T.R. (2003). Thermal remote sensing of urban climates.
3. USGS Landsat Collection 2 Level 2 Science Products.
4. ESA Sentinel-2 User Handbook.

## 6. Study Area Justification

Document why your city/campus was chosen: urban diversity (commercial, residential, park, industrial, water), accessibility, and safety for field teams.
