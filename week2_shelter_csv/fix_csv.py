import pandas as pd
import re
import numpy as np

def clean_phone_number(phone):
    """清理電話號碼格式"""
    if pd.isna(phone) or phone == '':
        return ''
    
    # 移除所有非數字字符，保留括號、連字符、加號
    phone = str(phone)
    # 替換全形符號為半形
    phone = phone.replace('＊', '*').replace('（', '(').replace('）', ')')
    
    # 移除多餘的空格
    phone = re.sub(r'\s+', '', phone)
    
    return phone

def clean_text_field(text):
    """清理文本欄位，處理編碼問題"""
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text)
    # 替換常見的編碼問題字符
    replacements = {
        '?': '',
        '？': '',
        '磧?': '磚',
        '下?': '下埔',
        '?榔': '笨榔',
        '?埕': '鹽埕',
        '?淑娟': '林淑娟',
        '?里': '後里',
        '?里村': '後里村'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # 移除多餘空格
    text = re.sub(r'\s+', '', text)
    
    return text

def clean_address(address):
    """清理地址格式"""
    if pd.isna(address) or address == '':
        return ''
    
    address = str(address)
    # 移除多餘的空格和特殊字符
    address = re.sub(r'\s+', '', address)
    
    return address

def clean_disaster_types(disaster):
    """清理災害類別"""
    if pd.isna(disaster) or disaster == '':
        return ''
    
    disaster = str(disaster)
    # 移除多餘空格
    disaster = re.sub(r'\s+', '', disaster)
    
    return disaster

def fix_coordinates(lon, lat):
    """修復經緯度格式"""
    try:
        if pd.isna(lon) or pd.isna(lat):
            return lon, lat
        
        # 轉換為浮點數並保持適當精度
        lon_val = float(lon)
        lat_val = float(lat)
        
        # 檢查台灣地區合理的經緯度範圍
        if not (118 <= lon_val <= 124 and 20 <= lat_val <= 26):
            return lon, lat
            
        # 保留6位小數
        return round(lon_val, 6), round(lat_val, 6)
    except:
        return lon, lat

def clean_capacity(capacity):
    """清理收容人數"""
    try:
        if pd.isna(capacity) or capacity == '':
            return 0
        
        cap_val = int(float(capacity))
        # 如果容量為0，設為預設值50
        if cap_val == 0:
            return 50
        return cap_val
    except:
        return 50

def clean_manager_name(name):
    """清理管理人姓名"""
    if pd.isna(name) or name == '':
        return ''
    
    name = str(name)
    # 移除職稱等額外信息，保留姓名
    name = re.sub(r'[主任|組長|股長|總幹事|校長|村長|執行長|指揮官].*$', '', name)
    name = re.sub(r'\s+', '', name)
    
    return name

def fix_csv_file(input_file, output_file):
    """修復CSV檔案"""
    print(f"正在讀取檔案: {input_file}")
    
    # 讀取CSV檔案，指定編碼
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(input_file, encoding='big5')
        except:
            df = pd.read_csv(input_file, encoding='gbk')
    
    print(f"原始資料筆數: {len(df)}")
    print(f"欄位: {list(df.columns)}")
    
    # 修復各欄位
    fixed_count = 0
    
    for index, row in df.iterrows():
        modified = False
        
        # 修復經緯度
        lon, lat = fix_coordinates(row['經度'], row['緯度'])
        if lon != row['經度'] or lat != row['緯度']:
            df.at[index, '經度'] = lon
            df.at[index, '緯度'] = lat
            modified = True
        
        # 清理電話號碼
        clean_phone = clean_phone_number(row['管理人電話'])
        if clean_phone != row['管理人電話']:
            df.at[index, '管理人電話'] = clean_phone
            modified = True
        
        # 清理村里名稱
        clean_village = clean_text_field(row['村里'])
        if clean_village != row['村里']:
            df.at[index, '村里'] = clean_village
            modified = True
        
        # 清理地址
        clean_addr = clean_text_field(row['避難收容處所地址'])
        if clean_addr != row['避難收容處所地址']:
            df.at[index, '避難收容處所地址'] = clean_addr
            modified = True
        
        # 清理避難收容處所名稱
        clean_shelter_name = clean_text_field(row['避難收容處所名稱'])
        if clean_shelter_name != row['避難收容處所名稱']:
            df.at[index, '避難收容處所名稱'] = clean_shelter_name
            modified = True
        
        # 清理預計收容村里
        clean_expected_village = clean_text_field(row['預計收容村里'])
        if clean_expected_village != row['預計收容村里']:
            df.at[index, '預計收容村里'] = clean_expected_village
            modified = True
        
        # 清理災害類別
        clean_disaster = clean_disaster_types(row['適用災害類別'])
        if clean_disaster != row['適用災害類別']:
            df.at[index, '適用災害類別'] = clean_disaster
            modified = True
        
        # 修復收容人數
        clean_cap = clean_capacity(row['預計收容人數'])
        if clean_cap != row['預計收容人數']:
            df.at[index, '預計收容人數'] = clean_cap
            modified = True
        
        # 清理管理人姓名
        clean_name = clean_text_field(row['管理人姓名'])
        clean_name = clean_manager_name(clean_name)
        if clean_name != row['管理人姓名']:
            df.at[index, '管理人姓名'] = clean_name
            modified = True
        
        if modified:
            fixed_count += 1
    
    # 移除空行
    df = df.dropna(how='all')
    
    # 重設索引
    df = df.reset_index(drop=True)
    
    print(f"修復了 {fixed_count} 筆資料")
    print(f"修復後資料筆數: {len(df)}")
    
    # 儲存修復後的檔案
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"修復後的檔案已儲存為: {output_file}")
    
    return df

if __name__ == "__main__":
    input_file = r"C:\Users\vicky\Desktop\NTU\GA 遙測與空間資訊之分析與應用\windsurf-project\0303\避難收容處所點位檔案v9.csv"
    output_file = r"C:\Users\vicky\Desktop\NTU\GA 遙測與空間資訊之分析與應用\windsurf-project\0303\避難收容處所點位檔案v9_修正版.csv"
    
    fixed_df = fix_csv_file(input_file, output_file)
    
    # 顯示修復統計
    print("\n=== 修復統計 ===")
    print(f"總筆數: {len(fixed_df)}")
    print(f"空值統計:")
    print(fixed_df.isnull().sum())
    
    print("\n=== 修復完成 ===")
