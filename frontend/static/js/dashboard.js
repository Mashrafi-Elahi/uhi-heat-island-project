const API = "";
let map, fieldLayer, heatLayer, predLayer;
let zoneChart, timeChart;

function tempColor(temp) {
  if (temp < 30) return "#22c55e";
  if (temp < 33) return "#eab308";
  return "#ef4444";
}

async function fetchJSON(url) {
  const r = await fetch(API + url);
  return r.json();
}

function initMap(center, zoom) {
  map = L.map("map").setView([center.lat, center.lon], zoom);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 19,
  }).addTo(map);
  fieldLayer = L.layerGroup().addTo(map);
  heatLayer = null;
  predLayer = L.layerGroup();
}

function renderFieldPoints(records, fusedById) {
  fieldLayer.clearLayers();
  records.forEach((p) => {
    const fused = fusedById[p.location_id] || {};
    const temp = p.air_temp_c;
    const lst = fused.lst_c || temp;
    const ndvi = fused.ndvi || 0;
    const radius = 8 + (lst - 30) * 0.8;
    const marker = L.circleMarker([p.latitude, p.longitude], {
      radius: Math.max(6, Math.min(radius, 22)),
      fillColor: tempColor(temp),
      color: ndvi > 0.5 ? "#166534" : "#374151",
      weight: 2,
      fillOpacity: 0.85,
    });
    marker.bindPopup(`
      <strong>${p.location_name}</strong><br/>
      Air: ${temp}°C · LST: ${fused.lst_c ?? "—"}°C<br/>
      NDVI: ${ndvi || "—"} · Zone: ${p.zone_type}<br/>
      Surface: ${p.surface_type} · ${p.time_of_day}
    `);
    marker.addTo(fieldLayer);
  });
}

function renderHeatGrid(grid) {
  if (heatLayer) map.removeLayer(heatLayer);
  if (!grid.heat_points?.length) return;
  heatLayer = L.heatLayer(grid.heat_points, {
    radius: 28,
    blur: 18,
    maxZoom: 17,
    gradient: { 0.2: "blue", 0.5: "lime", 0.7: "yellow", 1.0: "red" },
  });
}

function renderPredictions(geojson) {
  predLayer.clearLayers();
  (geojson.features || []).forEach((f) => {
    const [lon, lat] = f.geometry.coordinates;
    const p = f.properties;
    const m = L.circleMarker([lat, lon], {
      radius: 10,
      fillColor: tempColor(p.predicted_temp_c),
      color: "#7c2d12",
      weight: 2,
      dashArray: "4",
      fillOpacity: 0.7,
    });
    m.bindPopup(`
      <strong>${p.location_name}</strong><br/>
      Observed: ${p.air_temp_c}°C<br/>
      Predicted: ${p.predicted_temp_c.toFixed(1)}°C<br/>
      Risk: ${p.heat_risk}
    `);
    m.addTo(predLayer);
  });
}

function renderStats(stats) {
  const el = document.getElementById("stats-panel");
  el.innerHTML = `
    <ul class="list-unstyled mb-0 small">
      <li><strong>Avg air temp:</strong> ${stats.avg_air_temp}°C</li>
      <li><strong>Hottest:</strong> ${stats.hottest_location} (${stats.max_air_temp}°C)</li>
      <li><strong>Coolest:</strong> ${stats.coolest_location} (${stats.min_air_temp}°C)</li>
      <li><strong>Samples:</strong> ${stats.sample_count}</li>
      ${stats.avg_lst ? `<li><strong>Avg LST:</strong> ${stats.avg_lst}°C</li>` : ""}
      ${stats.avg_ndvi ? `<li><strong>Avg NDVI:</strong> ${stats.avg_ndvi}</li>` : ""}
    </ul>
  `;
}

function renderMetrics(metrics) {
  const el = document.getElementById("metrics-panel");
  if (!metrics.selected_model) {
    el.innerHTML = "<p class='text-muted'>Run pipeline to train model.</p>";
    return;
  }
  const m = metrics.models[metrics.selected_model];
  el.innerHTML = `
    <p><strong>Model:</strong> ${metrics.selected_model}</p>
    <p>RMSE: ${m.rmse} · MAE: ${m.mae}<br/>R²: ${m.r2}</p>
  `;
}

function renderCharts(stats) {
  const zoneCtx = document.getElementById("zoneChart");
  const timeCtx = document.getElementById("timeChart");
  if (zoneChart) zoneChart.destroy();
  if (timeChart) timeChart.destroy();

  const zones = stats.temp_by_zone || {};
  zoneChart = new Chart(zoneCtx, {
    type: "bar",
    data: {
      labels: Object.keys(zones),
      datasets: [{
        label: "Avg °C",
        data: Object.values(zones),
        backgroundColor: "#f97316",
      }],
    },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: false } } },
  });

  const times = stats.temp_by_time || {};
  timeChart = new Chart(timeCtx, {
    type: "line",
    data: {
      labels: Object.keys(times),
      datasets: [{
        label: "Avg °C",
        data: Object.values(times),
        borderColor: "#3b82f6",
        tension: 0.3,
      }],
    },
    options: { plugins: { legend: { display: false } } },
  });
}

function setupLayerToggle() {
  document.querySelectorAll("[data-layer]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-layer]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const layer = btn.dataset.layer;
      fieldLayer.addTo(map);
      if (heatLayer) map.removeLayer(heatLayer);
      map.removeLayer(predLayer);
      if (layer === "heat" && heatLayer) heatLayer.addTo(map);
      if (layer === "predictions") predLayer.addTo(map);
    });
  });
}

async function init() {
  const config = await fetchJSON("/api/config");
  document.getElementById("study-area-label").textContent = config.study_area;
  initMap(config.center, config.zoom);

  const [field, fused, stats, metrics, grid, predictions] = await Promise.all([
    fetchJSON("/api/field-data"),
    fetchJSON("/api/fused-data"),
    fetchJSON("/api/statistics"),
    fetchJSON("/api/model-metrics"),
    fetchJSON("/api/heat-grid"),
    fetchJSON("/api/predictions"),
  ]);

  const fusedById = {};
  fused.forEach((r) => { fusedById[r.location_id] = r; });

  renderFieldPoints(field, fusedById);
  renderHeatGrid(grid);
  renderPredictions(predictions);
  renderStats(stats);
  renderMetrics(metrics);
  renderCharts(stats);
  setupLayerToggle();
}

init().catch(console.error);
