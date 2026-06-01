# Week 14 Homework: ARIA v9.5 — The Resilience Monitor

**Course:** NTU Remote Sensing & Spatial Information Analysis (遙測與空間資訊之分析與應用)  
**Instructor:** Prof. Su Wen-Ray  
**Assignment:** Week 14 Homework  
**Due Date:** See NTUCool (typically 1 week after class)  
**Case Study:** Landsat Multi-Decadal Trend Analysis & Resilience — Xiulin / Taroko Study Area（秀林 / 太魯閣研究區）

---

## Overview

本週你要將 ARIA 系統從 v9.0 升級到 **v9.5 — The Resilience Monitor**。v9.0 使用 Sentinel-2（6 年、數百張影像）進行時序趨勢分析；v9.5 引入 **Landsat 全系列（L5/L7/L8/L9）的波段調和（band harmonization）**，將分析時間軸從 6 年拉長到 **26 年（2000–2026）**，並加入**桃園埤塘消失分析**和**植被韌性指標**，回答指揮官最關鍵的問題：這片土地的長期趨勢是什麼？它有沒有從災害中恢復的能力？

**升級邏輯：**
```
v5.0 (W8)  → 光譜分析引擎：一張影像、一個指標（NDVI）
v6.0 (W9)  → 變遷偵測引擎：兩張影像、一個差值（ΔNDVI）
v7.0 (W10) → SAR 穿雲引擎：一張光學 + 一張 SAR
v8.0 (W12) → 分類引擎：一張影像 → 土地覆蓋圖
v9.0 (W13) → 雲端引擎：數百張影像 → 6 年時序趨勢分析
v9.5 (W14) → 韌性監測引擎：數千張影像 → 26 年長期趨勢 + 韌性分析 ⬆
```

**Key Deliverable:** A Colab/Jupyter notebook (.ipynb) that demonstrates:
- Landsat 多衛星波段調和（L5/L7 → L8/L9 band mapping）
- Collection 2 Level 2 scale factor 校正 + QA_PIXEL 雲遮罩
- 26 年 NDVI / MNDWI / NBR 年均時序分析
- 像素級線性趨勢分析（greening vs. browning）
- 桃園埤塘消失偵測（MNDWI 水頻率圖）
- 植被韌性指標計算（recovery ratio）
- GeoTIFF 匯出（EPSG:32651）

**Total: 100 pts + 30 pts bonus**

---

## Scenario（任務情境）

指揮官現在需要的是**長期脈絡（long-term context）**。W13 的 6 年 Sentinel-2 時序已經證明了時序分析的威力，但 6 年太短了——指揮官的問題是跨越世代的：

- 「2024 年地震造成的植被損失是前所未有的，還是這個地區過去也經歷過類似規模的擾動？」
- 「桃園台地的埤塘在過去 26 年消失了多少？對都市防洪有什麼影響？」
- 「地震後植被有恢復的跡象嗎？這片土地的韌性（resilience）夠不夠？」

這些問題需要**數十年的觀測記錄**。Sentinel-2 從 2017 年才開始有 L2A 資料，時間不夠長。但 **Landsat 系列**從 1984 年就開始連續觀測——L5（1984–2012）、L7（1999–至今）、L8（2013–至今）、L9（2021–至今）。挑戰在於：不同世代的 Landsat 衛星波段編號不同，必須先做**波段調和（band harmonization）**才能建立一致的長期時序。

> **Important:** The homework study area remains **Xiulin / Taroko**（秀林 / 太魯閣山區）, same as W13. But the temporal depth is vastly different: W13 covered 6 years (2020–2026) with Sentinel-2 at 10m resolution; W14 covers 26 years (2000–2026) with Landsat at 30m resolution. You will discover patterns invisible in a 6-year window — long-term greening/browning trends, pond disappearance in Taoyuan, and the true resilience of ecosystems.

---

## Study Area & Data

### GEE Setup

```python
import ee
import geemap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

ee.Authenticate()  # First time only
ee.Initialize(project='your-project-id')

# Xiulin / Taroko study area BBOX (same as W13)
# West: Central Mountain Range; East: Pacific Ocean
TAROKO_BBOX = [121.34526379253053, 24.046021742135874, 121.85149217685861, 24.35767637905926]
aoi = ee.Geometry.Rectangle(TAROKO_BBOX)

print(f"Study area: Xiulin / Taroko")
print(f"BBOX: {TAROKO_BBOX}")
print(f"Time range: 2000–2026 (26 years)")
```

### Available Data in GEE

| Dataset | GEE Collection ID | Period | Resolution | Bands |
|---------|-------------------|--------|------------|-------|
| Landsat 5 TM | `LANDSAT/LT05/C02/T1_L2` | 1984–2012 | 30m | SR_B1–B5, SR_B7 |
| Landsat 7 ETM+ | `LANDSAT/LE07/C02/T1_L2` | 1999–present | 30m | SR_B1–B5, SR_B7 |
| Landsat 8 OLI | `LANDSAT/LC08/C02/T1_L2` | 2013–present | 30m | SR_B2–B7 |
| Landsat 9 OLI-2 | `LANDSAT/LC09/C02/T1_L2` | 2021–present | 30m | SR_B2–B7 |
| SRTM DEM | `USGS/SRTMGL1_003` | Static | 30m | Elevation |

### Band Harmonization Reference（波段對照表）

| Spectral Band | L5/L7 Band Name | L8/L9 Band Name |
|---------------|-----------------|-----------------|
| Blue | SR_B1 | SR_B2 |
| Green | SR_B2 | SR_B3 |
| Red | SR_B3 | SR_B4 |
| NIR | SR_B4 | SR_B5 |
| SWIR1 | SR_B5 | SR_B6 |
| SWIR2 | SR_B7 | SR_B7 |

### Scale Factor & QA Bitmask

```python
# Landsat Collection 2 Level 2 scale factor
# DN → Surface Reflectance: pixel * 0.0000275 + (-0.2)

# QA_PIXEL bitmask for cloud/shadow masking
# Bit 3: Cloud (1 = cloud)
# Bit 4: Cloud Shadow (1 = shadow)
```

---

## Core Requirements (4 Tasks)

### Task 1: Landsat Harmonization + 26-Year NDVI Time Series (25%)

**目標：** 將四代 Landsat 衛星（L5/L7/L8/L9）的波段名稱統一，建立 2000–2026 年的年度 NDVI 時序，觀察太魯閣地區植被的長期變化趨勢。

**Procedure：**

1. **定義波段調和函數：**
   ```python
   # Harmonize L5/L7 band names to match L8/L9 naming convention
   def harmonize_l57(image):
       """Rename L5/L7 bands to match L8/L9 band names."""
       return (image.select(
           ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL'],
           ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']
       ).copyProperties(image, ['system:time_start']))

   def harmonize_l89(image):
       """Rename L8/L9 bands to match harmonized naming convention."""
       return (image.select(
           ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL'],
           ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']
       ).copyProperties(image, ['system:time_start']))
   ```

2. **Apply scale factors + cloud masking（QA_PIXEL 位元遮罩）：**
   ```python
   def apply_scale_and_mask(image):
       """Apply C2 L2 scale factors and mask clouds/shadows using QA_PIXEL."""
       # QA_PIXEL bitmask: bit 3 = cloud, bit 4 = cloud shadow
       qa = image.select('QA_PIXEL')
       cloud = qa.bitwiseAnd(1 << 3).eq(0)    # 0 = no cloud
       shadow = qa.bitwiseAnd(1 << 4).eq(0)    # 0 = no shadow
       mask = cloud.And(shadow)

       # Apply scale factor to spectral bands
       spectral = (image.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'])
           .multiply(0.0000275).add(-0.2)
           .clamp(0, 1))  # Clamp to valid reflectance range

       return spectral.updateMask(mask).copyProperties(image, ['system:time_start'])
   ```

3. **Merge all Landsat collections（合併四代 Landsat）：**
   ```python
   # Load and harmonize each collection
   l5 = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
       .filterBounds(aoi).filterDate('2000-01-01', '2012-12-31')
       .map(harmonize_l57))

   l7 = (ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
       .filterBounds(aoi).filterDate('2000-01-01', '2026-12-31')
       .map(harmonize_l57))

   l8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
       .filterBounds(aoi).filterDate('2013-01-01', '2026-12-31')
       .map(harmonize_l89))

   l9 = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
       .filterBounds(aoi).filterDate('2021-01-01', '2026-12-31')
       .map(harmonize_l89))

   # Merge and apply scale/mask
   landsat_all = l5.merge(l7).merge(l8).merge(l9).map(apply_scale_and_mask)

   print(f"Total Landsat images (2000–2026): {landsat_all.size().getInfo()}")
   ```

4. **Compute annual median NDVI（年度 NDVI 中值合成）：**
   ```python
   def compute_ndvi(image):
       ndvi = image.normalizedDifference(['NIR', 'Red']).rename('NDVI')
       return ndvi.copyProperties(image, ['system:time_start'])

   ndvi_collection = landsat_all.map(compute_ndvi)

   # Compute annual median NDVI for each year
   years = list(range(2000, 2027))
   annual_ndvi = []
   for year in years:
       yearly = (ndvi_collection
           .filterDate(f'{year}-01-01', f'{year}-12-31')
           .median()
           .reduceRegion(
               reducer=ee.Reducer.mean(),
               geometry=aoi,
               scale=30,
               maxPixels=1e9))
       annual_ndvi.append({'year': year, 'ndvi': yearly.get('NDVI').getInfo()})
   ```

5. **Plot 26-year NDVI trend（繪製 26 年趨勢圖）：**
   - Plot as bar chart or line chart (x = year, y = mean NDVI)
   - Mark the 2024 earthquake year with a distinctive color or vertical line
   - Add a linear trendline across the full period
   - Include year labels on the x-axis

6. **分析與討論：**
   - Is there a long-term greening or browning trend?（長期是綠化還是退化？）
   - Are there years with anomalously low NDVI? What events correspond?（哪些年份 NDVI 異常低？對應什麼事件？）
   - How does the 2024 earthquake compare to other disturbance years?（2024 地震和歷史上其他擾動年份相比如何？）
   - How many total Landsat images were used? How does this compare to W13's Sentinel-2 count?

**Deliverables:**
- [ ] 26-year annual NDVI trend plot (2000–2026, with 2024 earthquake marker and trendline)
- [ ] Brief analysis (3–5 sentences): long-term trend, anomalous years, earthquake context
- [ ] Code with comments explaining band harmonization and scale factor logic

---

### Task 2: Pixel-Level Linear Trend Analysis (25%)

**目標：** 使用 `ee.Reducer.linearFit()` 對每個像素進行 26 年 NDVI 線性趨勢分析，製作 greening/browning 空間分布圖，並與 W13 的 6 年趨勢比較。

**Procedure：**

1. **建立帶時間戳的年度 NDVI ImageCollection：**
   ```python
   def annual_ndvi_image(year):
       """Create an annual median NDVI image with a time band."""
       start = ee.Date.fromYMD(year, 1, 1)
       end = ee.Date.fromYMD(year, 12, 31)
       median_ndvi = ndvi_collection.filterDate(start, end).median()
       # Add a time band (year as fractional value for linear regression)
       time_band = ee.Image.constant(year).float().rename('time')
       return median_ndvi.addBands(time_band).set('system:time_start', start.millis())

   year_list = ee.List.sequence(2000, 2026)
   annual_col = ee.ImageCollection(year_list.map(
       lambda y: annual_ndvi_image(ee.Number(y).int())))
   ```

2. **Apply linear regression（線性回歸）：**
   ```python
   # linearFit: dependent = NDVI, independent = time
   trend = annual_col.select(['time', 'NDVI']).reduce(ee.Reducer.linearFit())

   # 'scale' band = slope (NDVI change per year)
   # 'offset' band = y-intercept
   slope = trend.select('scale')
   ```

3. **Visualize slope map（斜率圖）：**
   - Positive slope = greening（綠化）→ display in green
   - Negative slope = browning（退化）→ display in red/brown
   - Use a diverging color palette centered on zero
   - Overlay on a basemap with the study area boundary

4. **Compute statistics（統計分析）：**
   ```python
   # Count pixels: greening vs browning vs stable
   # Define thresholds (e.g., slope > 0.001 = greening, < -0.001 = browning)
   greening = slope.gt(0.001)
   browning = slope.lt(-0.001)
   stable = slope.gte(-0.001).And(slope.lte(0.001))

   # Calculate percentages
   # Use ee.Reducer.frequencyHistogram() or pixel counting
   ```

5. **Compare with W13's 6-year trend（與 W13 比較）：**
   - W13 used 6 years of Sentinel-2 data (2020–2026)
   - W14 uses 26 years of Landsat data (2000–2026)
   - Does a longer time window reveal different patterns?
   - Are areas identified as "browning" in a 6-year window actually on a long-term greening trajectory (or vice versa)?
   - Discussion: short-term noise vs long-term signal

6. **Export trend map as GeoTIFF：**
   ```python
   task = ee.batch.Export.image.toDrive(
       image=trend,
       description='taroko_ndvi_trend_26yr',
       folder='GEE_Exports',
       region=aoi,
       scale=30,
       crs='EPSG:32651',
       maxPixels=1e9,
   )
   task.start()
   ```

**Deliverables:**
- [ ] Slope map showing greening vs browning pixels across the study area
- [ ] Statistics: percentage of pixels greening, browning, stable
- [ ] Comparison paragraph: W13 6-year trend vs W14 26-year trend — does the longer window tell a different story?
- [ ] Exported GeoTIFF of the trend map (screenshot of Google Drive file)
- [ ] Code with comments

---

### Task 3: Taoyuan Pond Disappearance with MNDWI (25%)

**目標：** 利用 MNDWI（Modified Normalized Difference Water Index）分析桃園台地過去 26 年的埤塘消失情形，量化都市化對水塘景觀的衝擊。

**背景：** 桃園台地在日治時期桃園大圳興建前，曾擁有約 6,000–8,000 口埤塘（農田水利署），是台灣規模最大的灌溉水塘景觀。隨著桃園升格直轄市和航空城計畫推動，大量埤塘被填平，目前僅存約 3,000 口。

**Procedure：**

1. **Define Taoyuan AOI and load Landsat（定義桃園研究區）：**
   ```python
   # Taoyuan Plateau — FULL RANGE (水頻率圖用)
   TAOYUAN_BBOX = [120.94, 24.83, 121.35, 25.08]
   aoi_taoyuan = ee.Geometry.Rectangle(TAOYUAN_BBOX)

   # Urbanization corridor (消失偵測聚焦區)
   TAOYUAN_URBAN_BBOX = [121.00, 24.88, 121.28, 25.05]
   aoi_taoyuan_urban = ee.Geometry.Rectangle(TAOYUAN_URBAN_BBOX)

   # Load Landsat for Taoyuan (same harmonization functions)
   l5_ty = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(aoi_taoyuan).filterDate('2000-01-01', '2012-12-31').map(harmonize_l57)
   l7_ty = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(aoi_taoyuan).filterDate('2000-01-01', '2026-12-31').map(harmonize_l57)
   l8_ty = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(aoi_taoyuan).filterDate('2013-01-01', '2026-12-31').map(harmonize_l89)
   l9_ty = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(aoi_taoyuan).filterDate('2021-01-01', '2026-12-31').map(harmonize_l89)

   landsat_taoyuan = l5_ty.merge(l7_ty).merge(l8_ty).merge(l9_ty).map(apply_scale_and_mask)
   ```

2. **Compute MNDWI and create water frequency map（水體出現頻率圖）：**
   ```python
   def compute_mndwi(image):
       """MNDWI = (Green - SWIR1) / (Green + SWIR1)"""
       mndwi = image.normalizedDifference(['Green', 'SWIR1']).rename('MNDWI')
       return mndwi.copyProperties(image, ['system:time_start'])

   mndwi_taoyuan = landsat_taoyuan.map(compute_mndwi)

   # For each year, classify pixels as water (MNDWI > 0.1) or non-water
   def yearly_water(year):
       start = ee.Date.fromYMD(year, 1, 1)
       end = ee.Date.fromYMD(year, 12, 31)
       median_mndwi = mndwi_taoyuan.filterDate(start, end).median()
       water = median_mndwi.gt(0.1).rename('water')
       return water.set('system:time_start', start.millis())

   water_col = ee.ImageCollection(year_list.map(
       lambda y: yearly_water(ee.Number(y).int())))
   water_freq = water_col.mean().rename('water_frequency')
   ```

3. **Compare early vs recent periods（早期 vs 近期比較）：**
   ```python
   # Early period: 2000–2005
   early_water = (mndwi_taoyuan
       .filterDate('2000-01-01', '2005-12-31')
       .median().gt(0.1).rename('early_water'))

   # Recent period: 2021–2026
   recent_water = (mndwi_taoyuan
       .filterDate('2021-01-01', '2026-12-31')
       .median().gt(0.1).rename('recent_water'))

   # Pond disappearance: areas that changed
   lost_ponds = early_water.And(recent_water.Not())    # Was water, now land
   new_water = recent_water.And(early_water.Not())      # Was land, now water
   ```

4. **Estimate area of pond change（面積估算）：**
   ```python
   pixel_area = ee.Image.pixelArea()

   lost_area = (lost_ponds.multiply(pixel_area)
       .reduceRegion(reducer=ee.Reducer.sum(), geometry=aoi_taoyuan, scale=30, maxPixels=1e9)
       .get('early_water'))
   # Convert m^2 to hectares: / 10000
   ```

5. **視覺化：**
   - Display water frequency map (blue gradient: 0% = never water, 100% = always water)
   - Display lost ponds (red) and new water (green) areas
   - Overlay on basemap to identify which areas experienced most pond loss

6. **驗證：用已知埤塘位置檢驗 MNDWI 偵測準確度**

   老師提供了 223 口已知埤塘的中心點座標（GeoJSON 格式），作為 ground truth 驗證資料。

   **下載驗證資料：**
   ```python
   # 下載埤塘中心點 GeoJSON（223 口已知埤塘，TWD97 → WGS84）
   !pip install -q gdown
   import gdown
   gdown.download(
       'https://drive.google.com/uc?id=1qwrIIELIJXbrBL_oCBTcoE-aoWq1bdXw',
       'taoyuan_ponds_223.geojson', quiet=False)
   ```

   **載入為 GEE FeatureCollection：**
   ```python
   import json
   with open('taoyuan_ponds_223.geojson') as f:
       ponds_geojson = json.load(f)

   pond_features = []
   for feat in ponds_geojson['features']:
       coords = feat['geometry']['coordinates']
       pond_features.append(ee.Feature(ee.Geometry.Point(coords)))
   ponds_fc = ee.FeatureCollection(pond_features)
   print(f"Loaded {len(pond_features)} known pond locations")
   ```

   **計算偵測率（Detection Rate）：**
   ```python
   # 用近期 MNDWI 水體圖（recent_water）在 223 個已知埤塘位置取樣
   mndwi_at_ponds = recent_water.unmask(0).sampleRegions(
       collection=ponds_fc, scale=30)
   detected = mndwi_at_ponds.filter(ee.Filter.eq('recent_water', 1)).size()
   total = ponds_fc.size()
   counts = ee.List([total, detected]).getInfo()

   print(f"Known ponds: {counts[0]}")
   print(f"MNDWI detected: {counts[1]}")
   print(f"Detection rate: {counts[1]/counts[0]*100:.1f}%")
   ```

   **分析與討論：**
   - MNDWI 閾值法（> 0.1）的偵測率是多少？
   - 有哪些埤塘沒被偵測到？可能的原因是什麼？（提示：面積太小、被植被覆蓋、季節性乾涸）
   - 如果要提高偵測率，你會怎麼調整閾值或方法？

**Deliverables:**
- [ ] Water frequency map (26-year water occurrence probability, Taoyuan)
- [ ] Pond change map (lost ponds in red, new water in green)
- [ ] Area estimate (hectares): lost pond area, new water area, net change
- [ ] Verification: MNDWI detection rate against 223 known ponds (偵測率 + 分析未偵測到的原因)
- [ ] Brief analysis (3–5 sentences): where have ponds disappeared? What does this mean for urban flood resilience?
- [ ] Code with comments

---

### Task 4: Vegetation Resilience Metrics + Summary (25%)

**目標：** 定義基線期（baseline）、衝擊期（impact）、恢復期（recovery），計算植被韌性指標（resilience metrics），並撰寫跨週整合摘要報告。

**Procedure：**

1. **Define three periods（定義三個時期）：**

   > **Note:** 課堂 Demo 使用更精確的時間切分（以地震日期 2024/04/03 為界：Baseline = 2020–2024/03, Impact = 2024/04–2024/12, Recovery = 2025/06–2026/03）。以下為簡化版，你也可以使用 Demo 的精確切分。

   ```python
   # Baseline period: 2020–2023 (pre-earthquake normal)
   baseline_ndvi = (ndvi_collection
       .filterDate('2020-01-01', '2023-12-31')
       .median())

   # Impact period: 2024 (earthquake year)
   impact_ndvi = (ndvi_collection
       .filterDate('2024-01-01', '2024-12-31')
       .median())

   # Recovery period: 2025–2026 (post-earthquake recovery)
   recovery_ndvi = (ndvi_collection
       .filterDate('2025-01-01', '2026-12-31')
       .median())
   ```

2. **Compute recovery ratio（韌性恢復比率）：**
   ```python
   # Recovery Ratio = (Recovery_NDVI - Impact_NDVI) / (Baseline_NDVI - Impact_NDVI)
   # Interpretation:
   #   RR > 1.0 → full recovery (exceeded baseline)
   #   RR = 1.0 → complete recovery (back to baseline)
   #   0 < RR < 1 → partial recovery
   #   RR = 0 → no recovery
   #   RR < 0 → continued degradation

   numerator = recovery_ndvi.subtract(impact_ndvi)
   denominator = baseline_ndvi.subtract(impact_ndvi)

   # Avoid division by zero: mask pixels where baseline ≈ impact (no damage)
   damage_mask = denominator.abs().gt(0.05)

   recovery_ratio = (numerator.divide(denominator)
       .updateMask(damage_mask)
       .rename('recovery_ratio')
       .clamp(-1, 2))  # Clamp extreme values
   ```

3. **Map resilience across study area：**
   - Visualize recovery ratio: red (< 0, degrading) → yellow (0–0.5, slow recovery) → green (0.5–1.0, recovering) → blue (> 1.0, exceeded baseline)
   - Compute zonal statistics: what percentage of damaged pixels are recovering?
   - Identify the most resilient and least resilient areas

4. **Integration summary report（跨週整合摘要報告）：**

   Write a structured summary (300–500 words) covering:

   **a. Cross-week connections（跨週連結）：**
   - W6 Kriging 空間內插 + W14 時序趨勢分析 = 時空全貌（space-time picture）
   - W8 single-scene NDVI → W14 26-year pixel-level trend: how has your understanding evolved?
   - W9 two-scene change detection → W14 multi-decadal trend: from snapshot to movie
   - W10 SAR → W13 SAR time series → how would SAR complement W14's optical analysis?
   - W12 land cover classification → fed by W14's exported composites?

   **b. W13 (6-year) vs W14 (26-year) comparison：**
   - What patterns are visible in 26 years that are invisible in 6 years?
   - What is the trade-off? (resolution: 10m vs 30m; temporal depth: 6 yr vs 26 yr)
   - When would you use Sentinel-2 vs Landsat for trend analysis?

   **c. Resilience assessment：**
   - Is the Taroko ecosystem showing signs of recovery after the 2024 earthquake?
   - How does the recovery ratio vary spatially? (valleys vs ridges, low elevation vs high)
   - Are there precedents in the 26-year record for similar disturbance-recovery cycles?

   **d. Limitations：**
   - Landsat's 30m resolution vs Sentinel-2's 10m — what details are lost?
   - L7 SLC-off striping artifact (post-2003): how does it affect the time series?
   - Cloud cover in mountain areas: how many valid observations per year on average?

**Deliverables:**
- [ ] Recovery ratio map with color-coded resilience classes
- [ ] Statistics: % of damaged pixels in each recovery class (degrading / slow / recovering / exceeded)
- [ ] Integration summary report (300–500 words)
- [ ] Code with comments

---

## Bonus 1: Multi-Index Dashboard (+10%)

**目標：** 同時計算 NDVI、MNDWI、NBR 三個指標的 26 年時序，製作多面板趨勢儀表板，分析不同指標是否講述不同的故事。

**Procedure：**

1. **Compute NBR alongside NDVI and MNDWI：**
   ```python
   def compute_indices(image):
       """Compute NDVI, MNDWI, and NBR for each image."""
       ndvi = image.normalizedDifference(['NIR', 'Red']).rename('NDVI')
       mndwi = image.normalizedDifference(['Green', 'SWIR1']).rename('MNDWI')
       nbr = image.normalizedDifference(['NIR', 'SWIR2']).rename('NBR')
       return (ndvi.addBands(mndwi).addBands(nbr)
           .copyProperties(image, ['system:time_start']))

   multi_index_col = landsat_all.map(compute_indices)
   ```

2. **Create annual time series for all three indices：**
   ```python
   # For each year, compute area-mean NDVI, MNDWI, NBR
   results = []
   for year in range(2000, 2027):
       yearly = (multi_index_col
           .filterDate(f'{year}-01-01', f'{year}-12-31')
           .median()
           .reduceRegion(
               reducer=ee.Reducer.mean(),
               geometry=aoi, scale=30, maxPixels=1e9))
       results.append({
           'year': year,
           'NDVI': yearly.get('NDVI').getInfo(),
           'MNDWI': yearly.get('MNDWI').getInfo(),
           'NBR': yearly.get('NBR').getInfo(),
       })
   ```

3. **Create multi-panel time series plot：**
   ```python
   fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
   indices = ['NDVI', 'MNDWI', 'NBR']
   colors = ['forestgreen', 'steelblue', 'darkorange']

   for ax, idx, color in zip(axes, indices, colors):
       values = [r[idx] for r in results]
       ax.plot(years, values, color=color, linewidth=1.5, marker='o', markersize=4)
       ax.axvline(x=2024, color='red', linestyle='--', alpha=0.7, label='2024 Earthquake')
       ax.set_ylabel(idx)
       ax.legend()
       ax.grid(True, alpha=0.3)

   axes[-1].set_xlabel('Year')
   fig.suptitle('Taroko Multi-Index Dashboard (2000–2026)', fontsize=14)
   plt.tight_layout()
   plt.savefig('multi_index_dashboard.png', dpi=150)
   ```

4. **Analysis：**
   - Do NDVI, MNDWI, and NBR show the same trend?（三個指標的趨勢一致嗎？）
   - Does NBR (burn ratio) capture disturbance events that NDVI misses?
   - Does MNDWI reveal hydrological changes that are invisible in vegetation indices?
   - Which index is the best single indicator for monitoring this area?

**Deliverables:**
- [ ] Multi-panel time series figure (NDVI, MNDWI, NBR, all 26 years)
- [ ] Brief analysis (3–5 sentences): do different indices tell different stories?
- [ ] Code with comments

---

## Bonus 2: NDVI Time-Lapse Animation — 26 Years (+10%)

**目標：** 製作太魯閣/秀林研究區 2000–2026 年的 NDVI 年度動畫 GIF，用 26 幀展現超過二十年的植被變化歷程。

**背景：** W13 的 Bonus 2 製作了 6 年的半年度動畫（13 幀）。本次要製作 26 年的年度動畫（27 幀），時間跨度是 W13 的四倍以上。在動畫中，你將能看到多次颱風破壞、2024 地震衝擊，以及長期的植被演替過程——這是靜態圖無法呈現的時間維度。

**Procedure：**

1. **建立年度 NDVI composite 序列（2000–2026）：**
   ```python
   import io, requests
   from PIL import Image, ImageDraw, ImageFont
   import imageio

   years = list(range(2000, 2027))  # 27 frames
   ndvi_palette = ['brown', 'yellow', 'green', 'darkgreen']
   ```

2. **對每一年產生 NDVI 中值合成縮圖：**
   ```python
   frames = []
   for year in years:
       composite = (ndvi_collection
           .filterDate(f'{year}-01-01', f'{year}-12-31')
           .median())

       thumb_url = composite.getThumbURL({
           'region': aoi,
           'dimensions': 512,
           'min': 0, 'max': 0.8,
           'palette': ndvi_palette,
       })
       response = requests.get(thumb_url)
       img = Image.open(io.BytesIO(response.content)).convert('RGB')

       # Add time label and event markers
       draw = ImageDraw.Draw(img)
       label = str(year)
       if year == 2024:
           label += ' ★ Earthquake'
       # Add more event markers as needed (e.g., major typhoons)
       draw.text((10, 10), label, fill='white')
       frames.append(img)
       print(f"  {year}: OK")
   ```

3. **組合為動畫 GIF：**
   ```python
   imageio.mimsave('taroko_ndvi_26yr_timelapse.gif',
                    [np.array(f) for f in frames],
                    duration=0.8,   # 0.8 seconds per frame
                    loop=0)         # infinite loop
   print("Saved: taroko_ndvi_26yr_timelapse.gif")
   ```

4. **進階挑戰（加分中的加分）：**
   - Add event markers for known typhoons (e.g., Typhoon Morakot 2009, Typhoon Soudelor 2015)
   - Add a color bar legend for NDVI values
   - Create a dual-panel animation: NDVI + MNDWI side by side
   - Add a running trendline that extends year by year

**技術提示：**
- 27 幀 = 約 21.6 秒的動畫（0.8 秒/幀），足以觀察長期變化
- GIF 檔案建議控制在 8 MB 以內（降低 `dimensions` 或壓縮品質）
- L7 SLC-off 問題可能導致某些年份的影像有條帶狀空缺（striping），標記為已知 artifact 即可
- 如果某年影像太少，可以將該幀標記為 "limited data"

**Deliverables:**
- [ ] Animation GIF file (`taroko_ndvi_26yr_timelapse.gif`)
- [ ] Code with comments
- [ ] Brief description (50–100 words): what are the three most visually striking moments in the animation?

---

## Bonus 3: Landsat × Sentinel-2 Cross-Sensor Change Detection (+10%)

**目標：** 結合 Landsat（30m, 26 年）和 Sentinel-2（10m, 6 年）的優勢，對太魯閣/秀林研究區的地震受損區進行多解析度變遷分析。

**背景：** 在課堂 D9b 中，我們展示了「望遠鏡 + 顯微鏡」策略：Landsat 找到長期趨勢中的變遷熱區，Sentinel-2 提供高解析度的細節驗證。這個 Bonus 要求你深入實作這個策略。

**Procedure：**

1. **Cross-sensor NDVI 一致性分析：**
   - 計算 2017–2026 重疊時段的年均 NDVI（兩個感測器都算）
   - 繪製散點圖 + 線性回歸，報告 R²
   - 分析：為什麼 Sentinel-2 的 NDVI 通常比 Landsat 高？（提示：pixel purity）

2. **多解析度地震損害評估：**
   - 用 Landsat 30m 和 Sentinel-2 10m 分別計算地震 ΔNDVI
   - 用閾值（例如 ΔNDVI < -0.15）分別框出「受損區域」
   - 比較受損面積：30m 和 10m 的估計差多少？為什麼？

3. **Landsat 趨勢引導的 S2 深入分析：**
   - 從 D5 的 26 年趨勢圖中，找出一個 browning hotspot（NDVI slope < -0.005/yr）
   - 用 Sentinel-2 的 10m 真彩色影像（pre vs post earthquake）深入檢視這個熱區
   - 描述你在 S2 高解析度影像中看到了什麼 Landsat 看不到的細節

4. **方法論反思（100–200 字）：**
   - 什麼情況下應該優先使用 Landsat？什麼情況下優先用 Sentinel-2？
   - 在你未來的研究（或期末提案）中，你會怎麼結合兩個感測器？

**Deliverables:**
- [ ] Cross-sensor scatter plot with R² (Landsat vs S2 annual NDVI)
- [ ] Multi-resolution damage area comparison table
- [ ] Hotspot zoom-in comparison (Landsat 30m vs S2 10m screenshots)
- [ ] Methodology reflection (100–200 words)
- [ ] Code with comments

---

## Technical Notes

### 常見問題

**Q: Band harmonization 後的波段名稱不一致導致報錯？**
- 確認 `harmonize_l57` 和 `harmonize_l89` 函數的輸入/輸出波段名稱一致
- 確認四個 collection merge 之後，所有影像都有相同的波段名稱：`['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']`
- Debug 技巧：`print(landsat_all.first().bandNames().getInfo())`

**Q: Scale factor 後反射率出現負值或大於 1？**
- `pixel * 0.0000275 + (-0.2)` 可能產生些微超出 [0, 1] 的值
- 使用 `.clamp(0, 1)` 截斷至合理範圍
- 負值通常表示水體或深陰影——在 NDVI 計算中不影響

**Q: Landsat 7 的 SLC-off 條帶問題？**
- L7 的 Scan Line Corrector 在 2003 年故障，此後影像有楔形空白條帶
- 使用年度 median composite 可以大幅減輕此問題（多張影像的條帶位置不同，取中值後自動填補）
- 如果仍有殘留條帶，可以考慮排除 L7 post-2003 資料，但會損失 2003–2012 間的時序密度

**Q: `linearFit()` 的 slope 單位是什麼？**
- slope 的單位是 NDVI per year（每年的 NDVI 變化量）
- 例如 slope = 0.002 表示每年平均 NDVI 增加 0.002，26 年累積增加 0.052
- 用 slope 乘以總年數可得累積變化量

**Q: Recovery ratio 出現極端值或 NaN？**
- 當 baseline NDVI ≈ impact NDVI（分母接近零）時，比率會爆炸
- 用 `damage_mask = denominator.abs().gt(0.05)` 遮罩掉未受損區域
- 用 `.clamp(-1, 2)` 截斷極端值

**Q: 26 年的年度循環跑很慢？**
- GEE `getInfo()` 是同步呼叫，27 次循環可能需要數分鐘
- 進階做法：用 `ee.FeatureCollection` + `ee.Reducer` 一次性計算所有年份，避免 Python 循環
- 或者用 `geemap.chart` 系列函數直接產生圖表

---

## Submission Format

1. **Notebook** (.ipynb) — 包含所有 4 個 Core Tasks 的程式碼和執行結果
2. **Exported GeoTIFF screenshots** — Google Drive 中的匯出檔案截圖（至少 trend map）
3. **Integration summary report** — Task 4 的 300–500 字摘要（可在 notebook 的 Markdown cell 中撰寫）
4. **簡短心得**（100–200 字）：
   - 26 年和 6 年的分析結果差異有多大？
   - 「韌性」（resilience）這個概念在防災管理中為什麼重要？
   - 從 W8 到 W14，ARIA 系統的演進給你什麼啟發？

上傳至 NTUCool 作業區。

---

## Grading Rubric

| 項目 | 配分 | 評分重點 |
|------|------|---------|
| Task 1: Landsat Harmonization + 26-yr NDVI | 25% | 波段調和正確性、scale factor 處理、時序圖品質、長期趨勢分析 |
| Task 2: Pixel-Level Trend Analysis | 25% | linearFit 使用正確性、slope map 品質、greening/browning 統計、W13 vs W14 比較 |
| Task 3: Taoyuan Pond Disappearance | 25% | MNDWI 計算、水頻率圖品質、埤塘消失分析、面積估算 |
| Task 4: Resilience Metrics + Summary | 25% | Recovery ratio 計算正確、韌性分類圖、Integration summary 深度與跨週連結 |
| **Bonus 1** | +10% | Multi-index dashboard（NDVI + MNDWI + NBR）、多指標比較分析 |
| **Bonus 2** | +10% | NDVI 26-year animation GIF（動畫品質、事件標記、變化說明） |
| **Bonus 3** | +10% | Landsat × S2 Cross-Sensor（跨感測器一致性分析、多解析度比較、方法論反思） |

---

## The Captain's Tip

> 「六年的資料讓你看到一個事件的前因後果。但二十六年的資料讓你看到一個生態系的心跳——它有季節的脈搏、有擾動後的恢復期、有長期的演替方向。指揮官不只要知道『地震破壞了多少』，更要知道『這片土地過去花了多少年從上一次災害中恢復，這次又需要多久。』這就是韌性分析的價值：它把快照變成心電圖，讓你判斷這個生態系是活的、在恢復中、還是正在衰退。記住，一張快照是情報，但數十年的趨勢線才是智慧。」

---

*Note: This homework does NOT require GPU. All GEE computation runs on Google's cloud servers. A regular laptop with internet access is sufficient. Landsat processing at 30m resolution is less computationally intensive than Sentinel-2 at 10m, so exports should be faster. If you encounter any issues, post on NTUCool or email Prof. Su.*
