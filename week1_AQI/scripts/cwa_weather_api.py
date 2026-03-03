#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中央氣象署自動氣象站觀測資料串接腳本
API: O-A0003-001 (自動氣象站-氣象觀測資料)
"""

import os
import requests
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv
import geopandas as gpd
from shapely.geometry import Point

# 載入環境變數
load_dotenv()

class CWAWeatherAPI:
    """中央氣象署 API 串接類別"""
    
    def __init__(self):
        self.api_key = os.getenv('CWA_API_KEY')
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        self.dataset_id = "O-A0003-001"  # 自動氣象站-氣象觀測資料
        
        if not self.api_key:
            raise ValueError("請在 .env 檔案中設定 CWA_API_KEY")
    
    def get_weather_data(self, limit=None):
        """
        獲取全台自動氣象站觀測資料
        
        Args:
            limit (int): 限制回傳資料筆數，None 表示全部
            
        Returns:
            dict: API 回應資料
        """
        url = f"{self.base_url}/{self.dataset_id}"
        params = {
            'Authorization': self.api_key,
            'format': 'JSON'
        }
        
        if limit:
            params['limit'] = limit
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {e}")
            return None
    
    def parse_temperature_data(self, api_data):
        """
        解析氣溫資料並轉換為 DataFrame
        
        Args:
            api_data (dict): API 回應資料
            
        Returns:
            pd.DataFrame: 包含氣溫資料的 DataFrame
        """
        if not api_data or 'records' not in api_data:
            return pd.DataFrame()
        
        records = api_data['records']['Station']
        
        weather_data = []
        for station in records:
            try:
                # 基本站點資訊
                station_info = {
                    '站點編號': station['StationId'],
                    '站點名稱': station['StationName'],
                    '城市': station['GeoInfo']['CountyName'],
                    '鄉鎮': station['GeoInfo']['TownName'],
                    '經度': float(station['GeoInfo']['Coordinates'][1]['StationLongitude']),  # 使用 WGS84 坐標
                    '緯度': float(station['GeoInfo']['Coordinates'][1]['StationLatitude']),
                    '海拔高度': float(station['GeoInfo']['StationAltitude']),
                    '觀測時間': station['ObsTime']['DateTime']
                }
                
                # 氣象觀測要素
                weather_elements = station['WeatherElement']
                
                # 主要氣象資料
                main_weather = {
                    '天氣現象': weather_elements.get('Weather', ''),
                    '能見度描述': weather_elements.get('VisibilityDescription', ''),
                    '日照時數': self._safe_float(weather_elements.get('SunshineDuration', '0')),
                    '風向': self._safe_float(weather_elements.get('WindDirection', '0')),
                    '風速': self._safe_float(weather_elements.get('WindSpeed', '0')),
                    '氣溫': self._safe_float(weather_elements.get('AirTemperature', '0')),
                    '相對濕度': self._safe_float(weather_elements.get('RelativeHumidity', '0')),
                    '氣壓': self._safe_float(weather_elements.get('AirPressure', '0')),
                    '紫外線指數': self._safe_float(weather_elements.get('UVIndex', '0'))
                }
                
                # 即時降水
                now_data = weather_elements.get('Now', {})
                main_weather['即時降水量'] = self._safe_float(now_data.get('Precipitation', '0'))
                
                # 極端溫度
                daily_extreme = weather_elements.get('DailyExtreme', {})
                if daily_extreme:
                    daily_high = daily_extreme.get('DailyHigh', {}).get('TemperatureInfo', {})
                    daily_low = daily_extreme.get('DailyLow', {}).get('TemperatureInfo', {})
                    main_weather['當日最高溫'] = self._safe_float(daily_high.get('AirTemperature', '0'))
                    main_weather['當日最低溫'] = self._safe_float(daily_low.get('AirTemperature', '0'))
                else:
                    main_weather['當日最高溫'] = None
                    main_weather['當日最低溫'] = None
                
                # 合併資料
                station_data = {**station_info, **main_weather}
                weather_data.append(station_data)
                
            except (KeyError, ValueError, TypeError) as e:
                print(f"解析站點資料時發生錯誤 {station.get('StationId', 'Unknown')}: {e}")
                continue
        
        df = pd.DataFrame(weather_data)
        return df
    
    def _safe_float(self, value):
        """安全轉換為浮點數"""
        if value in ['X', '-99', '-99.0', '', None]:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_temperature_dataframe(self, limit=None):
        """
        獲取氣溫資料的 DataFrame
        
        Args:
            limit (int): 限制回傳資料筆數
            
        Returns:
            pd.DataFrame: 氣溫資料 DataFrame
        """
        api_data = self.get_weather_data(limit)
        df = self.parse_temperature_data(api_data)
        
        if not df.empty:
            # 轉換觀測時間為 datetime
            df['觀測時間'] = pd.to_datetime(df['觀測時間'])
            
            # 按氣溫排序
            if '氣溫' in df.columns:
                df = df.sort_values('氣溫', ascending=False)
        
        return df
    
    def create_geodataframe(self, df):
        """
        將 DataFrame 轉換為 GeoDataFrame
        
        Args:
            df (pd.DataFrame): 氣象資料 DataFrame
            
        Returns:
            gpd.GeoDataFrame: 地理資料框
        """
        if df.empty:
            return gpd.GeoDataFrame()
        
        # 創建幾何點
        geometry = [Point(xy) for xy in zip(df['經度'], df['緯度'])]
        
        # 建立 GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        return gdf
    
    def save_to_file(self, df, filename=None, file_format='csv'):
        """
        儲存資料到檔案
        
        Args:
            df (pd.DataFrame): 要儲存的資料
            filename (str): 檔案名稱
            file_format (str): 檔案格式 ('csv', 'json', 'geojson')
        """
        if df.empty:
            print("沒有資料可以儲存")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_data_{timestamp}"
        
        output_path = os.path.join('..', 'data', 'output')
        os.makedirs(output_path, exist_ok=True)
        
        if file_format.lower() == 'csv':
            filepath = os.path.join(output_path, f"{filename}.csv")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"資料已儲存至: {filepath}")
            
        elif file_format.lower() == 'json':
            filepath = os.path.join(output_path, f"{filename}.json")
            df.to_json(filepath, orient='records', ensure_ascii=False, indent=2)
            print(f"資料已儲存至: {filepath}")
            
        elif file_format.lower() == 'geojson':
            gdf = self.create_geodataframe(df)
            if not gdf.empty:
                filepath = os.path.join(output_path, f"{filename}.geojson")
                gdf.to_file(filepath, driver='GeoJSON', encoding='utf-8')
                print(f"地理資料已儲存至: {filepath}")
    
    def get_temperature_summary(self, df):
        """
        獲取氣溫統計摘要
        
        Args:
            df (pd.DataFrame): 氣象資料 DataFrame
            
        Returns:
            dict: 氣溫統計資訊
        """
        if df.empty or '氣溫' not in df.columns:
            return {}
        
        temp_data = df['氣溫'].dropna()
        
        if temp_data.empty:
            return {}
        
        summary = {
            '總測站數': len(df),
            '有效氣溫測站數': len(temp_data),
            '最高氣溫': temp_data.max(),
            '最低氣溫': temp_data.min(),
            '平均氣溫': temp_data.mean(),
            '最高氣溫測站': df.loc[temp_data.idxmax(), '站點名稱'],
            '最低氣溫測站': df.loc[temp_data.idxmin(), '站點名稱'],
            '資料時間': df['觀測時間'].max().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary


def main():
    """主程式"""
    print("=== 中央氣象署自動氣象站氣溫資料串接 ===")
    
    try:
        # 建立 API 串接物件
        cwa_api = CWAWeatherAPI()
        
        # 獲取氣溫資料
        print("正在獲取氣溫資料...")
        df = cwa_api.get_temperature_dataframe()
        
        if df.empty:
            print("沒有獲取到資料")
            return
        
        # 顯示基本資訊
        print(f"\n成功獲取 {len(df)} 個測站資料")
        
        # 顯示氣溫統計
        summary = cwa_api.get_temperature_summary(df)
        if summary:
            print("\n=== 氣溫統計摘要 ===")
            for key, value in summary.items():
                print(f"{key}: {value}")
        
        # 顯示前10個測站的氣溫資料
        if '氣溫' in df.columns:
            print("\n=== 氣溫排名前10的測站 ===")
            top_10 = df[['站點名稱', '城市', '氣溫', '觀測時間']].head(10)
            print(top_10.to_string(index=False))
        
        # 儲存資料
        print("\n正在儲存資料...")
        cwa_api.save_to_file(df, file_format='csv')
        cwa_api.save_to_file(df, file_format='geojson')
        
        print("\n資料串接完成！")
        
    except Exception as e:
        print(f"程式執行錯誤: {e}")


if __name__ == "__main__":
    main()
