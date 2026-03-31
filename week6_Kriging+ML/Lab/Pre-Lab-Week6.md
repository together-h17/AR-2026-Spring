# 第 6 週課前實驗：Kriging + 機器學習環境設定

> 請於上課前完成以下步驟，以確保你的環境已準備就緒。
> 預估時間：15–20 分鐘

---

## 步驟 1：安裝新套件

```bash
# 請先啟用你的虛擬環境！
# macOS / Linux：
source gis-env/bin/activate
# Windows：
gis-env\Scripts\activate

# 安裝 pykrige（Kriging）、scikit-learn（機器學習）及相關支援套件
pip install pykrige scipy scikit-learn matplotlib rasterio rasterstats
```

驗證安裝：

```python
import pykrige
from pykrige.ok import OrdinaryKriging
import scipy
import sklearn
import rasterio

print(f"PyKrige 版本：{pykrige.__version__}")
print(f"SciPy 版本：{scipy.__version__}")
print(f"scikit-learn 版本：{sklearn.__version__}")
print("✅ 第 6 週所有套件已準備完成！")
```

快速機器學習測試：

```python
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor(n_estimators=10, random_state=42)
print("✅ RandomForestRegressor 匯入成功！")
```

> **注意**：`pykrige` 依賴 `scipy` 和 `numpy`；`scikit-learn` 也依賴 `numpy` 和 `scipy`。
> 如果你已經完成第 3–5 週的環境設定，這些套件通常已經安裝好了。

---

## 步驟 2：回顧第 5 週 ARIA v3.0 輸出結果

第 6 週將直接建立在你第 5 週的成果上。請確認你已經具備以下資料：

1. **雨量站 GeoDataFrame**（來自 `parse_rainfall_json()`）
   包含欄位：`station_name`, `lat`, `lon`, `rain_1hr`

2. **ARIA v3.0 動態風險分級結果**
   包含：CRITICAL / URGENT / WARNING / SAFE

3. **花蓮縣 + 宜蘭縣鄉鎮界資料**
   來自 TGOS

> **為什麼？**
> 第 5 週將降雨視為**離散點資料**（測站位置）。
> 第 6 週要回答的是：
> **「那沒有測站的 95% 土地區域呢？」**

我們將比較：

* **Kriging（統計方法）**
* **Random Forest（機器學習）**

看看哪種方法更適合補足這些空白區域。

---

## 步驟 3：理解問題

請看看你第 5 週的 Folium 地圖，注意以下幾點：

* 花蓮山區有大片**無測站區域**
* 那些區域的降雨量是多少？
* HeatMap 只是視覺化的「熱度圖」
* **它不是真正的空間內插**

指揮官可能會問：

> **「秀林鄉山區的降雨量估計是多少？可信度如何？」**

**Kriging** 是地統計學（Geostatistics）的核心方法。

它不只給你內插值，還會提供：

> **估計不確定性（variance）**

---

## 步驟 4：快速概念預覽

### 什麼是 Kriging？

Kriging 是一種 **最佳線性無偏估計器（BLUE, Best Linear Unbiased Estimator）**，它會：

1. 分析已知點之間的**空間自相關性**（Variogram）
2. 根據距離與方向分配每個已知點的**最佳權重**
3. 產出：

   * **內插值**
   * **變異數（不確定性）**

---

### 課堂中會看到的重要術語

| 英文               | 中文         | 說明                     |
| ---------------- | ---------- | ---------------------- |
| Variogram        | 變異圖 / 半變異圖 | 描述空間自相關結構的函數           |
| Sill             | 基台值        | 變異達到的最大值               |
| Range            | 影響範圍       | 超過此距離後資料不再相關           |
| Nugget           | 塊金效應       | 零距離時的變異（量測誤差 + 微尺度變異）  |
| Ordinary Kriging | 普通克利金      | 最常見 Kriging 類型（假設均值未知） |

---

### 什麼是 Random Forest？

Random Forest 是一種 **機器學習方法**。

核心概念很直觀：

1. 將每個測站的**座標（easting, northing）**作為輸入特徵
2. 將**降雨量**作為預測目標
3. 使用大量決策樹進行投票平均

換句話說：

```text
f(座標) → 降雨量
```

---

## Kriging 與 Random Forest 比較

課堂中會比較兩者差異：

| 項目   | Kriging              | Random Forest  |
| ---- | -------------------- | -------------- |
| 理論基礎 | 空間自相關（距離越近越相似）       | 資料模式學習         |
| 不確定性 | ✅ 可提供誤差地圖（Sigma Map） | ❌ 原生不提供        |
| 優勢   | 物理意義清楚、可信度高          | 易加入額外特徵（海拔、坡度） |

> **課堂核心問題：**
> 「同一份資料，兩種方法會得到多不一樣的結果？
> 指揮官該相信哪一個？」

---

## 步驟 5：（選用）Google Colab 準備

如果你的電腦 RAM 小於 8GB，建議在 Colab 上執行 Kriging：

```python
# Colab 儲存格
!pip install pykrige scikit-learn rasterio rasterstats
```

請上傳你第 5 週的雨量站 GeoDataFrame
（建議儲存為 GeoJSON 或含 lat/lon/rain 的 CSV）

---

## 疑難排解

**Q：`pykrige` 匯入失敗？**
A：請嘗試：

```bash
pip install --upgrade pykrige
```

某些系統可再試：

```bash
pip install pykrige[plot]
```

---

**Q：`scipy` 版本衝突？**
A：請確認版本 >= 1.7

```bash
pip install --upgrade scipy
```

---

**Q：如果我的第 5 週 notebook 還跑不起來怎麼辦？**
A：課堂上我們會提供一個預先製作好的降雨量 GeoDataFrame 作為備用方案。請專注於 `pykrige` 的安裝。


