# 第 7 週課前實驗：OSMnx 與網路分析環境準備

> 請務必於**上課前**完成以下步驟，以確保你的環境已準備完成。
> 預估時間：15–20 分鐘

---

## 步驟 1：安裝新套件

```bash
# 請先啟用你的虛擬環境！
# macOS / Linux：
source gis-env/bin/activate

# Windows：
gis-env\Scripts\activate

# 安裝 OSMnx（道路網路）與 NetworkX（圖論演算法）
pip install osmnx networkx

# 安裝 rasterio（用於將第 6 週 Kriging 輸出整合至網路分析）
pip install rasterio
```

確認安裝是否成功：

```python
import osmnx as ox
import networkx as nx
import rasterio
from shapely.geometry import Point, Polygon

print(f"OSMnx 版本：{ox.__version__}")
print(f"NetworkX 版本：{nx.__version__}")
print(f"Rasterio 版本：{rasterio.__version__}")
print("✅ 第 7 週所需套件已準備完成！")
```

> **注意**：OSMnx 會自動安裝 `geopandas`、`shapely`、`requests` 等相依套件。
> `rasterio` 需另外安裝，用來讀取第 6 週的 Kriging GeoTIFF，並將降雨量映射至道路權重。
> 若先前環境正常，通常只需安裝 `osmnx` 與 `rasterio` 即可。

---

## 步驟 2：測試 OSMnx — 抓取小型道路網路

```python
import osmnx as ox

# 抓取台大周邊的小型道路網路
G = ox.graph_from_address(
    "National Taiwan University, Taipei",
    dist=500,
    network_type='drive'
)

# 基本資訊
print(f"節點數（路口）：{G.number_of_nodes()}")
print(f"邊數（路段）：{G.number_of_edges()}")

# 投影為公尺座標系（EPSG:3826）
G_proj = ox.project_graph(G, to_crs='EPSG:3826')

print(f"CRS：{G_proj.graph['crs']}")
print("✅ OSMnx 道路網路抓取功能正常！")
```

> **故障排除**：若出現 timeout 錯誤，可能是網路問題。
> OSMnx 會透過 OpenStreetMap 的 Overpass API 抓取資料，偶爾回應較慢。請稍後幾分鐘再試一次。

---

## 步驟 3：測試 NetworkX — 基本圖論操作

```python
import networkx as nx

# 中介中心性（Betweenness Centrality）— 找出瓶頸節點
centrality = nx.betweenness_centrality(G, weight='length')

# 最重要的前三個路口
top_nodes = sorted(
    centrality,
    key=centrality.get,
    reverse=True
)[:3]

for node in top_nodes:
    print(f"  節點 {node}: centrality = {centrality[node]:.4f}")

print("✅ NetworkX 圖論演算法運作正常！")
```

---

## 步驟 4：更新 `.env` 檔案

請在專案的 `.env` 中加入第 7 週設定：

```env
# 第 7 週新增設定 — 路網分析
NETWORK_DIST=5000
ISOCHRONE_MINUTES=5,10,15

# 塞車係數門檻（降雨 mm → 壅塞因子）
# <10mm → cf=0, 10-40mm → cf=0.3, 40-80mm → cf=0.6, >80mm → cf=0.9
CONGESTION_METHOD=threshold
CONGESTION_BREAK_1=10
CONGESTION_BREAK_2=40
CONGESTION_BREAK_3=80

# AI 顧問（第 7 週 Cell [16]，可選）
GOOGLE_API_KEY=your-gemini-api-key-here

# 保留先前設定
CWA_API_KEY=CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
APP_MODE=SIMULATION
SIMULATION_DATA=data/scenarios/fungwong_202511.json
PROJECT_CRS=3826
TARGET_COUNTY=花蓮縣
SLOPE_THRESHOLD=30
```

> **⚠️ 塞車係數說明**：課堂中將採用 threshold 方法，將時雨量分為四級（正常／略慢／嚴重延滯／幾乎無法通行）。
> 門檻值 10 / 40 / 80 mm 對應台灣氣象署降雨強度分級。

---

## 步驟 5：準備第 6 週輸出成果

本週內容將延續第 6 週的 Kriging 結果，請確認你已具備：

* **`kriging_rainfall.tif`** — Kriging 插值降雨圖（EPSG:3826）
* **`kriging_variance.tif`** — Kriging 變異數 / sigma 圖（EPSG:3826）

這些 GeoTIFF 將用於依據預測降雨強度設定**動態道路權重**，即使該區域沒有雨量站也可使用。

> **若尚未有這些檔案**：仍可完成第 7 週內容，使用模擬權重即可。
> 老師會示範如何利用 Kriging raster 結果進行道路加權，但核心網路分析邏輯可獨立運作。

---

## 步驟 6（選修）：複習核心概念

請確認你熟悉以下概念：

* **圖論基礎**：節點（vertices）、邊（edges）、有向圖與無向圖
* **最短路徑**：Dijkstra 演算法概念（不需自行實作）
* **等時線（Isochrone）**：從一點出發，X 分鐘內可到達多遠？
  （可視為 buffer zone 的現實世界版本）
* **中介中心性（Betweenness Centrality）**：哪些節點位於最多最短路徑上？
  （瓶頸識別）
* **動態加權（Dynamic Weighting）**：降雨 / 淹水如何影響道路通行時間
* **GraphML 格式**：XML 圖形檔格式
  （將使用 `ox.save_graphml()` / `ox.load_graphml()`）
* **GeoPandas CRS**：`.to_crs()` 與為何 EPSG:3826（公尺）對距離計算至關重要
* **第 5–6 週 ARIA 輸出**：避難所風險等級、降雨資料、Kriging GeoTIFF 成果

---

## 常見問題排除（Troubleshooting）

**Q：`osmnx` 匯入失敗，出現 `No module named 'osmnx'`？**
A：請確認已啟用虛擬環境。可再執行：

```bash
pip install --upgrade osmnx
```

---

**Q：`ox.graph_from_address()` 發生錯誤？**
A：請確認網路連線正常。OSMnx 需要即時連線至 OpenStreetMap。
若位於防火牆環境，請聯絡網管開放 `overpass-api.de`。

---

**Q：圖形結果為 0 個節點？**
A：搜尋範圍可能太小，或 `network_type` 與實際道路類型不符。
請嘗試增加 `dist`，或改用：

```python
network_type='all'
```

---

**Q：`ox.project_graph()` 出現 CRS 警告？**
A：這是正常現象，OSMnx 有時會自動偵測不同本地 CRS。
可強制指定：

```python
ox.project_graph(G, to_crs='EPSG:3826')
```

---

**Q：Windows 上 `rasterio` 安裝失敗？**
A：請嘗試：

```bash
pip install rasterio --no-binary rasterio
```

或使用 conda：

```bash
conda install -c conda-forge rasterio
```

若仍失敗，仍可完成核心網路分析；
Raster-to-Network 整合（Cell [14]）屬進階內容。

---

**Q：什麼是塞車係數（congestion factor）？**
A：課堂中會使用 `rain_to_congestion()` 函數，將降雨量轉換為 0～0.9 的係數。

公式如下：

```python
travel_time_adj = length / (speed * (1 - cf))
```

其中：

* `cf = 0` → 正常通行
* `cf = 0.9` → 幾乎無法通行

門檻值 10 / 40 / 80 mm 已寫入 `.env`。
