import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from dotenv import load_dotenv
import urllib3

# 關閉 urllib3 未核驗 SSL 的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. 載入環境變數 (自動定位同目錄下的 .env 檔案)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),          
    'password': os.getenv("DB_PASSWORD"),
    'port': os.getenv("DB_PORT", "3306"), # 預設使用 3306
    'database': os.getenv("DB_NAME")    
}

# 建立 SQLAlchemy 引擎
engine = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4"
)

# 2. 環境部 AQI API 網址
API_URL = "https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=af57253c-e838-46da-a1f5-12b43afd75f3&limit=1000&sort=ImportDate%20desc&format=JSON"

# 定義寫入資料庫 aqi_records 的欄位清單 (含 API 所有即時量測欄位如 pm25, no2, nox, no 等)
DB_COLS = [
    'siteid', 'sitename', 'county', 'aqi', 'pollutant', 'status', 'so2', 'co', 
    'o3', 'o3_8hr', 'pm10', 'pm25', 'no2', 'nox', 'no', 'wind_speed', 'wind_direc', 
    'publishtime', 'co_8hr', 'pm25_avg', 'pm10_avg', 'so2_avg', 'longitude', 'latitude'
]

def fetch_and_update_aqi():
    """執行 ETL：抓取即時 AQI API 並更新資料庫"""
    print(f"[{datetime.now()}] 開始抓取 AQI 即時資料...")
    
    try:
        # 設定 timeout，並加上 SSL verify 相容處理
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            response = requests.get(API_URL, timeout=10, verify=False)
            response.raise_for_status()
            
        json_data = response.json()
        
        # 相容 API 回傳為 dict (含 'records' key) 或直接回傳 list 格式
        records = json_data.get('records', json_data) if isinstance(json_data, dict) else json_data
        df = pd.DataFrame(records)
        
        # 修正欄位名稱避免 MySQL 點號報錯 (pm2.5 -> pm25, pm2.5_avg -> pm25_avg)
        rename_dict = {}
        if 'pm2.5' in df.columns:
            rename_dict['pm2.5'] = 'pm25'
        if 'pm2.5_avg' in df.columns:
            rename_dict['pm2.5_avg'] = 'pm25_avg'
        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)
            
        # 僅保留資料庫 table 包含的欄位
        df = df[[col for col in DB_COLS if col in df.columns]].copy()
            
        # 3. 確保資料寫入的原子性 (Transaction)
        with engine.begin() as conn:
            # 關鍵：使用 TRUNCATE 清空資料表，此方法執行速度最快，且能完整保留先前設定好的 DDL Schema (如 Primary Key)
            conn.execute(text("TRUNCATE TABLE aqi_records;"))
            
            # 使用 append 寫入新資料
            df.to_sql('aqi_records', con=conn, if_exists='append', index=False)
            
        print(f"[{datetime.now()}] ✅ 成功清空並寫入 {len(df)} 筆最新 AQI 資料！")
        
    except Exception as e:
        # 遇到錯誤時只記錄 Log，不立即重試。等待下一次排程時間再抓取，避免頻繁 Request 被 API 伺服器封鎖
        print(f"[{datetime.now()}] ❌ 抓取或寫入失敗：{e}")

# 4. 設定 APScheduler 排程器
if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    
    fetch_and_update_aqi()
    
    # 針對有抓取次數限制的 API，維持每小時執行一次 (固定於 15 分) 是最穩定的做法
    scheduler.add_job(fetch_and_update_aqi, 'cron', minute=15)
    
    print("啟動背景排程器... (按 Ctrl+C 終止)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("排程器已關閉。")