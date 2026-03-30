# 第 5 週課前預習：CWA API 設定與 Folium 環境準備

> 請於**上課前完成以下步驟**，以確保你的環境已準備就緒。
> 預估時間：20–30 分鐘

---

## 步驟 1：安裝新的套件

```bash
# 請先啟動你的虛擬環境！
# macOS / Linux：
source gis-env/bin/activate

# Windows：
gis-env\Scripts\activate

# 安裝 Folium（互動式地圖）與 requests（API 呼叫）
pip install folium requests python-dotenv branca
```

驗證安裝：

```python
import folium
import requests

print(f"Folium version: {folium.__version__}")
print("✅ 第 5 週所有套件已準備完成！")
```

---

## 步驟 2：註冊 CWA 開放資料 API 金鑰

本週課堂中我們會使用 **中央氣象署（CWA）即時雨量 API**。

1. 前往 **氣象資料開放平臺**
   https://opendata.cwa.gov.tw/

2. 點選
   **「會員登入」→「加入會員」**

3. 使用你的電子郵件註冊（建議使用學校信箱）

4. 登入後進入
   **「會員中心」** → 找到你的 **授權碼（Authorization Key）**

5. 複製該金鑰，格式類似：

```text
CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

> **重要**：請妥善保管你的 API 金鑰，切勿上傳至 GitHub。

---

### 測試 API

```python
import requests

API_KEY = "CWA-6AA937C9-D85D-4684-B581-2D53E304C2EF"  # 請替換成你的金鑰

URL = (
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/"
    f"O-A0002-001?Authorization={API_KEY}&limit=3&format=JSON"
)

resp = requests.get(URL)
data = resp.json()

if data.get("success") == "true":
    stations = data["records"]["Station"]

    for s in stations:
        name = s["StationName"]
        rain = s["RainfallElement"]["Past1hr"]["Precipitation"]
        print(f"  {name}: {rain} mm/hr")

    print(f"\n✅ CWA API 正常運作！共取得 {len(stations)} 個測站。")
else:
    print("❌ API 呼叫失敗，請檢查你的 API 金鑰。")
```

> **注意**：如果你看到 `Precipitation: -998.0`，代表的是「無資料」，並不是負雨量。

---

## 步驟 3：設定你的 `.env` 檔案

請將你的 CWA API 金鑰加入專案的 `.env`：

```text
# 第 5 週新增設定
CWA_API_KEY=CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
APP_MODE=LIVE
SIMULATION_DATA=data/scenarios/fungwong_202511.json

# 保留第 3–4 週設定
PROJECT_CRS=3826
TARGET_COUNTY=花蓮縣
SLOPE_THRESHOLD=30
```

請確認 `.env` 已加入 `.gitignore`！

---

## 步驟 4：下載鳳凰颱風歷史資料

課堂中我們將使用 **2025 年鳳凰颱風（Typhoon Fung-wong）** 的歷史雨量資料，來測試你的 ARIA 系統。

---

### 資料來源：CoLife 歷史資料庫

歷史資料來源為 **CoLife（Community of Life）**，臺灣的開放環境資料平台。

> 網址：
> https://history.colife.org.tw/

> 路徑：
> **氣象 → 中央氣象署_雨量站 → 202511**

CoLife 會將 CWA 測站觀測資料整理成可下載的 **CSV 檔案**
（每一列代表一個測站在某個時間點的觀測值）。

授課教師已經將原始 CSV 預先轉換成 JSON：

```text
fungwong_202511.json
```

其結構與 CWA API 相容，方便你使用相同程式處理。

---

### 設定方式

1. **下載鳳凰颱風歷史雨量 JSON**

   * Google Drive 下載連結
   * 下載後放入：

```text
data/scenarios/fungwong_202511.json
```

2. **快速測試**

```python
import json

with open(
    "data/scenarios/fungwong_202511.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

print(f"測站數量: {len(data['records']['Station'])}")
print(
    f"快照時間: "
    f"{data['records']['Station'][0]['ObsTime']['DateTime']}"
)
print("✅ 歷史資料載入成功！")
```

---

### 這個檔案是什麼？

教師從 CoLife 下載原始 CSV：

```text
rain_20251111.csv
```

約 **18 萬筆資料**，涵蓋整天觀測。

之後篩選出：

```text
2025/11/11 18:50
```

也就是鳳凰颱風高峰時刻，轉成 JSON。

---

### 與即時 API 的差異

#### CoLife JSON

* 每站只有 **1 組座標**
* 使用 **WGS84**
* 數值通常是 `float`

---

#### Live API

* 每站有 **2 組座標**
* TWD67 + WGS84
* 數值可能是字串

---

因此你的程式應該寫：

```python
normalize_cwa_json()
```

來統一格式。

---

## 步驟 5（選修）：複習第 3–4 週概念

請確認你熟悉以下內容：

* **GeoDataFrame**

  * `.to_crs()`
  * `.buffer()`
  * `gpd.sjoin()`

* **Raster 基礎**

  * DEM
  * slope
  * zonal statistics

* **ARIA v1.0 / v2.0**

  * 河川緩衝區風險
  * 地形風險

* **`.env` + `python-dotenv`**

  * 環境變數讀取

---

## 疑難排解（Troubleshooting）

### Q：CWA API 回傳 401 Unauthorized？

A：你的 API 金鑰可能錯誤，請重新登入平台複製。

---

### Q：`folium` 匯入失敗？

A：請確認已啟動虛擬環境，並執行：

```bash
pip install --upgrade folium
```

---

### Q：API 回傳空測站？

A：部分測站可能離線，可嘗試移除 `limit` 參數。

---

### Q：沒有 Google 帳號無法下載？

A：可改從課程 LMS 下載歷史 JSON。
