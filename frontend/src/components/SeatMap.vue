<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { SeatDetail } from '../types/RestaurantApi';
// 引入剛剛寫好的 Service
import { seatService } from '../services/seatService';

// --- 1. 資料變數 (這裡改成空陣列，等待資料載入) ---
const seats = ref<SeatDetail[]>([]); 
const nextQueueNumber = ref(106);

// --- 2. 生命週期 Hooks ---
// 當這個 html 骨架被掛載到畫面上時，自動執行
onMounted(async () => {
  // 3. 呼叫 Service (關鍵協作點！)
  // await 的意思是：「暫停在這裡，等 seatService.getSeats 做完再往下走」
  // 這時候 JavaScript 引擎會去跑 service 裡的 setTimeout，0.5秒後回來
  seats.value = await seatService.getSeats(1);
});

// --- 3. 彈窗控制 ---
const showModal = ref(false);
const selectedSeat = ref<SeatDetail | null>(null);

const handleSeatClick = (seat: SeatDetail) => {
  selectedSeat.value = seat;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedSeat.value = null;
};

// --- 4. 修改後的確認動作 (加入 Service 呼叫) ---
const confirmAction = async () => {
  if (!selectedSeat.value) return;

  // 1. 先決定新狀態是什麼
  const newStatus = selectedSeat.value.status === 'eating' ? 'empty' : 'eating';
  
  // 2. 呼叫 Service 通知後端 (雖然現在是假的，但結構是對的)
  // 這裡用了 await，代表會等後端回應成功後，才繼續往下執行
  const success = await seatService.updateTableStatus(selectedSeat.value.table_id, newStatus);

  // 3. 如果後端說 OK，前端才更新畫面
  if (success) {
    selectedSeat.value.status = newStatus;
    
    if (newStatus === 'eating') {
      nextQueueNumber.value++;
    }
    closeModal();
  } else {
    alert("更新失敗，請稍後再試");
  }
};

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