# 第 7 週作業：ARIA v4.0（無障礙稽核員）

**繳交期限：下次上課前**

---

## 1. 情境說明

指揮官不僅想知道「**危險區域在哪裡**」，更重要的是：

**「哪些區域已經變成孤島？」**

鳳凰颱風在蘇澳造成 **130.5 mm/hr 的極端降雨**，導致蘇花公路淹水，以及花蓮山區道路中斷。

你的任務是升級 ARIA 系統，透過網路分析評估：

**「災害期間可達性如何崩潰」**

### 與課堂實驗的主要差異

* 實驗 1 使用台大校園做瓶頸分析
  → **本作業改用花蓮市／秀林鄉真實道路網路**
* 實驗 2 使用簡化版 `congestion_factor`
  → **本作業整合第 5 週 / 第 6 週真實降雨資料**
* 課堂僅從單一起點計算等時線
  → **本作業需比較多個重要設施的可達性變化**

---

## 2. 資料來源

### A. 道路網路資料

* **OSMnx**：從 OpenStreetMap 擷取花蓮市（或指定花蓮縣鄉鎮）道路網路
* 使用 `network_type='drive'`
* 儲存為 `.graphml`

---

### B. 前幾週成果資料

* **第 3 週避難所** GeoDataFrame
  （包含河川距離分類）
* **第 4 週地形風險**

  * `mean_elevation`
  * `max_slope`
  * `terrain_risk`
* **第 5 週降雨資料**

  * 鳳凰颱風 `fungwong_202511.json`
* **第 6 週 Kriging 輸出**

  * `kriging_rainfall.tif`
  * （建議使用，但非必須）

---

### C. 鄉鎮行政區界線

* TGOS（國土測繪中心）鄉鎮市區界 shapefile

---

## 3. 核心要求

必須以 **`.ipynb`（Jupyter Notebook）格式**繳交。

---

## A. 道路網路擷取與封存

1. 擷取 **花蓮市**（或指定行政區）汽車道路網路
2. 投影至 **EPSG:3826（公尺座標）**
3. 計算每條道路的旅行時間

```python
travel_time = length / (speed / 3.6)
```

* `speed` 來自 OSM `maxspeed`
* 若缺值，預設 **40 km/h**

4. 儲存為 `.graphml`
   （避免重複下載）

---

## B. 瓶頸與風險診斷

1. 計算道路網路的 **介數中心性（Betweenness Centrality）**
2. 找出 **前 5 個瓶頸節點**
3. 將 Top 5 節點與第 4 週 `terrain_risk` 疊圖：

* 使用 `gpd.sjoin()`
* 或 nearest-neighbor 方法

判斷這些節點的 `terrain_risk`

4. 找出：

**最脆弱交通樞紐**
（高 centrality + 高 terrain_risk）

5. 視覺化：

在道路網路圖上顯示 Top 5 節點

* 顏色 = `terrain_risk`

---

## C. 動態可達性分析

### 1. 定義降雨 → 壅塞映射函數

```python
rain_to_congestion(rain_mm)
```

使用課堂公式：

```python
travel_time_adj = length / (speed × (1 − cf))
```

降雨分級請自行設計
（參考課堂 Slide 12）

---

### 2. 指定降雨資料來源（二選一）

### 選項 A（推薦）

使用第 6 週：

```python
kriging_rainfall.tif
```

在道路中點進行 raster sampling

---

### 選項 B

使用第 5 週雨量站資料：

* buffer
* `sjoin`

對道路分段套用降雨值

---

### 3. 選擇 5 個關鍵設施

（避難所或醫院）

對每個設施計算：

* **災前等時線**

  * 5 分鐘
  * 10 分鐘
* **災後等時線**

  * 5 分鐘
  * 10 分鐘

---

### 4. 計算面積收縮率

```python
shrinkage = 1 − (A_after / A_before)
```

---

### 5. 整理成可達性影響表

| 設施  | 災前 5 分鐘 (km²) | 災後 5 分鐘 (km²) | 收縮率 % | 災前 10 分鐘 | 災後 10 分鐘 | 收縮率 % |
| --- | ------------: | ------------: | ----: | -------: | -------: | ----: |
| ... |           ... |           ... |   ... |      ... |      ... |   ... |

---

## D. AI 策略簡報（加分）

1. 安裝

```python
google-generativeai
```

2. 將以下資料送入 AI 工具
   （ChatGPT / Gemini / Claude 均可）

* 可達性影響表
* Top 5 瓶頸
* 孤立設施資訊

3. Prompt 身分設定：

**花蓮縣防災指揮中心交通顧問**

4. AI 報告須包含：

* 優先搶通路段與原因
* 孤島區域替代救援方式
* 資源配置優先順序

---

### 加分 Prompt 範例

```python
prompt = f"""你是花蓮縣防災指揮中心交通顧問。
以下為鳳凰颱風道路網路分析結果：
Top 5 瓶頸節點: {top5_info}
可達性影響表: {accessibility_table}
孤立設施: {isolated_shelters}

請以專業防災語言提供：
1. 優先搶通道路
2. 替代救援方式
3. 資源配置建議"""
```

---

## E. 專業標準（Infrastructure First）

1. **環境變數**
   將壅塞參數與搜尋半徑寫入 `.env`

2. **GraphML 封存**
   道路只下載一次，後續直接讀 `.graphml`

3. **Markdown Cells**
   每步分析前撰寫：

**Captain’s Log**

4. **AI 診斷紀錄**
   README 至少描述一項問題解法：

* OSMnx timeout
* 等時線 polygon 異常
* raster 採樣 nodata
* 道路中斷導致 `NetworkXNoPath`
* 缺失道路速度屬性

---

## 4. 推薦程式撰寫 Prompt

> 我要建立 ARIA v4.0 —— 基於網路的災害可達性系統。
> 我有：
>
> 1. 第 3–4 週 shelter GeoDataFrame（EPSG:3826）
> 2. 第 5 週降雨 JSON 或第 6 週 Kriging GeoTIFF
>
> 請幫我分 Jupyter cells 完成：
>
> 1. 使用 OSMnx 擷取花蓮市道路
> 2. 計算 travel_time
> 3. 計算介數中心性
> 4. 與 W4 terrain_risk 疊圖
> 5. 建立 rain_to_congestion()
> 6. 採樣 raster 或雨量站
> 7. 套用動態權重
> 8. 計算 5 個避難所災前後等時線
> 9. 計算面積收縮率
> 10. 儲存 graphml 與 summary table

---

## 5. 繳交項目

1. **GitHub Repo URL**
2. **`ARIA_v4.ipynb`**
3. **`hualien_network.graphml`**
4. **`README.md`**
5. **Accessibility Impact Table**

---

## 6. 評分標準

| 項目                           |  配分 |
| ---------------------------- | --: |
| 道路網路 + travel_time + GraphML | 15% |
| 介數中心性 + Top 5 + W4 疊圖        | 20% |
| 動態可達性分析                      | 30% |
| 專業標準                         | 15% |
| 視覺化品質                        | 10% |
| AI 策略簡報（加分）                  | 10% |

---

## 7. 提示與注意事項

* **CRS 必須一致**
  全部使用 `EPSG:3826`

* **速度預設值**
  建議：

```python
primary = 60
secondary = 40
residential = 30
```

* **等時線 polygon**
  可使用：

```python
alphashape
shapely.concave_hull()
```

* **效能**
  花蓮市約 3000 nodes
  全縣約 30000 nodes

* **道路中斷判定**

```python
congestion_factor >= 0.95
```

視為不可通行

---

> **風險地圖告訴你哪裡壞了。
> 網路分析告訴你，是否還來得及救人。**
