# ARIA v8.0：太魯閣災後土地覆蓋分類報告

## Abstract

本研究以 2024 年 4 月 3 日花蓮地震後之 Sentinel-2 L2A 多光譜影像，針對秀林／太魯閣研究區建立土地覆蓋分類。方法上先使用 SCL 遮罩去除雲、雲影與雪，再以 6 個反射率波段建立特徵矩陣。Task 1 使用 K-means 進行 K=5 非監督式分群，分析各群平均光譜並對應水體、森林、農田、裸地／崩塌與建物／都市等類別。Task 2 使用 Random Forest 進行監督式分類，產生土地覆蓋圖與 feature importance。Task 3 以 confusion matrix、OOB accuracy 與 SWCB 官方新生崩塌地資料進行內外部驗證。Task 4 統計各類別面積並產生災害應變簡報式分析報告。

## 1. Data and Preprocessing

- 研究區 BBOX：[121.4, 24.1, 121.8, 24.25]
- Sentinel-2 影像日期：2024-08-27
- 雲量：8.4%
- 使用波段：B02, B03, B04, B08, B11, B12
- 有效像素數：1,593,879
- 前處理：反射率縮放、SCL 雲／雲影／雪遮罩、異常值過濾。

## 2. Task 1：K-means 非監督分類

K-means 以 6 波段反射率作為特徵，設定 K=5 進行分群。水體與森林通常較容易判讀，因水體在 NIR/SWIR 反射率低，森林則具有高 NIR、低 Red 的植生特徵。較困難的是裸地／崩塌、建物／都市與地形陰影，因其光譜可能相近。

### K-means 平均光譜表

|   Cluster |    B02 |    B03 |    B04 |    B08 |    B11 |    B12 |    NDVI |    NDWI |    NDBI |   Pixels | Suggested label                               |
|----------:|-------:|-------:|-------:|-------:|-------:|-------:|--------:|--------:|--------:|---------:|:----------------------------------------------|
|         0 | 0.1276 | 0.1594 | 0.1304 | 0.5301 | 0.3109 | 0.192  |  0.6051 | -0.5376 | -0.2606 |   445552 | Forest（森林）                                |
|         1 | 0.1903 | 0.1825 | 0.1709 | 0.1688 | 0.1682 | 0.157  | -0.0063 |  0.039  | -0.0016 |   584867 | Bare/Landslide or Built-up（裸地/崩塌或建物） |
|         2 | 0.2378 | 0.2584 | 0.2554 | 0.3679 | 0.3577 | 0.2885 |  0.1804 | -0.1748 | -0.014  |   108382 | Bare/Landslide or Built-up（裸地/崩塌或建物） |
|         3 | 0.1245 | 0.1478 | 0.1285 | 0.4121 | 0.2772 | 0.1808 |  0.5246 | -0.4721 | -0.1957 |   434352 | Forest（森林）                                |
|         4 | 0.4254 | 0.4357 | 0.4319 | 0.526  | 0.5154 | 0.4383 |  0.0982 | -0.0938 | -0.0101 |    20726 | Bare/Landslide or Built-up（裸地/崩塌或建物） |

## 3. Task 2：Random Forest 監督式分類

Random Forest 使用訓練樣本建立五類土地覆蓋分類模型。本次模型設定 n_estimators=200，並啟用 OOB validation。

- Training accuracy：1.0000
- Test accuracy：0.9492
- OOB accuracy：0.9522
- Cohen's Kappa：0.9333

### Feature Importance

| Band   | Name   |   Importance |
|:-------|:-------|-------------:|
| B12    | SWIR2  |     0.204108 |
| B11    | SWIR1  |     0.196351 |
| B02    | Blue   |     0.193536 |
| B04    | Red    |     0.150146 |
| B03    | Green  |     0.13395  |
| B08    | NIR    |     0.121908 |

Random Forest 相較於 K-means 的優點在於可直接產生具有語意的地物類別圖；缺點是高度依賴訓練樣本品質。若 ROI 樣本不純或未涵蓋地形差異，分類圖會出現系統性誤差。

## 4. Task 3：Accuracy Assessment and SWCB Validation

### Internal Validation

- Macro F1：0.9116
- Weighted F1：0.9473
- F1 gap：0.0358

若 Weighted F1 明顯高於 Macro F1，表示多數類別可能主導整體精度，少數類別（如農田、建物）表現可能被稀釋。

### External Validation with SWCB Landslide Inventory

| Metric    |      Value | Meaning                                  |
|:----------|-----------:|:-----------------------------------------|
| Recall    | 0.177524   | SWCB 崩塌地中被 RF 偵測為裸地/崩塌的比例 |
| Precision | 0.00910366 | RF 裸地/崩塌中與 SWCB 崩塌地重疊的比例   |
| IoU       | 0.00873523 | RF 與 SWCB 崩塌地交集 / 聯集             |

完美重疊（IoU=1）不太可能出現，原因包括 Sentinel-2 與 SWCB 判釋影像日期不同、Sentinel-2 解析度為 20 m、官方資料可能使用高解析度影像判釋，以及本分類中的 Bare/Landslide 類別同時包含河床、裸岩、道路邊坡等非崩塌裸地。FN 常集中在小型、狹長、地形陰影或植生恢復中的崩塌地；FP 則可能出現在河床、道路、裸露岩盤或建物。

## 5. Task 4：Area Statistics and AI Report

### Area Statistics

|                | class_zh   |   pixels |   area_ha |   percentage |
|:---------------|:-----------|---------:|----------:|-------------:|
| Water          | 水體       |   583121 |  23324.8  |        36.59 |
| Forest         | 森林       |   820944 |  32837.8  |        51.51 |
| Cropland       | 農田       |   144255 |   5770.2  |         9.05 |
| Bare/Landslide | 裸地/崩塌  |    39215 |   1568.6  |         2.46 |
| Built-up       | 建物/都市  |     5671 |    226.84 |         0.36 |

### AI-generated Classification Report

本次分析以 Sentinel-2 L2A 震後影像建立秀林／太魯閣研究區土地覆蓋分類圖，並以 Random Forest 將像素分為水體、森林、農田、裸地／崩塌與建物／都市五類。分類結果顯示，研究區以森林覆蓋為主，森林約占有效分類像素的 51.5%；水體約占 36.6%，主要分布於研究區東側海域與河道。建物／都市比例約為 0.4%，符合太魯閣山區聚落與建成區較少的地理特性。

裸地／崩塌分類面積約為 1568.6 公頃，主要代表崩塌地、裸露岩盤、河床與道路邊坡等高反射地表。與 SWCB 官方新生崩塌地資料比對後，IoU 為 0.009，Recall 為 0.178，Precision 為 0.009。此結果顯示 Sentinel-2 分類能掌握部分崩塌空間分布，但與官方高解析度判釋仍有落差。

不確定性主要來自影像日期與 SWCB 判釋日期不同、Sentinel-2 20 m 解析度造成混合像素、山區地形陰影，以及裸地／崩塌與河床、道路、建物光譜相似。建議後續將本分類圖與道路、聚落、避難所與坡度資料套疊，用於識別可能受崩塌影響的路段、評估避難所周邊可達性，並作為災後現地查核與高解析度影像判釋的優先篩選圖層。

### Critical Evaluation

AI 報告中的面積與百分比需逐一對照 class_area_stats.csv，避免將像素數、百分比或公頃數誤寫。就本次結果而言，最需要檢查的是裸地／崩塌面積、SWCB IoU、Recall 與 Precision，因為這些數值直接影響災害判讀。報告的不確定性說明大致合理，已提到時間差、空間解析度、混合像素與類別定義差異。不過仍可補充：本 notebook 若使用自動光譜種子樣本，其訓練資料不如 Google Earth 手繪 ROI 獨立，可能使內部測試精度偏高。因此正式繳交時應改用人工 ROI，並將 FN/FP 的主要空間位置與真色彩影像、Google Earth 或現地資料交叉檢查。

## 6. ARIA v8.0 Upgrade Reflection

ARIA v7.0 的閾值法適合快速偵測特定異常，例如 NDVI 下降或 SAR 後向散射變化，但其限制是一次只能處理少數指標，且通常只能進行二分類。ARIA v8.0 引入 K-means 與 Random Forest 後，可同時利用多個波段進行多類別土地覆蓋分類，產生更完整的災後基礎圖資。然而，分類器並不會自動保證正確，訓練資料品質、類別定義、影像時間與空間解析度仍是分類可信度的核心限制。

## 7. Output Files

- kmeans_classification.png
- rf_classification.png
- confusion_matrix.png
- swcb_overlay.png
- class_area_stats.csv
