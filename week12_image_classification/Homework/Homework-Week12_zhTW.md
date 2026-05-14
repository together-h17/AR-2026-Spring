# 第 12 週作業：ARIA v8.0 — 分類引擎

**課程：** NTU Remote Sensing & Spatial Information Analysis（遙測與空間資訊之分析與應用）  
**授課教師：** 蘇文瑞教授  
**作業：** 第 12 週作業  
**繳交期限：** 請參閱 NTUCool（通常為課後一週）  
**案例研究：** 地震後土地覆蓋分類 — 秀林 / 太魯閣研究區

---

## 概述

本週你將把 ARIA 系統從 v7.0 升級至 **v8.0 — 分類引擎（The Classification Engine）**。

v7.0 使用的是像素層級閾值法（NDVI > T、VV < T_dB）；  
v8.0 則導入分類器，從「單一指標二分類」升級為「多波段多類別分類」。

**升級邏輯：**

```text
v5.0 (W8)  → 光譜判讀：哪裡有異常？（目視 + 假彩色）
v6.0 (W9)  → 變遷偵測：變了多少？可信嗎？（ΔNDVI + confusion matrix）
v7.0 (W10) → SAR 融合：雲下發生了什麼？（多源閾值 + 確信度）
v8.0 (W12) → 影像分類：每個像素是什麼地物？（K-means + Random Forest）
```

**主要成果要求：**
請提交一份 Colab/Jupyter Notebook（`.ipynb`），內容需展示：

- 使用 STAC API 串流 Sentinel-2 多光譜影像
- K-means 非監督式分類
- Random Forest 監督式分類
- Confusion Matrix 分類精度評估
- AI 自動生成分類報告

---

## 任務情境（Scenario）

指揮官已不再滿足於「哪裡有異常」，而是需要一張完整的災後土地覆蓋圖。

每個像素都需被分類為：

- 水體
- 森林
- 農田
- 裸地 / 崩塌
- 建物 / 都市

這張圖將成為：

- 避難所評估
- 路網可達性分析
- 崩塌面積統計

等後續分析的重要基礎圖資。

你的任務是：

利用地震後 Sentinel-2 影像，建立秀林 / 太魯閣地區的多類別土地覆蓋分類圖，並評估分類品質。

> 注意：
> 本次作業研究區與課堂示範的花蓮市不同。
> 秀林 / 太魯閣地區以山區、森林與崩塌地為主，
> 建成區與農地比例極低。
> 你必須重新在 Google Earth 中判釋地物並重新建立訓練樣本。

---

## 研究區與資料

### STAC API（延續 W8–W10 工作流程）

以下 Python 程式碼保持原樣：

```python
import pystac_client
import planetary_computer as pc
import stackstac

catalog = pystac_client.Client.open(
    'https://planetarycomputer.microsoft.com/api/stac/v1',
    modifier=pc.sign_inplace,
)

TAROKO_BBOX = [121.40, 24.10, 121.80, 24.25]
```

---

## 分類使用波段與 SCL 雲遮罩

```python
BANDS = ['B02', 'B03', 'B04', 'B08', 'B11', 'B12']
BANDS_ALL = BANDS + ['SCL']
```

- B02 = Blue
- B03 = Green
- B04 = Red
- B08 = NIR
- B11 = SWIR1
- B12 = SWIR2

SCL（Scene Classification Layer）為 Sentinel-2 內建場景分類層，可辨識：

- 雲
- 雲影
- 雪

你必須先做雲遮罩後才能進行分類。

---

# 目標土地覆蓋類別

| 類別 ID | 名稱 | 英文 | 光譜特徵 |
|---|---|---|---|
| 1 | 水體 | Water | NIR 低、SWIR 低 |
| 2 | 森林 | Forest | NIR 高、Red 低 |
| 3 | 農田 | Cropland | NIR 中高、季節變化大 |
| 4 | 裸地/崩塌 | Bare/Landslide | SWIR 高 |
| 5 | 建物/都市 | Built-up | 各波段混合、高反射 |

---

# 核心要求（4 Tasks）

# Task 1：K-means 非監督式分類（15%）

## 目標

使用 K-means 對地震後多光譜影像進行非監督式分類。

## 需完成內容

- 建立 feature matrix
- K=5 K-means clustering
- 重建分類圖
- 分析各 cluster 平均光譜
- 手動對應土地覆蓋類別

## Deliverables

- K-means 分類圖
- 各 cluster 平均光譜表
- 分類解釋與討論

---

# Task 2：Random Forest 監督式分類（25%）

## 目標

建立具有標籤的土地覆蓋分類圖。

## 流程

1. 建立訓練樣本
2. Random Forest 訓練
3. 整張影像分類
4. 分析 Feature Importance

## 訓練樣本原則

- 每類至少 50–100 像素
- 樣本需分散
- 避免混合像素

## Deliverables

- RF 分類圖
- Training/Test accuracy
- Feature importance 圖
- K-means 與 RF 比較

---

# Task 3：精度評估與獨立驗證（35%）

## Part A：內部驗證

需完成：

- Confusion Matrix
- Classification Report
- OOB Accuracy
- Macro vs Weighted F1 分析

## Part B：SWCB 崩塌地驗證

使用：

`20240802新生崩塌地.kml`

作為官方獨立參考資料。

需完成：

- 載入 KML
- Rasterize
- 計算：
  - Recall
  - Precision
  - IoU
- TP/FN/FP Overlay 圖

## 必答討論

- 為何不可能完全重疊（IoU=1）？
- FN 集中在哪裡？
- 外部驗證與內部精度有何差異？

---

# Task 4：AI 分類報告（25%）

## 目標

計算面積統計並利用 LLM 自動產生災後分析報告。

## 需完成內容

- 各類別面積統計
- Gemini 生成中文報告
- AI 幻覺檢查
- 不確定性評估

---

# 繳交格式

## 必交檔案

1. `.ipynb`
2. `.md`
3. 輸出圖檔：

- `kmeans_classification.png`
- `rf_classification.png`
- `confusion_matrix.png`
- `swcb_overlay.png`
- `class_area_stats.csv`

---

# 評分標準

| Task | 比例 | 重點 |
|---|---|---|
| Task 1 | 15% | 光譜分析與 cluster 解釋 |
| Task 2 | 25% | RF 分類品質 |
| Task 3 | 35% | 精度評估與 SWCB 驗證 |
| Task 4 | 25% | AI 報告與批判分析 |

---

# Captain's Tip

> 閾值法只能看單一維度；
> 分類器則能同時分析所有波段。
>
> 但再好的模型也需要高品質訓練資料：
>
> garbage in = garbage out

---

# FAQ

## Q：如何選訓練樣本？

- 使用真彩色 / 假彩色影像判釋
- 參考 Google Earth 歷史影像
- 每類至少 50 pixels

## Q：K-means 太慢？

- 降低解析度
- 或隨機抽樣

## Q：RF 要多少樹？

- 100–500 通常足夠
- 預設 200 可作為起點

## Q：分類結果有 salt-and-pepper noise？

可使用：

```python
scipy.ndimage.median_filter(class_map, size=3)
```

## Q：如何上傳 SWCB KML？

- 從 Google Drive 下載
- 上傳至 Colab working directory

---

*若有問題請至 NTUCool 發問或寄信給 Prof. Su。*
