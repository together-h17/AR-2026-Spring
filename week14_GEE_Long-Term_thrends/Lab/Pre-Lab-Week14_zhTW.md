# 第 14 週預習：GEE 進階 —— 長期趨勢與氣候韌性分析 — ARIA v9.5 設定 

**課程：** 台大《遙測與空間資訊之分析與應用》
**授課教師：** 蘇文瑞教授
**週次：** 第 14 週｜**主題：** GEE 進階 —— Landsat 多年代趨勢分析與韌性（GEE Advanced — Landsat Multi-Decadal Trend Analysis & Resilience）
**預估時間：** 約 20 分鐘

---

# 目標

完成本次預習後，你將能：

* 理解從 W13（Sentinel-2、6 年）升級到 W14（Landsat、20+ 年）的意義
* 回顧 Landsat 任務歷史與波段命名規則
* 理解長期趨勢分析為何需要多感測器一致化（harmonization）
* 複習植生監測中的線性回歸與韌性概念
* 確認你的 GEE 環境已準備完成（應已於 W13 設定）

---

# Step 1：確認 GEE 環境（延續 W13）

你應該已經在第 13 週完成可運作的 GEE 環境。請執行以下快速測試：

```python
import ee
import geemap

ee.Initialize(project='your-project-id')

# Quick test
point = ee.Geometry.Point([121.5, 24.1])
elev = ee.Image('USGS/SRTMGL1_003').sample(point, 30).first().get('elevation').getInfo()
print(f"✓ GEE connected — elevation: {elev} m")
```

若失敗，請回到第 13 週預習 Step 2 重新進行驗證設定。

---

# Step 2：升級 —— 從 6 年到 20+ 年

## W13 vs W14 比較

|       | W13（Sentinel-2） | W14（Landsat）    |
| ----- | --------------- | --------------- |
| 時間跨度  | 2020–2026（6 年）  | 2000–2026（26 年） |
| 空間解析度 | 10 m            | 30 m            |
| 重訪時間  | 5 天             | 8–16 天          |
| 適合分析  | 高細節近期變化         | 長期年代趨勢          |
| 核心問題  | 「地震後發生了什麼？」     | 「過去 20 年發生了什麼？」 |

## 為什麼使用 Landsat？

Sentinel-2 於 2015 年發射，僅有約 10 年資料。若要回答：

* 「這段河岸是否已侵蝕數十年？」
* 「這片森林是否在 15 年前颱風後逐漸恢復？」

就需要使用自 1984 年持續提供全球資料的 **Landsat archive**。

W14 使用：

* Landsat 5（2000–2012）
* Landsat 7（2000–至今）
* Landsat 8（2013–至今）
* Landsat 9（2021–至今）

並將它們整合為單一時間序列。

## 升級邏輯

```text
W13:  S2 time series (6 yrs)
      → 「地震後發生了什麼？」

W14:  Landsat time series (26 yrs)
      → 「過去二十年發生了什麼？」
      + 桃園埤塘消失分析（MNDWI）
      + 韌性指標（災後恢復速率）
```

---

# Step 3：Landsat 波段對應 —— 一致化挑戰

不同 Landsat 任務對相同光譜區域使用不同波段編號。

這是多年代分析的核心技術問題。

## 波段對應表

| 光譜區域  | L5 TM | L7 ETM+ | L8 OLI | L9 OLI-2 | 用途    |
| ----- | ----- | ------- | ------ | -------- | ----- |
| Blue  | SR_B1 | SR_B1   | SR_B2  | SR_B2    | 大氣散射  |
| Green | SR_B2 | SR_B2   | SR_B3  | SR_B3    | 植生活力  |
| Red   | SR_B3 | SR_B3   | SR_B4  | SR_B4    | 葉綠素吸收 |
| NIR   | SR_B4 | SR_B4   | SR_B5  | SR_B5    | 植生結構  |
| SWIR1 | SR_B5 | SR_B5   | SR_B6  | SR_B6    | 水分含量  |
| SWIR2 | SR_B7 | SR_B7   | SR_B7  | SR_B7    | 地質／礦物 |

## 重要指標

| 指標    | 公式                                | 偵測內容  |
| ----- | --------------------------------- | ----- |
| NDVI  | (NIR − Red) / (NIR + Red)         | 植生健康  |
| MNDWI | (Green − SWIR1) / (Green + SWIR1) | 水體    |
| NBR   | (NIR − SWIR2) / (NIR + SWIR2)     | 火災嚴重度 |

## 核心概念

我們會撰寫一個「一致化函式」，將不同 Landsat 任務的波段重新命名為：

```text
Blue, Green, Red, NIR, SWIR1, SWIR2
```

如此即可在 26 年間一致地計算 NDVI 與 MNDWI。

---

# Step 4：GEE Landsat Collections

## GEE Collection ID

| 任務        | GEE Collection ID        | 年代        | 備註                 |
| --------- | ------------------------ | --------- | ------------------ |
| Landsat 5 | `LANDSAT/LT05/C02/T1_L2` | 1984–2012 | TM 感測器             |
| Landsat 7 | `LANDSAT/LE07/C02/T1_L2` | 1999–至今   | ETM+，2003 後 SLC 故障 |
| Landsat 8 | `LANDSAT/LC08/C02/T1_L2` | 2013–至今   | OLI 感測器            |
| Landsat 9 | `LANDSAT/LC09/C02/T1_L2` | 2021–至今   | OLI-2 感測器          |

---

## 使用 QA_PIXEL 進行雲遮罩

與 Sentinel-2 的 SCL 波段不同，Landsat 使用 QA_PIXEL 位元遮罩：

```python
def mask_landsat_clouds(image):
    qa = image.select('QA_PIXEL')
    # Bit 3 = cloud, Bit 4 = cloud shadow
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)
    shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)
    return image.updateMask(cloud_mask.And(shadow_mask))
```

---

## Landsat 7 的 SLC-off 問題

2003 年 5 月，Landsat 7 的 Scan Line Corrector（SLC）故障。

造成：

* 條紋狀缺值
* 楔形空洞
* 空間覆蓋率下降

GEE 會自動遮罩這些像素。

當使用中位數合成（median composite）時，其餘影像可自動填補缺口。

---

## 自我測驗 Q1

### 問題

為何在建立 20 年 NDVI 時間序列前，需要先統一 Landsat 波段名稱？

### 答案

不同 Landsat 任務對相同光譜區域使用不同波段編號。

例如：

* L5/L7 的 NIR = B4
* L8/L9 的 NIR = B5

若不統一：

```python
normalizedDifference(['B4', 'B3'])
```

在 L5/L7 會正確計算 NDVI，但在 L8/L9 會產生錯誤結果。

---

# Step 5：線性趨勢與韌性概念

## 像素層級線性回歸

W13 使用：

```python
ee.Reducer.linearFit()
```

對 6 年 Sentinel-2 NDVI 做分析。

W14 則擴展到完整 26 年 Landsat 序列：

```text
NDVI(t) = slope × t + offset
```

### 解讀 slope

| slope | 意義           |
| ----- | ------------ |
| > 0   | 長期綠化（恢復／造林）  |
| < 0   | 長期褐化（退化／都市化） |
| ≈ 0   | 穩定           |

---

# 韌性（Resilience）

韌性指生態系在干擾後恢復的能力。

## 高韌性

* NDVI 大幅下降
* 1–2 年內恢復接近原始值

## 低韌性

* NDVI 下降後維持低值
* 或持續惡化

## 不可恢復

永久土地覆蓋改變：

* 崩塌地變裸岩
* 水塘被填平

---

## W14 韌性指標

* Recovery rate（恢復速率）
* Recovery ratio（恢復比例）
* Time to recovery（恢復時間）

---

# 桃園埤塘消失分析

桃園台地曾有約：

```text
6,000–8,000 口埤塘
```

隨都市化，目前剩約 3,000 口。

使用 MNDWI 時間序列可追蹤埤塘變化。

## 判斷標準

| MNDWI | 判定 |
| ----- | -- |
| > 0.1 | 水體 |
| < 0   | 陸地 |

透過年度 MNDWI 合成，可偵測：

* 水體新增
* 水體消失
* 都市化壓力
* 防洪韌性變化

---

## 自我測驗 Q2

### 情境

桃園埤塘：

* 2005：0.5
* 2015：0.3
* 2025：−0.2

太魯閣山坡：

* 2005：0.8
* 2015：0.2（颱風後）
* 2025：0.75

### 問題

哪個像素展現韌性？哪個是永久變化？

### 答案

* 山坡像素展現韌性（0.2 → 0.75）
* 埤塘像素為永久變化（水體 → 陸地）

代表埤塘被填平開發。

---

# Step 6：跨週整合預覽

## 時空框架

| 週次  | 維度         | 技術          | 解析度       |
| --- | ---------- | ----------- | --------- |
| W6  | 空間插值       | Kriging     | 點資料 → 連續面 |
| W13 | 時間分析（6 年）  | GEE S2      | 高空間、短時間   |
| W14 | 時間分析（26 年） | GEE Landsat | 中空間、長時間   |

## 核心概念

* W6：填補空間缺口
* W14：填補時間缺口

兩者結合：

```text
完整的時空環境變遷圖像
```

---

## 自我測驗 Q3

### 問題

若將 W13 的 2020–2026 NDVI 分析延伸至 2000–2026，會看見哪些原本隱藏的現象？

### 答案

可觀察：

* 長期都市化趨勢
* 反覆颱風破壞與恢復循環
* 桃園埤塘逐漸消失
* 2024 地震是否屬於長期擾動模式之一

6 年窗口可能只看到單一事件。

26 年窗口則能看見歷史背景與長期趨勢。

---

# 延伸閱讀

## 1. 呂明倫（2024）

使用深度學習演算法進行 Sentinel-2 影像之土地利用和土地覆蓋分類

* 航測及遙測學刊，29(4): 231–240
* DOI: 10.6574/JPRS.202412_29(4).0003

內容：

* 使用 CNN 分類 Sentinel-2
* 與 Random Forest 比較
* OA 達 89%

連結：

* W9 混淆矩陣
* W12 影像分類

---

## 2. NCDR（2020）

108 年度豪雨事件災情彙整與勘災報告

內容包含：

* 2019 豪雨事件
* 農損統計
* Sentinel-2 崩塌前後比較

可與本週 Landsat 長期趨勢分析互相對照。

---

# 上課前檢查清單

* [ ] GEE 環境正常
* [ ] 理解 W13 → W14 升級
* [ ] 熟悉 Landsat 波段對應
* [ ] 理解 QA_PIXEL 雲遮罩
* [ ] 知道 Landsat 7 SLC-off 問題
* [ ] 理解 NDVI 長期趨勢
* [ ] 理解韌性概念
* [ ] 理解 MNDWI 與埤塘偵測
* [ ] 完成 3 題自我測驗

---

**你已準備好進入 Week 14。**
