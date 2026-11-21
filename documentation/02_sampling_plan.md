# Sampling Plan (Week 2)

## Study Area Zones

| Zone | Purpose | Target samples |
|------|---------|----------------|
| Commercial | Peak anthropogenic heat | 2–3 |
| Residential | Medium built-up | 2–3 |
| Park / garden | Cooling baseline | 2–3 |
| Industrial | Heat source | 1–2 |
| Water body | Cooling influence | 1–2 |

## Survey Schedule

| Session | Time | Purpose |
|---------|------|---------|
| Morning | 08:00–09:30 | Baseline before peak solar load |
| Afternoon | 13:00–15:00 | Peak UHI conditions |
| Evening | 17:30–19:00 | Heat retention in built-up zones |

## Per-Location Checklist

- [ ] GPS locked (±10 m accuracy)
- [ ] Air temperature at 1.5 m height
- [ ] Surface type recorded
- [ ] Vegetation cover (low / medium / high)
- [ ] Traffic density noted
- [ ] Timestamp in ISO format
- [ ] Photo optional (same filename as location_id)

## Data Entry

Use `field_data/field_observation_sheet_template.csv` during survey, then merge into `field_data/field_measurements.csv`.

## Team Assignments

| Student | Week 2–3 task |
|---------|----------------|
| 1 | Lead all field visits; quality-check GPS |
| 2 | Match satellite acquisition date to survey week |
| 3 | Pre-draw sampling map in QGIS |
| 4 | Prepare fusion column definitions |
| 5 | Build mobile-friendly form (optional POST `/api/field-data`) |

## Minimum Sample Size

**Recommended:** ≥ 15 locations × 3 time periods = 45 readings (demo uses 10 locations).
