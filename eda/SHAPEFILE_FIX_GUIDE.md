# Shapefile Missing Components - Fix Guide

## Problem Identified

The boundary shapefile is incomplete:
- **Found**: `sindhupalchok_boundary.shp` (59 KB)
- **Missing**: `.shx`, `.dbf`, `.prj` files

Shapefiles require **ALL** companion files to work properly:
- `.shp` - Main file with geometry
- `.shx` - Shape index (tells GIS where each record is)
- `.dbf` - Attribute database (properties like name, area, etc.)
- `.prj` - Projection info (coordinate system)

## Solutions

### Option 1: Use Raster Data Only (RECOMMENDED)
The notebook now automatically **skips the boundary** if it's missing. All raster analysis will work fine:
- ✓ Load and visualize all 9 raster layers
- ✓ Generate distribution histograms
- ✓ Calculate data quality statistics
- ✗ Won't show boundary map (not critical for EDA)

**No action needed** - notebook adapted to handle missing boundary.

---

### Option 2: Find Complete Shapefile
If you have the complete shapefile elsewhere:
1. Find all 4 files: `.shp`, `.shx`, `.dbf`, `.prj`
2. Copy them to: `d:\sindupalchok_landslide\data\processed\shapefiles\`
3. Restart notebook kernel
4. Re-run cells 2-3

**Where to look**:
- Original project source/data folder
- GIS database or file server
- Online data repository (if project sourced from public data)

---

### Option 3: Recreate Missing Files (Advanced)
If you only have the `.shp` file, use Python/GDAL:

```python
import subprocess
import os

shp_path = r'd:\sindupalchok_landslide\data\processed\shapefiles\sindhupalchok_boundary.shp'

# Use ogrinfo to rebuild index
os.chdir(os.path.dirname(shp_path))
subprocess.run(['ogrinfo', 'sindhupalchok_boundary.shp'], capture_output=True)

# This may regenerate missing files
```

**Note**: Only works if `.shp` contains valid geometry data.

---

### Option 4: Extract Boundary from Raster Data (Workaround)
If boundary is essential, create it from raster extent:

```python
import rasterio
import geopandas as gpd
from shapely.geometry import box

# Get extent from first raster
with rasterio.open('path_to_raster.tif') as src:
    bounds = src.bounds  # (left, bottom, right, top)
    
# Create boundary polygon
from_raster = gpd.GeoDataFrame(
    {'name': ['study_area']},
    geometry=[box(*bounds)],
    crs=src.crs
)

# Save as shapefile
from_raster.to_file('recreated_boundary.shp')
```

---

## Current Notebook Status

✓ **Adapted to handle missing boundary gracefully**
- Attempts to load shapefile
- If fails: logs error and continues
- All raster analysis proceeds normally
- Skips boundary visualization only

## Next Steps

1. **Run notebook as-is**: Full EDA will complete without boundary map
2. **Check project source**: Look for complete shapefile
3. **If found**: Copy files and re-run cells 2-3

## Files Needed

All in: `d:\sindupalchok_landslide\data\processed\shapefiles\`

| File | Size | Status |
|------|------|--------|
| sindhupalchok_boundary.shp | 59 KB | ✓ Found |
| sindhupalchok_boundary.shx | ? | ✗ Missing |
| sindhupalchok_boundary.dbf | ? | ✗ Missing |
| sindhupalchok_boundary.prj | ? | ✗ Missing |
