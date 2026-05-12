# 第 12 週課前實驗：影像分類與地表覆蓋製圖 — ARIA v8.0 設定

**課程：** NTU Remote Sensing & Spatial Information Analysis（遙測與空間資訊之分析與應用）  
**授課教師：** 蘇文瑞教授  
**週次：** 第 12 週 | **主題：** 影像分類與地物辨識  
**預估時間：** 約 20 分鐘

---

## 學習目標

完成本次課前實驗後，你將能夠：

- 確認 W8–W10 的 STAC API 環境仍可正常運作
- 安裝分類相關套件（若尚未安裝 scikit-learn）
- 理解從「閾值法（thresholding）」到「分類（classification）」的概念升級
- 複習非監督式（K-means）與監督式（Random Forest）分類概念
- 準備將分類結果與 W9 的混淆矩陣架構連結

---

## Step 1：確認環境

### 1a. Colab 或本機環境

本週 **不需要 GPU**。傳統分類器（K-means、Random Forest）在 CPU 上即可高效率執行。

```python
# Colab 使用者
from google.colab import drive
drive.mount('/content/drive')

# 或使用你的本機環境（沿用 W8–W10 的 conda / venv）
```

### 1b. 確認核心套件

```python
import pystac_client
import planetary_computer as pc
import stackstac
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
import rasterio
import geopandas as gpd

print("✓ pystac_client:", pystac_client.__version__)
print("✓ scikit-learn:", __import__('sklearn').__version__)
print("✓ 所有核心相依套件已成功載入")
```

若有任何 import 失敗：

```bash
pip install pystac_client stackstac planetary-computer scikit-learn rasterio geopandas
```

---

## Step 2：概念升級 — 為什麼需要分類？

### W8–W10 做了什麼

在前幾週中，我們依賴的是 **閾值法（thresholding）** —— 使用單一指標、單一閾值，進行二元分類：

| 週次 | 方法 | 邏輯 | 限制 |
|------|------|------|------|
| W8 | NDVI > 0.4 → 植被 | 人工設定單一閾值 | 只能分成兩類 |
| W9 | ΔNDVI > T → 變化區 | 人工設定差值閾值 | 無法知道「變成了什麼」 |
| W10 | VV < −18 dB → 水體 | 人工設定 SAR 閾值 | 只能分水體 / 非水體 |

**核心限制：** 閾值法一次只使用一個指標，而且只能區分兩類。然而真實世界存在許多地表覆蓋類型，例如水體、森林、裸地、建成區、農地、崩塌地等。

### W12 升級了什麼

**分類（Classification）** 會同時使用 **多個波段**，將每個像素分配到某個 **地表覆蓋類別**：

```text
閾值法：       NDVI（單一數值）                 → 是否為植被
分類法： [B2, B3, B4, B8, B11, B12] → 水體 / 森林 / 裸地 / 建成區 / 農地 / 崩塌地
```

**升級路徑：**

```text
W8–W10   閾值法（人類規則、一次一個指標）
   ↓
W12a     非監督式分類（機器自行找群集：K-means）
   ↓
W12b     監督式分類（人類提供範例、機器學習規則：Random Forest）
```

---

## Step 3：特徵空間（Feature Space）概念複習

### 什麼是特徵空間？

每個像素都具有多個波段值，因此可形成一個「多維座標」：

| 波段 | 物理意義 | 在特徵空間中的角色 |
|------|----------|------------------|
| B2（Blue） | 藍光反射率 | 第 1 維 |
| B3（Green） | 綠光反射率 | 第 2 維 |
| B4（Red） | 紅光反射率 | 第 3 維 |
| B8（NIR） | 近紅外反射率 | 第 4 維 |
| B11（SWIR1） | 短波紅外 | 第 5 維 |
| B12（SWIR2） | 短波紅外 | 第 6 維 |

**核心直覺：** 在這個六維空間中，同類型地物的像素往往會聚集在一起。

- 水體：低 NIR、低 SWIR → 聚集在左下區域
- 植被：高 NIR、低 Red → 聚集在右上區域
- 裸地：各波段中等值 → 聚集在中間區域

分類的本質，就是 **在特徵空間中劃分邊界**。

---

## Step 4：K-means — 非監督式分類

### 核心概念

**非監督式（Unsupervised）** = 不需要人類提供標記範例；機器自行尋找群集。

**K-means 演算法：**

1. 在特徵空間中隨機放置 K 個「中心點（centroids）」
2. 將每個像素分配到最近的中心點
3. 重新計算每個群集的平均中心
4. 重複步驟 2–3，直到結果收斂

**你需要決定：** K（群集數量）

**優點：** 快速；不需要訓練資料  
**缺點：** 群集未必對應真實地物類別；K 值需要自行猜測

### 自我測驗 Q1

在 K-means 的結果中，「Cluster 3」代表什麼地物類型？

**答案：** 你不知道。K-means 只會給群集編號，不會提供名稱。你必須根據光譜特徵自行解讀每個群集。這就是「非監督式」的意義——機器不知道真實世界中的標籤。

---

## Step 5：Random Forest — 監督式分類

### 核心概念

**監督式（Supervised）** = 人類提供帶有標籤的範例（training samples），機器從中學習分類規則。

**Random Forest 演算法：**

1. 隨機抽取部分訓練資料
2. 建立決策樹（例如：「若 NIR > 0.3 且 Red < 0.1 → 植被」）
3. 重複步驟 1–2 建立大量決策樹（100 棵以上）
4. 進行預測時，由所有樹投票，多數決定結果

**你需要準備：** 各類別具代表性的訓練樣本

**優點：** 輸出類別可對應真實地物；通常比 K-means 更準確  
**缺點：** 需要人工標記訓練資料（較耗時）

### 自我測驗 Q2

為什麼稱為「Forest（森林）」？

**答案：** 因為它由許多決策樹組成（通常 100–500 棵）。每棵樹都使用不同的隨機特徵與樣本子集進行訓練，最終以多數決作為預測結果。「Random」則代表特徵與樣本選擇中的隨機性。

---

## Step 6：混淆矩陣（Confusion Matrix）— 第二次登場

### W9 與 W12 的混淆矩陣比較

| | W9（變遷偵測） | W12（影像分類） |
|---|---|---|
| 目的 | 評估變化 / 非變化偵測精度 | 評估多類別分類精度 |
| 類別數 | 2（變化 / 未變化） | N（水體 / 森林 / 裸地 / 建成區…） |
| 核心指標 | Producer's / User's accuracy | 相同，但需針對每個類別計算 |
| 災害應用 | 漏掉變化 = omission | 崩塌地被分成森林 = omission |

**教學連結：** W9 中你學到的是 2×2 混淆矩陣；W12 則升級為 N×N。概念完全相同，但資訊量更豐富。

### 自我測驗 Q3

若是 5 類別分類，混淆矩陣大小是多少？

**答案：** 5×5。對角線代表正確分類的像素；非對角線代表誤分類。每一列加總為該類別的驗證樣本總數。

---

## Step 7：綜合測驗

### Q4：Thresholding vs K-means vs Random Forest

完成下表：

| 性質 | Thresholding | K-means | Random Forest |
|------|--------------|---------|---------------|
| 需要訓練資料？ | ❌ | ❌ | ✅ |
| 需要人類指定 K？ | N/A | _____ | N/A |
| 是否同時使用多波段？ | ❌（一次一個指標） | _____ | _____ |
| 輸出是否有類別名稱？ | 有（人類定義） | _____ | _____ |
| 輸出類別數量 | 2 | _____ | _____ |

**答案：**

- K-means：需要 K = ✅；多波段 = ✅；類別名稱 = ❌（只有群集 ID）；輸出類別數 = K
- Random Forest：多波段 = ✅；類別名稱 = ✅（來自訓練資料）；輸出類別數 = 訓練資料中的類別數

---

## Q5：特徵空間思維

為什麼使用 6 個波段（B2–B4、B8、B11–B12）的分類，通常會優於只使用 RGB（B2–B4）的分類？

**答案：** 更多維度代表更多可區辨資訊。NIR 與 SWIR 波段攜帶了植被結構與含水量等 RGB 無法呈現的物理訊號。例如健康植被與受壓植被在 RGB 中可能很像，但在 NIR 中差異非常明顯。

---

## Step 8：反思問題（選做）

1. **如何選擇 K 值？** 如果研究區已知有 5 種地表覆蓋類型，是否應該設定 K = 5？（提示：同一種地物可能具有多種光譜子類型）

2. **訓練樣本品質：** 如果所有訓練樣本都來自都市中心，分類器在鄉村地區是否仍會表現良好？為什麼？（訓練樣本的空間代表性）

3. **分類 + W10 融合：** 若 Random Forest 判定某區域為「崩塌地」，而 W10 SAR 也在同區域偵測到異常回波，這與「感測器融合（sensor fusion）」的概念有何關聯？

---

## 上課前檢查清單

- [ ] STAC API 環境（pystac_client、stackstac、planetary_computer）可正常運作
- [ ] 已安裝 scikit-learn（可 import KMeans、RandomForestClassifier）
- [ ] 理解特徵空間概念（多波段 = 多維座標）
- [ ] 理解 K-means（非監督式：機器自行分群）與 Random Forest（監督式：人類提供標記範例）的差異
- [ ] 理解混淆矩陣如何從 W9 的 2×2 升級為 W12 的 N×N
- [ ] 已完成自我測驗（5 題）
- [ ] 選做：思考 K 值選擇與訓練樣本品質問題

**你已準備好進入第 12 週課程！**

---

*備註：若遇到任何環境問題，請於上課前在 NTUCool 發文或寄信給蘇教授。*
