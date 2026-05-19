# 第 13 週課前準備：Google Earth Engine 與雲端尺度時間序列 — ARIA v9.0 環境設定

**課程：** 臺大遙測與空間資訊之分析與應用  
**授課教師：** 蘇文瑞教授  
**週次：** 第 13 週｜**主題：** Google Earth Engine 與雲端尺度時間序列分析（雲端運算與多時相分析）  
**所需時間：** 約 25 分鐘

---

## 學習目標

完成本課前準備後，你將能夠：
- 建立或確認你的 Google Earth Engine（GEE）帳號
- 安裝 `earthengine-api` 與 `geemap` Python 套件
- 理解從**單景影像分析**到**雲端尺度時間序列分析**的概念轉換
- 複習 GEE 的核心抽象概念：`Image`、`ImageCollection`、`Reducer`
- 理解 InSAR 的基礎概念，作為概念參考（不實作）

---

## 步驟 1：建立／確認 GEE 帳號

### 1a. 註冊 Google Earth Engine

GEE 對研究與教育用途免費。

1. 前往 [https://code.earthengine.google.com/register](https://code.earthengine.google.com/register)
2. 使用你的 Google 帳號登入
3. 接受服務條款
4. 建立一個 **Cloud Project**（可以使用既有 Google Cloud 專案，也可以建立新的專案；免費額度即足夠本課使用）

> **重要：** GEE 帳號通常會即時核准，但偶爾可能需要最多 24 小時。請務必在**上課前**完成這個步驟。

### 1b. 確認存取權限

註冊完成後，前往 [https://code.earthengine.google.com/](https://code.earthengine.google.com/)，確認你能看到 Code Editor 介面。本課不需要使用 Code Editor，我們會使用 Python API；但能看到編輯器代表你的帳號已啟用。

---

## 步驟 2：安裝 Python 套件並完成驗證

本週**不需要 GPU**。所有運算都會在 Google 雲端伺服器上執行；你的本機電腦只負責送出指令與顯示結果。

### 2a. 安裝套件

```bash
# 本機使用者（VS Code / Windsurf / Terminal）— 使用 pip 安裝
pip install earthengine-api geemap
```

```python
# 確認安裝
import ee
import geemap

print("✓ earthengine-api:", ee.__version__)
print("✓ geemap:", geemap.__version__)
```

> **Colab 使用者：** `earthengine-api` 與 `geemap` 已預先安裝，可略過 pip install。

### 2b. 驗證 — 依你的開發環境選擇方式

GEE 驗證只需要做一次，之後 token 會儲存在本機（`~/.config/earthengine/`）。但不同開發環境的驗證方式不同，請依你的環境選擇。

#### 選項 A：Google Colab（推薦初學者）

在 Colab 上最簡單，直接在 notebook cell 執行：

```python
ee.Authenticate()
ee.Initialize(project='your-project-id')  # 替換為你的 Cloud Project ID
print("✓ GEE authenticated and initialized")
```

Colab 會自動跳出 Google 登入視窗，依照提示授權即可。Token 會自動存入 Colab runtime。

#### 選項 B：VS Code / Windsurf / Cursor（本機 IDE + Jupyter Kernel）

> **⚠️ 已知問題：** VS Code、Windsurf、Cursor 等 IDE 的 Jupyter kernel **不支援 `input()` 互動輸入**。若直接在 notebook cell 執行 `ee.Authenticate()`，可能會卡住，因為它需要你貼上驗證碼，但 IDE 不會顯示輸入框。

**解決方式：先在 Terminal 完成驗證，再回 notebook 使用。**

**步驟 1 — 開啟 Terminal（終端機）：**
- VS Code：上方選單 `Terminal` → `New Terminal`，或快捷鍵 `` Ctrl+` ``
- Windsurf：與 VS Code 相同，使用底部 Terminal panel
- macOS 系統 Terminal 或 Windows PowerShell 也可以

**步驟 2 — 在 Terminal 執行驗證指令：**

```bash
earthengine authenticate
```

這會開啟瀏覽器，引導你登入 Google 帳號並授權。授權完成後，Terminal 會顯示 `Successfully saved authorization token.`

> **如果出現 `command not found: earthengine`：**  
> 表示 `earthengine-api` 尚未安裝，或安裝路徑不在 PATH 中。請先執行：
> ```bash
> pip install earthengine-api
> ```
> 如果使用 conda，改用 `conda install -c conda-forge earthengine-api`。  
> 安裝完成後，可能需要重新開啟 Terminal，系統才找得到指令。

**步驟 3 — 回到 notebook，只需 Initialize（不需再 Authenticate）：**

```python
import ee
ee.Initialize(project='your-project-id')  # 替換為你的 Cloud Project ID
print("✓ GEE initialized — token loaded from terminal authentication")
```

因為 token 已存在 `~/.config/earthengine/`，`ee.Initialize()` 會自動讀取，不需要再執行 `ee.Authenticate()`。

#### 選項 C：純 Terminal / 命令列（不用 Jupyter）

如果你偏好使用 `.py` 腳本，而不是 notebook：

```bash
# 步驟 1：Authenticate（只需一次）
earthengine authenticate

# 步驟 2：執行你的腳本
python my_gee_script.py
```

腳本中同樣只需要 `ee.Initialize(project='your-project-id')`。

#### 驗證方式比較表

| 環境 | 驗證方式 | 備註 |
|------|---------|------|
| **Google Colab** | 在 notebook cell 執行 `ee.Authenticate()` | 最簡單，自動彈出授權視窗 |
| **VS Code** | Terminal `earthengine authenticate` → notebook `ee.Initialize()` | IDE Jupyter 不支援 `input()`，必須用 Terminal |
| **Windsurf** | 同 VS Code | Windsurf 基於 VS Code，行為一致 |
| **Cursor** | 同 VS Code | Cursor 基於 VS Code，行為一致 |
| **JupyterLab（本機）** | 在 notebook cell 執行 `ee.Authenticate()` | 支援 `input()`，和 Colab 一樣簡單 |
| **PyCharm** | Terminal `earthengine authenticate` → script `ee.Initialize()` | PyCharm 的 Python Console 可能支援 `input()` |
| **Terminal + .py** | `earthengine authenticate` → `python script.py` | 適合自動化腳本 |

### 2c. 確認連線

不管你使用哪一種方式驗證，最後都用以下程式碼確認 GEE 連線正常：

```python
# 快速測試：取得花蓮某點的海拔
point = ee.Geometry.Point([121.6, 23.97])
dem = ee.Image('USGS/SRTMGL1_003')
elevation = dem.sample(point, 30).first().get('elevation').getInfo()
print(f"✓ GEE connected — Hualien elevation: {elevation} m")
```

如果印出海拔高度值（例如 `15 m`），代表你的 GEE 環境已就緒。

### 2d. 確認其他套件

```python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 這些套件應該已在 W8–W12 使用過
print("✓ numpy:", np.__version__)
print("✓ All core dependencies loaded successfully")
```

### 常見問題排解

| 問題 | 原因 | 解決方式 |
|------|------|---------|
| `ee.Authenticate()` 卡住不動 | VS Code/Windsurf 的 Jupyter 不支援 `input()` | 改用 Terminal 執行 `earthengine authenticate` |
| `command not found: earthengine` | 未安裝 `earthengine-api` 或 PATH 未更新 | `pip install earthengine-api`，然後重開 Terminal |
| `ee.Initialize()` 報錯 `project not found` | Project ID 打錯或未啟用 Earth Engine API | 到 [Google Cloud Console](https://console.cloud.google.com/) 確認 project ID 並啟用 Earth Engine API |
| `HttpError 403: Earth Engine is not enabled` | Cloud Project 未開啟 Earth Engine API | 到 Cloud Console → APIs & Services → 搜尋 “Earth Engine” → Enable |
| `google.auth.exceptions.DefaultCredentialsError` | Token 過期或損壞 | 重新執行 `earthengine authenticate` |
| Colab 上 `ee.Authenticate()` 沒有跳視窗 | 瀏覽器擋了彈出視窗 | 允許 colab.research.google.com 的彈出視窗 |

---

## 步驟 3：概念跳躍 — 從單景影像到時間序列

### W8–W12 做了什麼

前幾週，我們使用 STAC API + 本機運算，**一次分析一張影像**：

| 週次 | 我們做了什麼 | 限制 |
|------|-------------|------|
| W8 | 從一張 Sentinel-2 影像計算 NDVI | 只有一個時間點的快照 |
| W9 | 計算兩個日期之間的 ΔNDVI | 只有兩個日期；需要手動下載 |
| W10 | 從一張 SAR 影像取得 backscatter | 單次 SAR 觀測 |
| W12 | 從一張影像進行分類 | 分類器只用單一日期訓練 |

**核心限制：** 我們下載個別影像，在本機處理，因此只能處理少量場景。如果你需要 10 年資料呢？如果需要 500 張影像呢？

### W13 升級什麼

**Google Earth Engine** 將運算移到雲端。你不再下載影像，而是把分析指令送到 Google 伺服器，由伺服器處理 petabyte 級衛星資料，最後只回傳結果。

```
W8–W12：  下載影像 → 本機處理 → 一次處理一張場景
W13：     送出指令 → GEE 在雲端處理 500+ 張影像 → 回傳結果
```

**升級路徑：**
```
v5.0 (W8)  → 光譜分析：一張影像、一個指標
v6.0 (W9)  → 變遷偵測：兩張影像、一個差值
v7.0 (W10) → SAR 融合：一張光學 + 一張 SAR
v8.0 (W12) → 分類：一張影像、多個波段 → 土地覆蓋圖
v9.0 (W13) → 雲端時間序列：數百張影像 → 時間趨勢 ⬆
```

---

## 步驟 4：GEE 核心概念 — 概念複習

### Image（影像）

`ee.Image` 是一張具有波段與 metadata 的 raster 影像。它類似你透過 STAC API 載入的影像，但資料存放在 Google 伺服器上，你不會下載原始像元。

```python
# 範例：一張 Sentinel-2 影像
image = ee.Image('COPERNICUS/S2_SR_HARMONIZED/20240405T021601_20240405T022256_T51RUH')
print(image.bandNames().getInfo())  # ['B1', 'B2', ..., 'B12', 'SCL', ...]
```

### ImageCollection（影像集合）

`ee.ImageCollection` 是一疊影像，可能包含數千張，並可依位置、日期與 metadata 篩選。這是本週的關鍵升級：不再像 STAC API 那樣一張一張手動搜尋，而是描述你要什麼，讓 GEE 找出所有符合條件的影像。

```python
# 花蓮上空所有 Sentinel-2 影像（2020–2026），雲量 < 40%
collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(ee.Geometry.Point([121.6, 23.97]))
    .filterDate('2020-01-01', '2026-03-31')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40)))

print(f"Found {collection.size().getInfo()} images")
```

### Reducer（聚合器）

`Reducer` 會將一個集合摘要成單一數值或影像。例如，`ee.Reducer.median()` 會計算集合中所有影像的逐像元中位數，有效建立近似無雲的合成影像。

| Reducer | 功能 | 使用情境 |
|---------|------|----------|
| `median()` | 逐像元中位數 | 無雲合成影像 |
| `mean()` | 逐像元平均值 | 平均反射率 |
| `min()` / `max()` | 逐像元最小值／最大值 | 極端值偵測 |
| `linearFit()` | 每個像元做線性迴歸 | 長期趨勢分析 |

### Lazy Evaluation（延遲運算）

GEE 使用**延遲運算**：除非你明確要求結果，例如 `.getInfo()`、`geemap.Map` 或 `.getDownloadURL()`，否則不會真正執行計算。這代表你可以連續串接許多操作而不用等待；只有當你要求最終輸出時，GEE 才會執行。

---

## 步驟 5：InSAR — 概念參考（不實作）

### 什麼是 InSAR？

**InSAR（Interferometric SAR，合成孔徑雷達干涉測量）** 透過比較不同時間取得的兩張 SAR 影像的**相位**，量測地表位移。W10 使用的是 SAR **振幅**（backscatter intensity，回波強度）來偵測淹水；InSAR 則使用 SAR **相位**，用來偵測毫米等級的地表移動，例如地震造成的下陷、邊坡蠕動或火山膨脹。

| | W10 SAR（Amplitude，振幅） | InSAR（Phase，相位） |
|---|---|---|
| 量測內容 | Backscatter intensity（回波強度） | Phase difference（相位差） |
| 可偵測現象 | 地表粗糙度、淹水 | Ground displacement（地表位移） |
| 精度 | Qualitative（定性） | mm-level（毫米級定量） |
| 應用 | 淹水製圖、崩塌偵測 | 地層下陷、邊坡蠕動、斷層滑移 |

### 為什麼不能在 GEE 做 InSAR？

GEE 只提供 Sentinel-1 **GRD**（Ground Range Detected）資料，也就是只有強度，沒有相位資訊。InSAR 需要含有相位的 **SLC**（Single Look Complex）資料，而 GEE 並未提供。InSAR 處理也需要專門演算法，例如共配準、干涉圖產生、相位展開，這些超出 GEE 的運算模型。

### 可用資源與工具

如果你想自行探索 InSAR，以下是重要資源。

**資料來源：**
- ASF DAAC ([https://search.asf.alaska.edu/](https://search.asf.alaska.edu/)) — Sentinel-1 SLC 資料下載
- UNAVCO / EarthScope — 大地測量 InSAR 產品
- COMET LiCSAR ([https://comet.nerc.ac.uk/COMET-LiCS-portal/](https://comet.nerc.ac.uk/COMET-LiCS-portal/)) — 預先處理好的 Sentinel-1 干涉圖

**處理軟體：**
| 工具 | 類型 | 說明 |
|------|------|------|
| **ESA SNAP** | 桌面 GUI + CLI | 免費、ESA 官方工具箱，適合初學者 |
| **ISCE2** | Python library | NASA JPL，研究級，命令列操作 |
| **MintPy** | Python library | 時間序列 InSAR（PS-InSAR、SBAS），建立在 ISCE2 之上 |
| **GMTSAR** | CLI | 基於 GMT，有完整教學文件 |
| **LiCSBAS** | Python library | 搭配 COMET LiCSAR 產品使用，是最容易入門的方式 |

**建議學習路徑：**
1. 從 ESA SNAP 教學開始（視覺化、逐步操作）
2. 使用預先處理好的 LiCSAR 產品嘗試 LiCSBAS（不需要自己處理 SLC）
3. 若進入研究階段：使用 ISCE2 + MintPy 做時間序列 InSAR

**推薦閱讀：**
- [InSAR 彩虹干涉環判讀](https://tech.ardswc.gov.tw/EPaper/Home/EPaper?PaperID=97f62ecf-44eb-4f41-a5a7-5a1d4048ef67) — 農村發展及水土保持署技術電子報第 141 期（2025）。使用 Kīlauea 火山與 2016 熊本地震案例，圖解四步驟干涉環判讀法：確認衛星波段 → 計算干涉環數 → 判斷接近／遠離方向 → 估算位移量。中文，入門必讀。
- [大型山崩判釋新利器：結合 InSAR 與光達數值地形](https://www.ceci.org.tw/Upload/Download/F45F3A64-D098-465A-9CDB-F2A4B7A9DD10.pdf) — 陳柔妃、林慶偉（2018），中華技術期刊第 119 期。以南投縣定遠新村為例，說明如何結合 TCP-InSAR 地表變形分析與 LiDAR DEM 地形特徵判釋，修正大型山崩潛勢區範圍。台灣本土案例，與本課防災主題直接相關。
- 水保署技術電子報 InSAR 系列：[第 84 期](https://tech.ardswc.gov.tw/EPaper/Home/EPaper?PaperID=30781387-f5d7-4ce9-8484-816b15841fba)（SAR 波段介紹）、[第 120 期](https://tech.ardswc.gov.tw/EPaper/Home/EPaper?PaperID=30080cd6-2491-42f7-b744-034c838eefd7)（D-InSAR 與 PS-InSAR 基本概念）、[第 126 期](https://tech.ardswc.gov.tw/EPaper/Home/EPaper?PaperID=de1a4386-5f25-4b33-bf0d-ffc71aa121c9)（MT-InSAR + INV 崩塌預警）

> **注意：** InSAR 處理需要大量計算資源與儲存空間（SLC 檔案每個約 4–8 GB）。它本身足以構成一門完整課程。本段介紹的目的，是讓你了解這項技術，若未來研究需要，可以自行深入探索。

### 自我測驗 Q1

SAR 振幅分析（W10）與 InSAR 的關鍵差異是什麼？

**答案：** SAR 振幅分析量測回波強度（地表粗糙度、水分），適合定性偵測淹水或崩塌。InSAR 則量測兩次觀測之間的相位差，可用毫米級精度定量量測地表位移，適合監測地層下陷、邊坡蠕動與斷層滑移。

---

## 步驟 6：GEE vs STAC API — 概念複習

### 什麼時候用哪個？

| | STAC API（W8–W12） | GEE（W13+） |
|---|---|---|
| 運算位置 | 本機（你的電腦） | 雲端（Google 伺服器） |
| 資料存取 | 下載 → 處理 | 在伺服器處理 → 下載結果 |
| 優勢 | 完整控制，可使用任意演算法 | 大規模處理、petabyte 級 catalog |
| 限制 | 受限於你的 RAM／硬碟 | 受限於 GEE 支援的運算 |
| 最適合 | 自訂分析、ML 訓練 | 時間序列、大範圍監測 |
| Python 套件 | `pystac_client` + `stackstac` | `earthengine-api` + `geemap` |

**關鍵觀念：** 兩者互補，不是競爭。當你需要在大範圍處理數百張影像時，使用 GEE。當你需要對單一場景進行細緻控制時，例如用特定波段組合訓練分類器，使用 STAC API。

### 自我測驗 Q2

你需要計算 2015 到 2024 年花蓮縣每個月的平均 NDVI（120 個月合成，來自數百張 Sentinel-2 影像）。你會使用 STAC API 還是 GEE？為什麼？

**答案：** 使用 GEE。若在本機下載數百張影像，可能需要 TB 級儲存空間與數天處理時間。GEE 會在伺服器上處理影像，最後只回傳 120 個月平均 NDVI 值；繁重運算不會進入你的本機電腦。

---

## 步驟 7：自我測驗 — 綜合題

### Q3：GEE 核心概念

將每個 GEE 概念與其描述配對：

| 概念 | 描述 |
|------|------|
| `ee.Image` | _____ |
| `ee.ImageCollection` | _____ |
| `ee.Reducer` | _____ |
| Lazy evaluation | _____ |

選項：
- A. 將多個數值摘要成一個值，例如 median、mean、linear fit
- B. 具有波段與 metadata 的單一 raster 影像
- C. 依位置、日期與 metadata 篩選出的一疊影像
- D. 只有在你要求最終結果時才會執行計算

**答案：** Image = B，ImageCollection = C，Reducer = A，Lazy evaluation = D。

### Q4：時間序列思考

為什麼即使每張個別影像都有 20–40% 雲量，從 50 張影像計算**中位數**合成仍可產生近似無雲的結果？

**答案：** 雲在每張影像中出現的位置不同。對任一像元而言，50 次觀測中大多數通常是無雲狀態。中位數會自動選取「典型」的無雲值，因為雲（非常亮）與雲影（非常暗）屬於統計離群值，會被中位數忽略。

### Q5：InSAR 認知

可以在 Google Earth Engine 中做 InSAR 處理嗎？為什麼可以或不可以？

**答案：** 不可以。GEE 只提供 Sentinel-1 GRD 資料（只有強度），不提供 InSAR 所需、含相位資訊的 SLC 資料。InSAR 也需要共配準與相位展開等專門演算法，而 GEE 不支援這些處理。若要做 InSAR，需要使用 ESA SNAP、ISCE2 或 MintPy 等工具，並從 ASF DAAC 取得 SLC 資料。

---

## 步驟 8：反思問題（選做）

1. **尺度思考：** W9 計算兩個日期之間的 ΔNDVI。如果你計算 10 年中每個連續月份之間的 ΔNDVI，是否能偵測季節型態與長期趨勢？與兩日期比較相比，會揭露哪些新的資訊？

2. **雲端運算取捨：** GEE 很強大，但你不能在上面安裝任意 Python 套件，也不能直接執行自訂深度學習模型。什麼情況下，STAC API 方法（W8–W12）仍然會是更好的選擇？

3. **InSAR + GEE 整合：** 有些研究者會在外部使用 SNAP/ISCE2 處理 InSAR，然後把變形圖匯入 GEE 進行大尺度分析。為什麼這種混合方法會有用？

---

## 上課前檢查清單

- [ ] 已註冊並確認 GEE 帳號（可進入 [code.earthengine.google.com](https://code.earthengine.google.com)）
- [ ] 已安裝 `earthengine-api` 與 `geemap`（`pip install earthengine-api geemap`）
- [ ] 已成功完成 `ee.Authenticate()`
- [ ] `ee.Initialize(project='...')` 可正常執行（快速測試會回傳海拔值）
- [ ] 理解 GEE 核心概念：Image、ImageCollection、Reducer、lazy evaluation
- [ ] 理解 GEE（雲端）與 STAC API（本機）的差異
- [ ] 理解 InSAR 概念（以相位為基礎的位移量測，無法在 GEE 中完成）
- [ ] 知道哪裡可以找到 InSAR 資源（ASF DAAC、SNAP、ISCE2、MintPy）
- [ ] 已完成自我測驗（5 題）

**你已準備好進入第 13 週課程！**

---

*註：如果遇到環境設定問題，請在上課前於 NTUCool 發文或寄信給蘇教授。最常見的問題是 GEE 帳號尚未啟用，請至少在上課前 24 小時完成步驟 1。*
