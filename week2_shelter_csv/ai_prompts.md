## 初始 prompt
1. 開啟C:\Users\vicky\Desktop\NTU\GA 遙測與空間資訊之分析與應用\windsurf-project\0303\避難收容處所點位檔案v9.csv
2. 查看文件內容。找出問題所在。
3. 修復csv中不合理的問題，另外輸出一個新的修正後csv檔案。

## 輸出報告 prompt
### 個人觀察 (個人發現csv的問題)
1. 資料中有空值
2. 避難收容處所地址 未正規化，(1)數字格式未統一，如12-1號或十二之一號。(2)有些標示為地標而非地址，如。(3)英文地址，如No.105,Zhengxing,Jinfeng Township,(4)
3. 預計收容村里 分隔未統一，如桃山村、竹林村 / 桃山村 竹林村(使用頓號或空格分隔)
4. 電話號碼格式未統一
---
將我的"個人觀察"與你的"修復完成總結"以markdown語法寫一篇audit report documenting every issue and correction.分為兩個主題，分別標示"個人觀察(人為)"與"AI修復完成總結"部分

## git commit message
將修改內容 重新 push 到 github，並填寫 commit message