import type {
  RestaurantListResponse,
  RestaurantItem, // 來自 dev (保留)
  QueueStatusResponse,
  UserQueueStatusResponse,
  JoinQueueResponse,
  JoinQueueRequest,
  SeatDetail, // 來自 HEAD (保留)
} from '@/types/RestaurantApi'

const API_BASE = 'http://localhost:8000/api';

// =======================
// Part 1: 客戶端 API (Client Side)
// =======================

// 餐廳列表
export async function getRestaurants(): Promise<RestaurantListResponse> {
  const response = await fetch(`${API_BASE}/restaurants`)
  if (!response.ok) throw new Error('Network response was not ok')
  return await response.json()
}

// 餐廳排隊狀態
export async function getQueueStatus(restaurantId: number): Promise<QueueStatusResponse> {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue/status`)
  if (!response.ok) throw new Error('Network response was not ok')
  return await response.json()
}

// 使用者個人排隊狀態
export async function getUserQueueStatus(userId: number): Promise<UserQueueStatusResponse> {
  const response = await fetch(`${API_BASE}/user/${userId}/queue`)
  if (!response.ok) throw new Error('Network response was not ok')
  return await response.json()
}

// 加入排隊
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

// 取消排隊
export async function leaveQueue(restaurantId: number, userId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    const error = new Error(errorData.error?.message || '取消排隊失敗')
    // 保留隊友的錯誤代碼處理邏輯
    ;(error as any).code = errorData.error?.code 
    throw error
  }
}

// =======================
// Part 2: 店家端 API (Admin Side - 你的新功能)
// =======================

// 1. 取得座位表
export async function getSeats(restaurantId: number): Promise<SeatDetail[]> {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/table`);
  
  if (!response.ok) {
    console.error("無法取得座位資料");
    return [];
  }
  
  const data = await response.json();
  return data.seats || []; 
}

// 2. 查詢下組叫號資訊
export async function getNextQueueInfo(restaurantId: number) {
  const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/queue/next`);
  if (!response.ok) {
    return null;
  }
  return await response.json();
}

// 3. 更新座位狀態 (入座/離座)
export async function updateTableStatus(
  restaurantId: number, 
  tableId: number, 
  action: 'eating' | 'empty',
  ticketNumber: number = 0 
): Promise<boolean> {
  
  const response = await fetch(`${API_BASE}/restaurant/${restaurantId}/tables/${tableId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      action: action,
      queue_ticket_number: ticketNumber
    }) 
  });

  return response.ok;
}