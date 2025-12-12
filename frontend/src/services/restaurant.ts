import type {
  RestaurantListResponse,
  RestaurantItem,
  QueueStatusResponse,
} from '@/types/RestaurantApi'

export async function getRestaurants(): Promise<RestaurantListResponse> {
  const response = await fetch(`http://localhost:8000/api/restaurants`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}


export async function getQueueStatus(restaurantId: number): Promise<QueueStatusResponse> {
  const response = await fetch(`http://localhost:8000/api/restaurants/${restaurantId}/queue/status`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}
