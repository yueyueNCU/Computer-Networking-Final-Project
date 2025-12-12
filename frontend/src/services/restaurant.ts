import type {
  RestaurantListResponse,
  RestaurantItem,
  QueueStatusResponse,
  UserQueueStatusResponse,
  JoinQueueResponse,
  JoinQueueRequest,
} from '@/types/RestaurantApi'

// 餐廳資訊
export async function getRestaurants(): Promise<RestaurantListResponse> {
  const response = await fetch(`http://localhost:8000/api/restaurants`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}

// 在 home page 點我要排隊時出現的餐廳排隊資訊
export async function getQueueStatus(restaurantId: number): Promise<QueueStatusResponse> {
  const response = await fetch(`http://localhost:8000/api/restaurants/${restaurantId}/queue/status`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}

// 個人的排隊狀態
export async function getUserQueueStatus(userId: number): Promise<UserQueueStatusResponse> {
  const response = await fetch(`http://localhost:8000/api/user/${userId}/queue`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}

// 加入餐廳的排隊
export async function joinQueue(restaurantId: number, userId: number): Promise<JoinQueueResponse> {
  const requestBody: JoinQueueRequest = { user_id: userId }
  const response = await fetch(`http://localhost:8000/api/restaurants/${restaurantId}/queue`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })

  if (!response.ok) {
    // 嘗試解析後端回傳的錯誤結構 { error: { code: ..., message: ... } }
    const errorData = await response.json().catch(() => ({}))
    const errorMessage = errorData.error?.message || '加入排隊失敗'
    throw new Error(errorMessage)
  }

  return await response.json()
}

export async function leaveQueue(restaurantId: number, userId: number): Promise<void> {
  const response = await fetch(`http://localhost:8000/api/restaurants/${restaurantId}/queue`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  })

  if (!response.ok) {
    // 解析錯誤訊息
    const errorData = await response.json().catch(() => ({}))
    
    // 建立一個 Error 物件，並附加 code 屬性以便 View 層判斷
    const error = new Error(errorData.error?.message || '取消排隊失敗')
    ;(error as any).code = errorData.error?.code // 將後端的 error code (如 NOT_IN_QUEUE) 綁在 error 物件上
    throw error
  }
  
  // 成功時沒有回傳 body (204 No Content)，直接結束即可
}