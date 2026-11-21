/**
 * Google Earth Engine — Landsat 8/9 LST + Sentinel-2 NDVI
 * Student 2: Remote Sensing Lead
 *
 * Setup: https://earthengine.google.com → paste in Code Editor
 * Update STUDY_AREA and DATE_RANGE for your city.
 */

var STUDY_AREA = ee.Geometry.Rectangle([90.35, 23.75, 90.48, 23.88]); // Dhaka demo
var START = '2026-05-01';
var END = '2026-06-01';
var CLOUD_MAX = 20;

// --- NDVI (Sentinel-2) ---
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(STUDY_AREA)
  .filterDate(START, END)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CLOUD_MAX));

function addNDVI(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
}

var ndviComposite = s2.map(addNDVI).select('NDVI').median().clip(STUDY_AREA);

// --- LST (Landsat 8/9 Collection 2 Level 2) ---
var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2'))
  .filterBounds(STUDY_AREA)
  .filterDate(START, END)
  .filter(ee.Filter.lt('CLOUD_COVER', CLOUD_MAX));

function scaleLST(image) {
  var lst = image.select('ST_B10')
    .multiply(0.00341802).add(149.0)
    .subtract(273.15)  // Kelvin to Celsius
    .rename('LST_C');
  return image.addBands(lst);
}

var lstComposite = landsat.map(scaleLST).select('LST_C').median().clip(STUDY_AREA);

// --- Visualization ---
Map.centerObject(STUDY_AREA, 12);
Map.addLayer(ndviComposite, {min: 0, max: 0.8, palette: ['brown', 'yellow', 'green']}, 'NDVI');
Map.addLayer(lstComposite, {min: 25, max: 45, palette: ['blue', 'yellow', 'red']}, 'LST (°C)');

// --- Export sample points (match field location_id CSV) ---
// After field survey, upload GPS points as ee.FeatureCollection and use:
// Export.table.toDrive({collection: pointsWithLST, description: 'uhi_sample_points'});

print('Median LST °C:', lstComposite.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: STUDY_AREA,
  scale: 30,
  maxPixels: 1e9
}));

print('Median NDVI:', ndviComposite.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: STUDY_AREA,
  scale: 10,
  maxPixels: 1e9
}));
