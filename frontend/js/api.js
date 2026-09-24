const API_BASE_URL = ""; // 設定 API 基礎網址，空字串代表使用目前網站來源

async function requestApi(endpoint) { // 建立共用 API 請求函式
    const response = await fetch(`${API_BASE_URL}${endpoint}`); // 呼叫指定的 API 路徑

    if (!response.ok) { // 判斷 API 回應是否成功
        throw new Error(`API 請求失敗：${response.status}`); // 回傳錯誤狀態
    }

    return await response.json(); // 將 API 回應轉換成 JSON
}

async function getStations() { // 取得所有測站基本資料
    return await requestApi("/api/stations"); // 呼叫測站 API
}

async function getAirQuality() { // 取得所有測站空氣品質資料
    return await requestApi("/api/air-quality"); // 呼叫空氣品質 API
}

async function getAttractions() { // 取得所有觀光景點資料
    return await requestApi("/api/attractions"); // 呼叫觀光景點列表 API
}

async function getAttractionDetail(attractionId) { // 取得單一景點詳細資料
    return await requestApi(`/api/attractions/${attractionId}`); // 呼叫景點詳細資料 API
}

async function getDistrictAirQuality() { // 取得鄉鎮 AQI 資料
    return await requestApi("/api/districts/air-quality"); // 呼叫鄉鎮空氣品質 API
} 