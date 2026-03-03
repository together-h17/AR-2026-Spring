#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試 MOENV API 連接
"""

import os
import requests
import json
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def debug_moenv_api():
    """調試 MOENV API 連接"""
    print("=== 調試 MOENV API ===")
    
    api_key = os.getenv('MOENV_API_KEY')
    
    if not api_key:
        print("[ERROR] 請在 .env 檔案中設定 MOENV_API_KEY")
        print("範例: MOENV_API_KEY=your_api_key_here")
        return
    
    print(f"[OK] API Key 已載入: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
    
    # 測試 API 連接
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
    params = {
        'api_key': api_key,
        'format': 'JSON',
        'limit': 5  # 只取前5筆資料進行測試
    }
    
    try:
        print("[INFO] 正在請求 API...")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"[INFO] 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] API 連接成功！")
            
            if 'records' in data:
                records = data['records']
                print(f"[INFO] 獲取到 {len(records)} 筆資料")
                
                if records:
                    print("\n[INFO] 第一筆資料範例:")
                    first_record = records[0]
                    print(json.dumps(first_record, indent=2, ensure_ascii=False))
                else:
                    print("[WARNING] 沒有資料記錄")
            else:
                print("[WARNING] 回應中沒有 records 欄位")
                print("完整回應:", json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"[ERROR] API 請求失敗: {response.status_code}")
            print(f"回應內容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 網路請求錯誤: {e}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析錯誤: {e}")
    except Exception as e:
        print(f"[ERROR] 其他錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_moenv_api()
