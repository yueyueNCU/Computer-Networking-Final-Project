<script setup lang="ts">
import { ref, computed } from 'vue';
// 直接引入隊友寫好的 Type 定義
import type { SeatDetail } from '../types/RestaurantApi';

// --- 1. 模擬資料 (Mock Data) ---
// 使用 SeatDetail 這個介面來規範資料格式
const seats = ref<SeatDetail[]>([
  { table_id: 1, label: "1 桌", x: 1, y: 1, status: 'eating' },
  { table_id: 2, label: "2 桌", x: 2, y: 1, status: 'empty' },
  { table_id: 3, label: "3 桌", x: 3, y: 1, status: 'eating' },
  { table_id: 4, label: "4 桌", x: 4, y: 1, status: 'eating' },
  { table_id: 5, label: "5 桌", x: 1, y: 2, status: 'eating' },
  { table_id: 6, label: "6 桌", x: 2, y: 2, status: 'eating' },
  { table_id: 7, label: "7 桌", x: 4, y: 2, status: 'empty' },
]);

// 模擬下一個排隊號碼
const nextQueueNumber = ref(106);

// --- 2. 彈窗控制 (UI 狀態) ---
const showModal = ref(false);
const selectedSeat = ref<SeatDetail | null>(null);  // 暫存目前被點擊的是哪一張桌子

// 處理點擊座位
const handleSeatClick = (seat: SeatDetail) => {
  selectedSeat.value = seat;
  showModal.value = true;
};

// 關閉彈窗
const closeModal = () => {
  showModal.value = false;
  selectedSeat.value = null;
};

// 執行動作：清桌 或 帶位
const confirmAction = () => {
  if (!selectedSeat.value) return;

  if (selectedSeat.value.status === 'eating') {
    // 如果現在是用餐中 -> 改為空桌 (清桌)
    selectedSeat.value.status = 'empty';
  } else {
    // 如果現在是空桌 -> 改為用餐中 (帶位)
    selectedSeat.value.status = 'eating';
    nextQueueNumber.value++; // 號碼牌往後跳一號
  }
  closeModal();
};

// 計算彈窗標題
const modalTitle = computed(() => {
  if (!selectedSeat.value) return '';
  return selectedSeat.value.status === 'eating' ? '即將清桌' : '即將帶位';
});
</script>

<template>
  <div class="seat-map-container">
    <h2 class="title">寶咖咖座位管理系統</h2>

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

.btn-green { background-color: #7bc07b; }
.btn-yellow { background-color: #f0c040; }
</style>