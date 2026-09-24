const map = L.map("map").setView([23.7, 120.9], 7); // 建立 Leaflet 地圖並設定台灣為中心

L.tileLayer( // 建立 OpenStreetMap 地圖圖層
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png", // 設定地圖圖磚網址
    { // 設定地圖圖層選項
        attribution: "&copy; OpenStreetMap contributors" // 顯示地圖資料來源
    }
).addTo(map); // 將地圖圖層加入地圖

const stationLayer = L.layerGroup().addTo(map); // 建立測站圖層並加入地圖
const aqiLayer = L.layerGroup().addTo(map); // 建立 AQI 圖層並加入地圖
const attractionLayer = L.layerGroup().addTo(map); // 建立觀光景點圖層並加入地圖
const townshipBoundaryLayer = L.layerGroup(); // 建立鄉鎮邊界線圖層但先不加入地圖
const townshipAqiLayer = L.layerGroup(); // 建立鄉鎮 AQI 填色圖層但先不加入地圖

const stationData = { // 建立測站示範資料
    station_id: "CH001", // 設定測站編號
    name: "彰化測站", // 設定測站名稱
    county: "彰化縣", // 設定所屬縣市
    district: null, // 設定鄉鎮市區資料
    longitude: 120.541, // 設定測站經度
    latitude: 24.075, // 設定測站緯度
    aqi: 109, // 設定 AQI 數值
    status: "對敏感族群不健康", // 設定空品狀態
    primary_pollutant: "細懸浮微粒", // 設定主要污染物
    pollutants: { // 建立污染物資料
        pm25: "38 μg/m³", // 設定 PM2.5 數值與單位
        pm10: "52 μg/m³", // 設定 PM10 數值與單位
        o3: "48 ppb", // 設定臭氧數值與單位
        co: "0.4 ppm", // 設定一氧化碳數值與單位
        so2: "2 ppb" // 設定二氧化硫數值與單位
    },
    published_at: "示範資料" // 設定資料發布時間
};

const attractionData = { // 建立觀光景點示範資料
    attraction_id: 1, // 設定觀光景點編號
    name: "八卦山大佛", // 設定觀光景點名稱
    county: "彰化縣", // 設定觀光景點所屬縣市
    district: "彰化市", // 設定觀光景點所屬鄉鎮市區
    longitude: 120.545, // 設定觀光景點經度
    latitude: 24.075 // 設定觀光景點緯度
};

function getAqiColor(aqi) { // 建立 AQI 顏色判斷函式
    if (aqi <= 50) { // 判斷 AQI 是否為良好
        return "#43b581"; // 回傳綠色
    }

    if (aqi <= 100) { // 判斷 AQI 是否為普通
        return "#f2c94c"; // 回傳黃色
    }

    if (aqi <= 150) { // 判斷 AQI 是否對敏感族群不健康
        return "#f2994a"; // 回傳橘色
    }

    if (aqi <= 200) { // 判斷 AQI 是否對所有族群不健康
        return "#eb5757"; // 回傳紅色
    }

    if (aqi <= 300) { // 判斷 AQI 是否非常不健康
        return "#9b51e0"; // 回傳紫色
    }

    return "#8f4b4b"; // 回傳危害深紅色
}

function getAqiStatus(aqi) { // 建立 AQI 狀態判斷函式
    if (aqi <= 50) { // 判斷 AQI 是否為良好
        return "良好"; // 回傳良好狀態
    }

    if (aqi <= 100) { // 判斷 AQI 是否為普通
        return "普通"; // 回傳普通狀態
    }

    if (aqi <= 150) { // 判斷 AQI 是否對敏感族群不健康
        return "對敏感族群不健康"; // 回傳敏感族群不健康狀態
    }

    if (aqi <= 200) { // 判斷 AQI 是否對所有族群不健康
        return "對所有族群不健康"; // 回傳所有族群不健康狀態
    }

    if (aqi <= 300) { // 判斷 AQI 是否非常不健康
        return "非常不健康"; // 回傳非常不健康狀態
    }

    return "危害"; // 回傳危害狀態
}

function formatPublishedAt(dateTime) { // 將 API 日期格式轉成容易閱讀的格式
    if (!dateTime) { // 判斷是否沒有日期資料
        return "暫無資料"; // 沒有日期時顯示提示文字
    }

    return dateTime
        .replace("T", " ")
        .slice(0, 16)
        .replace(/-/g, "/"); // 顯示為 YYYY/MM/DD HH:mm
}

function createAqiPopupContent(boundary) { // 建立鄉鎮 AQI popup 內容
    const pollutants = boundary.pollutants || stationData.pollutants; // 優先使用鄉鎮污染物資料，沒有時使用示範資料
    const status = boundary.status || getAqiStatus(boundary.aqi); // 優先使用鄉鎮狀態，沒有時依 AQI 判斷
    const primaryPollutant = boundary.primary_pollutant || stationData.primary_pollutant; // 取得主要污染物
    const publishedAt = boundary.published_at || "示範資料"; // 取得資料發布時間

    return [ // 回傳完整 AQI popup HTML
        `<div class="station-popup">`, // 建立 popup 外層
        `<div class="popup-header">`, // 建立 popup 標題區域
        `<div>`, // 建立鄉鎮名稱區域
        `<h3>${boundary.town_name}</h3>`, // 顯示鄉鎮名稱
        `<p>${boundary.county_name}</p>`, // 顯示所屬縣市
        `</div>`, // 結束鄉鎮名稱區域
        `<strong class="aqi-value" style="background-color: ${getAqiColor(boundary.aqi)}">${boundary.aqi}</strong>`, // 顯示依 AQI 變色的數值
        `</div>`, // 結束 popup 標題區域
        `<div class="popup-divider"></div>`, // 建立 popup 分隔線
        `<p>${status}・指標污染物：${primaryPollutant}</p>`, // 顯示空品狀態與主要污染物
        `<div class="pollutant-grid">`, // 建立污染物資訊網格
        `<div><span>PM2.5</span><strong>${pollutants.pm25}</strong></div>`, // 顯示 PM2.5
        `<div><span>PM10</span><strong>${pollutants.pm10}</strong></div>`, // 顯示 PM10
        `<div><span>臭氧</span><strong>${pollutants.o3}</strong></div>`, // 顯示臭氧
        `<div><span>一氧化碳</span><strong>${pollutants.co}</strong></div>`, // 顯示一氧化碳
        `<div><span>二氧化硫</span><strong>${pollutants.so2}</strong></div>`, // 顯示二氧化硫
        `</div>`, // 結束污染物資訊網格
        `<p class="published-time">最後更新：${formatPublishedAt(publishedAt)}</p>`, // 顯示最後更新時間
        `</div>` // 結束 popup 外層
    ].join(""); // 合併 popup HTML 內容
}

const stationMarker = L.circleMarker( // 建立測站圓形標記
    [stationData.latitude, stationData.longitude], // 使用測站緯度與經度
    { // 設定測站標記樣式
        radius: 12, // 設定標記半徑
        color: "#ffffff", // 設定標記外框顏色
        weight: 2, // 設定標記外框寬度
        fillColor: "#0891b2", // 使用青綠色代表測站點位，避免與 AQI 顏色混淆
        fillOpacity: 0.95 // 設定標記透明度
    }
).addTo(stationLayer); // 將測站標記加入測站圖層

const popupContent = [ // 建立測站基本資訊 popup 內容
    `<div class="station-popup">`, // 建立 popup 外層
    `<div class="popup-header">`, // 建立 popup 標題區域
    `<div>`, // 建立測站文字資訊區域
    `<h3>${stationData.name}</h3>`, // 顯示測站名稱標題
    `<p>${stationData.county}</p>`, // 顯示所屬縣市
    `<p class="station-meta">測站名稱：${stationData.name}</p>`, // 顯示測站名稱欄位
    `<p class="station-meta">測站編號：${stationData.station_id}</p>`, // 顯示測站編號欄位
    `</div>`, // 結束測站文字資訊區域
    `</div>`, // 結束 popup 標題區域
    `</div>` // 結束 popup 外層
].join(""); // 將 popup 內容合併成 HTML 字串

stationMarker.bindPopup(popupContent); // 將 popup 綁定到測站標記

const attractionMarker = L.circleMarker( // 建立觀光景點圓形標記
    [attractionData.latitude, attractionData.longitude], // 使用觀光景點緯度與經度
    { // 設定觀光景點標記樣式
        radius: 9, // 設定標記半徑
        color: "#ffffff", // 設定標記外框顏色
        weight: 2, // 設定標記外框寬度
        fillColor: "#696969", // 使用藍色代表觀光景點，避免與 AQI 顏色混淆
        fillOpacity: 0.95 // 設定標記透明度
    }
).addTo(attractionLayer); // 將觀光景點標記加入觀光景點圖層

const attractionPopupContent = [ // 建立觀光景點 popup 內容
    `<div class="station-popup">`, // 建立 popup 外層
    `<div class="popup-header">`, // 建立 popup 標題區域
    `<div>`, // 建立景點名稱區域
    `<h3>${attractionData.name}</h3>`, // 顯示景點名稱
    `<p>${attractionData.county} - ${attractionData.district}</p>`, // 使用同一行顯示縣市與鄉鎮市區
    `</div>`, // 結束景點名稱區域
    `</div>`, // 結束 popup 標題區域
    `<div class="popup-divider"></div>`, // 建立 popup 分隔線
    `<a class="popup-button" href="http://localhost:4000/attraction.html?id=${attractionData.attraction_id}">觀光景點</a>`, // 導向 TourAQI 複製的景點詳細頁
    `</div>` // 結束 popup 外層
].join(""); // 將景點 popup 內容合併成 HTML 字串

attractionMarker.bindPopup(attractionPopupContent); // 將 popup 綁定到觀光景點標記

async function loadTownshipBoundaries() { // 建立載入鄉鎮邊界測試資料的函式
    const [boundaryResponse, aqiResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/api/boundaries"),
        fetch("http://127.0.0.1:8000/api/air-quality")
    ]);

    const boundaryResult = await boundaryResponse.json();
    const aqiResult = await aqiResponse.json();

    const boundaries = boundaryResult.data.map((boundary) => ({
        town_code: boundary.towncode,
        county_name: boundary.countyname,
        town_name: boundary.townname,
        geometry: boundary.geometry
    }));

    const aqiColorByTown = new Map(
        aqiResult.data.map((item) => [
            item.district_code,
            item.status_color
        ])
    );

    const aqiStationByTown = new Map(
        aqiResult.data.map((item) => [
            item.district_code,
            item.station_id
        ])
    );

    boundaries.forEach((boundary) => {
        const aqiColor =
            aqiColorByTown.get(boundary.town_code) || "#d1d5db";
        const aqiBorderColors = {
            "#43b581": "#237a5b",
            "#f2c94c": "#c79b16",
            "#f2994a": "#c46f1e",
            "#eb5757": "#b93636",
            "#9b51e0": "#7133aa",
            "#8f4b4b": "#663333",
            "#d1d5db": "#9ca3af"
        };
        const aqiBorderColor =
            aqiBorderColors[aqiColor] || "#6b7280";
        const boundaryPolygon = L.geoJSON(boundary.geometry, { // 使用 GeoJSON 建立透明鄉鎮邊界線
            style: { // 設定鄉鎮多邊形樣式
                color: "#ffffff", // 設定鄉鎮邊界線顏色
                weight: 1.5, // 設定鄉鎮邊界線寬度
                fillOpacity: 0 // 讓鄉鎮邊界圖層保持透明
            },
            onEachFeature: (feature, layer) => { // 設定每個鄉鎮區塊的互動行為
                layer.bindPopup(`<div class="township-simple-popup">${boundary.county_name}  ${boundary.town_name}</div>`); 
            }
        });

        const aqiPolygon = L.geoJSON(boundary.geometry, { // 使用相同 GeoJSON 建立 AQI 填色區塊
            style: { // 設定 AQI 填色區塊樣式
                color: aqiBorderColor, // 使用比填色更深的 AQI 邊框顏色
                weight: 1.5, // 設定 AQI 填色區塊邊界線寬度
                opacity: 1, // 讓 AQI 邊框清楚顯示
                fillColor: aqiColor,// 套用 AQI 顏色
                fillOpacity: 0.55 // 設定 AQI 填色區塊透明度
            }, // 結束 AQI 填色區塊樣式
            onEachFeature: (feature, layer) => { // 設定 AQI 填色區塊互動行為
                layer.bindPopup("空氣品質資料載入中..."); // 點擊區塊時先顯示載入提示

                layer.on("click", async () => { // 點擊鄉鎮區塊時取得 AQI 詳細資料
                    const stationId = aqiStationByTown.get(boundary.town_code); // 取得該鄉鎮對應的測站編號

                    if (!stationId) { // 判斷該鄉鎮是否沒有測站
                        layer.setPopupContent("此鄉鎮目前沒有測站資料"); // 顯示沒有資料提示
                        layer.openPopup(); // 開啟提示視窗
                        return; // 結束目前事件
                    }

                    try { // 嘗試取得單一測站 AQI 詳細資料
                        const detailResponse = await fetch(
                            `http://127.0.0.1:8000/api/air-quality?siteid=${stationId}`
                        );

                        const detailResult = await detailResponse.json(); // 讀取 API 回傳內容
                        const detail = detailResult.data; // 取得測站 AQI 詳細資料

                        layer.setPopupContent(
                            createAqiPopupContent({ ...boundary, ...detail })
                        ); // 用鄉鎮資料與 AQI 詳細資料組合彈窗
                        layer.openPopup(); // 開啟完整 AQI 視窗
                    } catch (error) { // 處理 AQI 詳細資料載入失敗
                        layer.setPopupContent("空氣品質資料載入失敗"); // 顯示錯誤提示
                        layer.openPopup(); // 開啟錯誤提示視窗
                        console.error("鄉鎮 AQI 詳細資料載入失敗：", error); // 印出錯誤原因
                    }
                });
            }
        });

        boundaryPolygon.addTo(townshipBoundaryLayer); // 將透明鄉鎮邊界線加入邊界圖層
        aqiPolygon.addTo(townshipAqiLayer); // 將 AQI 填色區塊加入 AQI 圖層
    }); // 結束逐一處理鄉鎮邊界

    if (document.querySelector("#aqi-layer")?.checked) { // 判斷 AQI 圖層是否預設勾選
        townshipAqiLayer.addTo(map); // AQI 預設勾選時顯示鄉鎮 AQI 顏色
    }
}

loadTownshipBoundaries().catch((error) => console.error("鄉鎮邊界載入失敗：", error)); // 載入失敗時在主控台顯示錯誤

const stationCheckbox = document.querySelector("#stations-layer"); // 取得測站點位 checkbox

stationCheckbox.addEventListener("change", () => { // 監聽 checkbox 勾選狀態變化
    if (stationCheckbox.checked) { // 判斷 checkbox 是否被勾選
        stationLayer.addTo(map); // 勾選時顯示測站圖層
    } else { // 如果 checkbox 沒有被勾選
        map.removeLayer(stationLayer); // 取消勾選時移除測站圖層
    }
});
const aqiCheckbox = document.querySelector("#aqi-layer"); // 取得 AQI checkbox

aqiCheckbox.addEventListener("change", () => { // 監聽 AQI checkbox 狀態變化
    if (aqiCheckbox.checked) { // 判斷 AQI checkbox 是否勾選
        aqiLayer.addTo(map); // 勾選時顯示 AQI 圖層
        townshipAqiLayer.addTo(map); // 勾選時顯示鄉鎮 AQI 顏色圖層
    } else { // 如果 AQI checkbox 沒有勾選
        map.removeLayer(aqiLayer); // 取消勾選時移除 AQI 圖層
        map.removeLayer(townshipAqiLayer); // 取消勾選時移除鄉鎮 AQI 顏色圖層
    }
});

const attractionCheckbox = document.querySelector("#attractions-layer"); // 取得觀光景點 checkbox

attractionCheckbox.addEventListener("change", () => { // 監聽觀光景點 checkbox 狀態變化
    if (attractionCheckbox.checked) { // 判斷觀光景點 checkbox 是否勾選
        attractionLayer.addTo(map); // 勾選時顯示觀光景點圖層
    } else { // 如果觀光景點 checkbox 沒有勾選
        map.removeLayer(attractionLayer); // 取消勾選時移除觀光景點圖層
    }
});

const townshipCheckbox = document.querySelector("#townships-layer"); // 取得鄉鎮邊界 checkbox

const attractionLegend = document.querySelector("#attraction-legend"); // 取得觀光景點圖例
const stationLegend = document.querySelector("#station-legend"); // 取得測站點位圖例
const townshipLegend = document.querySelector("#township-legend"); // 取得鄉鎮邊界圖例

function updateMapLegend() { // 依照目前勾選狀態更新地圖圖例
    const attractionChecked = attractionCheckbox.checked; // 取得觀光景點勾選狀態
    const stationChecked = stationCheckbox.checked; // 取得測站點位勾選狀態
    const townshipChecked = townshipCheckbox.checked; // 取得鄉鎮邊界勾選狀態

    attractionLegend.hidden = !attractionChecked; // 沒勾選時隱藏觀光景點圖例
    stationLegend.hidden = !stationChecked; // 沒勾選時隱藏測站點位圖例
    townshipLegend.hidden = !townshipChecked; // 沒勾選時隱藏鄉鎮邊界圖例
}

townshipCheckbox.addEventListener("change", () => { // 監聽鄉鎮邊界 checkbox 狀態變化
    if (townshipCheckbox.checked) { // 判斷鄉鎮邊界 checkbox 是否勾選
        townshipBoundaryLayer.addTo(map); // 勾選時顯示透明鄉鎮邊界線
    } else { // 如果鄉鎮邊界 checkbox 沒有勾選
        map.removeLayer(townshipBoundaryLayer); // 取消勾選時移除透明鄉鎮邊界線
    }
});

attractionCheckbox.addEventListener("change", updateMapLegend); // 觀光景點狀態改變時更新圖例
stationCheckbox.addEventListener("change", updateMapLegend); // 測站點位狀態改變時更新圖例
townshipCheckbox.addEventListener("change", updateMapLegend); // 鄉鎮邊界狀態改變時更新圖例

updateMapLegend(); // 頁面載入時依照預設勾選狀態更新圖例

async function loadStationsFromApi() {
    const response = await fetch("http://127.0.0.1:8000/api/stations");
    const result = await response.json();
    const stationCount = document.querySelector("#station-count");
    const stationUpdatedAt = document.querySelector("#station-updated-at");

    if (stationCount) {
        stationCount.textContent = result.meta.count;
    }

    if (stationUpdatedAt) {
        stationUpdatedAt.textContent = "最後更新：載入中...";
    }

    try {
        const airQualityResponse = await fetch(
            "http://127.0.0.1:8000/api/air-quality"
        );

        const airQualityResult = await airQualityResponse.json();
        const firstStationId = airQualityResult.data[0]?.station_id;

        if (firstStationId) {
            const detailResponse = await fetch(
                `http://127.0.0.1:8000/api/air-quality?siteid=${firstStationId}`
            );

            const detailResult = await detailResponse.json();

            if (stationUpdatedAt) {
                stationUpdatedAt.textContent =
                    `最後更新：${formatPublishedAt(detailResult.data.published_at)}`;
            }
        }
    } catch (error) {
        if (stationUpdatedAt) {
            stationUpdatedAt.textContent = "最後更新：暫無資料";
        }

        console.error("取得空氣品質更新時間失敗：", error);
    }

    stationLayer.removeLayer(stationMarker);

    result.data.forEach((station) => {
        const marker = L.circleMarker(
            [station.latitude, station.longitude],
            {
                radius: 7,
                color: "#ffffff",
                weight: 2,
                fillColor: "#0891b2",
                fillOpacity: 0.95
            }
        );

        marker.on("click", async () => {
            marker.bindPopup("資料載入中...").openPopup();

            try {
                const response = await fetch(
                    `http://127.0.0.1:8000/api/stations?siteid=${station.station_id}`
                );

                const result = await response.json();
                const detail = result.data;

                const airQualityResponse = await fetch(
                    `http://127.0.0.1:8000/api/air-quality?siteid=${station.station_id}`
                );

                const airQualityResult = await airQualityResponse.json();

                console.log("單一測站空品 API 回傳成功：", airQualityResult);

                const popupContent = `
                    <div class="station-popup">
                        <div class="popup-header">
                            <div>
                                <h3>${detail.name}</h3>
                                <p>${detail.county}</p>
                                <p class="station-meta">
                                    測站名稱：${detail.name}
                                </p>
                                <p class="station-meta">
                                    測站編號：${detail.station_id}
                                </p>
                            </div>
                        </div>
                    </div>
                    `;

                marker.setPopupContent(popupContent);
            } catch (error) {
                marker.setPopupContent("測站資料載入失敗");
                console.error("單一測站 API 載入失敗：", error);
            }
        });

        marker.addTo(stationLayer); // 把測站標記加入測站圖層，之後可透過 checkbox 控制顯示或隱藏
    });

    console.log(`測站點位建立完成：${result.meta.count} 筆`);
}

loadStationsFromApi().catch((error) => {
    console.error("測站 API 載入失敗：", error);
});

async function loadAttractionsFromApi() {
    const response = await fetch(
        "http://127.0.0.1:8000/api/attractions/sptpoint/"
    );

    const result = await response.json();

    attractionLayer.removeLayer(attractionMarker);

    result.data.forEach((attraction) => {
        const marker = L.circleMarker(
            [attraction.latitude, attraction.longitude],
            {
                radius: 5,
                color: "#ffffff",
                weight: 1,
                fillColor: "#696969",
                fillOpacity: 0.9
            }
        );

        marker.on("click", async () => {
            marker.bindPopup("景點資料載入中...").openPopup();

            try {
                const response = await fetch(
                    `http://127.0.0.1:8000/api/attraction/${attraction.attraction_id}`
                );

                const result = await response.json();
                const detail = result.data;

                const city = detail.PostalAddress_City || "";
                const town = detail.PostalAddress_Town || "";
                // 畫面只顯示正式景點 ID 的最後一段，完整 ID 仍用於導向與 API
                const displayAttractionId = String(detail.AttractionID || "").split("_").pop();

                const popupContent = `
            <div class="station-popup attraction-popup">
                <h3>${detail.AttractionName}</h3>
                <p>${city} - ${town}</p>
                <p>景點編號：${displayAttractionId}</p>
                <a class="popup-button" href="/attraction.html?id=${encodeURIComponent(detail.AttractionID)}">
                    觀光景點
                </a>
            </div>
        `;

                marker.setPopupContent(popupContent);
            } catch (error) {
                marker.setPopupContent("景點資料載入失敗");
                console.error("景點詳細 API 載入失敗：", error);
            }
        });

        marker.addTo(attractionLayer);
    });

    console.log(`觀光景點點位建立完成：${result.meta.count} 筆`);
}

loadAttractionsFromApi().catch((error) => {
    console.error("觀光景點點位載入失敗：", error);
});
