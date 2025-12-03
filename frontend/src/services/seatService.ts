//定義RestaurantService介面
// src/services/seatService.ts
import type { SeatDetail } from '../types/RestaurantApi';

// 這是原本寫在 Vue 裡的假資料，現在搬到這裡
//讓getSeats可以回傳假的座位資料
const MOCK_SEATS: SeatDetail[] = [
  { table_id: 1, label: "1 桌", x: 1, y: 1, status: 'eating' },
  { table_id: 2, label: "2 桌", x: 2, y: 1, status: 'empty' },
  { table_id: 3, label: "3 桌", x: 3, y: 1, status: 'eating' },
  { table_id: 4, label: "4 桌", x: 4, y: 1, status: 'eating' },
  { table_id: 5, label: "5 桌", x: 1, y: 2, status: 'eating' },
  { table_id: 6, label: "6 桌", x: 2, y: 2, status: 'eating' },
  { table_id: 7, label: "7 桌", x: 4, y: 2, status: 'empty' },
];

export const seatService = {
  // 模擬 GET /api/restaurants/{id}/seats
  // 使用 Promise 模擬非同步請求 (像是真的去網路上抓資料一樣)
  async getSeats(restaurantId: number): Promise<SeatDetail[]> {
    return new Promise((resolve) => {
      // 假裝延遲 0.5 秒，感覺更像真的 API
      setTimeout(() => {
        console.log(`[Mock API] 取得餐廳 ${restaurantId} 的座位資料`);
        resolve(MOCK_SEATS); // 回傳假資料
      }, 500);
    });
  },

  // 模擬 POST /api/tables/{id}/status

  async updateTableStatus(tableId: number, action: 'eating' | 'empty'): Promise<boolean> {
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log(`[Mock API] 更新桌號 ${tableId} 狀態為 ${action}`);
        resolve(true); // 假裝更新成功
      }, 300);
    });
  }
};

