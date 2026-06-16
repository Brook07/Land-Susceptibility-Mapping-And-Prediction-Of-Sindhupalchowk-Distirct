# EDA (Exploratory Data Analysis) Guide
## Landslide Susceptibility Mapping - Sindhupalchok District

---

## 📁 Folder Structure

```
eda/
├── 01_eda_analysis.ipynb          # Main EDA notebook
├── requirements_eda.txt            # Python dependencies
├── README.md                       # This file
├── figures/                        # Output visualizations
│   ├── 01_boundary_map.png
│   ├── 02_all_rasters_visualization.png
│   ├── 03_landslide_locations.png
│   ├── 04_raster_distributions.png
│   └── 05_correlation_matrix.png
└── data/                          # Output CSV/TXT files
    ├── raster_statistics.csv
    ├── data_quality_report.csv
    ├── landslide_points_extracted_values.csv
    ├── correlation_matrix.csv
    ├── EDA_SUMMARY_REPORT.txt
    └── NEXT_STEPS_RECOMMENDATIONS.txt
```

---

## 🎯 EDA Objectives

### 1. **Data Inventory & Validation**
   - Load and verify all raster layers
   - Check data completeness and NoData values
   - Validate CRS and spatial alignment
   - Assess landslide inventory quality

### 2. **Descriptive Statistics**
   - Calculate min, max, mean, std for each layer
   - Generate distribution histograms
   - Identify outliers and anomalies
   - Compare statistics at landslide vs. non-landslide areas

### 3. **Spatial Analysis**
   - Visualize all raster layers
   - Map landslide locations
   - Show district boundary with landslide density
   - Create distribution plots for each variable

### 4. **Correlation Analysis**
   - Extract raster values at landslide points
   - Calculate correlation matrix
   - Identify highly correlated variables
   - Detect multicollinearity issues

### 5. **Data Quality Assessment**
   - Report data completeness percentage
   - Identify missing or problematic areas
   - Check for spatial coverage gaps
   - Document data issues for preprocessing

---

## 📊 Data Layers Analyzed

### **Topographic Features**
- **DEM**: Digital Elevation Model (terrain height)
- **Slope**: Angle of terrain incline
- **Aspect**: Direction of slope facing
- **TWI**: Topographic Wetness Index

### **Environmental Features**
- **NDVI**: Normalized Difference Vegetation Index
- **LULC**: Land Use/Land Cover classification
- **Rainfall**: Annual rainfall patterns

### **Distance-based Features**
- **RiverProximity**: Distance to nearest river/stream
- **RoadProximity**: Distance to nearest road network

### **Reference Data**
- **Boundary Shapefile**: District administrative boundary
- **Landslide Inventory**: CSV with landslide locations & attributes

---

## 🚀 How to Run the EDA

### **Step 1: Install Dependencies**
```bash
cd eda
pip install -r requirements_eda.txt
```

### **Step 2: Update Data Paths (if needed)**
Edit the data paths in Section 1 of the notebook if your data location differs:
```python
base_path = r'd:\sindupalchok_landslide\data\processed'
```

### **Step 3: Run the Notebook**
```bash
jupyter notebook 01_eda_analysis.ipynb
```

Or use VS Code:
- Open the notebook with Jupyter extension
- Run cells sequentially from top to bottom
- Monitor output messages for data loading confirmation

### **Step 4: Review Outputs**
- Check `figures/` for visualization outputs
- Review CSV files in `data/` for statistics
- Read summary reports for key insights

---

## 📈 Key Sections Explained

### **Section 1: Setup**
- Imports required libraries (numpy, pandas, rasterio, geopandas)
- Defines data paths
- Sets up visualization style

### **Section 2-3: Vector Data**
- Loads boundary shapefile
- Calculates area statistics
- Creates map visualization

### **Section 4: Raster Data Loading**
- Reads all TIF files
- Calculates basic statistics
- Handles NoData values properly

### **Section 5-6: Landslide Inventory**
- Loads CSV file
- Creates GeoDataFrame with geometry
- Visualizes landslide locations on map

### **Section 7-8: Distribution Analysis**
- Generates histograms for each layer
- Performs data quality assessment
- Reports data completeness

### **Section 9: Value Extraction**
- Extracts raster values at landslide points
- Creates correlation matrix
- Identifies variable relationships

### **Section 10: Summary & Recommendations**
- Generates comprehensive report
- Provides next steps for modeling

---

## 💡 Interpretation Guide

### **Understanding Raster Statistics**
```
Min/Max: Range of values in the raster
Mean: Average value across all pixels
Std: Standard deviation (variability)
Median: 50th percentile value
NoData_Pixels: Count of missing/masked pixels
Data_Completeness_%: Percentage of valid data
```

### **Interpreting Correlation Values**
- **> 0.7**: Strong positive correlation
- **0.3 to 0.7**: Moderate correlation
- **< 0.3**: Weak correlation
- **Negative values**: Inverse relationship

### **Data Quality Checklist**
- ✓ Data completeness > 95%
- ✓ All layers have same spatial extent
- ✓ NoData values handled properly
- ✓ CRS consistent across all data
- ✓ Landslide points fall within boundary

---

## ⚠️ Common Issues & Solutions

### **Issue: "Module not found" errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements_eda.txt
```

### **Issue: Raster file not found**
- Verify file paths match your system
- Check if files are corrupted or moved
- Ensure rasterio can read GeoTIFF format

### **Issue: Landslide points outside boundary**
- Check CRS alignment
- Verify coordinates are in correct format
- Review coordinate transformation logic

### **Issue: Memory error with large rasters**
- Process rasters in smaller chunks
- Use dtype conversion to reduce memory
- Consider downsampling for initial analysis

---

## 📋 Checklist for EDA Completion

- [ ] All raster files loaded successfully
- [ ] Boundary shapefile loaded and visualized
- [ ] Landslide inventory CSV processed
- [ ] Statistics calculated for all layers
- [ ] Distribution histograms generated
- [ ] Landslide location map created
- [ ] Correlation matrix computed
- [ ] Data quality report generated
- [ ] All outputs saved to figures/ and data/
- [ ] Summary report reviewed
- [ ] Next steps identified

---

## 📊 Next Steps After EDA

### **1. Data Preprocessing**
- Normalize/standardize raster values
- Handle missing data (interpolation or masking)
- Create training/validation/test splits

### **2. Feature Engineering**
- Create derived features (slope-aspect interactions)
- Calculate terrain indices
- Generate proximity gradient features
- Extract spectral indices from NDVI

### **3. Sample Preparation**
- Generate random negative samples (non-landslide areas)
- Balance positive/negative classes
- Create stratified sampling within slope/aspect zones

### **4. Model Development**
- Build machine learning models (RF, SVM, XGBoost)
- Train deep learning models (CNN, DNN)
- Implement ensemble methods
- Perform hyperparameter tuning

### **5. Validation & Mapping**
- Test on holdout validation set
- Generate susceptibility map
- Calculate accuracy metrics (ROC-AUC, precision, recall)
- Create uncertainty maps

---

## 📚 References

- **Rasterio Documentation**: https://rasterio.readthedocs.io/
- **GeoPandas Documentation**: https://geopandas.org/
- **Scikit-learn**: https://scikit-learn.org/

---

## 👤 Author Notes
- Created for Sindhupalchok District Landslide Susceptibility Project
- Supports semester project coursework
- Extensible framework for future analysis

---

**Last Updated**: 2024
**Status**: Ready for execution
