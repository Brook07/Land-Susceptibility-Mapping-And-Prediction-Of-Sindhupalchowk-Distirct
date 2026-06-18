# Landslide Susceptibility Mapping - Data Preprocessing
This notebook handles data loading, raster alignment, vector processing, feature extraction, and data cleaning to produce an ML-ready dataset.

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
os.environ["SHAPE_RESTORE_SHX"] = "YES"\n

# Configuration
TARGET_CRS = "EPSG:32645"
DATA_DIR = Path(r"D:\Semester_Projects\6th_sem_project\Land-Susceptibility-Mapping-And-Prediction-Of-Sindhupalchowk-Distirct\backend\data\Raw_Sindhupalchowk_Dataset_Landslide")
OUTPUT_DIR = DATA_DIR.parent / "Processed_Dataset"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

## Helper Functions

def find_file(directory, extensions):
    """Find the first file in a directory matching given extensions."""
    if directory is None or not directory.exists():
        return None
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
                'height': height,
                'nodata': src.nodata
            })
        else:
            with rasterio.open(ref_raster) as ref:
                transform = ref.transform
                width = ref.width
                height = ref.height
                kwargs = ref.meta.copy()
                kwargs.update({
                    'crs': TARGET_CRS,
                    'transform': transform,
                    'width': width,
                    'height': height
                })

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
        meta.update(dtype=rasterio.float32, count=1, nodata=-9999)

        shapes = ((geom, 1) for geom in gdf.geometry if geom is not None and not geom.is_empty)
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

        pixel_size = abs(ref.transform[0])
        dist_meters = (dist_pixels * pixel_size).astype(np.float32)

        with rasterio.open(out_path, 'w', **meta) as dst:
            dst.write(dist_meters, 1)

    return out_path


def generate_negative_samples(boundary_path, num_samples):
    """Generate random non-landslide points inside the boundary."""
    print(f"Generating {num_samples} non-landslide points...")
    boundary = gpd.read_file(boundary_path)
    if boundary.crs != TARGET_CRS:
        boundary = boundary.to_crs(TARGET_CRS)

    poly = boundary.geometry.unary_union
    minx, miny, maxx, maxy = poly.bounds

    neg_points = []
    attempts = 0
    max_attempts = max(num_samples * 50, 1000)

    while len(neg_points) < num_samples and attempts < max_attempts:
        pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if poly.contains(pnt):
            neg_points.append(pnt)
        attempts += 1

    if len(neg_points) < num_samples:
        raise RuntimeError("Could not generate enough negative samples inside the boundary.")

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
        'target': points_gdf['target'].values
    })

    for name, path in raster_dict.items():
        with rasterio.open(path) as src:
            values = list(src.sample(coords))
            df[name] = [v[0] for v in values]

            nodata = src.nodata
            if nodata is not None:
                df[name] = df[name].replace(nodata, np.nan)

    return df

## 1. Identify Raw Files

dem_raw = find_file(DATA_DIR / "DEM", ['.tif'])
slope_raw = find_file(DATA_DIR / "Slope", ['.tif']) or find_file(DATA_DIR / "DEM", ['.tif'])
aspect_raw = find_file(DATA_DIR / "Aspect", ['.tif']) or find_file(DATA_DIR / "DEM", ['.tif'])
ndvi_raw = find_file(DATA_DIR / "NDVI", ['.tif'])
twi_raw = find_file(DATA_DIR / "TWI", ['.tif'])
lulc_raw = find_file(DATA_DIR / "LU_LC", ['.tif', '.tiff']) or find_file(DATA_DIR / "LULC", ['.tif', '.tiff'])
elevation_raw = find_file(DATA_DIR / "Elevation", ['.tif'])

inventory_raw = find_file(DATA_DIR / "Inventory Datasets", ['.csv', '.shp']) or find_file(DATA_DIR / "Landslide_Inventory_Datasets", ['.csv', '.shp'])
rainfall_raw = find_file(DATA_DIR / "Rainfall", ['.csv', '.xlsx', '.xls', '.tif', '.tiff'])

vectors_dir = DATA_DIR / "Road And River Networks With Sindupalchok Boundary (shapefiles and gdb)"
boundary_candidates = list(vectors_dir.rglob("*boundary*.shp")) if vectors_dir.exists() else []
roads_candidates = list(vectors_dir.rglob("*road*.shp")) if vectors_dir.exists() else []
rivers_candidates = list(vectors_dir.rglob("*river*.shp")) if vectors_dir.exists() else []

boundary_raw = boundary_candidates[0] if boundary_candidates else find_file(DATA_DIR / "Boundary", ['.shp'])
roads_raw = roads_candidates[0] if roads_candidates else None
rivers_raw = rivers_candidates[0] if rivers_candidates else None

required_inputs = [dem_raw, boundary_raw, inventory_raw]
if not all(required_inputs):
    raise FileNotFoundError("Could not find required DEM, boundary, or inventory files in the dataset folder.")

## 2. Align and Reproject Rasters

aligned_dir = OUTPUT_DIR / "aligned_rasters"
aligned_dir.mkdir(exist_ok=True)

# DEM is the reference grid for all raster alignment.
dem_aligned = aligned_dir / "DEM.tif"
align_and_reproject_raster(dem_raw, dem_aligned)

rasters_to_align = {
    'slope': slope_raw,
    'aspect': aspect_raw,
    'ndvi': ndvi_raw,
    'twi': twi_raw,
    'lulc': lulc_raw,
    'elevation': elevation_raw,
}

aligned_rasters = {'dem': dem_aligned}
for name, path in rasters_to_align.items():
    if path:
        out_path = aligned_dir / f"{name}.tif"
        aligned_rasters[name] = align_and_reproject_raster(path, out_path, ref_raster=dem_aligned)

## 3. Vector Processing (Distance Rasters)

if roads_raw:
    road_dist_path = aligned_dir / "distance_to_road.tif"
    aligned_rasters['distance_to_road'] = create_distance_raster(roads_raw, dem_aligned, road_dist_path)

if rivers_raw:
    river_dist_path = aligned_dir / "distance_to_river.tif"
    aligned_rasters['distance_to_river'] = create_distance_raster(rivers_raw, dem_aligned, river_dist_path)

## 4. Handle Rainfall Data

def load_rainfall_time_series(rainfall_path):
    """Load rainfall time series from CSV/XLSX and prepare month-day climatology."""
    if rainfall_path is None:
        return None, None, None

    suffix = rainfall_path.suffix.lower()
    if suffix in ['.csv']:
        rainfall_df = pd.read_csv(rainfall_path)
    elif suffix in ['.xlsx', '.xls']:
        rainfall_df = pd.read_excel(rainfall_path)
    else:
        raise ValueError("Rainfall file must be CSV/XLSX for temporal rainfall mode.")

    date_candidates = [c for c in rainfall_df.columns if 'date' in c.lower()]
    rain_candidates = [c for c in rainfall_df.columns if 'rain' in c.lower()]

    date_col = date_candidates[0] if date_candidates else None
    rain_col = rain_candidates[0] if rain_candidates else None

    if date_col is None or rain_col is None:
        raise ValueError("Rainfall table must have date and rainfall columns.")

    rainfall_df = rainfall_df[[date_col, rain_col]].copy()
    rainfall_df.columns = ['date', 'rainfall']
    rainfall_df['date'] = pd.to_datetime(rainfall_df['date'], errors='coerce')
    rainfall_df['rainfall'] = pd.to_numeric(rainfall_df['rainfall'], errors='coerce')
    rainfall_df = rainfall_df.dropna(subset=['date', 'rainfall'])

    rainfall_df['month'] = rainfall_df['date'].dt.month
    rainfall_df['day'] = rainfall_df['date'].dt.day

    climatology = rainfall_df.groupby(['month', 'day'])['rainfall'].mean()
    default_value = float(rainfall_df['rainfall'].median())

    return rainfall_df, climatology, default_value


def assign_rainfall_from_event_dates(event_dates, climatology, default_value):
    """Assign rainfall using month-day climatology from event dates."""
    values = []
    for dt in pd.to_datetime(event_dates, errors='coerce'):
        if pd.isna(dt):
            values.append(default_value)
            continue
        values.append(float(climatology.get((dt.month, dt.day), default_value)))
    return np.array(values, dtype=np.float32)


rainfall_mode = None
rainfall_climatology = None
rainfall_default_value = None
rainfall_raw = find_file(DATA_DIR / "Rainfall", ['.csv', '.xlsx', '.xls', '.tif', '.tiff'])

if rainfall_raw:
    if rainfall_raw.suffix.lower() in ['.tif', '.tiff']:
        rain_aligned = aligned_dir / "rainfall.tif"
        aligned_rasters['rainfall'] = align_and_reproject_raster(rainfall_raw, rain_aligned, ref_raster=dem_aligned)
        rainfall_mode = 'spatial_raster'
        print("Rainfall mode: spatial raster")
    else:
        _, rainfall_climatology, rainfall_default_value = load_rainfall_time_series(rainfall_raw)
        rainfall_mode = 'temporal_timeseries'
        print("Rainfall mode: temporal time series (event-date climatology)")
else:
    print("No rainfall file found. Skipping rainfall feature.")
## 5. Load Positive Inventory & 6. Generate Negative Inventory

def parse_inventory_date(value):
    """Parse mixed inventory date formats like 5/3/015, 12/04/014, 3/8/04."""
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()
    parts = text.split('/')
    if len(parts) == 3:
        m, d, y = parts
        m = m.zfill(2)
        d = d.zfill(2)
        y = y.strip()

        if y.isdigit():
            if len(y) == 3:
                y = f"2{y}"  # 015 -> 2015
            elif len(y) == 2:
                y_int = int(y)
                y = f"20{y}" if y_int <= 30 else f"19{y}"

        normalized = f"{m}/{d}/{y}"
        parsed = pd.to_datetime(normalized, format='%m/%d/%Y', errors='coerce')
        if not pd.isna(parsed):
            return parsed

    return pd.to_datetime(text, errors='coerce')


if inventory_raw.suffix.lower() == '.csv':
    df_inv = pd.read_csv(inventory_raw)
    lon_col = next((c for c in df_inv.columns if 'lon' in c.lower()), 'longitude')
    lat_col = next((c for c in df_inv.columns if 'lat' in c.lower()), 'latitude')

    date_candidates = [c for c in df_inv.columns if 'date' in c.lower()]
    if 'Name' in df_inv.columns:
        date_candidates = ['Name'] + date_candidates
    date_col = date_candidates[0] if date_candidates else None

    geometry = [Point(xy) for xy in zip(df_inv[lon_col], df_inv[lat_col])]
    pos_gdf = gpd.GeoDataFrame(df_inv, geometry=geometry, crs="EPSG:4326")

    if date_col is not None:
        pos_gdf['event_date'] = pos_gdf[date_col].apply(parse_inventory_date)
    else:
        pos_gdf['event_date'] = pd.NaT
else:
    pos_gdf = gpd.read_file(inventory_raw)
    if 'event_date' in pos_gdf.columns:
        pos_gdf['event_date'] = pd.to_datetime(pos_gdf['event_date'], errors='coerce')
    elif 'date' in [c.lower() for c in pos_gdf.columns]:
        exact_date_col = next((c for c in pos_gdf.columns if c.lower() == 'date'), None)
        pos_gdf['event_date'] = pd.to_datetime(pos_gdf[exact_date_col], errors='coerce')
    elif 'Name' in pos_gdf.columns:
        pos_gdf['event_date'] = pos_gdf['Name'].apply(parse_inventory_date)
    else:
        pos_gdf['event_date'] = pd.NaT

pos_gdf = pos_gdf[pos_gdf.geometry.notnull()].copy()
pos_gdf = pos_gdf[~pos_gdf.geometry.is_empty].copy()
pos_gdf = pos_gdf.to_crs(TARGET_CRS)
pos_gdf['target'] = 1

boundary = gpd.read_file(boundary_raw)
if boundary.crs != TARGET_CRS:
    boundary = boundary.to_crs(TARGET_CRS)

boundary = boundary[boundary.geometry.notnull()].copy()
boundary = boundary[~boundary.geometry.is_empty].copy()

pos_gdf = gpd.clip(pos_gdf, boundary)
neg_gdf = generate_negative_samples(boundary_raw, len(pos_gdf))

# Keep landslide inventory points and assign synthetic event dates to negatives
# sampled from positives to avoid target leakage by date.
pos_valid_dates = pos_gdf['event_date'].dropna()
if len(pos_valid_dates) > 0:
    neg_gdf['event_date'] = np.random.choice(pos_valid_dates.to_numpy(), size=len(neg_gdf), replace=True)
else:
    neg_gdf['event_date'] = pd.NaT

all_points = pd.concat([
    pos_gdf[['geometry', 'target', 'event_date']],
    neg_gdf[['geometry', 'target', 'event_date']]
], ignore_index=True)

print(f"Positive inventory points kept: {len(pos_gdf)}")
print(f"Negative points generated: {len(neg_gdf)}")
print(f"Positive points with parsed event dates: {pos_gdf['event_date'].notna().sum()}/{len(pos_gdf)}")
## 7. Extract Features & 8. Data Cleaning

dataset_df = extract_raster_values(all_points, aligned_rasters)

# Add rainfall feature depending on the rainfall mode.
if rainfall_mode == 'temporal_timeseries':
    dataset_df['rainfall'] = assign_rainfall_from_event_dates(
        all_points['event_date'],
        rainfall_climatology,
        rainfall_default_value
    )
elif rainfall_mode == 'spatial_raster':
    # Rainfall is already sampled from aligned raster by extract_raster_values.
    pass
else:
    # If rainfall is unavailable, keep a placeholder for consistent schema.
    dataset_df['rainfall'] = np.nan

print("Cleaning data and imputing missing values...")
feature_columns = [col for col in dataset_df.columns if col not in ['latitude', 'longitude', 'target']]
X = dataset_df[feature_columns]

imputer = SimpleImputer(strategy='median')
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=feature_columns)

final_df = pd.concat([
    dataset_df[['latitude', 'longitude']].reset_index(drop=True),
    X_imputed.reset_index(drop=True),
    dataset_df[['target']].reset_index(drop=True)
], axis=1)

final_df = final_df.dropna(subset=['latitude', 'longitude', 'target'])

if 'rainfall' in final_df.columns:
    print(f"Rainfall unique values: {final_df['rainfall'].nunique()}")
    print(final_df['rainfall'].describe())
## 9. Output Result

out_csv = OUTPUT_DIR / "ml_ready_dataset.csv"
final_df.to_csv(out_csv, index=False)
print(f"Success! ML-ready dataset saved to: {out_csv}")
print(f"Dataset shape: {final_df.shape}")
print(f"Class balance:\n{final_df['target'].value_counts()}")
