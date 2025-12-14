import type {
  RestaurantListResponse,
  QueueStatusResponse,
  UserQueueStatusResponse,
  JoinQueueResponse,
  JoinQueueRequest,
  SeatDetail,
} from '@/types/RestaurantApi'

const API_BASE = 'http://localhost:8000/api';

// =======================
// Part 1: 客戶端 API (完全保留，不要刪除)
// =======================

export async function getRestaurants(): Promise<RestaurantListResponse> {
  const response = await fetch(`${API_BASE}/restaurants`)
  if (!response.ok) throw new Error('Network response was not ok')
  return await response.json()
}

export async function getQueueStatus(restaurantId: number): Promise<QueueStatusResponse> {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue/status`)
  if (!response.ok) throw new Error('Network response was not ok')
  return await response.json()
}

export async function getUserQueueStatus(userId: number): Promise<UserQueueStatusResponse> {
  const response = await fetch(`${API_BASE}/user/${userId}/queue`)
  if (!response.ok) throw new Error('Network response was not ok')
  return await response.json()
}

export async function joinQueue(restaurantId: number, userId: number): Promise<JoinQueueResponse> {
  const requestBody: JoinQueueRequest = { user_id: userId }
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    const errorMessage = errorData.error?.message || '加入排隊失敗'
    throw new Error(errorMessage)
  }
  return await response.json()
}

export async function leaveQueue(restaurantId: number, userId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    const error = new Error(errorData.error?.message || '取消排隊失敗')
    ;(error as any).code = errorData.error?.code 
    throw error
  }
}

// =======================
// Part 2: 店家端 API (更新過的部分)
// =======================

// 1. 取得座位表
export async function getSeats(restaurantId: number): Promise<SeatDetail[]> {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/table`);
  
  if (!response.ok) {
    console.error("無法取得座位資料");
    return [];
  }
  
  const data = await response.json();
  // 根據你的 Agenda.md，後端回傳格式是 { restaurant_id:..., seats: [...] }
  return data.seats || []; 
}

// 2. (新增) 查詢下組叫號資訊
// 前端要先 Call 這個，才知道要帶哪一號客人入座
export async function getNextQueueInfo(restaurantId: number) {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue/next`);
  if (!response.ok) {
    return null;
  }
  return await response.json();
}

// 3. (修改) 更新座位狀態 (入座/離座)
// 我們增加了 ticketNumber 參數，用來傳送排隊號碼給後端
export async function updateTableStatus(
  restaurantId: number, 
  tableId: number, 
  action: 'eating' | 'empty',
  ticketNumber: number = 0  // <--- 這裡新增了參數，預設為 0
): Promise<boolean> {
  
  // 注意：Swagger 上這裡是單數 "restaurant"
  const response = await fetch(`${API_BASE}/restaurant/${restaurantId}/tables/${tableId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      action: action,
      queue_ticket_number: ticketNumber // <--- 這裡把號碼傳給後端
    }) 
  });

  return response.ok;
}