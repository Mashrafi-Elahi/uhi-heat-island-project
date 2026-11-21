# Validation Guide (Week 8)

## 1. Sensor Validation

- Compare two readings at the same spot within 2 minutes (should differ &lt; 0.5°C).
- Shade the sensor; avoid body heat and direct sunlight on the probe.

## 2. Ground vs Satellite (LST)

Compute at each `location_id`:

```
delta = LST - air_temp
```

**Expected:** Positive delta on sunny afternoons over concrete/asphalt; smaller delta over parks/water.

Report Pearson correlation between `air_temp_c` and `lst_c` in your report.

## 3. Model Validation

Check `ml_models/model_metrics.json`:

| Metric | Good target |
|--------|-------------|
| RMSE | &lt; 2°C (depends on sample size) |
| MAE | &lt; 1.5°C |
| R² | &gt; 0.7 with adequate samples |

With only 10 demo points, metrics are illustrative — collect more field data for real evaluation.

## 4. GIS Validation

- Visually confirm hottest interpolated cells align with commercial/industrial points.
- Cool cells should align with parks and water samples.

## 5. Dashboard Validation

- All sample points visible on map
- Zone bar chart matches manual Excel averages
- Heat layer toggles without console errors

## 6. Report Sections

1. Introduction & UHI background  
2. Methodology (field + GEE + GIS + ML)  
3. Results (maps, tables, metrics)  
4. Discussion (causes of hotspots)  
5. Planning recommendations (greening, cool roofs)  
6. Conclusion & future work (IoT, real-time alerts)
