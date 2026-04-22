# ARIA v6.0 — Barrier Lake Detection Report

**Case Study:** Matai'an Barrier Lake, Taiwan

---

## 1. 研究目的

本研究旨在利用 Sentinel-2 多時相影像，透過變異指標分析與閾值優化方法，偵測台灣馬太鞍地區之堰塞湖災害範圍，並評估模型準確性以支援災害監測應用。

---

## 2. 資料來源與前處理

### 2.1 影像資料

使用三個時期之 Sentinel-2 Level-2A 影像：

* Pre-event
* Mid-event
* Post-event

透過 STAC API (Planetary Computer) 進行資料存取。

### 2.2 雲遮罩 (Cloud Masking)

使用 Scene Classification Layer (SCL) 過濾雲與陰影：

* 保留類別：2, 4, 5, 6, 7, 11
* 建立三時期交集遮罩，確保比較像元一致性

---

## 3. 方法

### 3.1 指標計算

計算三種光譜指標：

* NDVI（植生）
* NDWI（水體）
* BSI（裸地）

並計算時序變化：

* ΔNDVI (Pre → Mid)
* ΔNDWI
* ΔBSI

---

### 3.2 變化偵測

透過 ΔNDVI 觀察植被減少區域，推測潛在崩塌與水體形成區。

---

### 3.3 Threshold Optimization

設定多個閾值掃描 ΔNDVI，並透過驗證點計算：

* Precision (User’s Accuracy)
* Recall (Producer’s Accuracy)
* F1-score
* Confusion Matrix

以 F1-score 作為最佳閾值選擇依據。

---

## 4. 結果

### 4.1 最佳閾值

* Threshold = **0.1**

---

### 4.2 精度評估

| 指標                  | 數值     |
| ------------------- | ------ |
| Overall Accuracy    | 68.52% |
| Producer’s Accuracy | 73.33% |
| User’s Accuracy     | 45.83% |
| Kappa               | 0.338  |

---

### 4.3 空間分布結果

* 高信心區域：**38.444 km²**
* 空間上沿河道及崩塌區集中
* 存在大量零散偽陽性（False Positives）

---

## 5. 結果分析

### 5.1 優點

* 能有效捕捉主要災害區（PA > 70%）
* 成功識別河道阻塞與潛在水體區域
* 雲遮罩後顯著降低雜訊

---

### 5.2 問題

* User’s Accuracy 僅 45.83% → 誤報偏高
* Kappa = 0.338 → 模型一致性偏低
* 閾值偏寬鬆導致過度偵測

---

## 6. 技術困難與解決方法

### 6.1 座標遺失問題（關鍵）

**問題：**
雲遮罩後資料轉為 `ndarray`，導致空間座標資訊遺失，無法進行驗證點取值。

**影響：**

* Threshold Optimization 無法正常運作
* 驗證結果全部為空值

**解決方法：**

* 改用 `xarray.DataArray` 保留座標
* 建立 template（以原始 NIR band 為基準）
* 將遮罩與計算結果映射回原座標系統

---

### 6.2 雲與陰影干擾

**問題：**

* 未遮罩時產生 Phantom Water（偽水體）

**解決：**

* 使用 SCL 遮罩
* 採用三時期交集提高穩定性

---

### 6.3 驗證點對應問題

**問題：**

* GeoJSON 座標需轉為影像 row/col
* 投影系統不一致

**解決：**

* 使用 rasterio / rioxarray 進行座標轉換

---

### 6.4 閾值選擇困難

**問題：**

* Precision 與 Recall trade-off 明顯

**解決：**

* 採用 F1-score 作為最佳化標準

---

## 7. 討論

目前模型特性為：

* 偏向「高召回、低精度」
* 適合災害初步篩查（screening）
* 不適合直接用於決策

主要限制來自：

* 單一指標（ΔNDVI）資訊不足
* 未整合地形與水文資料

---

## 8. 未來改進建議

### 8.1 多資料融合

* Sentinel-1 SAR（抗雲）
* DEM（地形分析）
* 河網資料

---

### 8.2 模型改進

* 使用多指標（NDWI + NDVI + BSI）
* 機器學習分類（Random Forest / XGBoost）

---

### 8.3 閾值優化

* ROC curve / Precision-Recall curve
* 提升 User’s Accuracy 至 >70%

---

## 9. 結論

本研究成功建立一套基於 Sentinel-2 的變化偵測流程，能有效識別堰塞湖潛在區域。然而目前模型仍存在誤報偏高問題，整體信賴度屬於**中低等級**。

未來需透過多源資料融合與模型優化，以提升精度並支援實際災害決策。

---
