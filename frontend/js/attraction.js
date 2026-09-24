// ==========================================
// 1. 解析網址取得 attractionId
// ==========================================
// 從網址的 ?id= 取得景點編號
const queryParams = new URLSearchParams(window.location.search);
const attractionId = queryParams.get('id');

// ==========================================
// 2. DOM 元素選取
// ==========================================
// 文字資訊區
const titleEl = document.getElementById('attraction-title');
const cityEl = document.getElementById('attraction-city');
const townEl = document.getElementById('attraction-town');
const descEl = document.getElementById('attraction-description');
const addressEl = document.getElementById('attraction-address');
const transportEl = document.getElementById('attraction-transport');

// 輪播圖與圖片區
const trackEl = document.getElementById('carousel-track');
const dotsEl = document.getElementById('carousel-dots');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');

// 全域變數儲存圖片與當前索引
let imagesList = [];
let currentImgIndex = 0;

// ==========================================
// 3. 頁面載入時 Fetch 資料並渲染
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
  fetchAttractionData();
});

async function fetchAttractionData() {
  try {
    // 呼叫你的後端 API
    const response = await fetch(
      `/api/attraction/${attractionId}`
    );
    const result = await response.json();
    const data = result.data; // 依照你的 API 格式，通常資料包在 data 裡面

    // ---- A. 渲染純文字資訊 ----
    titleEl.textContent = data.AttractionName;
    cityEl.textContent = data.PostalAddress_City;
    townEl.textContent = data.PostalAddress_Town;
    descEl.textContent = data.Description;
    addressEl.textContent = data.PostalAddress_StreetAddress;
    transportEl.textContent =
      data.TrafficInfo?.trim() || "目前尚無交通資訊";

    // ---- B. 渲染圖片與輪播指示器 ----
    imagesList = data.images;
    renderCarousel(imagesList);

  } catch (error) {
    console.error('取得景點資料失敗:', error);
  }
}

// ==========================================
// 4. 渲染輪播圖與橫向指示條
// ==========================================
function renderCarousel(images) {
  trackEl.innerHTML = '';
  dotsEl.innerHTML = '';

  images.forEach((imgUrl, index) => {
    // 建立圖片
    const img = document.createElement('img');
    img.src = imgUrl;
    img.className = 'carousel-img';
    if (index === 0) img.classList.add('active');
    trackEl.appendChild(img);

    // 建立橫向指示線段 (均分寬度)
    const bar = document.createElement('div');
    bar.className = 'indicator-bar';
    if (index === 0) bar.classList.add('active');

    // 點擊線段切換至該圖
    bar.addEventListener('click', () => {
      changeImage(index);
    });
    dotsEl.appendChild(bar);
  });
}

// ==========================================
// 5.切換圖片與指示條狀態 (上一張 / 下一張)
// ==========================================
function changeImage(newIndex) {
  const allImgs = document.querySelectorAll('.carousel-img');
  const allBars = document.querySelectorAll('.indicator-bar');

  // 移除舊的 active
  allImgs[currentImgIndex].classList.remove('active');
  allBars[currentImgIndex].classList.remove('active');

  // 更新 index
  currentImgIndex = newIndex;

  // 加上新的 active
  allImgs[currentImgIndex].classList.add('active');
  allBars[currentImgIndex].classList.add('active');
}

// 綁定左右按鈕點擊事件
prevBtn.addEventListener('click', () => {
  // 如果是第一張，按上一張就跳到最後一張；否則就 -1
  const newIndex = currentImgIndex === 0 ? imagesList.length - 1 : currentImgIndex - 1;
  changeImage(newIndex);
});

nextBtn.addEventListener('click', () => {
  // 如果是最後一張，按下一張就跳回第一張；否則就 +1
  const newIndex = currentImgIndex === imagesList.length - 1 ? 0 : currentImgIndex + 1;
  changeImage(newIndex);
});
