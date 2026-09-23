import os
import pymysql
import math
import json
from dotenv import load_dotenv
from fastapi import Query
from pathlib import Path
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

# -- 本機資料庫連線設定 -----

load_dotenv(Path(__file__).resolve().parent / ".env")


def get_db_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        autocommit=True,
    )


def fetch_all(sql, params=None):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #暫定不限Port, 留意正式部屬前是否需要修改
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# 資料文字轉換成數值

def to_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None


# -- 測站基本資訊 GET /api/stations -----

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

@app.get("/api/air-quality")
def get_air_quality():
    sql = """
        SELECT
            t.TOWNCODE AS district_code,
            t.COUNTYNAME AS county,
            t.TOWNNAME AS district_name,

            s.siteid AS station_id,
            s.sitename AS station_name,

            r.aqi,
            r.status,
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

        FROM town_boundaries AS t

        LEFT JOIN aqi_stations AS s
            ON s.siteid = (
                SELECT MIN(s2.siteid)
                FROM aqi_stations AS s2
                WHERE s2.county = t.COUNTYNAME
                  AND s2.township = t.TOWNNAME
            )

        LEFT JOIN aqi_records AS r
            ON r.siteid = s.siteid

        ORDER BY t.TOWNCODE
    """

    rows = fetch_all(sql)
    results = []

    for row in rows:
        results.append({
            "district_code": row["district_code"],
            "county": row["county"],
            "district_name": row["district_name"],

            "station_id": (
                str(row["station_id"])
                if row["station_id"] is not None
                else None
            ),
            "station_name": row["station_name"],

            "aqi": to_number(row["aqi"]),
            "status": row["status"],
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

    return {
        "data": results,
        "meta": {
            "count": len(results),
            "station_selection": "lowest_siteid",
        },
    }



# -- 景點資料(點位、彈出視窗) GET /api/attractions/sptpoint/ -----

@app.get("/api/attractions/sptpoint/")
def get_attraction_points():
    sql = """
        SELECT
            AttractionID,
            AttractionName,
            PositionLon,
            PositionLat,
            PostalAddress_City,
            PostalAddress_Town,
            PostalAddress_TownCode
        FROM attractions
        ORDER BY AttractionID
    """

    rows = fetch_all(sql)
    attractions = []

    for row in rows:
        longitude = to_number(row["PositionLon"])
        latitude = to_number(row["PositionLat"])

        # 沒有有效座標，就無法顯示在地圖上
        if longitude is None or latitude is None:
            continue

        if not (
            -180 <= longitude <= 180
            and -90 <= latitude <= 90
        ):
            continue

        attractions.append({
            "attraction_id": row["AttractionID"],
            "name": row["AttractionName"],
            "longitude": longitude,
            "latitude": latitude,
            "county": row["PostalAddress_City"],
            "district": row["PostalAddress_Town"],
        })

    return {
        "data": attractions,
        "meta": {
            "count": len(attractions),
        },
    }



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