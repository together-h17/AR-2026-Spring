# ARIA v3.0 — 鳳凰颱風動態風險監測系統

## 專案概述

本專案實作 **ARIA v3.0（The Living Auditor）**，建立一套可即時監測避難所風險的動態災害衝擊評估系統。

本系統整合以下成果：

* **第 3 週**：河川距離風險分析
* **第 4 週**：地形坡度風險分析
* **第 5 週**：即時與歷史雨量動態監測

系統目標是回答：

> **目前哪些避難所風險最高？**

系統支援兩種模式：

* **LIVE 模式** → 中央氣象署即時 API
* **SIMULATION 模式** → 鳳凰颱風歷史雨量快照

最終輸出為一份可互動的 Folium 地圖：

```text id="z6rtgk"
ARIA_v3_Fungwong.html
```

---

## 核心功能

### 1. 模式切換器（Mode Switcher）

系統透過 `.env` 讀取設定：

```text id="2m10ys"
APP_MODE=LIVE
APP_MODE=SIMULATION
```

可在即時模式與模擬模式間切換。

---

### 2. 雨量資料整合

資料來源包含：

* 中央氣象署（CWA）即時 API
* CoLife 歷史快照 JSON

使用資料：

```text id="9uzn4w"
fungwong_202511.json
```

---

### 3. 空間風險分析

分析流程包含：

* 雨量站 GeoDataFrame 建立
* CRS 轉換至 `EPSG:3826`
* 建立 5 公里降雨影響範圍
* 與避難所資料做 spatial join
* 動態風險分級

---

### 4. 動態風險分級邏輯

```text id="wxtzmo"
CRITICAL：雨量 > 80 mm/hr
URGENT：雨量 > 40 且地形高風險
WARNING：雨量 > 40 或地形高風險
SAFE：其餘
```

---

### 5. 互動式視覺化

使用 **Folium** 建立互動地圖，包含：

* 雨量站 CircleMarker
* HeatMap
* 避難所標記
* LayerControl
* Popup 風險資訊

---

## 輸出檔案

```text id="7s48zj"
ARIA_v3.ipynb
ARIA_v3_Fungwong.html
README.md
```

---

## 專案結構

```text id="smyznj"
Homework/
│
├── ARIA_v3.ipynb
├── README.md
├── .env
│
├── data/
│   fungwong_202511.json
│
└── outputs/
    ├── ARIA_v2_shelters_enhanced.gpkg
    └── ARIA_v3_Fungwong.html
```

---

# AI 診斷日誌（AI Diagnostic Log）

本段紀錄本次作業開發過程中的問題診斷與修正流程。

---

## 問題 1：CWA API 成功但雨量全為 0

### 問題描述

API 測試成功回傳：

```text id="9djvcz"
九份二山: 0.0 mm/hr
基隆: 0.0 mm/hr
淡水: 0.0 mm/hr
```

雖然成功，但所有雨量值皆為 `0.0`。

---

### 問題診斷

這並非 API 錯誤。

查詢欄位為：

```python id="mqhq3q"
Past1hr -> Precipitation
```

代表：

> 過去 1 小時累積雨量

當查詢時段無降雨，回傳 `0.0` 為正常結果。

---

### 解決方式

透過以下方式確認 API 正常：

* 增加 `limit`
* 移除 `limit`
* 改用 `SIMULATION mode`

確認 API 可正常運作。

---

## 問題 2：JSON 無法使用 GeoPandas 載入

### 問題描述

出現錯誤：

```text id="7rrtxz"
DataSourceError: not recognized as being in a supported file format
```

---

### 問題診斷

原本使用：

```text id="kmcr41"
terrain_risk_audit.json
```

該檔案屬於摘要報告 JSON，並非空間資料格式。

缺少：

```text id="w2jxjh"
geometry
coordinates
```

因此：

```python id="d8s1kb"
gpd.read_file()
```

無法讀取。

---

### 解決方式

改用正確空間資料：

```text id="1ucw57"
ARIA_v2_shelters_enhanced.gpkg
```

此檔案已包含：

* geometry
* risk_level
* 坡度統計
* 避難所座標

完全符合 Week 5 作業需求。

---

## 問題 3：CRS 不一致導致空間疊合失敗

### 問題描述

若 CRS 不一致，`sjoin()` 可能回傳空結果。

---

### 解決方式

在空間疊合前加入檢查：

```python id="zhzwim"
assert str(shelters.crs) == str(rain_buffer.crs)
```

統一轉換為：

```text id="73t42u"
EPSG:3826
```

成功解決問題。

---

## 心得反思

本次作業讓我更深入理解：

* 資料格式驗證的重要性
* CRS 一致性對空間分析的影響
* fallback 機制的必要性
* GIS 專案流程的專業實務

系統已可在鳳凰颱風情境下執行動態風險監測。
