#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試地圖生成問題
"""

import os
import pandas as pd
import folium
from datetime import datetime

def debug_map_creation():
    """調試地圖創建過程"""
    print("=== 調試地圖創建 ===")
    
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
        print(f"原始資料行數: {len(df)}")
        print(f"欄位: {list(df.columns)}")
        
        # 檢查氣溫欄位
        if '氣溫' in df.columns:
            print(f"氣溫欄位存在，資料類型: {df['氣溫'].dtype}")
            print(f"氣溫統計: min={df['氣溫'].min()}, max={df['氣溫'].max()}, mean={df['氣溫'].mean()}")
        else:
            print("氣溫欄位不存在")
            return
        
        # 檢查經緯度
        if '經度' in df.columns and '緯度' in df.columns:
            print(f"經緯度欄位存在")
            print(f"經度範圍: {df['經度'].min()} ~ {df['經度'].max()}")
            print(f"緯度範圍: {df['緯度'].min()} ~ {df['緯度'].max()}")
        else:
            print("經緯度欄位不存在")
            return
        
        # 過濾有效資料
        df_filtered = df.dropna(subset=['氣溫', '經度', '緯度'])
        print(f"過濾後有效資料行數: {len(df_filtered)}")
        
        if df_filtered.empty:
            print("過濾後沒有有效資料")
            return
        
        # 嘗試創建簡單地圖
        print("創建簡單地圖...")
        center_lat = df_filtered['緯度'].mean()
        center_lon = df_filtered['經度'].mean()
        
        print(f"地圖中心: ({center_lat}, {center_lon})")
        
        # 創建地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7
        )
        
        # 添加第一個測站
        first_row = df_filtered.iloc[0]
        print(f"添加第一個測站: {first_row['站點名稱']}")
        
        folium.CircleMarker(
            location=[first_row['緯度'], first_row['經度']],
            radius=8,
            popup=f"{first_row['站點名稱']}: {first_row['氣溫']:.1f}°C",
            color='red',
            fillColor='red',
            fillOpacity=0.7
        ).add_to(m)
        
        # 儲存地圖
        map_path = os.path.join(output_dir, 'debug_map.html')
        m.save(map_path)
        print(f"調試地圖已儲存至: {map_path}")
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_map_creation()
