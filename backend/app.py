import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

# 強制載入 .env 檔案中的變數到目前的環境中
load_dotenv(override=True)

app = FastAPI()

# 1. 取得目前 app.py 所在的絕對路徑 (backend 資料夾)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 往上一層找到 frontend 資料夾
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

# MySQL 的實際連線資訊
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),          
    'password': os.getenv("DB_PASSWORD"),  
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

# --- 行政區邊界(鄉鎮圖層) ---
@app.get("/boundaries", summary="國內鄉鎮邊界圖")
def get_boundaries():
    """
    國內鄉鎮邊界圖
    """
    # 改用全域變數，避免每次 request 都讀取硬碟檔案
    geojson_str = TOWN_BOUNDARY_GDF.to_json()

    # 壓成 base64
    encoded = base64.b64encode(geojson_str.encode("utf-8")).decode("utf-8")

    return JSONResponse(content={"data_base64": encoded})



# 3. 將 frontend 資料夾掛載到根路徑 "/"，範圍最廣的 StaticFiles 必須「墊底」
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")