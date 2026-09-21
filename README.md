TourAQI/ (專案根目錄)
├── .gitignore
├── README.md
│
├── frontend/                # 前端目錄 (10 負責 - 原生開發版)
│   ├── index.html           # 主頁面 (包含地圖容器、圖層控制介面、彈出視窗骨架)
│   ├── css/
│   │   └── style.css        # 樣式表 (處理向右漸層、排版、UI 顏色)
│   ├── js/
│   │   ├── main.js          # 主程式 (處理畫面按鈕點擊、頁面初始化)
│   │   ├── map.js           # Leaflet 地圖專用邏輯 (初始化地圖、圖層套疊、圖示)
│   │   └── api.js           # 負責呼叫後端 API (使用 fetch 串接 Sammi 寫好的接口)
│   └── assets/              # 靜態資源
│       ├── icons/           # 自訂的 marker icon 或介面 icon
│       └── images/          # 預設圖片等
│
├── backend/                 # 後端目錄 (Sammi 負責)
│   ├── requirements.txt     
│   └── main.py              # FastAPI 程式進入點
│
└── data_pipeline/           # 資料流與排程目錄 (Dwayne 負責)
    ├── requirements.txt     
    ├── etl_jobs.py          
    └── scheduler.py