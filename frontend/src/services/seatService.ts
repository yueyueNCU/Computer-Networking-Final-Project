//定義RestaurantService介面
// src/services/seatService.ts
import type { SeatDetail } from '../types/RestaurantApi';

// 這是原本寫在 Vue 裡的假資料，現在搬到這裡
//讓getSeats可以回傳假的座位資料
// 定義餐廳 1 的座位 (原本的)
const RESTAURANT_1_SEATS: SeatDetail[] = [
  { table_id: 1, label: "1 桌", x: 1, y: 1, status: 'eating' },
  { table_id: 2, label: "2 桌", x: 2, y: 1, status: 'empty' },
  { table_id: 3, label: "3 桌", x: 3, y: 1, status: 'eating' },
  { table_id: 4, label: "4 桌", x: 4, y: 1, status: 'eating' },
  { table_id: 5, label: "5 桌", x: 1, y: 2, status: 'eating' },
  { table_id: 6, label: "6 桌", x: 2, y: 2, status: 'eating' },
  { table_id: 7, label: "7 桌", x: 4, y: 2, status: 'empty' },
];

// 定義餐廳 2 的座位 (不一樣的格局，例如只有一排)
const RESTAURANT_2_SEATS: SeatDetail[] = [
  { table_id: 201, label: "A1", x: 1, y: 1, status: 'empty' },
  { table_id: 202, label: "A2", x: 2, y: 1, status: 'empty' },
  { table_id: 203, label: "B1", x: 1, y: 2, status: 'eating' },
  { table_id: 204, label: "B2", x: 2, y: 2, status: 'eating' },
];

// 建立一個對照表：ID -> 資料
const MOCK_DB: Record<number, SeatDetail[]> = {
  1: RESTAURANT_1_SEATS,
  2: RESTAURANT_2_SEATS,
};

export const seatService = {
  async getSeats(restaurantId: number): Promise<SeatDetail[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log(`[Mock API] 正在讀取餐廳 ${restaurantId} 的資料...`);
        
        // 根據傳入的 ID 去資料庫找
        const data = MOCK_DB[restaurantId];
        
        if (data) {
          // 如果有找到，回傳資料 (複製一份以免互相影響)
          resolve(JSON.parse(JSON.stringify(data)));
        } else {
          // 如果沒找到 (例如輸入 id=99)，回傳空陣列
          resolve([]);
        }
      }, 500);
    });
  },

  async updateTableStatus(tableId: number, action: 'eating' | 'empty'): Promise<boolean> {
    // 這裡維持原樣，假裝更新成功
    return new Promise((resolve) => resolve(true));
  }
};

