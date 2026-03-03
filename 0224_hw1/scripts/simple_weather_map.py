#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版氣象站氣溫地圖視覺化
"""

import os
import pandas as pd
import folium
from datetime import datetime

def get_temperature_color(temp):
    """根據氣溫返回對應顏色"""
    if temp < 20:
        return 'blue'
    elif temp <= 28:
        return 'green'
    else:
        return 'orange'

def create_simple_map():
    """創建簡單的氣溫地圖"""
    print("=== 創建簡化氣溫地圖 ===")
    
    # 載入資料
    output_dir = '../data/output'
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv') and 'weather_data' in f]
    
    if not csv_files:
        print("找不到氣象資料檔案")
        return
    
    latest_file = sorted(csv_files)[-1]
    csv_path = os.path.join(output_dir, latest_file)
    
    print(f"載入檔案: {latest_file}")
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # 過濾有效資料
        df_filtered = df.dropna(subset=['氣溫', '經度', '緯度'])
        print(f"有效測站數: {len(df_filtered)}")
        
        if df_filtered.empty:
            print("沒有有效資料")
            return
        
        # 計算地圖中心
        center_lat = df_filtered['緯度'].mean()
        center_lon = df_filtered['經度'].mean()
        
        # 創建地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 添加測站標記
        for idx, row in df_filtered.iterrows():
            temp = row['氣溫']
            color = get_temperature_color(temp)
            
            # 創建簡單的彈出內容
            popup_content = f"""
            <div style="font-family: Arial; width: 180px;">
                <h4 style="margin: 5px 0;">{row['站點名稱']}</h4>
                <p style="margin: 2px 0;"><strong>城市:</strong> {row['城市']}</p>
                <p style="margin: 2px 0;"><strong>氣溫:</strong> <span style="color: {color}; font-weight: bold;">{temp:.1f}°C</span></p>
                <p style="margin: 2px 0;"><strong>濕度:</strong> {row['相對濕度']:.0f}%</p>
                <p style="margin: 2px 0;"><strong>風速:</strong> {row['風速']:.1f} m/s</p>
            </div>
            """
            
            folium.CircleMarker(
                location=[row['緯度'], row['經度']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=250),
                color=color,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                tooltip=f"{row['站點名稱']}: {temp:.1f}°C"
            ).add_to(m)
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><strong>氣溫圖例</strong></p>
        <p><span style="color:blue;">●</span> &lt; 20°C</p>
        <p><span style="color:green;">●</span> 20-28°C</p>
        <p><span style="color:orange;">●</span> &gt; 28°C</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 添加統計資訊
        max_temp = df_filtered.loc[df_filtered['氣溫'].idxmax()]
        min_temp = df_filtered.loc[df_filtered['氣溫'].idxmin()]
        avg_temp = df_filtered['氣溫'].mean()
        
        stats_html = f'''
        <div style="position: fixed; 
                    top: 50px; right: 50px; width: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px">
        <h4 style="margin: 5px 0;">氣溫統計</h4>
        <p style="margin: 2px 0;"><strong>最高:</strong> {max_temp['氣溫']:.1f}°C ({max_temp['站點名稱']})</p>
        <p style="margin: 2px 0;"><strong>最低:</strong> {min_temp['氣溫']:.1f}°C ({min_temp['站點名稱']})</p>
        <p style="margin: 2px 0;"><strong>平均:</strong> {avg_temp:.1f}°C</p>
        <p style="margin: 2px 0;"><strong>測站:</strong> {len(df_filtered)} 個</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(stats_html))
        
        # 儲存地圖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_path = os.path.join(output_dir, f"simple_temperature_map_{timestamp}.html")
        m.save(map_path)
        
        print(f"地圖已儲存至: {map_path}")
        print(f"最高氣溫: {max_temp['氣溫']:.1f}°C ({max_temp['站點名稱']})")
        print(f"最低氣溫: {min_temp['氣溫']:.1f}°C ({min_temp['站點名稱']})")
        print(f"平均氣溫: {avg_temp:.1f}°C")
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_simple_map()
