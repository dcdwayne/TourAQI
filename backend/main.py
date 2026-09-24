import os
# import pymysql
import math
import json
# from pathlib import Path
from fastapi import FastAPI, Query, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector import Error

# 強制載入 .env 檔案中的變數到目前的環境中
load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #暫定不限Port, 留意正式部屬前是否需要修改
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# MySQL 的實際連線資訊
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),          
    'password': os.getenv("DB_PASSWORD"),  
    'port': int(os.getenv("DB_PORT", "3306")),
    'database': os.getenv("DB_NAME")    
}

def get_db_connection():
    """建立資料庫連線的輔助函式"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"資料庫連線失敗: {e}")
        return None


def fetch_all(sql, params=None):
    connection = get_db_connection()

    try:
        # 關鍵修改：加上 dictionary=True，讓回傳的 row 變成 dict 而非 tuple
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

# 資料文字轉換成數值
def to_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None

# 1. 取得目前 app.py 所在的絕對路徑 (backend 資料夾)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 往上一層找到 frontend 資料夾
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

# --- 導向根目錄 ---
@app.get("/", include_in_schema=False)
async def index():
    # 組合出 index.html 的絕對路徑
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path, media_type="text/html")

# --- 導向景點頁面 ---
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(id: str):
    attraction_path = os.path.join(FRONTEND_DIR, "attraction.html")
    return FileResponse(attraction_path, media_type="text/html")

# --- 測站資本資訊 ---
@app.get("/api/stations")
def get_stations(siteid: int | None = Query(default=None, gt=0)):
    sql = """
        SELECT
            s.siteid,
            s.sitename,
            s.siteengname,
            s.areaname,
            s.county,
            s.township,
            s.siteaddress,
            s.twd97lon,
            s.twd97lat,
            s.sitetype,
            t.TOWNCODE AS towncode
        FROM aqi_stations AS s
        LEFT JOIN town_boundaries AS t
            ON s.county = t.COUNTYNAME
            AND s.township = t.TOWNNAME
    """

    params = None

    # 有指定 siteid，就只查這個測站
    if siteid is not None:
        sql += " WHERE s.siteid = %s"
        params = (siteid,)

    sql += " ORDER BY s.siteid"

    rows = fetch_all(sql, params)

    # 指定的測站不存在
    if siteid is not None and not rows:
        raise HTTPException(
            status_code=404,
            detail="找不到指定測站",
        )

    stations = []

    for row in rows:
        station = {
            "station_id": str(row["siteid"]),
            "name": row["sitename"],
            "county": row["county"],
            "district": row["township"],
            "towncode": row["towncode"],
            "longitude": row["twd97lon"],
            "latitude": row["twd97lat"],
        }

        # 有指定 siteid，補上彈窗需要的詳細資訊
        if siteid is not None:
            station.update({
                "english_name": row["siteengname"],
                "air_quality_area": row["areaname"],
                "address": row["siteaddress"],
                "station_type": row["sitetype"],
            })

        stations.append(station)

    # 列表回傳陣列，單站查詢回傳一個物件
    if siteid is not None:
        return {"data": stations[0]}

    return {
        "data": stations,
        "meta": {
            "count": len(stations),
        },
    }

# -- 測站最新空氣品質(顏色) GET /api/air-quality -----
# 用途：鄉鎮區塊上色＋鄉鎮空氣品質彈窗 (若鄉鎮區不是用這支API上色就要再改)
AQI_STATUS_MAPPING = {"良好":"#43b581",
                    "普通":"#f2c94c",
                    "對敏感族群不健康":"#f2994a",
                    "對所有族群不健康":"#eb5757",
                    "非常不健康":"#9b51e0",
                    "危害":"#8f4b4b"
                    }

@app.get("/api/air-quality")
def get_air_quality(siteid: int | None = Query(default=None, gt=0)):
    # 1. 調整 SQL：以 aqi_stations 與 aqi_records 進行 INNER JOIN，沒有數據的測站直接過濾
    sql = """
        SELECT
            s.siteid AS station_id,
            t.TOWNCODE AS district_code,
            r.status,
            t.COUNTYNAME AS county,
            t.TOWNNAME AS district_name,
            s.sitename AS station_name,
            r.aqi,
            r.pollutant,
            r.publishtime,
            r.pm25,
            r.pm10,
            r.o3,
            r.co,
            r.so2,
            r.no2,
            r.nox,
            r.`no` AS nitrogen_monoxide,
            r.o3_8hr,
            r.co_8hr,
            r.pm25_avg,
            r.pm10_avg,
            r.so2_avg,
            r.wind_speed,
            r.wind_direc
        FROM aqi_stations AS s
        INNER JOIN aqi_records AS r 
            ON s.siteid = r.siteid
        INNER JOIN town_boundaries AS t 
            ON s.county = t.COUNTYNAME AND s.township = t.TOWNNAME
    """
    params = None

    # 若前端有傳入 siteid，增加過濾條件
    if siteid is not None:
        sql += " WHERE s.siteid = %s"
        params = (siteid,)
    else:
        sql += " ORDER BY t.TOWNCODE"

    rows = fetch_all(sql, params)

    # 查無此站或該站無紀錄時回傳 404
    if siteid is not None and not rows:
        raise HTTPException(status_code=404, detail="找不到指定測站，或該測站目前無監測紀錄")

    results = []

    for row in rows:
        # 3. 處理顏色對應 (使用 dict.get 取值，若遇到非預期狀態則預設為灰色)
        status_text = row["status"]
        status_color = AQI_STATUS_MAPPING.get(status_text, "#808080")

        # 2. 依照是否有 siteid，決定回傳的資料結構
        if siteid is None:
            # 列表模式：只回傳地圖上色需要的三個關鍵欄位
            results.append({
                "station_id": str(row["station_id"]),
                "district_code": row["district_code"],
                "status_color": status_color
            })
        else:
            # 單站模式：回傳彈出視窗所需的完整詳細數據
            results.append({
                "district_code": row["district_code"],
                "county": row["county"],
                "district_name": row["district_name"],
                "station_id": str(row["station_id"]),
                "station_name": row["station_name"],
                "aqi": to_number(row["aqi"]),
                "status": status_text,
                "status_color": status_color,
                "primary_pollutant": row["pollutant"],
                "published_at": (
                    row["publishtime"].isoformat()
                    if row["publishtime"] is not None
                    else None
                ),
                "pollutants": {
                    "pm25": to_number(row["pm25"]),
                    "pm10": to_number(row["pm10"]),
                    "o3": to_number(row["o3"]),
                    "co": to_number(row["co"]),
                    "so2": to_number(row["so2"]),
                    "no2": to_number(row["no2"]),
                    "nox": to_number(row["nox"]),
                    "no": to_number(row["nitrogen_monoxide"]),
                },
                "averages": {
                    "o3_8hr": to_number(row["o3_8hr"]),
                    "co_8hr": to_number(row["co_8hr"]),
                    "pm25_avg": to_number(row["pm25_avg"]),
                    "pm10_avg": to_number(row["pm10_avg"]),
                    "so2_avg": to_number(row["so2_avg"]),
                },
                "wind": {
                    "speed": to_number(row["wind_speed"]),
                    "direction": to_number(row["wind_direc"]),
                },
            })

    # 若為單筆查詢，直接解開 Array 回傳該筆字典
    if siteid is not None:
        return {"data": results[0]}

    # 若為全域查詢，回傳極簡化的 List
    return {
        "data": results,
        "meta": {
            "count": len(results)
        }
    }

# -- 景點資料(點位、彈出視窗) -----
@app.get("/api/attractions/sptpoint/", tags=["Attraction"])
def get_attraction_points(attraction_id: str | None = Query(default=None)):
    # 增加彈出視窗可能會用到的詳細欄位
    sql = """
        SELECT
            AttractionID,
            AttractionName,
            PositionLon,
            PositionLat,
            PostalAddress_City,
            PostalAddress_Town
        FROM attractions
    """
    
    params = None

    # 若前端有傳入 attraction_id，則只過濾該筆景點
    if attraction_id is not None:
        sql += " WHERE AttractionID = %s"
        params = (attraction_id,)
        
    sql += " ORDER BY AttractionID"

    rows = fetch_all(sql, params)

    # 查無此景點時回傳 404
    if attraction_id is not None and not rows:
        raise HTTPException(status_code=404, detail="找不到指定景點")

    attractions = []

    for row in rows:
        longitude = to_number(row["PositionLon"])
        latitude = to_number(row["PositionLat"])

        # 確保有取到數值後，再取到小數點第四位
        longitude = round(longitude, 4) if longitude is not None else None
        latitude = round(latitude, 4) if latitude is not None else None

        # 排除無效座標
        if longitude is None or latitude is None:
            continue
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            continue

        # 地圖打點必備的基本資料
        attraction_data = {
            "attraction_id": row["AttractionID"],
            "name": row["AttractionName"],
            "longitude": longitude,
            "latitude": latitude,
        }

        # 若是單筆查詢 (為了彈出視窗)，則合併詳細資訊
        if attraction_id is not None:
            attraction_data.update({
                "county": row["PostalAddress_City"],
                "district": row["PostalAddress_Town"],
            })

        attractions.append(attraction_data)

    # 如果有帶 ID，直接回傳單一物件 (字典)
    if attraction_id is not None:
        return {"data": attractions[0]}

    # 沒有帶 ID 時，回傳全部點位的陣列
    return {
        "data": attractions,
        "meta": {
            "count": len(attractions),
        },
    }

# -- 行政區邊界(鄉鎮圖層) -----
@app.get("/api/boundaries")
def get_boundaries():
    # 僅選取前端地圖套疊與資料綁定所需要的 4 個欄位
    sql = """
        SELECT
            TOWNCODE,
            COUNTYNAME,
            TOWNNAME,
            geometry_geojson
        FROM town_boundaries
    """
    
    rows = fetch_all(sql)
    results = []
    
    for row in rows:
        # 將字串格式的 GeoJSON 解析回字典，避免前端收到反斜線跳脫的字串
        try:
            geo_dict = json.loads(row["geometry_geojson"]) if row["geometry_geojson"] else None
        except Exception:
            geo_dict = None

        results.append({
            "towncode": row["TOWNCODE"],
            "countyname": row["COUNTYNAME"],
            "townname": row["TOWNNAME"],
            "geometry": geo_dict
        })
        
    return {
        "data": results,
        "meta": {
            "count": len(results)
        }
    }

# ==========================================
# 根據景點編號取得景點資料
# ==========================================
@app.get("/api/attraction/{attractionId}", summary="根據景點編號取得景點資料", tags=["Attraction"])
async def get_attraction_by_id(
    # 這裡的 Path 現在正確指向 fastapi.Path 了
    attractionId: str = Path(..., description="景點編號")
):
    try:
        # 1. 撈取該 ID 的景點主資料 (直接使用現成的 fetch_all 函式)
        sql_attraction = "SELECT * FROM attractions WHERE AttractionID = %s"
        attraction_rows = fetch_all(sql_attraction, (attractionId,))

        # 防呆機制：如果資料庫找不到這個 ID 的景點
        if not attraction_rows:
            return JSONResponse(
                status_code=400, 
                content={"error": True, "message": "景點編號不正確"}
            )

        # 取得第一筆 (也是唯一一筆) 資料
        attraction_data = attraction_rows[0]

        # 2. 撈取該景點的所有圖片
        # 注意欄位名稱需與資料庫相符 (AttractionID, URL)
        sql_images = "SELECT URL FROM attraction_images WHERE AttractionID = %s"
        images_data = fetch_all(sql_images, (attractionId,))

        # 將撈出來的多筆圖片資料，濃縮成一個只有網址字串的 List
        image_urls = [img["URL"] for img in images_data]

        # 3. 組合並回傳正確格式
        attraction_data["images"] = image_urls

        return {
            "data": attraction_data
        }

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )

# ==========================================
# 網站圖示 (Favicon)
# ==========================================
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # 利用 FRONTEND_DIR 組合出正確的本機絕對路徑
    favicon_path = os.path.join(FRONTEND_DIR, "assets", "images", "favicon.ico")
    return FileResponse(favicon_path)

# 3. 將 frontend 資料夾掛載到根路徑 "/"，範圍最廣的 StaticFiles 必須「墊底」
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


"""
# ----- 導向景點頁面 GET /api/attraction/{attraction_id} -----
@app.get("/api/attraction/{attraction_id}")
def redirect_to_attraction(attraction_id: str):
    # 確認景點存在
    rows = fetch_all(
        "SELECT AttractionID FROM attractions WHERE AttractionID = %s",
        (attraction_id,),
    )

    if not rows:
        raise HTTPException(status_code=404, detail="找不到這個景點")

    # 這裡要換成實際的前端景點頁面網址
    page_url = "http://localhost:3000/attraction.html"
    query = urlencode({"id": attraction_id})

    return RedirectResponse(
        url=f"{page_url}?{query}",
        status_code=302,
    )
"""
