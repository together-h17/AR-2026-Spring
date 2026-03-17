# Week 4 Pre-lab: Raster Environment Setup & Google Colab

> Please complete the following steps **before class** to ensure your environment is ready.
> Estimated time: 20–30 minutes

---

## Step 1: Create a Virtual Environment (Recommended)

To avoid dependency conflicts with your existing packages, create a dedicated virtual environment for this course:

```bash
# Create virtual environment (run once)
python -m venv gis-env

# Activate it (run every time you open a new terminal)
# macOS / Linux:
source gis-env/bin/activate
# Windows:
gis-env\Scripts\activate

# Install packages inside the virtual environment
pip install geopandas rioxarray xarray rasterstats numpy matplotlib folium mapclassify
```

> **Why?** Installing packages directly into your system Python may cause version conflicts (e.g., numpy 2.x vs. packages that require numpy <2.0). A virtual environment keeps each project's dependencies isolated.

> **Tip:** If you use VS Code or Windsurf, select the `gis-env` interpreter via `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the one inside `gis-env/`.

If you prefer conda:

```bash
conda create -n gis-env python=3.11 -y
conda activate gis-env
conda install -c conda-forge geopandas rioxarray xarray rasterstats folium mapclassify
```

> **Note:** We will also use Google Colab during class (no venv needed there). The Colab setup is in Step 3.

## Step 2: Verify Local Installation

Create a file called `test_raster.py` and run it:

```python
import numpy as np
import xarray as xr
import rioxarray

# Create a synthetic 10x10 DEM with a valley profile (elevation in meters)
elevation = np.array([
    [500, 450, 350, 200, 120,  80, 120, 200, 350, 500],
    [480, 430, 330, 180, 100,  60, 100, 180, 330, 480],
    [460, 410, 310, 160,  80,  40,  80, 160, 310, 460],
    [450, 400, 300, 150,  70,  30,  70, 150, 300, 450],
    [440, 390, 290, 140,  60,  20,  60, 140, 290, 440],
    [450, 400, 300, 150,  70,  30,  70, 150, 300, 450],
    [460, 410, 310, 160,  80,  40,  80, 160, 310, 460],
    [480, 430, 330, 180, 100,  60, 100, 180, 330, 480],
    [500, 450, 350, 200, 120,  80, 120, 200, 350, 500],
    [520, 470, 370, 220, 140, 100, 140, 220, 370, 520],
], dtype=np.float32)

# Wrap as xarray DataArray with spatial metadata
from rasterio.transform import from_bounds
transform = from_bounds(304000, 2637000, 304200, 2637200, 10, 10)

da = xr.DataArray(
    elevation[np.newaxis, :, :],
    dims=["band", "y", "x"],
    coords={
        "band": [1],
        "y": np.linspace(2637200, 2637000, 10),
        "x": np.linspace(304000, 304200, 10),
    },
)
# IMPORTANT: write_transform first, then write_crs last (order matters!)
da = da.rio.write_transform(transform)
da = da.rio.write_crs("EPSG:3826")

print("✅ rioxarray works!")
print(f"Shape: {da.shape}")
print(f"CRS: {da.rio.crs}")
print(f"Resolution: {da.rio.resolution()}")
print(f"Min elevation: {float(da.min()):.1f} m")
print(f"Max elevation: {float(da.max()):.1f} m")

# Test slope computation with numpy
dy, dx = np.gradient(elevation, 20)  # 20m resolution
slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
slope_deg = np.degrees(slope_rad)
print(f"\nSlope range: {slope_deg.min():.1f}° – {slope_deg.max():.1f}°")

print("\n✅ All checks passed! You are ready for Week 4.")
```

**Expected output:**
```
✅ rioxarray works!
Shape: (1, 10, 10)
CRS: EPSG:3826
Resolution: (20.0, -20.0)
Min elevation: 20.0 m
Max elevation: 520.0 m

Slope range: 0.0° – 82.5°

✅ All checks passed! You are ready for Week 4.
```

> The valley-shaped DEM has a wide slope range (flat valley floor to steep walls) — this is intentional to demonstrate terrain variation.

## Step 3: Set Up Google Colab

This week we will use Google Colab for heavy raster processing. Please complete these steps:

1. **Go to** [colab.research.google.com](https://colab.research.google.com)
2. **Sign in** with your Google account
3. **Create a new notebook** → name it `Week4-Colab-Test`
4. **Run the following in a cell** to verify Colab works:

```python
# Cell 1: Test Colab environment
import sys
print(f"Python version: {sys.version}")

# Install raster packages (Colab doesn't have these by default)
!pip install rioxarray rasterstats -q

import rioxarray
import numpy as np
print("✅ rioxarray installed successfully in Colab!")
```

5. **Download the Hualien DEM file** to your Google Drive:
   - Open this link: [花蓮縣 20m DEM (dem_20m_hualien.tif)](https://drive.google.com/file/d/1BFWevw_tGEXpgfbeCZ-Jtts0i_iJUcWU/view?usp=sharing)
   - Click **"Make a copy"** or **"Add shortcut to Drive"** → save to `MyDrive/GIS_data/`
   - If `GIS_data` folder doesn't exist, create it in your Google Drive first

6. **Test Google Drive mount + DEM loading** (we will use this DEM in class):

```python
# Cell 2: Mount Google Drive and test DEM loading
from google.colab import drive
drive.mount('/content/drive')

import rioxarray
dem = rioxarray.open_rasterio('/content/drive/MyDrive/GIS_data/dem_20m_hualien.tif')
print(f"✅ DEM loaded! Shape: {dem.shape}, CRS: {dem.rio.crs}")
print(f"Elevation range: {float(dem.min()):.0f} – {float(dem.max()):.0f} m")
```

> **Tip:** When prompted, allow Colab to access your Google Drive. If the path doesn't work, check that `dem_20m_hualien.tif` is in `MyDrive/GIS_data/`.

## Step 4 (Optional): Review Week 3 Concepts

Make sure you are comfortable with these Week 3 concepts (we will build on them):

- **GeoDataFrame**: attributes + geometry + CRS
- **CRS reprojection**: `.to_crs(epsg=3826)`
- **Buffer**: `.buffer(distance)` — units depend on CRS
- **Spatial Join**: `gpd.sjoin(left, right, predicate='within')`
- **Interactive maps**: `.explore()`

## Step 5 (Optional): Read About Rasters

Spend 10 minutes browsing:

- [Rioxarray documentation](https://corteva.github.io/rioxarray/stable/)
- [What is a DEM?](https://en.wikipedia.org/wiki/Digital_elevation_model)

Focus on:
- How a raster differs from vector data
- What "resolution" means for a grid
- What an affine transform does

---

## Troubleshooting

**Q: `pip install rioxarray` fails?**
A: rioxarray depends on rasterio, which needs GDAL. If pip fails, try conda: `conda install -c conda-forge rioxarray`

**Q: I see dependency conflict warnings (e.g., numpy version)?**
A: Make sure you activated your virtual environment first (`source gis-env/bin/activate`). If you installed into the system Python by mistake, create a fresh venv and reinstall.

**Q: Google Colab is slow or disconnects?**
A: Make sure you are using a stable internet connection. Colab free tier has usage limits — avoid leaving idle notebooks running.

**Q: I can't mount Google Drive in Colab?**
A: Make sure you are logged into Google and have allowed the Colab permission popup. Try refreshing the page and running the cell again.