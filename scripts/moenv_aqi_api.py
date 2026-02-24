#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境部空氣品質監測網 API 串接腳本
API: aqx_p_432 (空氣品質測站即時監測)
"""

import os
import requests
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv
import folium
from folium import plugins
import branca.colormap as cm

# 載入環境變數
load_dotenv()

class MOENVAQIAPI:
    """環境部空氣品質 API 串接類別"""
    
    def __init__(self):
        self.api_key = os.getenv('MOENV_API_KEY')
        self.base_url = "https://data.moenv.gov.tw/api/v2"
        self.dataset_id = "aqx_p_432"  # 空氣品質測站即時監測
        
        if not self.api_key:
            raise ValueError("請在 .env 檔案中設定 MOENV_API_KEY")
    
    def get_aqi_data(self, limit=None):
        """
        獲取全台空氣品質即時監測資料
        
        Args:
            limit (int): 限制回傳資料筆數，None 表示全部
            
        Returns:
            dict: API 回應資料
        """
        url = f"{self.base_url}/{self.dataset_id}"
        params = {
            'api_key': self.api_key,
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
    
    def parse_aqi_data(self, api_data):
        """
        解析空氣品質資料並轉換為 DataFrame
        
        Args:
            api_data (dict): API 回應資料
            
        Returns:
            pd.DataFrame: 包含空氣品質資料的 DataFrame
        """
        if not api_data:
            return pd.DataFrame()
        
        # MOENV API 直接返回陣列，不是包在 records 中
        records = api_data if isinstance(api_data, list) else api_data.get('records', [])
        
        aqi_data = []
        for record in records:
            try:
                # 基本測站資訊
                station_info = {
                    '測站編號': record.get('siteid', ''),
                    '測站名稱': record.get('sitename', ''),
                    '城市': record.get('county', ''),
                    '經度': self._safe_float(record.get('longitude', 0)),
                    '緯度': self._safe_float(record.get('latitude', 0)),
                    '觀測時間': record.get('publishtime', ''),
                    'AQI': self._safe_float(record.get('aqi')),
                    '空氣品質等級': record.get('status', ''),
                    '主要污染物': record.get('pollutant', '')
                }
                
                # 空氣品質指標
                aqi_metrics = {
                    'PM2.5': self._safe_float(record.get('pm2.5')),
                    'PM10': self._safe_float(record.get('pm10')),
                    'O3': self._safe_float(record.get('o3')),
                    'O3_8hr': self._safe_float(record.get('o3_8hr')),
                    'NO2': self._safe_float(record.get('no2')),
                    'SO2': self._safe_float(record.get('so2')),
                    'CO': self._safe_float(record.get('co')),
                    'CO_8hr': self._safe_float(record.get('co_8hr')),
                    'NOx': self._safe_float(record.get('nox')),
                    'NO': self._safe_float(record.get('no')),
                    '風速': self._safe_float(record.get('wind_speed')),
                    '風向': self._safe_float(record.get('wind_direc')),
                    'PM2.5_平均': self._safe_float(record.get('pm2.5_avg')),
                    'PM10_平均': self._safe_float(record.get('pm10_avg')),
                    'SO2_平均': self._safe_float(record.get('so2_avg'))
                }
                
                # 合併資料
                station_data = {**station_info, **aqi_metrics}
                aqi_data.append(station_data)
                
            except Exception as e:
                print(f"解析測站資料時發生錯誤 {record.get('sitename', 'Unknown')}: {e}")
                continue
        
        df = pd.DataFrame(aqi_data)
        return df
    
    def _safe_float(self, value):
        """安全轉換為浮點數"""
        if value in ['X', '-99', '-99.0', '', None, 'ND']:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_aqi_dataframe(self, limit=None):
        """
        獲取空氣品質資料的 DataFrame
        
        Args:
            limit (int): 限制回傳資料筆數
            
        Returns:
            pd.DataFrame: 空氣品質資料 DataFrame
        """
        api_data = self.get_aqi_data(limit)
        df = self.parse_aqi_data(api_data)
        
        if not df.empty:
            # 轉換觀測時間為 datetime
            df['觀測時間'] = pd.to_datetime(df['觀測時間'])
            
            # 按 AQI 排序
            if 'AQI' in df.columns:
                df = df.sort_values('AQI', ascending=False)
        
        return df
    
    def get_aqi_color(self, aqi):
        """
        根據 AQI 值返回對應顏色（簡化版）
        
        Args:
            aqi (float): AQI 值
            
        Returns:
            str: 顏色代碼
        """
        if aqi is None:
            return 'gray'
        elif aqi <= 50:
            return 'green'      # 良好
        elif aqi <= 100:
            return 'yellow'     # 普通
        else:
            return 'red'        # 不健康（101+）
    
    def get_aqi_level(self, aqi):
        """
        根據 AQI 值返回空氣品質等級
        
        Args:
            aqi (float): AQI 值
            
        Returns:
            str: 空氣品質等級
        """
        if aqi is None:
            return '無資料'
        elif aqi <= 50:
            return '良好'
        elif aqi <= 100:
            return '普通'
        elif aqi <= 150:
            return '對敏感族群不健康'
        elif aqi <= 200:
            return '對所有族群不健康'
        elif aqi <= 300:
            return '非常不健康'
        else:
            return '危害'
    
    def create_popup_content(self, row):
        """
        創建彈出視窗內容（簡化版）
        
        Args:
            row (pd.Series): 測站資料
            
        Returns:
            str: HTML 格式的彈出內容
        """
        try:
            # 安全獲取數值
            station_name = row.get('測站名稱', 'Unknown')
            city = row.get('城市', 'Unknown')
            aqi = row.get('AQI', '無資料')
            obs_time = row.get('觀測時間', '')
            
            # 處理觀測時間
            if isinstance(obs_time, str):
                obs_time_str = obs_time
            else:
                obs_time_str = str(obs_time)
            
            # AQI 顏色
            aqi_color = self.get_aqi_color(aqi) if isinstance(aqi, (int, float)) else 'gray'
            
            # 簡化的彈出內容
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 200px; text-align: center;">
                <h4 style="margin: 5px 0; color: #333; font-size: 16px;">{station_name}</h4>
                <p style="margin: 8px 0; font-size: 14px;"><strong>所在地：</strong>{city}</p>
                <div style="margin: 10px 0; padding: 10px; background-color: {aqi_color}; color: white; border-radius: 5px;">
                    <p style="margin: 0; font-size: 18px; font-weight: bold;">AQI {int(aqi) if isinstance(aqi, (int, float)) else 'N/A'}</p>
                </div>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">{obs_time_str}</p>
            </div>
            """
            return popup_html
        except Exception as e:
            print(f"創建彈出內容時出錯: {e}")
            return f"<div>錯誤: {row.get('測站名稱', 'Unknown')}</div>"
    
    def create_aqi_map(self, df, save_path=None):
        """
        創建 AQI 分佈地圖
        
        Args:
            df (pd.DataFrame): 空氣品質資料
            save_path (str): 地圖儲存路徑
            
        Returns:
            folium.Map: Folium 地圖物件
        """
        if df.empty:
            print("沒有資料可以創建地圖")
            return None
        
        # 計算地圖中心點（台灣中心）
        center_lat = df['緯度'].mean()
        center_lon = df['經度'].mean()
        
        # 創建地圖
        aqi_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 添加圖層控制
        folium.TileLayer('OpenStreetMap').add_to(aqi_map)
        folium.TileLayer('CartoDB positron').add_to(aqi_map)
        folium.TileLayer('CartoDB dark_matter').add_to(aqi_map)
        
        # 創建 AQI 顏色圖例（簡化版）
        try:
            # 使用簡單的圖例，避免 colormap 錯誤
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 150px; height: 90px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:12px; padding: 10px">
            <p><strong>AQI 等級圖例</strong></p>
            <p><span style="color:green;">●</span> 0-50 良好</p>
            <p><span style="color:yellow;">●</span> 51-100 普通</p>
            <p><span style="color:red;">●</span> 101+ 不健康</p>
            </div>
            '''
            aqi_map.get_root().html.add_child(folium.Element(legend_html))
        except Exception as e:
            print(f"創建圖例時出錯: {e}")
        
        # 添加測站標記
        for idx, row in df.iterrows():
            try:
                aqi = row.get('AQI')
                if aqi is None:
                    continue
                    
                color = self.get_aqi_color(aqi)
                
                # 根據 AQI 調整圓圈大小
                radius = 8 + min(aqi / 20, 12)  # 基礎8，最大20
                
                # 創建自定義圖標
                icon = folium.CircleMarker(
                    location=[row['緯度'], row['經度']],
                    radius=radius,
                    popup=folium.Popup(self.create_popup_content(row), max_width=300),
                    color=color,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2,
                    tooltip=f"{row.get('測站名稱', 'Unknown')}: AQI {int(aqi) if isinstance(aqi, (int, float)) else 'N/A'}"
                )
                icon.add_to(aqi_map)
            except Exception as e:
                print(f"添加測站 {row.get('測站名稱', 'Unknown')} 時出錯: {e}")
                continue
        
        # 添加全屏按鈕
        plugins.Fullscreen().add_to(aqi_map)
        
        # 添加圖層控制
        folium.LayerControl().add_to(aqi_map)
        
        # 添加統計資訊
        stats_html = self.create_statistics_html(df)
        folium.Marker(
            location=[center_lat - 2, center_lon + 1],
            icon=folium.DivIcon(html=stats_html, icon_size=(300, 150))
        ).add_to(aqi_map)
        
        # 儲存地圖
        if save_path:
            aqi_map.save(save_path)
            print(f"AQI 地圖已儲存至: {save_path}")
        
        return aqi_map
    
    def create_statistics_html(self, df):
        """
        創建統計資訊 HTML
        
        Args:
            df (pd.DataFrame): 空氣品質資料
            
        Returns:
            str: 統計資訊 HTML
        """
        if df.empty or 'AQI' not in df.columns:
            return "<div>無統計資料</div>"
        
        valid_aqi = df['AQI'].dropna()
        if valid_aqi.empty:
            return "<div>無有效 AQI 資料</div>"
        
        max_aqi = df.loc[valid_aqi.idxmax()]
        min_aqi = df.loc[valid_aqi.idxmin()]
        avg_aqi = valid_aqi.mean()
        
        # 計算各等級數量
        level_counts = {}
        for _, row in df.iterrows():
            aqi = row.get('AQI')
            if aqi is not None:
                level = self.get_aqi_level(aqi)
                level_counts[level] = level_counts.get(level, 0) + 1
        
        stats_html = f"""
        <div style="background-color: white; padding: 10px; border: 2px solid #333; border-radius: 5px; font-size: 12px;">
            <h4 style="margin: 5px 0; color: #333;">空氣品質統計</h4>
            <p style="margin: 3px 0;"><strong>最高 AQI:</strong> {int(max_aqi['AQI'])} ({max_aqi['測站名稱']})</p>
            <p style="margin: 3px 0;"><strong>最低 AQI:</strong> {int(min_aqi['AQI'])} ({min_aqi['測站名稱']})</p>
            <p style="margin: 3px 0;"><strong>平均 AQI:</strong> {avg_aqi:.1f}</p>
            <p style="margin: 3px 0;"><strong>測站數:</strong> {len(valid_aqi)}</p>
            <p style="margin: 3px 0; font-size: 10px; color: #666;">更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """
        return stats_html
    
    def save_to_file(self, df, filename=None, file_format='csv'):
        """
        儲存資料到檔案
        
        Args:
            df (pd.DataFrame): 要儲存的資料
            filename (str): 檔案名稱
            file_format (str): 檔案格式 ('csv', 'json')
        """
        if df.empty:
            print("沒有資料可以儲存")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aqi_data_{timestamp}"
        
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


def main():
    """主程式"""
    print("=== 環境部空氣品質監測網 API 串接 ===")
    
    try:
        # 建立 API 串接物件
        moenv_api = MOENVAQIAPI()
        
        # 獲取空氣品質資料
        print("正在獲取空氣品質資料...")
        df = moenv_api.get_aqi_dataframe()
        
        if df.empty:
            print("沒有獲取到資料")
            return
        
        # 顯示基本資訊
        print(f"\n成功獲取 {len(df)} 個測站資料")
        
        # 顯示 AQI 統計
        valid_aqi = df['AQI'].dropna()
        if not valid_aqi.empty:
            print(f"\n=== AQI 統計摘要 ===")
            print(f"有效 AQI 測站數: {len(valid_aqi)}")
            print(f"最高 AQI: {valid_aqi.max():.1f}")
            print(f"最低 AQI: {valid_aqi.min():.1f}")
            print(f"平均 AQI: {valid_aqi.mean():.1f}")
        
        # 顯示前10個測站的 AQI 資料
        if 'AQI' in df.columns:
            print("\n=== AQI 排名前10的測站 ===")
            top_10 = df[['測站名稱', '城市', 'AQI', '空氣品質等級']].head(10)
            print(top_10.to_string(index=False))
        
        # 儲存資料
        print("\n正在儲存資料...")
        moenv_api.save_to_file(df, file_format='csv')
        
        # 創建地圖
        print("正在創建 AQI 地圖...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_path = os.path.join('..', 'data', 'output', f"aqi_map_{timestamp}.html")
        moenv_api.create_aqi_map(df, map_path)
        
        print("\n空氣品質資料串接完成！")
        
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
