import csv
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #暫定不限Port, 留意正式部屬前是否需要修改
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 讀取測試版測站資料
CSV_PATH = (
    Path(__file__).resolve().parent
    / "sample_data"
    / "stations-10.csv"
)

# 讀取測試版行政區邊界資料
BOUNDARIES_PATH = (
    Path(__file__).resolve().parent
    / "sample_data"
    / "boundaries-sample.geojson"
)

# 讀取測試版空氣品質資料
DISTRICT_AIR_QUALITY_PATH = (
    Path(__file__).resolve().parent
    / "sample_data"
    / "district-air-quality-sample.json"
)

# 讀取測試版景點資料
ATTRACTIONS_PATH = (
    Path(__file__).resolve().parent
    / "sample_data"
    / "taipei-attractions-5.json"
)

# 數值轉換
def to_number(value):
    if value is None:
        return None

    try:
        return float(value.strip())
    except ValueError:
        return None


# -- 測站 GET/api/stations -----
@app.get("/api/stations")
def get_stations():
    stations = []
    seen_ids = set()

    with CSV_PATH.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            station_id = row["siteid"].strip()

            # 跳過缺少編號或重複的測站
            if not station_id or station_id in seen_ids:
                continue

            # 座標從文字轉成數字，缺值或格式錯誤則跳過
            try:
                longitude = float(row["longitude"])
                latitude = float(row["latitude"])
            except ValueError:
                continue

            if not (
                -180 <= longitude <= 180
                and -90 <= latitude <= 90
            ):
                continue

            stations.append({
                "station_id": station_id,
                "name": row["sitename"].strip(),
                "county": row["county"].strip(),
                "district": None,
                "longitude": longitude,
                "latitude": latitude,
            })

            seen_ids.add(station_id)

    return {
        "data": stations,
        "meta": {
            "count": len(stations),
            "is_mock": True,
        },
    }


# -- 最新空氣品質 GET /api/air-quality -----

# -- 鄉鎮代表空氣品質 GET /api/air-quality -----

@app.get("/api/air-quality")
def get_air_quality():
    with DISTRICT_AIR_QUALITY_PATH.open(
        "r", encoding="utf-8"
    ) as file:
        return json.load(file)


# -- 景點資料(彈出視窗) GET /api/attractions -----

@app.get("/api/attractions")
def get_attractions():
    with ATTRACTIONS_PATH.open(
        "r", encoding="utf-8-sig"
    ) as file:
        source = json.load(file)

    image_host = source["img_host"].rstrip("/")
    attractions = []

    for item in source["list"]:
        # 將座標文字轉成數字
        try:
            longitude = float(item["longitude"])
            latitude = float(item["latitude"])
        except (ValueError, TypeError):
            continue

        if not (
            -180 <= longitude <= 180
            and -90 <= latitude <= 90
        ):
            continue

        # 原始圖片路徑是多張串在一起，先取第一張當縮圖
        image_parts = (item.get("imgurls") or "").split("/imgs/")
        image_names = [
            part for part in image_parts if part.strip()
        ]

        thumbnail_url = None

        if image_names:
            thumbnail_url = (
                f"{image_host}/imgs/{image_names[0]}"
            )

        # 暫時取完整介紹的前 100 個字作為彈窗摘要 (若版面不需要則之後刪除)
        description = (item.get("description") or "").strip()
        summary = description[:100]

        if len(description) > 100:
            summary += "…"

        attractions.append({
            "attraction_id": str(item["_id"]),
            "name": item["name"],
            "longitude": longitude,
            "latitude": latitude,
            "address": item.get("address"),
            "summary": summary,
            "thumbnail_url": thumbnail_url,
        })

    return {
        "data": attractions,
        "meta": {
            "count": len(attractions),
            "is_mock": True,
        },
    }



# -- 景點詳細資訊 GET /api/attractions/{attraction_id} -----

@app.get("/api/attractions/{attraction_id}")
def get_attraction(attraction_id: str):
    with ATTRACTIONS_PATH.open(
        "r", encoding="utf-8-sig"
    ) as file:
        source = json.load(file)

    for item in source["list"]:
        # 尋找 ID 相符的景點
        if str(item["_id"]) != attraction_id:
            continue

        image_host = source["img_host"].rstrip("/")

        # 取得全部圖片的檔名
        image_parts = (item.get("imgurls") or "").split("/imgs/")
        image_names = [
            part for part in image_parts if part.strip()
        ]

        images = []

        for image_name in image_names:
            images.append({
                "url": f"{image_host}/imgs/{image_name}",
                "description": item["name"],
            })

        try:
            longitude = float(item["longitude"])
            latitude = float(item["latitude"])
        except (ValueError, TypeError):
            longitude = None
            latitude = None

        return {
            "data": {
                "attraction_id": str(item["_id"]),
                "name": item["name"],
                "category": item.get("CAT"),
                "description": item.get("description"),
                "address": item.get("address"),
                "transport": item.get("direction"),
                "mrt": item.get("MRT"),
                "opening_hours": item.get("MEMO_TIME"),
                "longitude": longitude,
                "latitude": latitude,
                "images": images,
            },
            "meta": {
                "is_mock": True,
            },
        }

    # 全部找完都沒有符合的景點
    raise HTTPException(
        status_code=404,
        detail="找不到指定景點",
    )



# -- 行政區邊界 GET /api/boundaries -----

@app.get("/api/boundaries")
def get_boundaries():
    if not BOUNDARIES_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="邊界資料尚未準備完成",
        )

    return FileResponse(
        path=BOUNDARIES_PATH,
        media_type="application/geo+json",
    )