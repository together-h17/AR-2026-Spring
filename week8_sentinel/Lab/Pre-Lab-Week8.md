# 第 8 週課前實驗：STAC API 與 Sentinel-2 雲端原生工作流程

> 請務必在上課前完成以下步驟，以確保您的環境已準備就緒。
> 預估時間：20–30 分鐘
> 目標：在第 8 週開始前，具備**搜尋、預覽與串流** Sentinel-2 衛星影像的能力——無需大量下載——並透過自己的程式碼見證 2025 年的 **馬太鞍溪堰塞湖事件**

---

## 為什麼這很重要（Captain 的直覺）

從第 3 週到第 7 週，ARIA 只知道**模型**預測了什麼。
從第 8 週開始，ARIA 將擁有**天空中的眼睛**——可以直接觀測地表實際發生狀況的衛星影像。

本週案例研究是 2025 年花蓮縣最具代表性的災害事件：**馬太鞍溪堰塞湖**。整個時間線就像一齣三幕劇，而每一幕都在可見光影像中留下清晰痕跡：

| 幕別           | 日期          | 事件                                                | 在 TCI 中將看到的內容       |
| ------------ | ----------- | ------------------------------------------------- | ------------------- |
| **前期（Pre）**  | 2025 年 6 月  | 颱風韋帕尚未侵襲，原始山林完整                                   | 茂密綠色森林山谷            |
| **中期（Mid）**  | 2025 年 8 月  | 7 月 21 日豪雨引發萬榮上游大規模崩塌，土石阻塞馬太鞍溪，形成約 **200 公尺深堰塞湖** | 原本森林位置出現全新的青綠色水體    |
| **後期（Post）** | 2025 年 10 月 | 9 月 23 日 14:50 潰決，30 分鐘內釋放 **1540 萬立方公尺** 洪水      | 湖泊消失，光復鄉出現新沉積物與結構損壞 |

這個案例對遙測來說最大的優點是：
**你不需要任何波段數學公式，也能直接看懂事件。**

只要載入三個日期的真彩色影像（TCI），你的眼睛就能理解整個故事。
後續波段運算只是將肉眼觀察結果進一步**量化**。

但有個問題：
單一張 Sentinel-2 影像瓦片約 600–800 MB，而三個時間點各自涵蓋 2 個瓦片。若全部下載，筆電很容易吃不消。

因此現代流程採用**雲端原生（cloud-native）**方法：

* 使用 **STAC（時空資產目錄）** 搜尋影像
* 使用內建 **TCI 真彩色預覽**
* 透過 `stackstac` + `rioxarray` 串流所需像素與波段

這就是遙測產業所說的 **glass-box protocol（玻璃盒協定）**：
你不必下載整本書，只需要透過玻璃直接閱讀內容。

---

## 步驟 1：安裝新套件

```bash
# 先啟動虛擬環境
# macOS / Linux:
source gis-env/bin/activate
# Windows:
gis-env\Scripts\activate

# STAC 與雲端原生 raster 核心套件
pip install pystac-client planetary-computer stackstac rioxarray

# 建議安裝：互動式預覽
pip install leafmap odc-stac
```

驗證安裝：

```python
import pystac_client
import planetary_computer
import stackstac
import rioxarray
import xarray as xr
print(f"pystac-client: {pystac_client.__version__}")
print(f"stackstac:      {stackstac.__version__}")
print(f"rioxarray:      {rioxarray.__version__}")
print("✅ 第 8 週套件已全部就緒！")
```

---

## 步驟 2：什麼是 STAC？（玻璃盒協定）

**STAC（SpatioTemporal Asset Catalog）** 是一種用來描述地理空間資料的 JSON 標準格式。

每個 STAC item 都包含：

* **Geometry**：影像覆蓋範圍
* **Datetime**：拍攝時間
* **Properties**：例如雲量 (`eo:cloud_cover`)
* **Assets**：各波段網址（B02、B03、B04、B08 等）與 TCI 預覽圖

這些網址對應的是 **COG（Cloud-Optimized GeoTIFF）**。

這代表你可以只讀取 256×256 的局部區塊，
而不必下載整張 10,000×10,000 的大影像。

---

## 步驟 3：第一次 STAC 查詢 —— 找出事件前基準影像

本週研究區域為：

**馬太鞍溪上游集水區 + 光復鄉**

```python
import pystac_client
import planetary_computer as pc

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=pc.sign_inplace,
)

mataian_bbox = [121.28, 23.56, 121.52, 23.76]

search_pre = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=mataian_bbox,
    datetime="2025-06-01/2025-07-15",
    query={"eo:cloud_cover": {"lt": 20}},
)

items_pre = search_pre.item_collection()
print(f"事件前（6 月–7 月上旬）：{len(items_pre)} 張乾淨影像")
```

預期結果：
應有 **2–6 張低雲量影像**

---

## 步驟 4：TCI 快速品質檢查（Quick QA）

Sentinel-2 L2A 提供內建 **TCI（True Color Image）**

這是預先處理好的 RGB 預覽圖，通常可在 2 秒內載入。

```python
import rioxarray as rxr
import matplotlib.pyplot as plt

best_pre = min(items_pre, key=lambda i: i.properties["eo:cloud_cover"])

tci_href = best_pre.assets["visual"].href
tci = rxr.open_rasterio(tci_href, overview_level=3)

fig, ax = plt.subplots(figsize=(8, 8))
tci.plot.imshow(ax=ax)
ax.set_title("TCI 預覽圖（事件前）")
plt.show()
```

> **規則：先看 TCI，再做波段運算。**

---

## 步驟 5：測試波段串流（stackstac）

```python
import stackstac

wanted_bands = ["B02", "B03", "B04", "B08", "B11", "B12"]

cube = stackstac.stack(
    [best_pre],
    assets=wanted_bands,
    epsg=32651,
    resolution=10,
    bounds_latlon=mataian_bbox,
    chunksize=2048,
)

print(f"Cube dims: {dict(cube.sizes)}")
print("✅ STAC 串流正常")
```

這裡得到的是延遲載入（lazy loading）的 `xarray.DataArray`

只有在 `.compute()` 時才真正下載資料。

---

## 步驟 6：更新 `.env`

```env
STAC_ENDPOINT=https://planetarycomputer.microsoft.com/api/stac/v1
S2_COLLECTION=sentinel-2-l2a
S2_CLOUD_MAX=20
S2_BANDS=B02,B03,B04,B08,B11,B12

MATAIAN_BBOX=121.28,23.56,121.52,23.76
TARGET_EPSG=32651
```

---

## 步驟 7：準備前幾週輸出資料

請確認以下檔案可使用：

* `shelters_hualien.gpkg`
* `hualien_network.graphml`
* `top5_bottlenecks.gpkg`

---

## 步驟 7b：自行建立 `guangfu_overlay.gpkg`（必做）

這是**必交課前作業**

請建立包含以下 5 個節點的 GeoPackage：

* 光復火車站
* 光復國小
* 光復鄉公所
* 台 9 線馬太鞍溪橋
* 佛祖街沉積區中心

**Why build it yourself?**
In Lab 2 you will see that spatial joining satellite findings with `shelters_hualien.gpkg` returns essentially zero hits. That's not a bug — it's the whole teaching point: **your SOP vector layers and your eyes in the sky are reporting different geographies, and when that happens, you trust the eyes and extend the layers**. Building this overlay is the "extending" half of that lesson.

**Required schema** (5 columns, 5 points minimum):

| column | type | description |
|---|---|---|
| `name` | str | English identifier, e.g. `Guangfu_Station` |
| `cn_name` | str | Chinese name, e.g. `光復火車站` |
| `node_type` | str | one of `shelter`, `critical_infra`, `bridge` |
| `priority` | int | 1 = highest (life-safety), 5 = lowest |
| `geometry` | Point | EPSG:4326 input, save as EPSG:3826 |

**Required nodes** (these are the five the Demo notebook expects):

| name | cn_name | node_type | priority | lon | lat |
|---|---|---|---|---|---|
| `Guangfu_Station` | 光復火車站 | critical_infra | 2 | 121.4235 | 23.6719 |
| `Guangfu_Elementary` | 光復國小 | shelter | 1 | 121.4240 | 23.6688 |
| `Guangfu_Township_Office` | 光復鄉公所 | shelter | 1 | 121.4210 | 23.6684 |
| `Mataian_Hwy9_Bridge` | 台9線馬太鞍溪橋 | bridge | 1 | 121.4100 | 23.6380 |
| `Foxu_Debris_Zone` | 佛祖街沉積區中心 | critical_infra | 3 | 121.4260 | 23.6640 |

**Starter code** (complete the `# TODO` lines yourself):

```python
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

# --- 1. Build the in-memory GeoDataFrame ---
rows = [
    {"name": "Guangfu_Station",        "cn_name": "光復火車站",        "node_type": "critical_infra", "priority": 2, "lon": 121.4235, "lat": 23.6719},
    {"name": "Guangfu_Elementary",     "cn_name": "光復國小",          "node_type": "shelter",        "priority": 1, "lon": 121.4240, "lat": 23.6688},
    {"name": "Guangfu_Township_Office","cn_name": "光復鄉公所",        "node_type": "shelter",        "priority": 1, "lon": 121.4210, "lat": 23.6684},
    {"name": "Mataian_Hwy9_Bridge",    "cn_name": "台9線馬太鞍溪橋",   "node_type": "bridge",         "priority": 1, "lon": 121.4100, "lat": 23.6380},
    {"name": "Foxu_Debris_Zone",       "cn_name": "佛祖街沉積區中心",  "node_type": "critical_infra", "priority": 3, "lon": 121.4260, "lat": 23.6640},
]

# TODO 1: Convert `rows` into a GeoDataFrame.
#   - geometry column should be built with Point(lon, lat)
#   - initial CRS is EPSG:4326 (WGS84 lon/lat)

gdf = gpd.GeoDataFrame(
    rows,
    geometry=[Point(r["lon"], r["lat"]) for r in rows],
    crs="EPSG:4326",
).drop(columns=["lon", "lat"])

# TODO 2: Reproject to EPSG:3826 (TWD97 / TM2 — Taiwan official)
gdf_3826 = gdf.to_crs("EPSG:3826")

# TODO 3: Ensure the output folder exists
out_path = Path("data/guangfu_overlay.gpkg")
out_path.parent.mkdir(parents=True, exist_ok=True)

# TODO 4: Save as GeoPackage, driver="GPKG", layer="guangfu"
gdf_3826.to_file(out_path, driver="GPKG", layer="guangfu")

print(f"✅ Saved {len(gdf_3826)} nodes → {out_path}")
print(gdf_3826[["name", "cn_name", "node_type", "priority"]])
```

**Verification** (run after the script above):

```python
# Verify the file is readable and the schema is correct
check = gpd.read_file("data/guangfu_overlay.gpkg", layer="guangfu")
assert len(check) == 5,               f"Expected 5 rows, got {len(check)}"
assert check.crs.to_epsg() == 3826,   f"Expected EPSG:3826, got {check.crs}"
assert set(check["node_type"]) == {"shelter", "critical_infra", "bridge"}, \
       "node_type must include all three categories"
print("✅ guangfu_overlay.gpkg passes all schema checks")
```

Expected output:

```
✅ Saved 5 nodes → data/guangfu_overlay.gpkg
                    name          cn_name       node_type  priority
0        Guangfu_Station      光復火車站  critical_infra         2
1    Guangfu_Elementary          光復國小         shelter         1
2 Guangfu_Township_Office        光復鄉公所         shelter         1
3    Mataian_Hwy9_Bridge  台9線馬太鞍溪橋          bridge         1
4       Foxu_Debris_Zone   佛祖街沉積區中心  critical_infra         3
✅ guangfu_overlay.gpkg passes all schema checks
```

> **Safety net**: The Demo notebook's Cell [17] has a `try/except` that will still run even if `guangfu_overlay.gpkg` is missing — it will generate synthetic fallback nodes automatically. That's there so a single misplaced file can't brick the entire Lab 2. But **if you want full credit on Homework Part D, you must have your own real `guangfu_overlay.gpkg`** — the fallback is for robustness, not for skipping the exercise.

> **Optional bonus**: Add 2–3 more nodes of your own choosing (e.g., 光復國中, 光復醫院, 大富火車站). Just make sure they fall inside `MATAIAN_BBOX`. Document them in your Pre-lab submission notebook.


---

## 步驟 8（選讀）：複習重要概念

請確認熟悉以下內容：

* 電磁頻譜
* 光譜特徵
* DN 與反射率
* COG
* xarray DataArray

---

## 疑難排解

**Q：`pystac_client` 無法 import？**
A：重新啟動虛擬環境並更新套件

**Q：STAC 搜尋結果為 0？**
A：確認 bbox 順序為 `(lon_min, lat_min, lon_max, lat_max)`

**Q：TCI 全白？**
A：代表該景影像雲層過多，請更換影像

---

> *「STAC catalog 就像圖書館索書卡——你不必把整本書帶回家，只需在架上閱讀。」*
> *「而在馬太鞍案例中，這本書剛好記錄了一座只存在 64 天的湖泊。」*

