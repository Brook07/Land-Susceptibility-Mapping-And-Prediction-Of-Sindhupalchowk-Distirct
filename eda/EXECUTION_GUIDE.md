# EDA Execution Guide - Step by Step

## 🎯 Quick Start Guide

### For First-Time Setup:

**Option 1: Automated Setup (Recommended)**
```bash
cd eda
python setup_eda.py
```

This script will:
- ✅ Install all dependencies
- ✅ Verify data files exist
- ✅ Create output directories
- ✅ Check Jupyter installation
- ✅ Verify spatial libraries

**Option 2: Manual Setup**
```bash
cd eda
pip install -r requirements_eda.txt
jupyter notebook 01_eda_analysis.ipynb
```

---

## 📓 Notebook Execution Workflow

### **Before You Start:**
1. ✓ Verify all data files are in `d:\sindupalchok_landslide\data\processed\`
2. ✓ Python 3.8+ installed
3. ✓ VS Code with Jupyter extension OR Jupyter Lab
4. ✓ At least 4GB RAM available

---

## 🔄 Detailed Execution Steps

### **SECTION 1: Setup & Imports** [~10 seconds]
**What it does:**
- Imports all required libraries
- Sets up visualization styling
- Defines data paths

**Expected Output:**
```
✓ Libraries imported successfully
✓ Data paths defined
```

**If you see errors:**
- Missing library → Run: `pip install [library_name]`
- Path error → Update paths in notebook

---

### **SECTION 2: Load Boundary Shapefile** [~5 seconds]
**What it does:**
- Loads district boundary from shapefile
- Calculates area and properties
- Shows basic info

**Expected Output:**
```
Boundary Shapefile Info:
Shape: (1, 1)
CRS: EPSG:4326 (or similar)
Geometry type: Polygon
Boundary area (km²): XXXX.XX
```

**Typical Values for Sindhupalchok:**
- Area: ~2500-2800 km²
- Geometry: Polygon or MultiPolygon
- CRS: Should be geographic (EPSG:4326) or projected

---

### **SECTION 3: Visualize Boundary** [~10 seconds]
**What it does:**
- Creates map visualization of district boundary
- Saves figure: `01_boundary_map.png`

**Expected Output:**
```
✓ Boundary map saved
```

**Look for:**
- Clean district boundary outline
- Proper axes with lat/long labels
- Blue colored polygon

---

### **SECTION 4: Load Raster Data** [~30-60 seconds]
**What it does:**
- Loads all 9 TIF raster files
- Calculates statistics (min, max, mean, std)
- Creates statistics dataframe

**Expected Output:**
```
✓ Loaded DEM
✓ Loaded Slope
✓ Loaded Aspect
✓ Loaded LULC
✓ Loaded NDVI
✓ Loaded Rainfall
✓ Loaded RiverProximity
✓ Loaded RoadProximity
✓ Loaded TWI

RASTER DATA STATISTICS
                min        max        mean        std    median
DEM        XXXX.XX   XXXX.XX   XXXX.XX   XXXX.XX   XXXX.XX
Slope      XXXX.XX   XXXX.XX   XXXX.XX   XXXX.XX   XXXX.XX
...
```

**Typical Ranges (Sindhupalchok):**
- **DEM**: 600-4000 meters
- **Slope**: 0-89 degrees
- **Aspect**: 0-360 degrees
- **NDVI**: -1 to 1 (vegetation index)
- **Rainfall**: 1200-5000 mm/year
- **Proximity**: 0-10,000 meters

---

### **SECTION 5: Visualize All Rasters** [~30 seconds]
**What it does:**
- Creates 3x3 subplot visualization
- Shows all raster layers with histograms
- Saves: `02_all_rasters_visualization.png`

**Expected Output:**
```
✓ Raster visualization saved
```

**Look for:**
- 9 panels with different colormaps
- Min/Max values displayed
- Proper color bars on each panel

---

### **SECTION 6: Load Landslide Inventory** [~5 seconds]
**What it does:**
- Loads CSV file with landslide data
- Shows shape, columns, data types
- Displays missing values

**Expected Output:**
```
Landslide Inventory Info:
Shape: (XXX, YY)
Columns: [...list of columns...]
Data types:
  [column names and types]

First few rows:
[sample data rows]

Missing values:
[column]: X
```

**Expected Values:**
- Number of landslides: 100-1000+ points
- Must have columns: longitude, latitude (or x, y)
- Date information (if available)
- Size/area information (if available)

---

### **SECTION 7: Convert to GeoDataFrame** [~5 seconds]
**What it does:**
- Creates geospatial dataframe from coordinates
- Sets CRS to EPSG:4326
- Validates geometry

**Expected Output:**
```
✓ GeoDataFrame created from landslide inventory
CRS: EPSG:4326
```

---

### **SECTION 8: Visualize Landslide Locations** [~15 seconds]
**What it does:**
- Creates map showing:
  - District boundary (gray)
  - Landslide points (red markers)
- Saves: `03_landslide_locations.png`

**Expected Output:**
```
✓ Landslide location map saved
```

**Look for:**
- Red points concentrated in mountainous areas
- Points should fall within boundary
- Higher density in upper district

---

### **SECTION 9: Raster Distribution Analysis** [~20 seconds]
**What it does:**
- Creates histogram for each raster layer
- Shows frequency distributions
- Saves: `04_raster_distributions.png`

**Expected Output:**
```
✓ Distribution plots saved
```

**Look for:**
- Different distribution shapes for each layer
- DEM: Bimodal (low hills + high mountains)
- Slope: Right-skewed (more gentle slopes)
- NDVI: Bimodal (vegetation + non-vegetation)

---

### **SECTION 10: Data Quality Assessment** [~10 seconds]
**What it does:**
- Calculates data completeness % for each layer
- Reports NoData pixels
- Creates quality report

**Expected Output:**
```
DATA QUALITY ASSESSMENT
Layer               Total_Pixels  Valid_Pixels  NoData_Pixels  Data_Completeness_%
DEM                 XXXXXXXXX    XXXXXXXXX     XXXX           XXX.XX
...
```

**Save Output:**
- `data_quality_report.csv`

**Expected Values:**
- Data completeness > 95% for all layers
- Very few NoData pixels (< 5%)

---

### **SECTION 11: Extract Values at Landslide Points** [~60-120 seconds]
**What it does:**
- For each landslide point, extracts values from all 9 rasters
- Creates a table with values at each landslide
- Shows statistics of extracted values

**Expected Output:**
```
Extracting raster values at landslide locations...
✓ Extracted values for XXX landslides

Extracted Values Statistics:
             count        mean        std       min       max
DEM          XXX.0    XXXX.XX    XXXX.XX    XXXX.XX   XXXX.XX
Slope        XXX.0    XXXX.XX    XXXX.XX    XXXX.XX   XXXX.XX
...

✓ Extracted values saved
```

**Time Note:**
- This step takes longest (depends on landslide count)
- ~0.1-0.5 seconds per landslide point

---

### **SECTION 12: Correlation Analysis** [~10 seconds]
**What it does:**
- Calculates correlations between all variables
- Creates heatmap
- Saves: `05_correlation_matrix.png`

**Expected Output:**
```
✓ Correlation matrix saved
```

**Interpret Results:**
- Values close to 1: Strong positive correlation
- Values close to -1: Strong negative correlation
- Values close to 0: No correlation
- Look for landslide patterns:
  - Higher slopes → more landslides?
  - Steeper aspects → more landslides?

---

### **SECTION 13: Summary Report** [~5 seconds]
**What it does:**
- Generates comprehensive summary
- Displays all key findings
- Saves: `EDA_SUMMARY_REPORT.txt`

**Expected Output:**
```
================================================================================
EXPLORATORY DATA ANALYSIS - SUMMARY REPORT
Landslide Susceptibility Mapping - Sindhupalchok District, Nepal
================================================================================

1. STUDY AREA
   - Area: XXXX.XX km²
   - CRS: EPSG:XXXX
   - Geometry Type: Polygon

2. RASTER LAYERS ANALYZED
   - Total Layers: 9
   - Layers: DEM, Slope, Aspect, ...

3. LANDSLIDE INVENTORY
   - Total Landslides: XXX
   - Data Points: XXX
   - Variables: XX

4. DATA COMPLETENESS
[Quality table shown]

5. KEY OBSERVATIONS
   - All raster layers have been successfully loaded
   - Landslide inventory has been processed
   - Raster values extracted at landslide locations
   - Correlation analysis completed

6. OUTPUT FILES
   - Figures saved to: ./figures/
   - Data files saved to: ./data/
   ...
```

---

### **SECTION 14: Recommendations** [~5 seconds]
**What it does:**
- Lists next steps for preprocessing
- Suggests feature engineering tasks
- Saves: `NEXT_STEPS_RECOMMENDATIONS.txt`

---

## 📊 Total Runtime

- **First run**: 5-8 minutes (includes loading all data)
- **Subsequent runs**: 3-5 minutes (cached data)
- **Bottleneck**: Value extraction at landslide points

---

## 📁 Output Files Created

### Figures (saved to `figures/`):
```
01_boundary_map.png                    - District boundary visualization
02_all_rasters_visualization.png        - All 9 rasters in grid
03_landslide_locations.png              - Landslides overlaid on boundary
04_raster_distributions.png             - Histograms of all layers
05_correlation_matrix.png               - Heatmap of correlations
```

### Data Files (saved to `data/`):
```
raster_statistics.csv                   - Summary stats for each raster
data_quality_report.csv                 - Data completeness report
landslide_points_extracted_values.csv    - Values at each landslide
correlation_matrix.csv                  - Correlation coefficients
EDA_SUMMARY_REPORT.txt                  - Comprehensive summary
NEXT_STEPS_RECOMMENDATIONS.txt          - Suggested next steps
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'rasterio'"
```bash
pip install rasterio
# Or if that fails:
pip install --upgrade rasterio
```

### Error: "GDAL not found"
```bash
# Install GDAL dependencies
# Windows: conda install gdal (recommended)
# Or: pip install gdal
```

### Error: "File not found" for rasters
- Check file paths match your system exactly
- Use raw strings: `r'd:\path\to\file.tif'`
- Verify files are not corrupted

### Error: Memory issues with large rasters
- Close other applications
- Reduce image resolution for initial EDA
- Process rasters one at a time

### Error: Landslide points outside boundary
- Check CRS alignment (both should be EPSG:4326)
- Verify coordinates are in lat/long format
- Check for coordinate sign errors

---

## ✅ Verification Checklist

After running the notebook, verify:

- [ ] All 5 figures created in `figures/` folder
- [ ] All 6 CSV/TXT files in `data/` folder
- [ ] No errors in notebook execution
- [ ] Raster statistics make sense for region
- [ ] Landslide points appear on map
- [ ] Correlation matrix shows reasonable values
- [ ] Summary report is readable

---

## 🎯 What's Next After EDA?

Once you complete this EDA:

1. **Data Preprocessing** (next_step_1_preprocessing.ipynb)
   - Normalize raster values
   - Handle missing data
   - Create training/validation splits

2. **Feature Engineering** (next_step_2_features.ipynb)
   - Create interaction features
   - Generate derived indices
   - Handle class imbalance

3. **Model Development** (next_step_3_modeling.ipynb)
   - Train machine learning models
   - Tune hyperparameters
   - Evaluate performance

4. **Susceptibility Mapping** (next_step_4_mapping.ipynb)
   - Apply model to full raster
   - Generate susceptibility map
   - Create uncertainty maps

---

## 📞 Need Help?

1. Check the **README.md** file
2. Review inline notebook comments
3. Check **Common Issues** section above
4. Review data sources for expected value ranges
5. Contact project mentor if persistent issues

---

**Good luck with your EDA! 🚀**
