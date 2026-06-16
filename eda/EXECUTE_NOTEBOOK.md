# Notebook Execution Instructions

## Issues Fixed

✓ **Path Handling**: Updated to use `os.path.join()` for cross-platform compatibility  
✓ **Raster Loading**: Added error handling and file existence checks  
✓ **Data Validation**: Added checks in visualization cells to verify data exists  
✓ **Directory Creation**: Automatically creates output directories  

## How to Execute

### Step 1: Select the Correct Kernel
1. Open `01_eda_analysis.ipynb` in VS Code
2. Click the kernel selector (top right)
3. Select: **Python (geospatial)**

### Step 2: Run All Cells Sequentially
**Option A (Recommended):**
- Press `Ctrl+Home` to go to first cell
- Press `Ctrl+Shift+Enter` to run all cells sequentially

**Option B (Manual):**
- Click each cell and press `Ctrl+Enter` to run one at a time
- Wait for each cell to complete before moving to next

### Step 3: Expected Runtime
- **Total time**: 5-8 minutes
- **Critical sections**:
  - Section 1 (Setup): < 1 sec
  - Section 4 (Load Rasters): 2-3 minutes (largest files)
  - Section 5 (Visualize Rasters): 1-2 minutes
  - Sections 6-11: < 2 minutes total

## Output Files

### Figures (PNG, 300 DPI)
- `figures/02_all_rasters_visualization.png` - 3x3 grid of all raster layers
- `figures/03_landslide_locations.png` - Map of landslide points
- `figures/04_raster_distributions.png` - Histograms of raster values

### Data Files (CSV/TXT)
- `data/data_quality_report.csv` - Data completeness statistics
- `data/raster_statistics.csv` - Min/max/mean/std for each layer

## Troubleshooting

### Error: "No raster data loaded"
**Solution**: Make sure Section 4 ran successfully. Check output for file not found errors.

### Error: "FileNotFoundError" in Section 4
**Reason**: Data files not at expected path
**Solution**: Verify files exist at: `d:\sindupalchok_landslide\data\processed\rasters\`

### Kernel Won't Start
**Solution**:
1. Open terminal in VS Code
2. Run: `conda activate geospatial`
3. Run: `jupyter kernelspec list`
4. Verify 'geospatial' kernel is listed

### Blank Notebook Display
**Solution**:
1. Close the notebook
2. Press `Ctrl+Shift+P` and search for "Jupyter: Reload Window"
3. Reopen the notebook

## Quick Checklist

- [ ] Geospatial kernel selected
- [ ] All 9 TIF files exist in `rasters/` folder
- [ ] Landslide CSV exists in `landslide_inventory/` folder
- [ ] Shapefile exists in `shapefiles/` folder
- [ ] `figures/` directory exists (will be auto-created)
- [ ] `data/` directory exists (will be auto-created)
- [ ] Run all cells sequentially from top to bottom
- [ ] Wait for "EDA ANALYSIS COMPLETE" message

## Next Steps After Execution

1. **Review Outputs**: Check generated figures and statistics
2. **Analyze Results**: Examine value ranges and distributions
3. **Data Quality**: Review completeness report
4. **Next Phase**: Proceed to feature engineering or modeling
