#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 無法使用，改用 simple_weather_map.py
"""
氣象站氣溫地圖視覺化腳本
使用 Folium 在地圖上標示測站位置並依氣溫分色
"""

import os
import pandas as pd
import folium
from folium import plugins
import branca.colormap as cm
from datetime import datetime
import json

class WeatherMapVisualization:
    """氣象地圖視覺化類別"""
    
    def __init__(self):
        self.data = None
        self.map = None
        
    def load_weather_data(self, csv_file_path):
        """
        載入氣象資料
        
        Args:
            csv_file_path (str): CSV 檔案路徑
            
        Returns:
            pd.DataFrame: 氣象資料
        """
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
            # 轉換觀測時間為 datetime
            df['觀測時間'] = pd.to_datetime(df['觀測時間'])
            # 過濾掉沒有氣溫資料的測站
            df = df.dropna(subset=['氣溫', '經度', '緯度'])
            print(f"成功載入 {len(df)} 個有效測站資料")
            return df
        except Exception as e:
            print(f"載入資料失敗: {e}")
            return pd.DataFrame()
    
    def get_temperature_color(self, temp):
        """
        根據氣溫返回對應顏色
        
        Args:
            temp (float): 氣溫
            
        Returns:
            str: 顏色代碼
        """
        if temp < 20:
            return 'blue'      # 藍色：低於20度
        elif temp <= 28:
            return 'green'     # 綠色：20-28度
        else:
            return 'orange'    # 橘色：高於28度
    
    def create_popup_content(self, row):
        """
        創建彈出視窗內容
        
        Args:
            row (pd.Series): 測站資料
            
        Returns:
            str: HTML 格式的彈出內容
        """
        try:
            # 安全獲取數值
            temp = row.get('氣溫', 0)
            humidity = row.get('相對濕度', 0)
            wind_speed = row.get('風速', 0)
            pressure = row.get('氣壓', 0)
            obs_time = row.get('觀測時間', '')
            
            # 處理觀測時間
            if isinstance(obs_time, str):
                obs_time_str = obs_time
            else:
                obs_time_str = str(obs_time)
            
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 200px;">
                <h4 style="margin: 5px 0; color: #333;">{row.get('站點名稱', 'Unknown')}</h4>
                <p style="margin: 3px 0; font-size: 14px;"><strong>城市:</strong> {row.get('城市', 'Unknown')}</p>
                <p style="margin: 3px 0; font-size: 14px;"><strong>氣溫:</strong> <span style="color: {self.get_temperature_color(temp)}; font-weight: bold;">{temp:.1f}°C</span></p>
                <p style="margin: 3px 0; font-size: 14px;"><strong>相對濕度:</strong> {humidity:.0f}%</p>
                <p style="margin: 3px 0; font-size: 14px;"><strong>風速:</strong> {wind_speed:.1f} m/s</p>
                <p style="margin: 3px 0; font-size: 14px;"><strong>氣壓:</strong> {pressure:.1f} hPa</p>
                <p style="margin: 3px 0; font-size: 12px; color: #666;"><strong>觀測時間:</strong><br>{obs_time_str}</p>
            </div>
            """
            return popup_html
        except Exception as e:
            print(f"創建彈出內容時出錯: {e}")
            return f"<div>錯誤: {row.get('站點名稱', 'Unknown')}</div>"
    
    def create_temperature_map(self, df, save_path=None):
        """
        創建氣溫分佈地圖
        
        Args:
            df (pd.DataFrame): 氣象資料
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
        self.map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 添加圖層控制
        folium.TileLayer('OpenStreetMap').add_to(self.map)
        folium.TileLayer('CartoDB positron').add_to(self.map)
        folium.TileLayer('CartoDB dark_matter').add_to(self.map)
        
        # 創建氣溫顏色圖例
        try:
            colormap = cm.LinearColormap(
                colors=['blue', 'green', 'orange'],
                index=[0, 20, 28, 40],
                vmin=df['氣溫'].min(),
                vmax=df['氣溫'].max(),
                caption='氣溫 (°C)'
            )
            colormap.add_to(self.map)
        except Exception as e:
            print(f"創建顏色圖例時出錯: {e}")
            # 使用簡單的圖例
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 150px; height: 90px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><strong>氣溫圖例</strong></p>
            <p><i class="fa fa-circle" style="color:blue"></i> &lt; 20°C</p>
            <p><i class="fa fa-circle" style="color:green"></i> 20-28°C</p>
            <p><i class="fa fa-circle" style="color:orange"></i> &gt; 28°C</p>
            </div>
            '''
            self.map.get_root().html.add_child(folium.Element(legend_html))
        
        # 添加測站標記
        for idx, row in df.iterrows():
            try:
                # 根據氣溫決定顏色和圖標大小
                color = self.get_temperature_color(row['氣溫'])
                
                # 創建自定義圖標
                icon = folium.CircleMarker(
                    location=[row['緯度'], row['經度']],
                    radius=8,
                    popup=folium.Popup(self.create_popup_content(row), max_width=300),
                    color=color,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2,
                    tooltip=f"{row['站點名稱']}: {row['氣溫']:.1f}°C"
                )
                icon.add_to(self.map)
            except Exception as e:
                print(f"添加測站 {row.get('站點名稱', 'Unknown')} 時出錯: {e}")
                continue
        
        # 添加全屏按鈕
        plugins.Fullscreen().add_to(self.map)
        
        # 添加比例尺
        # folium.ScaleControl() 在某些版本中可能不可用，暫時註解掉
        
        # 添加圖層控制
        folium.LayerControl().add_to(self.map)
        
        # 添加統計資訊
        stats_html = self.create_statistics_html(df)
        folium.Marker(
            location=[center_lat - 2, center_lon + 1],
            icon=folium.DivIcon(html=stats_html, icon_size=(300, 150))
        ).add_to(self.map)
        
        # 儲存地圖
        if save_path:
            self.map.save(save_path)
            print(f"地圖已儲存至: {save_path}")
        
        return self.map
    
    def create_statistics_html(self, df):
        """
        創建統計資訊 HTML
        
        Args:
            df (pd.DataFrame): 氣象資料
            
        Returns:
            str: 統計資訊 HTML
        """
        max_temp = df.loc[df['氣溫'].idxmax()]
        min_temp = df.loc[df['氣溫'].idxmin()]
        avg_temp = df['氣溫'].mean()
        
        stats_html = f"""
        <div style="background-color: white; padding: 10px; border: 2px solid #333; border-radius: 5px; font-size: 12px;">
            <h4 style="margin: 5px 0; color: #333;">氣溫統計</h4>
            <p style="margin: 3px 0;"><strong>最高溫:</strong> {max_temp['氣溫']:.1f}°C ({max_temp['站點名稱']})</p>
            <p style="margin: 3px 0;"><strong>最低溫:</strong> {min_temp['氣溫']:.1f}°C ({min_temp['站點名稱']})</p>
            <p style="margin: 3px 0;"><strong>平均溫:</strong> {avg_temp:.1f}°C</p>
            <p style="margin: 3px 0;"><strong>測站數:</strong> {len(df)}</p>
            <p style="margin: 3px 0; font-size: 10px; color: #666;">更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """
        return stats_html
    
    def create_heatmap(self, df, save_path=None):
        """
        創建氣溫熱力圖
        
        Args:
            df (pd.DataFrame): 氣象資料
            save_path (str): 地圖儲存路徑
            
        Returns:
            folium.Map: Folium 地圖物件
        """
        if df.empty:
            print("沒有資料可以創建熱力圖")
            return None
        
        # 計算地圖中心點
        center_lat = df['緯度'].mean()
        center_lon = df['經度'].mean()
        
        # 創建地圖
        heatmap_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='CartoDB positron'
        )
        
        # 準備熱力圖數據
        heat_data = [[row['緯度'], row['經度'], row['氣溫']] for idx, row in df.iterrows()]
        
        # 添加熱力圖
        plugins.HeatMap(
            heat_data,
            min_opacity=0.4,
            radius=25,
            blur=15,
            gradient={0.0: 'blue', 0.5: 'green', 1.0: 'orange'}
        ).add_to(heatmap_map)
        
        # 儲存地圖
        if save_path:
            heatmap_map.save(save_path)
            print(f"熱力圖已儲存至: {save_path}")
        
        return heatmap_map
    
    def generate_latest_map(self):
        """生成最新的氣溫地圖"""
        print("=== 生成氣溫分佈地圖 ===")
        
        # 找到最新的資料檔案
        output_dir = '../data/output'
        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv') and 'weather_data' in f]
        
        if not csv_files:
            print("找不到氣象資料檔案，請先執行 cwa_weather_api.py")
            return
        
        # 選擇最新的檔案
        latest_file = sorted(csv_files)[-1]
        csv_path = os.path.join(output_dir, latest_file)
        
        print(f"載入資料檔案: {latest_file}")
        
        # 載入資料
        df = self.load_weather_data(csv_path)
        
        if df.empty:
            print("載入的資料為空")
            return
        
        # 生成地圖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_path = os.path.join(output_dir, f"temperature_map_{timestamp}.html")
        heatmap_path = os.path.join(output_dir, f"temperature_heatmap_{timestamp}.html")
        
        # 創建氣溫分佈地圖
        print("正在創建氣溫分佈地圖...")
        self.create_temperature_map(df, map_path)
        
        # 創建熱力圖
        print("正在創建氣溫熱力圖...")
        self.create_heatmap(df, heatmap_path)
        
        print(f"\n地圖生成完成！")
        print(f"分佈圖: {map_path}")
        print(f"熱力圖: {heatmap_path}")
        
        # 顯示統計資訊
        print(f"\n=== 氣溫統計 ===")
        print(f"測站數量: {len(df)}")
        print(f"最高氣溫: {df['氣溫'].max():.1f}°C ({df.loc[df['氣溫'].idxmax(), '站點名稱']})")
        print(f"最低氣溫: {df['氣溫'].min():.1f}°C ({df.loc[df['氣溫'].idxmin(), '站點名稱']})")
        print(f"平均氣溫: {df['氣溫'].mean():.1f}°C")


def main():
    """主程式"""
    try:
        # 創建視覺化物件
        viz = WeatherMapVisualization()
        
        # 生成最新地圖
        viz.generate_latest_map()
        
    except Exception as e:
        print(f"程式執行錯誤: {e}")


if __name__ == "__main__":
    main()
