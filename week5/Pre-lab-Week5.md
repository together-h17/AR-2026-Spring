# Week 5 Pre-lab: CWA API Setup & Folium Environment

> Please complete the following steps **before class** to ensure your environment is ready.
> Estimated time: 20–30 minutes

---

## Step 1: Install New Packages

```bash
# Activate your virtual environment first!
# macOS / Linux:
source gis-env/bin/activate
# Windows:
gis-env\Scripts\activate

# Install Folium (interactive maps) and requests (API calls)
pip install folium requests python-dotenv branca
```

Verify installation:

```python
import folium
import requests
print(f"Folium version: {folium.__version__}")
print("✅ All packages ready for Week 5!")
```

---

## Step 2: Register for CWA Open Data API Key

We will use the Central Weather Administration (CWA) real-time rainfall API in class.

1. **Go to** [氣象資料開放平臺](https://opendata.cwa.gov.tw/)
2. **Click** 「會員登入」→「加入會員」
3. **Register** with your email (use school email)
4. **After login**, go to 「會員中心」→ find your **授權碼 (Authorization Key)**
5. **Copy** the key — it looks like: `CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

> **Important**: Keep your API key private. Never push it to GitHub.

### Test the API

```python
import requests

API_KEY = "your-api-key-here"  # Replace with your key
URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization={API_KEY}&limit=3&format=JSON"

resp = requests.get(URL)
data = resp.json()

if data.get("success") == "true":
    stations = data["records"]["Station"]
    for s in stations:
        name = s["StationName"]
        rain = s["RainfallElement"]["Past1hr"]["Precipitation"]
        print(f"  {name}: {rain} mm/hr")
    print(f"\n✅ CWA API works! Retrieved {len(stations)} stations.")
else:
    print("❌ API call failed. Check your API key.")
```

> **Note**: If you see `Precipitation: -998.0`, it means "no data" (not negative rainfall!).

---

## Step 3: Set Up Your `.env` File

Add your CWA API key to your project's `.env`:

```
# Week 5 additions
CWA_API_KEY=CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
APP_MODE=LIVE
SIMULATION_DATA=data/scenarios/fungwong_202511.json

# Keep Week 3-4 settings
PROJECT_CRS=3826
TARGET_COUNTY=花蓮縣
SLOPE_THRESHOLD=30
```

Make sure `.env` is in your `.gitignore`!

---

## Step 4: Download Typhoon Fung-wong Historical Data

In class we will "replay" the 2025 Typhoon Fung-wong rainfall to test our ARIA system.

### Data Source: CoLife 歷史資料庫

The historical data comes from **CoLife (Community of Life)**，Taiwan's open environmental data platform:

> **URL**: https://history.colife.org.tw/
>
> **Path**: 氣象 → 中央氣象署_雨量站 → 202511
>
> CoLife archives CWA station observations as downloadable **CSV files** (one row per station per time step). The course instructor has pre-processed the CSV into a JSON file (`fungwong_202511.json`) that mirrors the CWA API structure — so your code can handle both live and historical data with the same parser.

### Setup

1. **下載鳳凰颱風歷史雨量 JSON**：
   - [Google Drive 下載連結](https://drive.google.com/file/d/182rLmpqc9TcLAJctxBXW2Gsc0Xk6jWKF/view?usp=sharing)
   - 下載後放到你的專案資料夾：`data/scenarios/fungwong_202511.json`

2. **Quick check** (run in Python):

```python
import json

with open('data/scenarios/fungwong_202511.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Stations: {len(data['records']['Station'])}")
print(f"Snapshot time: {data['records']['Station'][0]['ObsTime']['DateTime']}")
print("✅ Historical data loaded!")
```

> **What is this file?** The instructor downloaded the CoLife CSV (`rain_20251111.csv`, ~180K rows covering the full day), filtered the 18:50 TST snapshot (Typhoon Fung-wong peak), and converted it to a JSON file that mirrors the CWA API structure. The structure is **similar** to the live API response (both use `records.Station[]`), but has minor differences:
> - **Converted CoLife JSON**: 1 coordinate set per station (WGS84 only), values are numbers (float)
> - **Live API**: 2 coordinate sets (TWD67 + WGS84), values may be strings
>
> Your `parse_rainfall_json()` should use a `normalize_cwa_json()` helper to handle both formats → analysis logic stays the same.

---

## Step 5 (Optional): Review Week 3-4 Concepts

Make sure you are comfortable with:

- **GeoDataFrame**: `.to_crs()`, `.buffer()`, `gpd.sjoin()`
- **Raster basics**: DEM, slope, zonal statistics
- **ARIA v1.0/v2.0**: River buffer risk + terrain risk
- **`.env` + `python-dotenv`**: Loading configuration variables

---

## Troubleshooting

**Q: CWA API returns 401 Unauthorized?**
A: Your API key might be wrong. Log in to the CWA platform and copy it again.

**Q: `folium` import fails?**
A: Make sure you activated your virtual environment. Try: `pip install --upgrade folium`

**Q: API returns empty stations?**
A: Some stations may be offline. Try removing the `limit` parameter to get all stations.

**Q: I don't have a Google account for Drive?**
A: You can download the historical JSON directly from the course LMS instead.