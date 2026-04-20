# ARIA v4.0 - 花蓮災害可達性評估系統

## 專案概述

本專案建立一套整合道路網路、降雨資料與地形風險的災害可達性評估系統，用於分析颱風期間花蓮地區的交通瓶頸、道路壅塞與避難設施可達性變化。

主要分析內容包括：

- 使用 OSMnx 擷取花蓮道路網路
- 計算道路節點介數中心性
- 整合真實雨量站資料建立動態壅塞模型
- 評估災前／災後等時線範圍
- 分析可達面積收縮比例

---

## 資料來源

- **道路網路**：OpenStreetMap（透過 OSMnx 擷取）
- **降雨資料**：Week 5 中央氣象署 JSON 測站資料（鳳凰颱風）

---

## AI 診斷紀錄

### 1. OSMnx 道路網路擷取

**問題：**  
在擷取花蓮道路網路時，曾出現 Overpass API 讀取速度較慢與 timeout 問題。

**解決方式：**  
改用較小搜尋範圍（以花蓮市為主），並於第一次成功擷取後儲存為 `.graphml`，避免重複下載。

```python
ox.save_graphml(G_proj, "hualien_network.graphml")
````

後續分析皆直接讀取本地 GraphML 檔案，提高穩定性與效率.


### 動態壅塞權重錯誤（NoneType 比較錯誤）

**問題：**

```python
TypeError: '>=' not supported between instances of 'NoneType' and 'float'
```

**原因：**
部分 edge 的 `congestion_factor` 為 `None`，導致以下判斷失敗：

```python
if cf >= 0.95:
```

主要原因為 `rain_to_congestion()` 在部分條件下沒有回傳值。

**解決方式：**
重寫函式，確保任何情況皆回傳 `float`。

```python
def rain_to_congestion(rainfall_mm):
    if rainfall_mm is None:
        return 0.0
    if rainfall_mm < 10:
        return 0.0
    elif rainfall_mm < 40:
        return 0.3
    elif rainfall_mm < 80:
        return 0.6
    else:
        return 0.9
```

並在動態權重函式中加入防呆：

```python
if cf is None:
    cf = 0.0
```

---

### 5. 真實雨量資料整合

**問題：**
原始 S10 使用隨機模擬雨量：

```python
np.random.choice(...)
```

不符合實際作業需求。

**解決方式：**
改用中央氣象署真實測站 JSON：

```python
rainfall_data["records"]["Station"]
```

抽取：

* `StationName`
* `StationLongitude`
* `StationLatitude`
* `Past1hr.Precipitation`

再透過 `gpd.sjoin_nearest()` 將每條道路中點配對至最近雨量站。

---

## 核心分析發現

* **最脆弱交通瓶頸：** 花蓮市主要幹道路口節點（Top 1 Centrality Node）
* **最大可達性損失：** 災後 10 分鐘等時線面積明顯縮小
* **優先救援順序：**

  1. 高 centrality 且高 terrain risk 節點
  2. 醫療設施周邊道路
  3. 避難所連外道路

