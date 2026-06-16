# Land-Susceptibility-Mapping-And-Prediction-Of-Sindhupalchowk-Distirct
Landslide susceptibility mapping using geospatial data, feature engineering, and machine learning models to assess landslide risk.
 # Landslide Susceptibility Mapping (LSM)

A machine learning–based **Landslide Susceptibility Mapping (LSM)** system for Sindhupalchok District, Nepal.  
GeoShield AI integrates terrain, rainfall, vegetation, and infrastructure data to generate spatial landslide risk maps and interactive GIS visualizations.

---

![GIS](https://img.shields.io/badge/GIS-Spatial%20Analysis-green)
![Flask](https://img.shields.io/badge/Flask-Backend-orange)
![React](https://img.shields.io/badge/React-Frontend-blue)

---

## 🎯 Objective

To develop a **data-driven Landslide Susceptibility Mapping (LSM) system** that:
- Identifies landslide-prone zones using ML models
- Integrates multi-source geospatial datasets
- Supports disaster risk visualization and planning
- Enables route-based hazard analysis
- Demonstrates GIS + Machine Learning integration

---

## 🗺️ Key Features

- 🌄 Landslide Susceptibility Map using Random Forest
- 🌧️ Rainfall impact simulation for dynamic risk updates
- 📊 Feature-based hazard scoring (slope, NDVI, elevation, TWI)
- 🛣️ Safe route analysis using OSRM + spatial risk overlay
- 🚨 Disaster reporting system with map markers
- 📍 Municipality-level hazard summaries
- 🗺️ Interactive Leaflet GIS dashboard

---

## 🧠 Methodology (LSM Pipeline)

### 1. Data Collection
- DEM (Elevation, Slope, Aspect)
- Rainfall (historical + recent)
- NDVI (Vegetation index)
- Distance to roads & rivers
- TWI (Topographic Wetness Index)
- Landslide inventory data

### 2. Preprocessing
- Raster reprojection (EPSG:32645)
- Feature stacking and normalization
- Spatial alignment of datasets
- Label preparation from historical events

### 3. Model Training
- Random Forest Classifier (`scikit-learn`)
- Feature importance analysis
- Cross-validation for performance evaluation

### 4. Susceptibility Mapping
- Pixel-wise prediction of landslide probability
- Classification:
  - Low
  - Medium
  - High
  - Very High

### 5. Spatial Risk Analysis
- Overlay with roads, rivers, settlements
- Route hazard scoring using spatial sampling

---

## 🧰 Tech Stack

**Backend**
- Python, Flask, Flask-CORS
- scikit-learn, pandas, numpy, joblib

**Frontend**
- React (Vite)
- Tailwind CSS
- Leaflet / React-Leaflet

**Geospatial Processing**
- GeoTIFF, Shapefiles
- OSRM Routing API
- QGIS-preprocessed datasets


