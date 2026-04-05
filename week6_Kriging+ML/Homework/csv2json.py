# -*- coding: utf-8 -*-
# 後來沒用到

import pandas as pd
import json

def csv_to_cwa_json(csv_path, json_path, obs_datetime):
    df = pd.read_csv(csv_path, encoding="utf-8")

    station_list = []

    for _, row in df.iterrows():
        station = {
            "StationName": row["StationName"],
            "StationId": row["StationId"],
            "ObsTime": {
                "DateTime": obs_datetime
            },
            "GeoInfo": {
                "CountyName": row["CountyName"],
                "TownName": row["TownName"],
                "Coordinates": [
                    {
                        "StationLatitude": float(row["Latitude"]),
                        "StationLongitude": float(row["Longitude"])
                    }
                ]
            },
            "RainfallElement": {
                "Past10Min": {
                    "Precipitation": float(row["Past10Min"])
                },
                "Past1hr": {
                    "Precipitation": float(row["Past1hr"])
                },
                "Past3hr": {
                    "Precipitation": float(row["Past3hr"])
                },
                "Past6hr": {
                    "Precipitation": float(row["Past6hr"])
                },
                "Past12hr": {
                    "Precipitation": float(row["Past12hr"])
                },
                "Past24hr": {
                    "Precipitation": float(row["Past24hr"])
                }
            }
        }

        station_list.append(station)

    output = {
        "success": "true",
        "result": {
            "resource_id": "O-A0002-001",
            "fields": []
        },
        "records": {
            "Station": station_list
        }
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"轉換完成：{json_path}")


    csv_to_cwa_json(
    "rain_20250728.csv",
    "rain_20250728.json",
    obs_datetime="2025-07-28T23:50:00+08:00"
)