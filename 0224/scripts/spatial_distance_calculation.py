#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空間距離計算腳本
計算各測站到台北車站的距離（公里）
"""

import os
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

class SpatialDistanceCalculator:
    """空間距離計算類別"""
    
    def __init__(self):
        # 台北車站坐標 (WGS84)
        self.taipei_station = {
            'name': '台北車站',
            'latitude': 25.0478,
            'longitude': 121.5170
        }
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        使用 Haversine 公式計算兩點間的距離
        
        Args:
            lat1, lon1: 起點的緯度和經度
            lat2, lon2: 終點的緯度和經度
            
        Returns:
            float: 距離（公里）
        """
        # 將角度轉換為弧度
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine 公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # 地球半徑（公里）
        r = 6371
        
        distance = c * r
        return distance
    
    def calculate_distances_from_aqi_data(self, aqi_csv_path):
        """
        從 AQI 資料計算各測站到台北車站的距離
        
        Args:
            aqi_csv_path (str): AQI CSV 檔案路徑
            
        Returns:
            pd.DataFrame: 包含距離資料的 DataFrame
        """
        try:
            # 讀取 AQI 資料
            df = pd.read_csv(aqi_csv_path, encoding='utf-8-sig')
            print(f"成功載入 AQI 資料：{len(df)} 個測站")
            
            # 過濾有效坐標的資料
            valid_df = df.dropna(subset=['緯度', '經度'])
            print(f"有效坐標的測站：{len(valid_df)} 個")
            
            if valid_df.empty:
                print("沒有有效坐標資料")
                return pd.DataFrame()
            
            # 計算距離
            distances = []
            for idx, row in valid_df.iterrows():
                try:
                    station_lat = row['緯度']
                    station_lon = row['經度']
                    
                    # 計算到台北車站的距離
                    distance = self.haversine_distance(
                        station_lat, station_lon,
                        self.taipei_station['latitude'], 
                        self.taipei_station['longitude']
                    )
                    
                    distance_info = {
                        '測站名稱': row['測站名稱'],
                        '城市': row['城市'],
                        '測站緯度': station_lat,
                        '測站經度': station_lon,
                        '台北車站緯度': self.taipei_station['latitude'],
                        '台北車站經度': self.taipei_station['longitude'],
                        '距離_公里': round(distance, 2),
                        'AQI': row.get('AQI', ''),
                        '空氣品質等級': row.get('空氣品質等級', ''),
                        '觀測時間': row.get('觀測時間', '')
                    }
                    
                    distances.append(distance_info)
                    
                except Exception as e:
                    print(f"計算測站 {row.get('測站名稱', 'Unknown')} 距離時出錯: {e}")
                    continue
            
            result_df = pd.DataFrame(distances)
            return result_df
            
        except Exception as e:
            print(f"處理 AQI 資料時出錯: {e}")
            return pd.DataFrame()
    
    def calculate_distances_from_weather_data(self, weather_csv_path):
        """
        從氣象資料計算各測站到台北車站的距離
        
        Args:
            weather_csv_path (str): 氣象 CSV 檔案路徑
            
        Returns:
            pd.DataFrame: 包含距離資料的 DataFrame
        """
        try:
            # 讀取氣象資料
            df = pd.read_csv(weather_csv_path, encoding='utf-8-sig')
            print(f"成功載入氣象資料：{len(df)} 個測站")
            
            # 過濾有效坐標的資料
            valid_df = df.dropna(subset=['緯度', '經度'])
            print(f"有效坐標的測站：{len(valid_df)} 個")
            
            if valid_df.empty:
                print("沒有有效坐標資料")
                return pd.DataFrame()
            
            # 計算距離
            distances = []
            for idx, row in valid_df.iterrows():
                try:
                    station_lat = row['緯度']
                    station_lon = row['經度']
                    
                    # 計算到台北車站的距離
                    distance = self.haversine_distance(
                        station_lat, station_lon,
                        self.taipei_station['latitude'], 
                        self.taipei_station['longitude']
                    )
                    
                    distance_info = {
                        '測站名稱': row['站點名稱'],
                        '城市': row['城市'],
                        '測站緯度': station_lat,
                        '測站經度': station_lon,
                        '台北車站緯度': self.taipei_station['latitude'],
                        '台北車站經度': self.taipei_station['longitude'],
                        '距離_公里': round(distance, 2),
                        '氣溫': row.get('氣溫', ''),
                        '觀測時間': row.get('觀測時間', '')
                    }
                    
                    distances.append(distance_info)
                    
                except Exception as e:
                    print(f"計算測站 {row.get('站點名稱', 'Unknown')} 距離時出錯: {e}")
                    continue
            
            result_df = pd.DataFrame(distances)
            return result_df
            
        except Exception as e:
            print(f"處理氣象資料時出錯: {e}")
            return pd.DataFrame()
    
    def save_distance_results(self, df, filename=None):
        """
        儲存距離計算結果到 CSV 檔案
        
        Args:
            df (pd.DataFrame): 距離計算結果
            filename (str): 檔案名稱
        """
        if df.empty:
            print("沒有資料可以儲存")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"distance_to_taipei_station_{timestamp}"
        
        # 確保 outputs 目錄存在
        outputs_dir = '../outputs'
        os.makedirs(outputs_dir, exist_ok=True)
        
        # 儲存到 outputs 目錄
        filepath = os.path.join(outputs_dir, f"{filename}.csv")
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"距離計算結果已儲存至: {filepath}")
        
        return filepath
    
    def generate_distance_summary(self, df):
        """
        生成距離計算摘要統計
        
        Args:
            df (pd.DataFrame): 距離計算結果
            
        Returns:
            dict: 統計摘要
        """
        if df.empty or '距離_公里' not in df.columns:
            return {}
        
        summary = {
            '總測站數': len(df),
            '最近測站': df.loc[df['距離_公里'].idxmin(), '測站名稱'],
            '最近距離_公里': df['距離_公里'].min(),
            '最遠測站': df.loc[df['距離_公里'].idxmax(), '測站名稱'],
            '最遠距離_公里': df['距離_公里'].max(),
            '平均距離_公里': df['距離_公里'].mean(),
            '中位數距離_公里': df['距離_公里'].median()
        }
        
        return summary


def main():
    """主程式"""
    print("=== 空間距離計算：測站到台北車站 ===")
    
    try:
        # 創建距離計算器
        calculator = SpatialDistanceCalculator()
        
        # 查找可用的資料檔案
        output_dir = '../data/output'
        aqi_files = [f for f in os.listdir(output_dir) if f.startswith('aqi_data_') and f.endswith('.csv')]
        weather_files = [f for f in os.listdir(output_dir) if f.startswith('weather_data_') and f.endswith('.csv')]
        
        print(f"找到 AQI 資料檔案: {len(aqi_files)} 個")
        print(f"找到氣象資料檔案: {len(weather_files)} 個")
        
        results = []
        
        # 處理 AQI 資料
        if aqi_files:
            latest_aqi_file = sorted(aqi_files)[-1]
            aqi_path = os.path.join(output_dir, latest_aqi_file)
            print(f"\n處理 AQI 資料: {latest_aqi_file}")
            
            aqi_distances = calculator.calculate_distances_from_aqi_data(aqi_path)
            if not aqi_distances.empty:
                # 儲存 AQI 距離結果
                aqi_filepath = calculator.save_distance_results(aqi_distances, "aqi_distances_to_taipei_station")
                results.append(('AQI', aqi_filepath))
                
                # 顯示統計
                summary = calculator.generate_distance_summary(aqi_distances)
                print(f"\n=== AQI 測站距離統計 ===")
                for key, value in summary.items():
                    print(f"{key}: {value}")
        
        # 處理氣象資料
        if weather_files:
            latest_weather_file = sorted(weather_files)[-1]
            weather_path = os.path.join(output_dir, latest_weather_file)
            print(f"\n處理氣象資料: {latest_weather_file}")
            
            weather_distances = calculator.calculate_distances_from_weather_data(weather_path)
            if not weather_distances.empty:
                # 儲存氣象距離結果
                weather_filepath = calculator.save_distance_results(weather_distances, "weather_distances_to_taipei_station")
                results.append(('氣象', weather_filepath))
                
                # 顯示統計
                summary = calculator.generate_distance_summary(weather_distances)
                print(f"\n=== 氣象測站距離統計 ===")
                for key, value in summary.items():
                    print(f"{key}: {value}")
        
        # 顯示最近的 10 個測站
        if results:
            print(f"\n=== 距離台北車站最近的 10 個測站 ===")
            
            # 使用 AQI 資料顯示（如果有的話）
            if not aqi_distances.empty:
                nearest_10 = aqi_distances.nsmallest(10, '距離_公里')
                print(nearest_10[['測站名稱', '城市', '距離_公里', 'AQI']].to_string(index=False))
            elif not weather_distances.empty:
                nearest_10 = weather_distances.nsmallest(10, '距離_公里')
                print(nearest_10[['測站名稱', '城市', '距離_公里', '氣溫']].to_string(index=False))
        
        print(f"\n空間距離計算完成！共處理 {len(results)} 種資料類型")
        print(f"結果檔案位置: ../outputs/")
        
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
