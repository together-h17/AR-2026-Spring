#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試 CWA API 資料結構
"""

import os
import requests
import json
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def debug_api_structure():
    """調試 API 資料結構"""
    api_key = os.getenv('CWA_API_KEY')
    
    if not api_key:
        print("請設定 CWA_API_KEY")
        return
    
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
    params = {
        'Authorization': api_key,
        'format': 'JSON',
        'limit': 5  # 只取前5筆資料進行調試
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("=== API 回應結構 ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"API 請求失敗: {e}")

if __name__ == "__main__":
    debug_api_structure()
