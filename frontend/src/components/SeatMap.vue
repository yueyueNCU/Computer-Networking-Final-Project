<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router'; // 1. 引入 useRoute 來抓網址參數
import type { SeatDetail } from '../types/RestaurantApi';
import { seatService } from '../services/seatService';

const route = useRoute(); // 取得目前的路由資訊
const seats = ref<SeatDetail[]>([]);
const nextQueueNumber = ref(106);

// --- 新增狀態變數 ---
const isLoading = ref(true);      // 是否正在載入
const errorMessage = ref('');     // 錯誤訊息 (空字串代表沒錯誤)

// --- 彈窗控制 (保持不變) ---
const showModal = ref(false);
const selectedSeat = ref<SeatDetail | null>(null);

// ... (handleSeatClick, closeModal, confirmAction, modalTitle 邏輯保持不變，請保留它們) ...
const handleSeatClick = (seat: SeatDetail) => {
  selectedSeat.value = seat;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedSeat.value = null;
};

const confirmAction = async () => {
  if (!selectedSeat.value) return;
  const newStatus = selectedSeat.value.status === 'eating' ? 'empty' : 'eating';
  const success = await seatService.updateTableStatus(selectedSeat.value.table_id, newStatus);
  if (success) {
    selectedSeat.value.status = newStatus;
    if (newStatus === 'eating') nextQueueNumber.value++;
    closeModal();
  } else {
    alert("更新失敗");
  }
};

const modalTitle = computed(() => {
  if (!selectedSeat.value) return '';
  return selectedSeat.value.status === 'eating' ? '即將清桌' : '即將帶位';
});

// --- 修改生命週期 ---
onMounted(async () => {
  // 1. 從網址取得 ID (route.params.id 是字串，要轉成數字)
  const restaurantId = Number(route.params.id);

  // 防呆：如果 ID 不是數字
  if (isNaN(restaurantId)) {
    errorMessage.value = "無效的餐廳 ID";
    isLoading.value = false;
    return;
  }

  try {
    // 2. 呼叫 Service
    const data = await seatService.getSeats(restaurantId);
    
    // 模擬：如果回傳空陣列，假設是找不到餐廳 (視後端實作而定)
    if (data.length === 0) {
        throw new Error("找不到該餐廳資料");
    }

    seats.value = data;
  } catch (error) {
    // 3. 錯誤處理
    console.error(error);
    errorMessage.value = "讀取資料失敗，請稍後再試。";
  } finally {
    // 4. 無論成功失敗，都把 Loading 關掉
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="seat-map-container">
    
    <div v-if="isLoading" class="loading-state">
      <h2>資料讀取中...</h2>
    </div>

    <div v-else-if="errorMessage" class="error-state">
      <h2>⚠️ 錯誤</h2>
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else class="content-wrapper">
      <h2 class="title">寶咖咖座位管理系統 (餐廳 ID: {{ $route.params.id }})</h2>

      <div class="grid-container">
        <div 
          v-for="seat in seats" 
          :key="seat.table_id"
          class="seat-item"
          :class="{ 
            'status-eating': seat.status === 'eating', 
            'status-empty': seat.status === 'empty' 
          }"
          :style="{ gridColumn: seat.x, gridRow: seat.y }"
          @click="handleSeatClick(seat)"
        >
          <div class="seat-icon">
            <span v-if="seat.status === 'eating'">🍽️</span>
          </div>
          <div class="seat-label">{{ seat.label }}</div>
        </div>
      </div>

      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
         <div class="modal-content">
            <h3>{{ modalTitle }}</h3>
            <div class="modal-info">
              <div v-if="selectedSeat?.status === 'empty'" class="queue-info">
                號碼: <span class="highlight">{{ nextQueueNumber }}號</span>
              </div>
              <div class="table-info">
                桌號: {{ selectedSeat?.label }}
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn btn-green" @click="confirmAction">
                {{ selectedSeat?.status === 'eating' ? '清桌' : '帶位' }}
              </button>
              <button class="btn btn-yellow" @click="closeModal">取消</button>
            </div>
         </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* 版面設定 */
.seat-map-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background-color: #cccccc; /* 灰色背景 */
  min-height: 100vh;
  width: 100%;
}

.title {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #333;
  font-weight: bold;
}

/* 網格系統 CSS Grid */
.grid-container {
  display: grid;
  grid-template-columns: repeat(4, 100px); /* 4欄 */
  grid-template-rows: repeat(2, 100px);    /* 2列 */
  gap: 20px; /* 間距 */
}

/* 座位卡片樣式 */
.seat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  width: 100px;
  height: 100px;
  transition: transform 0.2s;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}

.seat-item:hover {
  transform: scale(1.05); /* 滑鼠移過去放大 */
}

/* 狀態顏色 */
.status-empty {
  background-color: #a9a9a9; /* 深灰色代表空桌 */
}

.status-eating {
  background-color: #d3d3d3; /* 淺灰代表用餐 */
  border: 4px solid #a52a2a; /* 紅框代表有人 */
}

.seat-icon {
  font-size: 2rem;
  height: 40px;
}

.seat-label {
  margin-top: 5px;
  font-weight: bold;
  color: #000;
}

/* Modal 彈窗樣式 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5); /* 半透明黑底 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 300px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.modal-content h3 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: bold;
  color: #333;
}

.modal-info {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  text-align: left;
  padding-left: 2rem;
  color: #333;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  justify-content: space-around;
}

.btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  color: white;
  font-weight: bold;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
}

.error-state h2 {
  color: #a52a2a;
  font-size: 2rem;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.btn-green { background-color: #7bc07b; }
.btn-yellow { background-color: #f0c040; }
</style>