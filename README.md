
# Video Cutter Tool (影片轉圖片工具)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)

這是一個簡單且高效的視窗應用程式，使用 Python (Tkinter + OpenCV) 開發。它可以協助使用者將影片檔拆解成圖片序列。你可以選擇輸出每一幀，或是設定特定的時間間隔進行截圖。

## ✨ 功能特色 (Features)

* **圖形化介面 (GUI)**：直覺的操作介面，無需使用指令。
* **多種切割模式**：
    * **逐幀輸出 (Frame by Frame)**：適合製作深度學習資料集或細部分析。
    * **間隔輸出 (Interval)**：自訂每隔 N 秒擷取一張圖片（支援小數點，如 0.5 秒）。
* **格式支援**：支援常見影片格式 (`.mp4`, `.avi`, `.mov`, `.mkv`, `.ts`)。
* **防呆機制**：
    * 防止輸入非數值的間隔秒數（Try-Catch 保護）。
    * 檢查檔案路徑是否有效。
    * 支援非同步處理 (Threading)，轉換過程中視窗不會卡死。
* **響應式設計**：視窗大小可調整，元件會自動縮放排列。

## 🚀 安裝與執行 (Installation)

如果你是開發者或想要直接執行 Python 原始碼，請依照以下步驟：

### 1. 克隆專案
```bash
git clone [https://github.com/](https://github.com/)[你的帳號]/[你的專案名稱].git
cd [你的專案名稱]
```
### 2. 安裝依賴套件
本專案依賴 opencv-python 進行影像處理。

```Bash
pip install -r requirements.txt
```
### 3. 執行程式

```Bash
python video_cutter.py
```
## 📖 使用說明 (Usage)
選擇影片：點擊「瀏覽」按鈕選取你要處理的影片檔。

設定輸出位置：選擇圖片要儲存的資料夾。

選擇模式：

若選擇 「每隔...秒輸出一張」，請在輸入框填入秒數（例如 1 代表每秒一張，0.5 代表每半秒一張）。

開始轉換：點擊 「開始轉換」 按鈕。

程式會自動檢查輸入是否正確。

下方進度條會顯示目前處理進度。

完成：轉換結束後會跳出提示視窗。

## 📦 如何打包成 EXE (Build EXE)
如果你想將此程式打包成 Windows 可執行檔 (.exe) 分享給他人，請使用 pyinstaller。

安裝 PyInstaller

```Bash

pip install pyinstaller
```
執行打包指令

```Bash

pyinstaller --noconsole --onefile --name "VideoSplitter" video_cutter.py
```
取得檔案 打包完成後，你的 .exe 檔案會位於 dist/ 資料夾內。

## 📝 授權 (License)
本專案採用 MIT License 授權。 歡迎自由使用、修改與分發，但請保留原作者版權聲明。

Developed by yeeeN1234

