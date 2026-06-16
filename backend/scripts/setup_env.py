from pathlib import Path
import importlib.util
import subprocess
import sys

PROJECT_ROOT = Path(r"D:/Side_Projects/ai-ml/GeoShield_Ecothon")
DATASET_ROOT = Path(r"D:/Side_Projects/ai-ml/GeoShield_Ecothon/backend/data/Sindhupalchowk_Dataset_Landslide")

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
    "flask",
]


def is_installed(pkg_name: str) -> bool:
    return importlib.util.find_spec(pkg_name) is not None

missing = [p for p in packages if not is_installed(p)]
print("Missing packages:", missing)

if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])
else:
    print("All required packages are already installed.")

# Create standard folders used by the notebook
RAW_RASTER_DIR = PROJECT_ROOT / "data" / "raw" / "raster"
RAW_VECTOR_DIR = PROJECT_ROOT / "data" / "raw" / "vector"
RAW_INVENTORY_DIR = PROJECT_ROOT / "data" / "raw" / "inventory"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"

for p in [RAW_RASTER_DIR, RAW_VECTOR_DIR, RAW_INVENTORY_DIR, PROCESSED_DIR, OUTPUTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Ensure dataset root exists (notify but do not create data for user)
if DATASET_ROOT.exists():
    print(f"Dataset root found: {DATASET_ROOT}")
else:
    print(f"Warning: dataset root not found: {DATASET_ROOT}")

print("Setup script completed.")
