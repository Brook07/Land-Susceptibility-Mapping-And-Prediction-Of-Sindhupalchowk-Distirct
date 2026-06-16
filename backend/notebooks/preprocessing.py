# %% [markdown]
# # Landslide Susceptibility Mapping - Data Preprocessing
# This notebook handles data loading, raster alignment, vector processing, feature extraction, and data cleaning to produce an ML-ready dataset.

# %%
import os
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.features import rasterize
from shapely.geometry import Point
from scipy.ndimage import distance_transform_edt
from sklearn.impute import SimpleImputer
import warnings

warnings.filterwarnings('ignore')

# Configuration
TARGET_CRS = "EPSG:32645"
DATA_DIR = Path(r"D:\Semester_Projects\6th_sem_project\Land-Susceptibility-Mapping-And-Prediction-Of-Sindhupalchowk-Distirct\backend\data\Raw_Sindhupalchowk_Dataset_Landslide")
OUTPUT_DIR = DATA_DIR.parent / "Processed_Dataset"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Helper Functions

# %%
def find_file(directory, extensions):
    """Find the first file in a directory matching given extensions."""
    for ext in extensions:
        files = list(directory.rglob(f"*{ext}"))
        if files:
            return files[0]
    return None

def align_and_reproject_raster(src_path, dst_path, ref_raster=None):
    """Reproject raster to TARGET_CRS and align to ref_raster if provided."""
    print(f"Processing {src_path.name}...")
    with rasterio.open(src_path) as src:
        if ref_raster is None:
            transform, width, height = calculate_default_transform(
                src.crs, TARGET_CRS, src.width, src.height, *src.bounds
            )
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': TARGET_CRS,
                'transform': transform,
                'width': width,
                'height': height
            })
        else:
            with rasterio.open(ref_raster) as ref:
                transform = ref.transform
                width = ref.width
                height = ref.height
                kwargs = ref.meta.copy()
        
        with rasterio.open(dst_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=TARGET_CRS,
                    resampling=Resampling.nearest
                )
    return dst_path

def create_distance_raster(vector_path, ref_raster_path, out_path):
    """Rasterize vector lines and calculate Euclidean distance."""
    print(f"Creating distance raster for {vector_path.name}...")
    gdf = gpd.read_file(vector_path)
    if gdf.crs != TARGET_CRS:
        gdf = gdf.to_crs(TARGET_CRS)
    
    with rasterio.open(ref_raster_path) as ref:
        meta = ref.meta.copy()
        meta.update(dtype=rasterio.float32, nodata=-9999)
        
        shapes = ((geom, 1) for geom in gdf.geometry)
        burned = rasterize(
            shapes=shapes,
            out_shape=(ref.height, ref.width),
            transform=ref.transform,
            fill=0,
            all_touched=True,
            dtype=rasterio.uint8
        )
        
        inv_burned = 1 - burned
        dist_pixels = distance_transform_edt(inv_burned)
        
        pixel_size = ref.transform[0]
        dist_meters = (dist_pixels * pixel_size).astype(np.float32)
        
        with rasterio.open(out_path, 'w', **meta) as dst:
            dst.write(dist_meters, 1)
            
    return out_path

def generate_negative_samples(boundary_path, num_samples, positive_gdf):
    """Generate random non-landslide points inside the boundary."""
    print(f"Generating {num_samples} non-landslide points...")
    boundary = gpd.read_file(boundary_path)
    if boundary.crs != TARGET_CRS:
        boundary = boundary.to_crs(TARGET_CRS)
    
    poly = boundary.geometry.unary_union
    minx, miny, maxx, maxy = poly.bounds
    
    neg_points = []
    while len(neg_points) < num_samples:
        pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if poly.contains(pnt):
            neg_points.append(pnt)
            
    neg_gdf = gpd.GeoDataFrame(geometry=neg_points, crs=TARGET_CRS)
    neg_gdf['target'] = 0
    return neg_gdf

def extract_raster_values(points_gdf, raster_dict):
    """Extract values from all rasters at given points."""
    print("Extracting raster values for points...")
    coords = [(geom.x, geom.y) for geom in points_gdf.geometry]
    
    df = pd.DataFrame({
        'longitude': [c[0] for c in coords],
        'latitude': [c[1] for c in coords],
        'target': points_gdf['target']
    })
    
    for name, path in raster_dict.items():
        with rasterio.open(path) as src:
            values = list(src.sample(coords))
            df[name] = [v[0] for v in values]
            
            nodata = src.nodata
            if nodata is not None:
                df[name] = df[name].replace(nodata, np.nan)
                
    return df

# %% [markdown]
# ## 1. Identify Raw Files

# %%
dem_raw = find_file(DATA_DIR / "DEM", ['.tif'])
slope_raw = find_file(DATA_DIR / "Slope", ['.tif'])
aspect_raw = find_file(DATA_DIR / "Aspect", ['.tif'])
ndvi_raw = find_file(DATA_DIR / "NDVI", ['.tif'])
twi_raw = find_file(DATA_DIR / "TWI", ['.tif'])
lulc_raw = find_file(DATA_DIR / "LULC", ['.tif'])

inventory_raw = find_file(DATA_DIR / "Landslide_Inventory_Datasets", ['.csv', '.shp'])

vectors_dir = DATA_DIR / "Road And River Networks With Sindupalchok Boundary (shapefiles and gdb)"
boundary_raw = list(vectors_dir.rglob("*boundary*.shp"))[0] if list(vectors_dir.rglob("*boundary*.shp")) else None
roads_raw = list(vectors_dir.rglob("*road*.shp"))[0] if list(vectors_dir.rglob("*road*.shp")) else None
rivers_raw = list(vectors_dir.rglob("*river*.shp"))[0] if list(vectors_dir.rglob("*river*.shp")) else None

if not all([dem_raw, boundary_raw, inventory_raw]):
    raise FileNotFoundError("Could not find required DEM, boundary, or inventory files.")

# %% [markdown]
# ## 2. Align and Reproject Rasters

# %%
aligned_dir = OUTPUT_DIR / "aligned_rasters"
aligned_dir.mkdir(exist_ok=True)

dem_aligned = aligned_dir / "DEM.tif"
align_and_reproject_raster(dem_raw, dem_aligned) # DEM is the reference

rasters_to_align = {
    'slope': slope_raw,
    'aspect': aspect_raw,
    'ndvi': ndvi_raw,
    'twi': twi_raw,
    'lulc': lulc_raw
}

aligned_rasters = {'dem': dem_aligned}
for name, path in rasters_to_align.items():
    if path:
        out_path = aligned_dir / f"{name}.tif"
        aligned_rasters[name] = align_and_reproject_raster(path, out_path, ref_raster=dem_aligned)

# %% [markdown]
# ## 3. Vector Processing (Distance Rasters)

# %%
if roads_raw:
    road_dist_path = aligned_dir / "distance_to_road.tif"
    aligned_rasters['distance_to_road'] = create_distance_raster(roads_raw, dem_aligned, road_dist_path)
    
if rivers_raw:
    river_dist_path = aligned_dir / "distance_to_river.tif"
    aligned_rasters['distance_to_river'] = create_distance_raster(rivers_raw, dem_aligned, river_dist_path)

# %% [markdown]
# ## 4. Handle Rainfall Data

# %%
rainfall_raw = find_file(DATA_DIR / "Rainfall", ['.tif'])
if rainfall_raw:
    rain_aligned = aligned_dir / "rainfall.tif"
    aligned_rasters['rainfall'] = align_and_reproject_raster(rainfall_raw, rain_aligned, ref_raster=dem_aligned)
else:
    print("No rainfall raster found. Skipping rainfall feature for spatial extraction.")

# %% [markdown]
# ## 5. Load Positive Inventory & 6. Generate Negative Inventory

# %%
if inventory_raw.suffix == '.csv':
    df_inv = pd.read_csv(inventory_raw)
    lon_col = next((c for c in df_inv.columns if 'lon' in c.lower()), 'longitude')
    lat_col = next((c for c in df_inv.columns if 'lat' in c.lower()), 'latitude')
    
    geometry = [Point(xy) for xy in zip(df_inv[lon_col], df_inv[lat_col])]
    pos_gdf = gpd.GeoDataFrame(df_inv, geometry=geometry, crs="EPSG:4326")
else:
    pos_gdf = gpd.read_file(inventory_raw)
    
pos_gdf = pos_gdf.to_crs(TARGET_CRS)
pos_gdf['target'] = 1

boundary = gpd.read_file(boundary_raw).to_crs(TARGET_CRS)
pos_gdf = gpd.clip(pos_gdf, boundary)

neg_gdf = generate_negative_samples(boundary_raw, len(pos_gdf), pos_gdf)

all_points = pd.concat([pos_gdf[['geometry', 'target']], neg_gdf[['geometry', 'target']]], ignore_index=True)

# %% [markdown]
# ## 7. Extract Features & 8. Data Cleaning

# %%
dataset_df = extract_raster_values(all_points, aligned_rasters)

print("Cleaning data and imputing missing values...")
X = dataset_df.drop(columns=['latitude', 'longitude', 'target'])

imputer = SimpleImputer(strategy='median')
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

final_df = pd.concat([dataset_df[['latitude', 'longitude']], X_imputed, dataset_df[['target']]], axis=1)

# %% [markdown]
# ## 9. Output Result

# %%
out_csv = OUTPUT_DIR / "ml_ready_dataset.csv"
final_df.to_csv(out_csv, index=False)
print(f"✅ Success! ML-ready dataset saved to: {out_csv}")
print(f"Dataset shape: {final_df.shape}")
print(f"Class balance:\n{final_df['target'].value_counts()}")
