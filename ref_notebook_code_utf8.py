# Install only missing packages (fast re-runs)
import importlib.util
import subprocess
import sys

# pip package name -> import module name
package_module_pairs = [
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("geopandas", "geopandas"),
    ("rasterio", "rasterio"),
    ("shapely", "shapely"),
    ("pyproj", "pyproj"),
    ("fiona", "fiona"),
    ("scipy", "scipy"),
    ("scikit-learn", "sklearn"),
    ("matplotlib", "matplotlib"),
    ("joblib", "joblib"),
    ("localtileserver", "localtileserver"),
    ("folium", "folium"),
    ("flask", "flask"),
]

def is_installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None

missing = [
    pip_name
    for pip_name, module_name in package_module_pairs
    if not is_installed(module_name)
]
print("Missing packages:", missing)

if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])
else:
    print("All required packages are already installed.")

---CELL---

# Install core GIS + ML dependencies (run once)
import sys
import subprocess

packages = [
    "numpy",
    "pandas",
    "geopandas",
    "rasterio",
    "shapely",
    "pyproj",
    "fiona",
    "scipy",
    "scikit-learn",
    "matplotlib",
    "joblib",
    "localtileserver",
    "folium",
]

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *packages])

---CELL---

from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

# Base project paths: keep all generated artifacts inside backend/
PROJECT_ROOT = Path(r"D:/Side_Projects/ai-ml/GeoShield_Ecothon/backend")
DATASET_ROOT = PROJECT_ROOT / "data" / "Sindhupalchowk_Dataset_Landslide"

RAW_RASTER_DIR = PROJECT_ROOT / "data" / "raw" / "raster"
RAW_VECTOR_DIR = PROJECT_ROOT / "data" / "raw" / "vector"
RAW_INVENTORY_DIR = PROJECT_ROOT / "data" / "raw" / "inventory"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"

for p in [RAW_RASTER_DIR, RAW_VECTOR_DIR, RAW_INVENTORY_DIR, PROCESSED_DIR, OUTPUTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

DATASET_ROOT

---CELL---

# Raster layers (updated to match your current file names)
raster_paths = {
    "dem": DATASET_ROOT / "DEM" / "Sindhupalchok_DEM.tif",
    "slope": DATASET_ROOT / "Slope" / "Sindhupalchok_Slope.tif",
    "aspect": DATASET_ROOT / "Aspect" / "Sindhupalchok_Aspect.tif",
    "twi": DATASET_ROOT / "TWI" / "Sindhupalchok_TWI_2025.tif",
    # Rainfall raster now available
    "rainfall": DATASET_ROOT / "Rainfall" / "Sindhupalchok_Rainfall_2015_2025.tif",
    "ndvi": DATASET_ROOT / "NDVI" / "Sindhupalchok_NDVI_2025_30m.tif",
    "landcover": DATASET_ROOT / "LULC" / "Sindhupalchok_LULC_30m.tif",
    "river_proximity": DATASET_ROOT / "RiverProximity" / "Sindhupalchok_RiverProximity.tif",
}

# Vector layers
vector_paths = {
    "boundary": DATASET_ROOT / "Road and River Networks with Sindhupalchowk Boundary (shapefiles and gdb)" / "processed_data" / "sindhupalchok_boundary_utm.shp",
    "roads": DATASET_ROOT / "Road and River Networks with Sindhupalchowk Boundary (shapefiles and gdb)" / "processed_data" / "roads_sindhupalchok.shp",
    "rivers": DATASET_ROOT / "Road and River Networks with Sindhupalchowk Boundary (shapefiles and gdb)" / "processed_data" / "rivers_sindhupalchok.shp",
}

# Landslide inventory (CSV with lat/lon)
inventory_path = DATASET_ROOT / "Landslide_Inventory_Datasets" / "sindhupalchowk_landslides.csv"

# Optional rainfall CSVs (used only if raster is missing and CSV has lat/lon/value)
rainfall_csv_paths = [
    DATASET_ROOT / "Rainfall" / "GeoShield_Rainfall_Timeline_2015_2025.csv",
    DATASET_ROOT / "Rainfall" / "Sindhupalchok_CHIRPS_2020.csv",
]

raster_paths, vector_paths, inventory_path, rainfall_csv_paths

---CELL---

# Convert rainfall CSV(s) to a raster using DEM grid (only if raster is missing)
from typing import List, Tuple
from scipy.interpolate import griddata

def detect_columns(df: pd.DataFrame) -> Tuple[str, str, str]:
    lower = {c.lower(): c for c in df.columns}
    lat_col = next((lower[c] for c in lower if "lat" in c), None)
    lon_col = next((lower[c] for c in lower if "lon" in c or "long" in c), None)
    val_col = next((lower[c] for c in lower if "rain" in c or "precip" in c or "chirps" in c), None)
    if not (lat_col and lon_col and val_col):
        raise ValueError(f"Could not detect columns. Available: {list(df.columns)}")
    return lat_col, lon_col, val_col

def rainfall_csv_to_raster(csv_paths: List[Path], ref_raster: Path, out_path: Path) -> Path:
    dfs = []
    for p in csv_paths:
        if p.exists():
            dfs.append(pd.read_csv(p))
    if not dfs:
        raise FileNotFoundError("No rainfall CSV files found.")
    df = pd.concat(dfs, ignore_index=True)
    lat_col, lon_col, val_col = detect_columns(df)
    df = df[[lat_col, lon_col, val_col]].dropna()

    with rasterio.open(ref_raster) as ref:
        transform = ref.transform
        width, height = ref.width, ref.height
        crs = ref.crs
        # Build grid of pixel centers
        xs = np.arange(width) + 0.5
        ys = np.arange(height) + 0.5
        xs, ys = np.meshgrid(xs, ys)
        lon, lat = rasterio.transform.xy(transform, ys, xs)
        lon = np.array(lon)
        lat = np.array(lat)

    points = np.column_stack([df[lon_col].values, df[lat_col].values])
    values = df[val_col].values.astype("float32")

    # Nearest interpolation fills gaps and keeps it fast for hackathon demos
    grid = griddata(points, values, (lon, lat), method="nearest")
    grid = grid.astype("float32")

    out_meta = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": None,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(grid, 1)

    print("Rainfall raster created:", out_path)
    return out_path

# Build rainfall raster only if missing
if not raster_paths["rainfall"].exists():
    raster_paths["rainfall"] = rainfall_csv_to_raster(
        rainfall_csv_paths,
        raster_paths["dem"],
        PROJECT_ROOT / "data" / "raw" / "raster" / "rainfall_from_csv.tif",
    )
else:
    print("Rainfall raster found:", raster_paths["rainfall"])

raster_paths["rainfall"]

---CELL---

def read_raster_info(path: Path):
    if not path.exists():
        return {"path": str(path), "exists": False}
    with rasterio.open(path) as src:
        return {
            "path": str(path),
            "exists": True,
            "crs": src.crs.to_string() if src.crs else None,
            "resolution": src.res,
            "shape": (src.height, src.width),
            "bounds": src.bounds,
            "nodata": src.nodata,
        }

raster_meta = {name: read_raster_info(path) for name, path in raster_paths.items()}
pd.DataFrame(raster_meta).T

---CELL---

def read_vector_info(path: Path):
    if not path.exists():
        return {"path": str(path), "exists": False}
    gdf = gpd.read_file(path)
    return {
        "path": str(path),
        "exists": True,
        "crs": gdf.crs.to_string() if gdf.crs else None,
        "features": len(gdf),
        "bounds": gdf.total_bounds
    }

vector_meta = {name: read_vector_info(path) for name, path in vector_paths.items()}
pd.DataFrame(vector_meta).T

---CELL---

if inventory_path.exists():
    inventory_df = pd.read_csv(inventory_path)
    display(inventory_df.head())
    display(inventory_df.isna().sum())
else:
    inventory_df = pd.DataFrame()
    print("Inventory file not found. Check inventory_path.")

inventory_df.shape

---CELL---

TARGET_CRS = "EPSG:4326"

def needs_reprojection(crs_str: str | None):
    if not crs_str:
        return True
    return crs_str.upper() != TARGET_CRS

raster_reproject_flags = {name: needs_reprojection(meta.get("crs")) for name, meta in raster_meta.items()}
vector_reproject_flags = {name: needs_reprojection(meta.get("crs")) for name, meta in vector_meta.items()}

pd.DataFrame({"raster": raster_reproject_flags, "vector": vector_reproject_flags})

---CELL---

# Additional imports for geospatial processing and ML
import shutil
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from rasterio import features
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.transform import Affine
from rasterio.warp import calculate_default_transform, reproject
from shapely.geometry import Point
from scipy.ndimage import distance_transform_edt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib

# Subfolders for processed outputs
PROCESSED_RASTER_DIR = PROCESSED_DIR / "rasters"
PROCESSED_VECTOR_DIR = PROCESSED_DIR / "vectors"
PROCESSED_INVENTORY_DIR = PROCESSED_DIR / "inventory"
OUTPUT_FIG_DIR = OUTPUTS_DIR / "figures"

for p in [PROCESSED_RASTER_DIR, PROCESSED_VECTOR_DIR, PROCESSED_INVENTORY_DIR, OUTPUT_FIG_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Helper functions
# ----------------------------
def print_raster_info(path: Path, label: str) -> Dict:
    """Print and return basic raster metadata and missing-value stats."""
    info = {"label": label, "path": str(path), "exists": path.exists()}
    if not path.exists():
        print(info)
        return info
    with rasterio.open(path) as src:
        data = src.read(1, masked=True)
        nodata_count = int(np.ma.count_masked(data))
        nan_count = int(np.isnan(data.filled(np.nan)).sum())
        info.update({
            "crs": src.crs.to_string() if src.crs else None,
            "resolution": src.res,
            "shape": (src.height, src.width),
            "bounds": src.bounds,
            "nodata": src.nodata,
            "nodata_count": nodata_count,
            "nan_count": nan_count,
        })
    print(info)
    return info

def print_vector_info(path: Path, label: str) -> Dict:
    """Print and return basic vector metadata."""
    info = {"label": label, "path": str(path), "exists": path.exists()}
    if not path.exists():
        print(info)
        return info
    gdf = gpd.read_file(path)
    info.update({
        "crs": gdf.crs.to_string() if gdf.crs else None,
        "features": len(gdf),
        "bounds": gdf.total_bounds.tolist(),
    })
    print(info)
    return info

def reproject_raster(in_path: Path, out_path: Path, target_crs: str) -> Path:
    """Reproject a raster to the target CRS. Copies if already in target."""
    if not in_path.exists():
        raise FileNotFoundError(in_path)
    with rasterio.open(in_path) as src:
        src_crs = src.crs.to_string() if src.crs else None
        if src_crs and src_crs.upper() == target_crs.upper():
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(in_path, out_path)
            return out_path
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height,
        })
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(out_path, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.bilinear,
                )
    return out_path

def reproject_vector(in_path: Path, out_path: Path, target_crs: str) -> Path:
    """Reproject a vector layer to the target CRS."""
    if not in_path.exists():
        raise FileNotFoundError(in_path)
    gdf = gpd.read_file(in_path)
    gdf = gdf.to_crs(target_crs)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_path)
    return out_path

def clip_raster(in_path: Path, out_path: Path, boundary_gdf: gpd.GeoDataFrame) -> Path:
    """Clip raster to the boundary polygon."""
    with rasterio.open(in_path) as src:
        geom = [boundary_gdf.unary_union]
        out_image, out_transform = mask(src, geom, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(out_image)
    return out_path

def clip_vector(in_path: Path, out_path: Path, boundary_gdf: gpd.GeoDataFrame) -> Path:
    """Clip vector to the boundary polygon."""
    gdf = gpd.read_file(in_path)
    clipped = gpd.clip(gdf, boundary_gdf)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    clipped.to_file(out_path)
    return out_path

def align_raster_to_ref(in_path: Path, out_path: Path, ref_path: Path, resampling: Resampling) -> Path:
    """Resample and align a raster to a reference raster grid."""
    with rasterio.open(ref_path) as ref:
        ref_meta = ref.meta.copy()
    with rasterio.open(in_path) as src:
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": ref_meta["crs"],
            "transform": ref_meta["transform"],
            "width": ref_meta["width"],
            "height": ref_meta["height"],
        })
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(out_path, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=ref_meta["transform"],
                    dst_crs=ref_meta["crs"],
                    resampling=resampling,
                )
    return out_path

def rasterize_distance(vector_path: Path, ref_path: Path, out_path: Path) -> Path:
    """Create a distance-to-feature raster using a reference raster grid."""
    with rasterio.open(ref_path) as ref:
        ref_meta = ref.meta.copy()
        transform = ref.transform
        height, width = ref.height, ref.width
        pixel_size = (abs(transform.a), abs(transform.e))
    gdf = gpd.read_file(vector_path)
    shapes = [(geom, 1) for geom in gdf.geometry if geom is not None]
    raster = features.rasterize(
        shapes=shapes,
        out_shape=(height, width),
        transform=transform,
        fill=0,
        dtype="uint8",
    )
    # Distance transform: distance from each pixel to nearest feature
    distance = distance_transform_edt(raster == 0, sampling=pixel_size).astype("float32")
    out_meta = ref_meta.copy()
    out_meta.update({"count": 1, "dtype": "float32", "nodata": None})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(distance, 1)
    return out_path

def stack_rasters(raster_list: List[Path], out_path: Path) -> Path:
    """Stack aligned rasters into a single multi-band raster."""
    with rasterio.open(raster_list[0]) as ref:
        meta = ref.meta.copy()
        meta.update({"count": len(raster_list)})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **meta) as dst:
        for idx, path in enumerate(raster_list, start=1):
            with rasterio.open(path) as src:
                dst.write(src.read(1), idx)
    return out_path

def generate_random_points(boundary_gdf: gpd.GeoDataFrame, n_points: int, seed: int = 42) -> gpd.GeoDataFrame:
    """Generate random points inside the boundary polygon."""
    rng = np.random.default_rng(seed)
    minx, miny, maxx, maxy = boundary_gdf.total_bounds
    points = []
    while len(points) < n_points:
        x = rng.uniform(minx, maxx)
        y = rng.uniform(miny, maxy)
        pt = Point(x, y)
        if boundary_gdf.contains(pt).any():
            points.append(pt)
    return gpd.GeoDataFrame({"geometry": points}, crs=boundary_gdf.crs)

def extract_stack_values(stack_path: Path, points_gdf: gpd.GeoDataFrame, band_names: List[str]) -> pd.DataFrame:
    """Extract stack raster values at point locations.

    This function is defensive: it validates geometries, uses centroids
    when necessary, and returns a numeric DataFrame with the provided
    band names. Ensures the returned object is a proper `pd.DataFrame`
    (avoids tuple/None typing that Pylance warns about).
    """
    coords: List[Tuple[float, float]] = []
    for geom in points_gdf.geometry:
        if geom is None:
            # insert a NaN coordinate pair (will produce NaN values later)
            coords.append((float("nan"), float("nan")))
            continue
        # Prefer Point.x/.y when available; otherwise fall back to centroid
        if hasattr(geom, "x") and hasattr(geom, "y"):
            coords.append((float(geom.x), float(geom.y)))
        else:
            c = geom.centroid
            coords.append((float(c.x), float(c.y)))

    with rasterio.open(stack_path) as src:
        samples = [s for s in src.sample(coords)]

    # Ensure a numeric ndarray (this avoids tuple typing issues)
    data = np.asarray(samples, dtype="float32")
    # If sample returns 1D rows for single-band stacks, reshape accordingly
    if data.ndim == 1:
        data = data.reshape(-1, len(band_names))

    df = pd.DataFrame(data, columns=band_names)
    return df

---CELL---

# --- Step 1: CRS reprojection (target EPSG:4326) ---
reprojected_rasters = {}
reprojected_vectors = {}

# Reproject rasters if they exist; skip missing layers
for name, path in raster_paths.items():
    if not path.exists():
        print(f"Skipping missing raster: {name} -> {path}")
        continue
    out_path = PROCESSED_RASTER_DIR / "reprojected" / f"{name}_epsg4326.tif"
    reprojected_rasters[name] = reproject_raster(path, out_path, TARGET_CRS)
    print_raster_info(reprojected_rasters[name], f"reprojected_{name}")

# Reproject vectors if files exist (roads are optional)
for name, path in vector_paths.items():
    if not path.exists():
        print(f"Skipping missing vector: {name} -> {path}")
        continue
    out_path = PROCESSED_VECTOR_DIR / "reprojected" / f"{name}_epsg4326.shp"
    reprojected_vectors[name] = reproject_vector(path, out_path, TARGET_CRS)
    print_vector_info(reprojected_vectors[name], f"reprojected_{name}")

# --- Step 2: Clip to district boundary ---
if "boundary" not in reprojected_vectors:
    raise FileNotFoundError("Boundary vector not found in reprojected vectors; cannot clip datasets.")

boundary_path = reprojected_vectors["boundary"]
boundary_gdf = gpd.read_file(boundary_path)

clipped_rasters = {}
for name, path in reprojected_rasters.items():
    out_path = PROCESSED_RASTER_DIR / "clipped" / f"{name}_clip.tif"
    clipped_rasters[name] = clip_raster(path, out_path, boundary_gdf)
    print_raster_info(clipped_rasters[name], f"clipped_{name}")

clipped_vectors = {}
for name, path in reprojected_vectors.items():
    if name == "boundary":
        clipped_vectors[name] = path
        continue
    out_path = PROCESSED_VECTOR_DIR / "clipped" / f"{name}_clip.shp"
    clipped_vectors[name] = clip_vector(path, out_path, boundary_gdf)
    print_vector_info(clipped_vectors[name], f"clipped_{name}")

# --- Step 3: Align rasters to DEM grid ---
if "dem" not in clipped_rasters:
    raise FileNotFoundError("DEM not found in clipped rasters; alignment requires a reference DEM.")

ref_raster = clipped_rasters["dem"]
aligned_rasters = {}

resampling_map = {
    "landcover": Resampling.nearest,
}

for name, path in clipped_rasters.items():
    out_path = PROCESSED_RASTER_DIR / "aligned" / f"{name}_aligned.tif"
    method = resampling_map.get(name, Resampling.bilinear)
    aligned_rasters[name] = align_raster_to_ref(path, out_path, ref_raster, method)
    print_raster_info(aligned_rasters[name], f"aligned_{name}")

# --- Step 4: Distance rasters for roads and rivers ---
road_distance_path = None
river_distance_path = None

if "roads" in clipped_vectors:
    road_distance_path = PROCESSED_RASTER_DIR / "aligned" / "road_distance.tif"
    road_distance_path = rasterize_distance(clipped_vectors["roads"], ref_raster, road_distance_path)
    print_raster_info(road_distance_path, "road_distance")
else:
    print("Roads missing -> skipping road distance raster.")

if "river_proximity" in aligned_rasters:
    river_distance_path = aligned_rasters["river_proximity"]
    print_raster_info(river_distance_path, "river_proximity")
elif "rivers" in clipped_vectors:
    river_distance_path = PROCESSED_RASTER_DIR / "aligned" / "river_distance.tif"
    river_distance_path = rasterize_distance(clipped_vectors["rivers"], ref_raster, river_distance_path)
    print_raster_info(river_distance_path, "river_distance")
else:
    print("Rivers missing -> skipping river distance raster.")

---CELL---

# QA stats + plots for key predictors
def raster_stats(path: Path) -> Dict:
    with rasterio.open(path) as src:
        data = src.read(1, masked=True)
        nodata = int(np.ma.count_masked(data))
        flat = data.compressed()
        return {
            "min": float(np.min(flat)) if flat.size else np.nan,
            "max": float(np.max(flat)) if flat.size else np.nan,
            "mean": float(np.mean(flat)) if flat.size else np.nan,
            "missing": nodata,
            "count": int(flat.size),
        }

def plot_hist(path: Path, title: str, bins: int = 50):
    with rasterio.open(path) as src:
        data = src.read(1, masked=True)
        flat = data.compressed()
    plt.hist(flat, bins=bins, color="#4C78A8")
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Frequency")

# Paths for QA
qa_paths = {
    "slope": aligned_rasters["slope"],
    "ndvi": aligned_rasters["ndvi"],
    "rainfall": aligned_rasters["rainfall"],
    "landcover": aligned_rasters["landcover"],
}

# Print summary stats
for name, path in qa_paths.items():
    stats = raster_stats(path)
    print(name, stats)

# Histograms
plt.figure(figsize=(10, 8))
plt.subplot(2, 2, 1)
plot_hist(qa_paths["slope"], "Slope Histogram")
plt.subplot(2, 2, 2)
plot_hist(qa_paths["rainfall"], "Rainfall Histogram")
plt.subplot(2, 2, 3)
plot_hist(qa_paths["ndvi"], "NDVI Histogram")
plt.subplot(2, 2, 4)
plot_hist(qa_paths["landcover"], "Landcover Histogram", bins=30)
plt.tight_layout()
plt.show()

# Landcover class distribution
with rasterio.open(qa_paths["landcover"]) as src:
    lc = src.read(1, masked=True).compressed()
# Ensure integer dtype for class counts (avoid Pylance type ambiguity)
lc = np.asarray(lc, dtype="int32")
classes, counts = np.unique(lc, return_counts=True)
lc_df = pd.DataFrame({"class": classes, "count": counts}).sort_values("count", ascending=False)
display(lc_df.head(20))

plt.figure(figsize=(8, 4))
plt.bar(lc_df["class"].astype(str), lc_df["count"], color="#59A14F")
plt.title("Landcover Class Distribution")
plt.xlabel("Class")
plt.ylabel("Pixel Count")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

---CELL---

# Quick visual checks for alignment, clipping, and distance rasters
from typing import Optional

def plot_raster(path: Optional[Path], title: str):
    if path is None or not path.exists():
        plt.text(0.5, 0.5, f"Missing: {title}", ha="center")
        plt.title(title)
        plt.axis("off")
        return
    with rasterio.open(path) as src:
        data = src.read(1, masked=True)
    plt.imshow(data, cmap="viridis")
    plt.title(title)
    plt.axis("off")

plt.figure(figsize=(12, 8))
plt.subplot(2, 2, 1)
plot_raster(aligned_rasters.get("dem"), "DEM (Aligned + Clipped)")
plt.subplot(2, 2, 2)
plot_raster(aligned_rasters.get("slope"), "Slope (Aligned + Clipped)")
plt.subplot(2, 2, 3)
if road_distance_path is not None:
    plot_raster(road_distance_path, "Distance to Roads")
else:
    plot_raster(river_distance_path, "Distance to Rivers")
plt.subplot(2, 2, 4)
plot_raster(river_distance_path, "Distance to Rivers")
plt.tight_layout()
plt.show()

# Boundary overlay check on DEM
with rasterio.open(aligned_rasters.get("dem")) as src:
    dem = src.read(1, masked=True)
    extent = (
        float(src.bounds.left),
        float(src.bounds.right),
        float(src.bounds.bottom),
        float(src.bounds.top),
    )

plt.figure(figsize=(6, 6))
plt.imshow(dem, extent=extent, cmap="terrain")
boundary_gdf.boundary.plot(ax=plt.gca(), color="red", linewidth=1)
plt.title("Boundary Overlay on DEM")
plt.axis("off")
plt.show()

---CELL---

# --- Step 5: Stack aligned rasters ---
feature_band_names = ["slope", "aspect", "twi", "rainfall", "ndvi", "landcover", "river_proximity"]
aligned_feature_paths = [
    aligned_rasters["slope"],
    aligned_rasters["aspect"],
    aligned_rasters["twi"],
    aligned_rasters["rainfall"],
    aligned_rasters["ndvi"],
    aligned_rasters["landcover"],
    river_distance_path,
 ]

# If road distance is available, include it
if road_distance_path is not None:
    feature_band_names.insert(-1, "road_distance")
    aligned_feature_paths.insert(-1, road_distance_path)

stack_path = PROCESSED_RASTER_DIR / "stack" / "feature_stack.tif"
stack_path = stack_rasters(aligned_feature_paths, stack_path)
print_raster_info(stack_path, "feature_stack")

# --- Step 6: Landslide inventory preprocessing ---
# Update column names to match your CSV if needed
LAT_COL = "latitude"
LON_COL = "longitude"

inventory_df = pd.read_csv(inventory_path)
inventory_df = inventory_df.dropna(subset=[LAT_COL, LON_COL]).copy()
inventory_gdf = gpd.GeoDataFrame(
    inventory_df,
    geometry=gpd.points_from_xy(inventory_df[LON_COL], inventory_df[LAT_COL]),
    crs=TARGET_CRS,
 )
inventory_gdf = gpd.clip(inventory_gdf, boundary_gdf)
inventory_out = PROCESSED_INVENTORY_DIR / "landslides_epsg4326.geojson"
inventory_gdf.to_file(inventory_out, driver="GeoJSON")
print_vector_info(inventory_out, "landslide_inventory")

# --- Step 7: Create non-landslide samples ---
n_positive = len(inventory_gdf)
neg_multiplier = 3
n_negative = n_positive * neg_multiplier
non_landslide_gdf = generate_random_points(boundary_gdf, n_negative, seed=42)
non_landslide_gdf["label"] = 0
inventory_gdf = inventory_gdf.copy()
inventory_gdf["label"] = 1

samples_gdf = pd.concat([inventory_gdf, non_landslide_gdf], ignore_index=True)
samples_gdf = gpd.GeoDataFrame(samples_gdf, geometry="geometry", crs=TARGET_CRS)

# --- Step 8: Extract raster values at sample points ---
features_df = extract_stack_values(stack_path, samples_gdf, feature_band_names)
features_df["landslide"] = samples_gdf["label"].values

# Remove rows with missing values
features_df = features_df.replace([np.inf, -np.inf], np.nan).dropna()
features_df = features_df.drop_duplicates()

training_csv_path = OUTPUTS_DIR / "training_dataset.csv"
features_df.to_csv(training_csv_path, index=False)
print("Saved training dataset:", training_csv_path)
features_df.head()

---CELL---

# --- Step 9-12: Train Random Forest and evaluate ---
X = features_df[feature_band_names]
y = features_df["landslide"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
 )

rf_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced",
 )
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("Accuracy:", acc)
print(classification_report(y_test, y_pred, digits=3))

cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap="Blues")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()

# Save trained model (ensure target folder exists)
model_path = PROJECT_ROOT / "models" / "random_forest.pkl"
model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(rf_model, model_path)
print("Saved model:", model_path)

# --- Step 13: Feature importance visualization ---
importances = pd.Series(rf_model.feature_importances_, index=feature_band_names).sort_values(ascending=False)
plt.figure(figsize=(8, 4))
importances.plot(kind="bar")
plt.title("Feature Importance")
plt.ylabel("Importance")
plt.tight_layout()
fig_path = OUTPUT_FIG_DIR / "feature_importance.png"
OUTPUT_FIG_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(fig_path, dpi=150)
plt.show()
print("Saved feature importance figure:", fig_path)

# --- Step 14: Susceptibility prediction raster ---
susceptibility_path = OUTPUTS_DIR / "susceptibility_map.tif"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

with rasterio.open(stack_path) as src:
    profile = src.profile.copy()
    profile.update({"count": 1, "dtype": "float32", "nodata": None})
    with rasterio.open(susceptibility_path, "w", **profile) as dst:
        for _, window in src.block_windows(1):
            data = src.read(window=window)  # shape: (bands, rows, cols)
            bands, rows, cols = data.shape
            data_2d = data.reshape(bands, -1).T
            # Replace nodata with NaN and drop for prediction
            data_2d = np.where(np.isfinite(data_2d), data_2d, np.nan)
            valid_mask = ~np.isnan(data_2d).any(axis=1)
            preds = np.zeros(data_2d.shape[0], dtype="float32")
            feature_columns = feature_band_names
            if valid_mask.any():
                chunk_df = pd.DataFrame(data_2d[valid_mask], columns=feature_columns)
                preds[valid_mask] = rf_model.predict_proba(chunk_df)[:, 1].astype("float32")
            preds = preds.reshape(rows, cols)
            dst.write(preds, 1, window=window)

print("Saved susceptibility raster:", susceptibility_path)
