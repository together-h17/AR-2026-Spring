# ARIA v2 技術修正紀錄（Technical Fixes）

## 一、問題概述

在進行避難所風險分析（河川距離 + 地形分析）與資料輸出過程中，出現以下幾類常見錯誤：

1. GeoDataFrame 建立錯誤（scalar value）
2. Spatial Join 欄位衝突（`index_right`）
3. 多 geometry 欄位導致無法匯出

本文件整理問題原因與對應修正方式。

---

## 二、問題與修正

### 1️⃣ GeoDataFrame 建立錯誤

**錯誤訊息**

```
ValueError: If using all scalar values, you must pass an index
```

**原因**

```python
{'risk_level': 'high'}
```

為 scalar，但 geometry 為多筆資料，長度不一致。

**修正方式**

```python
buffer_geom = rivers_target.buffer(BUFFER_HIGH)

buffer_high_gdf = gpd.GeoDataFrame(
    {'risk_level': ['high'] * len(buffer_geom)},
    geometry=buffer_geom,
    crs='EPSG:3826'
)
```

**最佳實務（推薦）**
將 buffer 合併為單一幾何：

```python
buffer_high_gdf = gpd.GeoDataFrame(
    {'risk_level': ['high']},
    geometry=[rivers_target.buffer(BUFFER_HIGH).union_all()],
    crs='EPSG:3826'
)
```

---

### 2️⃣ Spatial Join 欄位衝突

**錯誤訊息**

```
ValueError: 'index_right' cannot be a column name in the frames being joined
```

**原因**
前一次 `sjoin()` 已產生 `index_right`，再次 join 時衝突。

**修正方式**
在每次 `sjoin()` 前清除欄位：

```python
df = df.drop(columns=['index_right', 'index_left'], errors='ignore')
```

**建議寫法**

```python
left = shelters_in_county.drop(columns=['index_right', 'index_left'], errors='ignore')
right = buffer_high_gdf.drop(columns=['index_right', 'index_left'], errors='ignore')

result = gpd.sjoin(left, right, predicate='within', how='left')
```

---

### 3️⃣ Spatial Join 判斷錯誤（隱性問題）

**問題**
使用 `how='left'` 時，所有資料都會保留，不能直接用 index 判斷是否落在 buffer。

**修正方式**

```python
valid_idx = result[result['index_right'].notna()].index
```

---

### 4️⃣ 多 Geometry 欄位錯誤

**錯誤訊息**

```
ValueError: GeoDataFrame contains multiple geometry columns
```

**原因**
資料中存在：

* `geometry`（主幾何）
* `analysis_buffer`（額外幾何）

---

## 三、解決方案

### ✅ 方法一（推薦）：移除額外 geometry

```python
shelters_export = shelters_enhanced.drop(columns=['analysis_buffer'])
shelters_export.to_file('outputs/ARIA_v2_shelters_enhanced.gpkg', driver='GPKG')
```


# buffer layer
analysis_buffers = shelters_enhanced[['shelter_id', 'name', 'analysis_buffer']].copy()
analysis_buffers = analysis_buffers.set_geometry('analysis_buffer')

analysis_buffers.to_file(
    'outputs/ARIA_v2_shelters_enhanced.gpkg',
    layer='analysis_buffers',
    driver='GPKG'
)
```

---

## 四、最佳實務總結

### 🔹 GeoDataFrame 建立

* 避免 scalar + geometry 混用
* 使用 list 或單一 union geometry

### 🔹 Spatial Join

* 每次 join 前清除 `index_right`
* 判斷結果要用 `.notna()`

### 🔹 Geometry 管理

* 每個 GeoDataFrame 只保留一個 active geometry
* 分析用 geometry 建議：

  * 分 layer
  * 或轉 WKT

### 🔹 CRS 管理

* 統一使用 `EPSG:3826`（台灣常用投影）
* buffer / area 計算前務必轉投影

---

## 五、建議優化方向（ARIA v2 → v3）

1. 改用 `intersects()` + union geometry 取代多次 `sjoin`
2. 將 buffer / terrain analysis 模組化
3. 建立自動 QA 檢查：

   * geometry 欄位數量
   * CRS 一致性
   * NaN 比例
4. 輸出標準化（GeoPackage 多 layer）

---

## 六、結論

本次問題主要來自：

* GeoPandas 結構限制（單一 geometry）
* Spatial Join 自動欄位機制
* geometry 管理不一致

經修正後，資料流程將：

* 更穩定
* 更符合 GIS 標準
* 更易於後續擴展（ARIA v3）

---
