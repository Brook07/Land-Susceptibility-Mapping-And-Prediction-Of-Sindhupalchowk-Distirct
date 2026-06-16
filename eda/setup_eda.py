"""
EDA Environment Setup Script
Landslide Susceptibility Mapping - Sindhupalchok District

This script automates the setup of the EDA analysis environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    requirements_file = Path(__file__).parent / 'requirements_eda.txt'
    
    if not requirements_file.exists():
        print("❌ requirements_eda.txt not found!")
        return False
    
    try:
        print(f"📦 Installing packages from {requirements_file.name}...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
        )
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def verify_data_paths():
    """Verify that all data files exist"""
    print_header("Verifying Data Paths")
    
    data_files = {
        'Boundary Shapefile': r'd:\sindupalchok_landslide\data\processed\shapefiles\sindhupalchok_boundary.shp',
        'DEM': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_DEM.tif',
        'Slope': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_Slope.tif',
        'Aspect': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_Aspect.tif',
        'LULC': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_LULC_30m.tif',
        'NDVI': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_NDVI_2025_30m.tif',
        'Rainfall': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_Rainfall_Raster.tif',
        'RiverProximity': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_RiverProximity.tif',
        'RoadProximity': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_RoadProximity.tif',
        'TWI': r'd:\sindupalchok_landslide\data\processed\rasters\Sindhupalchok_TWI_2025.tif',
        'Landslide Inventory': r'd:\sindupalchok_landslide\data\processed\landslide_inventory\sindhupalchowk_landslides.csv'
    }
    
    all_exist = True
    for name, path in data_files.items():
        if Path(path).exists():
            print(f"✅ {name}: Found")
        else:
            print(f"❌ {name}: NOT FOUND - {path}")
            all_exist = False
    
    return all_exist

def create_output_directories():
    """Create output directories if they don't exist"""
    print_header("Creating Output Directories")
    
    eda_dir = Path(__file__).parent
    dirs_to_create = [
        eda_dir / 'figures',
        eda_dir / 'data'
    ]
    
    for dir_path in dirs_to_create:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {dir_path}")
        else:
            print(f"ℹ️  Exists: {dir_path}")

def verify_jupyter():
    """Verify Jupyter is installed"""
    print_header("Checking Jupyter Installation")
    
    try:
        import jupyter
        print("✅ Jupyter is installed")
        print(f"   Version: {jupyter.__version__}")
        return True
    except ImportError:
        print("❌ Jupyter not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jupyter'])
        print("✅ Jupyter installed successfully")
        return True

def verify_spatial_libraries():
    """Verify spatial libraries are installed"""
    print_header("Verifying Spatial Libraries")
    
    libraries = {
        'rasterio': 'Raster data handling',
        'geopandas': 'Vector data handling',
        'shapely': 'Geometric operations',
        'numpy': 'Numerical operations',
        'pandas': 'Data manipulation',
    }
    
    all_installed = True
    for lib, description in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {lib}: {description}")
        except ImportError:
            print(f"❌ {lib}: NOT INSTALLED - {description}")
            all_installed = False
    
    return all_installed

def print_next_steps():
    """Print next steps"""
    print_header("Next Steps")
    print("""
1. 📓 Start the Jupyter notebook:
   
   jupyter notebook 01_eda_analysis.ipynb

2. 📂 Or open with VS Code:
   
   - Open the notebook in VS Code
   - Select Python kernel (3.8+)
   - Run cells from top to bottom

3. 📊 Review outputs:
   
   - Figures saved to: ./figures/
   - Data saved to: ./data/
   - Statistics in CSV files
   - Summary report in TXT files

4. 📈 After EDA completion:
   
   - Review data quality report
   - Analyze correlation matrix
   - Plan feature engineering
   - Prepare for modeling phase

5. 📚 For more help:
   
   - Check README.md for detailed guide
   - Review notebook sections for methodology
   - Check inline comments for explanations
""")

def main():
    """Main setup function"""
    print_header("EDA Environment Setup - Landslide Susceptibility Project")
    
    print("""
This script will:
1. Install required Python packages
2. Verify data files exist
3. Create output directories
4. Check Jupyter installation
5. Verify spatial libraries
""")
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return False
    
    # Step 2: Verify data
    if not verify_data_paths():
        print("\n⚠️  Warning: Some data files not found. Update paths in notebook if needed.")
    
    # Step 3: Create directories
    create_output_directories()
    
    # Step 4: Verify Jupyter
    if not verify_jupyter():
        print("\n❌ Setup failed at Jupyter verification")
        return False
    
    # Step 5: Verify libraries
    if not verify_spatial_libraries():
        print("\n❌ Setup failed at library verification")
        return False
    
    # Final steps
    print_header("Setup Completed Successfully! ✅")
    print_next_steps()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
