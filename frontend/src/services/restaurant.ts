import type {
  RestaurantListResponse,
  RestaurantItem,
  QueueStatusResponse,
} from '@/types/RestaurantApi'

// 假資料
const MOCK_RESTAURANTS: RestaurantItem[] = [
  {
    restaurant_id: 1,
    restaurant_name: '麥克小姐',
    lat: 24.9698,
    lng: 121.1925,
    image_url: 'https://placehold.co/600x400?text=Burger',
    average_price: '$150 - $250',
    specialties: '花生醬起司堡、炸雞翅',
    status: 'green',
  },
  {
    restaurant_id: 2,
    restaurant_name: '食間',
    lat: 24.9705,
    lng: 121.191,
    image_url: 'https://placehold.co/600x400?text=Beef+Noodles',
    average_price: '$120 - $180',
    specialties: '咖哩飯',
    status: 'red',
  },
  {
    restaurant_id: 3,
    restaurant_name: '櫥窗',
    lat: 24.969,
    lng: 121.1935,
    image_url: 'https://placehold.co/600x400?text=Pasta',
    average_price: '$200 - $350',
    specialties: '客家小炒',
    status: 'yellow',
  },
  {
    restaurant_id: 4,
    restaurant_name: '哈哈',
    lat: 24.98,
    lng: 121.188,
    image_url: 'https://placehold.co/600x400?text=Pasta',
    average_price: '$200 - $350',
    specialties: '13',
    status: 'yellow',
  },
]

/**
 * 取得所有餐廳資訊 (Mock 版)
 */
export async function getRestaurants(): Promise<RestaurantListResponse> {
  await new Promise((resolve) => setTimeout(resolve, 500))

  // 直接回傳假資料，而不是去呼叫 API
  // 因為這是一個 async 函式，它會自動把結果包成 Promise
  const response = await fetch(`http://localhost:8000/api/restaurants`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
}

/* // 等後端建置好後，解開這段程式碼並註解掉上面的 Mock 版本即可
const API_BASE_URL = 'http://localhost:8000/api'
export async function getRestaurants(): Promise<RestaurantListResponse> {
  const response = await fetch(`${API_BASE_URL}/restaurants`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return await response.json()
}
const response = await 
*/

export async function getQueueStatus(restaurantId: number): Promise<QueueStatusResponse> {
  // --- 這邊是 Mock，等資料庫建好之後用下面註解掉的地方 ---
  // 模擬網路延遲
  await new Promise((resolve) => setTimeout(resolve, 300))

  // 模擬回傳資料 (對應後端 QueueStatusResponse schema)
  const randomWaiting = Math.floor(Math.random() * 10) + 1 // 隨機 1~10 組

  return {
    restaurant_id: restaurantId,
    restaurant_name: '餐廳名稱(Mock)',
    current_number: 100,
    total_waiting: randomWaiting,
    // 這裡簡單模擬一組需等 5 分鐘
    avg_wait_time: randomWaiting * 5,
  }

  // --- 資料庫建好後切換成這個 ---
  /*
  const response = await fetch(`/api/restaurants/${restaurantId}/queue/status`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return await response.json()
  */
}
