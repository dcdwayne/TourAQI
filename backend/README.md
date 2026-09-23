# 後端測試方式

## 1. 確認資料

backend/sample_data/ 需有以下四個檔案：

- stations-10.csv
- taipei-attractions-5.json
- boundaries-sample.geojson
- district-air-quality-sample.json

## 2. 安裝與啟動

在 TourAQI 根目錄開啟 PowerShell，逐行執行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8000
```
(Port可自行修改未被占用的 Port)

已建立 .venv 可跳過第一行。啟動後保持終端機開啟。

## 3. 測試 API

開啟 http://localhost:8000/docs

| API | 功能 |
|---|---|
| GET /api/stations | 10 筆測站基本資料 |
| GET /api/air-quality | 11 筆鄉鎮代表空品 |
| GET /api/attractions | 5 筆景點摘要 |
| GET /api/attractions/{attraction_id} | 單一景點詳細資訊 |
| GET /api/boundaries | 11 個行政區邊界 GeoJSON |

前端 API 基底網址：http://localhost:8000

若 8000 被占用，啟動指令與前端 API 網址一起改成其他未被占用的Port (ex.8001)。

## 4. 前端配對方式

- 邊界的 features[].properties.district_code，
  對應空品的 data[].district_code。
- 空品的 representative_station_id，
  對應測站的 station_id。
- 污染物濃度與單位，例如 pollutants.pm25.value、pollutants.pm25.unit。
- 景點詳細查詢使用列表中的 attraction_id；不存在時回傳 404。
- 邊界直接回傳 GeoJSON；其餘 API 的資料放在 data 欄位。

## 注意

- 使用固定範例資料，尚未接資料庫或自動更新。
- 11 個行政區中，10 個有測試測站，1 個沒有。
- AQI 為 null 時，前端顯示白色「無資料」，不可當成 0。
- 無資料僅代表這份測試資料未提供，不代表當地實際沒有測站。
- 景點彈窗不顯示空品。