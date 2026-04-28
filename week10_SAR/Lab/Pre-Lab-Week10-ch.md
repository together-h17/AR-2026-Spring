以下為**完整逐字翻譯（保留原結構與內容）**：

---

# Week 10 預習實驗：SAR 與感測器融合 — ARIA v7.0 設定

**課程：** 台大遙測與空間資訊之分析與應用（NTU Remote Sensing & Spatial Information Analysis）
**授課教師：** 蘇文瑞教授（Prof. Su Wen-Ray）
**週次：** 第 10 週 | **主題：** 全天候監測與感測器融合（All-Weather Monitoring & Sensor Fusion）
**所需時間：** 約 20 分鐘

---

## 目標

在完成本預習實驗後，你將能夠：

* 確認你的 W8/W9 環境與結果仍然可使用
* 安裝 SAR 專用 Python 套件（rasterio、rioxarray）
* 理解 SAR 的基本物理原理（雷達後向散射，radar backscatter）
* 複習感測器融合（sensor fusion）的概念，以及其在災害監測中的重要性
* 為將 W9 光學變遷偵測結果與 SAR 資料融合做好準備

---

## 步驟 1：確認 Week 8/9 環境

### 1a. 啟動你的虛擬環境

```bash
# conda 範例
conda activate remo_w8
# 或使用 venv
source ~/remo_env/bin/activate
```

### 1b. 確認關鍵套件可用

```python
import pystac_client
import stackstac
import sklearn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio

print("✓ pystac_client:", pystac_client.__version__)
print("✓ rasterio:", rasterio.__version__)
print("✓ 所有核心套件載入成功")
```

如果有任何 import 失敗，請安裝：

```bash
pip install pystac_client stackstac scikit-learn rasterio rioxarray
```

---

## 步驟 2：安裝 SAR 專用套件

本週需要新增 `rasterio` 與 `rioxarray`，用於讀取預處理後的 SAR GeoTIFF 檔案。

```bash
pip install rasterio rioxarray
```

**驗證安裝：**

```python
import rasterio
import rioxarray
print("✓ rasterio:", rasterio.__version__)
print("✓ rioxarray 已可用於 SAR GeoTIFF 載入")
```

---

## 步驟 3：SAR 物理原理 — 概念複習

### 什麼是 SAR？

**SAR（Synthetic Aperture Radar，合成孔徑雷達）**是一種**主動式（active）**遙測系統：

* 衛星會**發射**微波訊號，並**接收**回傳訊號（後向散射，backscatter）
* 使用微波波長（Sentinel-1 為 C-band 約 5.6 公分）
* **可以穿透雲、雨，且可在夜間運作** —— 「全天候、日夜皆可」

---

### 主要後向散射機制（Backscatter Mechanisms）

| 地表類型          | 散射機制                              | 訊號強度 | 常見 dB        |
| ------------- | --------------------------------- | ---- | ------------ |
| **平靜水面**      | 鏡面反射（specular reflection，像鏡子反射出去） | 非常低  | < -20 dB     |
| **粗糙水面 / 濕地** | 部分擴散散射（diffuse scattering）        | 低–中  | -15 到 -10 dB |
| **裸地 / 都市**   | 表面散射（surface scattering）          | 中–高  | -10 到 -5 dB  |
| **森林 / 植被**   | 體積散射（volume scattering，多次反射）      | 高    | -8 到 -3 dB   |
| **建築物（雙重反射）** | 角反射效應（corner reflector）           | 非常高  | > 0 dB       |

---

### 為什麼這對洪水偵測有用？

在發生洪水時：

* **水體在 SAR 影像中會非常暗**（因為鏡面反射造成低回波）
* **周圍陸地會比較亮**（植被與土壤有較高回波）
* 簡單閾值判斷：**VV < -18 dB → 水體**（ARIA 文獻預設值，課堂會依情境調整）

這補足了光學遙測在颱風期間**無法穿透雲層**的限制。

> **注意：** -18 dB 是全球常用預設值，但最佳閾值會依場景改變。
> 課堂案例（堰塞湖泥沙水）會使用不同閾值與形態學後處理（morphological post-processing）。

---

## 步驟 4：SAR 與光學比較

請在上課前憑記憶完成下表：

| 特徵     | 光學（Sentinel-2）                     | SAR（Sentinel-1）      |
| ------ | ---------------------------------- | -------------------- |
| 能量來源   | 太陽（被動）                             | 衛星發射器（主動）            |
| 波長     | 可見光 + NIR + SWIR（0.4–2.2 μm）       | 微波 C-band（約 5.6 cm）  |
| 穿透雲能力  | ❌ 無法穿透雲                            | ✅ _____              |
| 夜間運作   | ❌ 需要陽光                             | ✅ _____              |
| 水體偵測方式 | NDWI = (Green − NIR)/(Green + NIR) | 後向散射閾值：VV < __-18__ dB |
| 植被偵測   | NDVI = (NIR − Red)/(NIR + Red)     | 體積散射（高回波）            |
| 空間解析度  | 10 m                               | 10 m                 |
| 重訪時間   | 5 天                                | 6 天                  |

**答案：** 可穿雲 = Yes；夜間 = Yes；水體閾值 ≈ -18 dB

---

## 步驟 5：理解你將使用的資料

### 課堂 Demo/Lab：STAC API 即時串流

延續 W8–W9 工作流程，本週直接從 **Microsoft Planetary Computer** 串流 Sentinel-1 RTC 資料：

| 步驟                       | 說明                             | 誰執行       |
| ------------------------ | ------------------------------ | --------- |
| STAC 搜尋 `sentinel-1-rtc` | 使用 `pystac_client`             | 你（課堂 Lab） |
| 串流讀取 VV/VH               | `stackstac.stack()` → `xarray` | 你         |
| Linear → dB 轉換           | `10 * np.log10(value)`         | 你         |
| Speckle 濾波               | `median_filter(size=5)`        | 你         |

**Sentinel-1 RTC（Radiometrically Terrain Corrected）**：已完成輻射與地形校正。

👉 你只需要做：

* dB 轉換
* speckle filtering

---

### 與 W8 的差異

* collection：從 `sentinel-2-l2a` → `sentinel-1-rtc`
* bands：從光學波段 → `vv` 或 `vh`
* 不需要除以 10000
* **不需要雲量過濾**

---

### 作業資料（GeoTIFF）

作業會提供：

* `S1_Hualien_dB.tif`（已預處理）

SAR 預處理流程（了解即可）：

| 步驟      | 工具               |
| ------- | ---------------- |
| 下載 GRD  | ASF / Copernicus |
| 軌道與雜訊處理 | SNAP / HyP3      |
| 輻射校正    | SNAP / HyP3      |
| 地形校正    | SNAP / HyP3      |
| 轉 dB    | 10 × log₁₀       |

---

## 步驟 6：課前準備

### 課堂 Lab

課堂的 Sensor Fusion Lab 會在 notebook 內直接從 STAC 載入 Sentinel-2 光學資料（同 W8–W9 的 `stream_cube()` 模式），**不需要事先準備 W9 輸出檔案**。

### 作業

需要使用 W9 結果：

| 項目   | 說明       | 狀態 |
| ---- | -------- | -- |
| 水體遮罩 | NDWI 二值化 | ☐ Ready  |
| 雲遮罩  | SCL-based cloud mask  | ☐ Ready  |

如果沒有，請重新執行 W9 notebook。

---

## 步驟 7：自我測驗 — dB 轉換

情境：

* σ⁰ = 0.001

A Sentinel-1 pixel has backscatter σ⁰ = 0.001 (linear scale).

計算：

1. 轉 dB  $\sigma^0_{dB} = 10 \times \log_{10}(0.001) = $ _____ dB
2. 判斷水或陸地
3. 是否低於 -18 dB？  would this pixel be classified as water?

**答案：**

* 10 × log₁₀(0.001) = -30 dB
* 非常低 → 水
* -30 < -18 → 判定為水 ✅

---

## 步驟 8：思考題（選做）

1. 為什麼不能只用 SAR？光學提供了什麼資訊？
2. 為什麼 SAR 有斑點雜訊？（提示：干涉）
3. 如果光學與 SAR 判斷不一致，原因可能是什麼？

---

## 課前檢查清單

* [ ] rasterio、rioxarray 已安裝
* [ ] 了解 SAR 散射機制
* [ ] 完成比較表
* [ ] 完成 dB 測驗
* [ ] W9 結果可用 (作業用；課堂 Lab 會從 STAC 即時載入)
* [ ] 了解課堂使用 STAC API 串流 Sentinel-1 RTC（延續 W8 工作流）
* [ ] 思考融合邏輯

---

**你已準備好 Week 10！**

---

*若有環境問題，請於課前聯絡教師或在 NTUCool 發問。*
