import type {
  RestaurantListResponse,
  RestaurantItem,
  QueueStatusResponse,
  UserQueueStatusResponse,
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
export async function getUserQueueStatus(restaurantId: number): Promise<UserQueueStatusResponse> {
  const response = await fetch(`http://localhost:8000/api/user/{user_id}/queue`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}