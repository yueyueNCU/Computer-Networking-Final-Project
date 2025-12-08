import type { RestaurantListResponse, RestaurantItem } from '@/types/RestaurantApi'

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
    lat: 24.980,
    lng: 121.1880,
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
  // 模擬網路延遲 0.5 秒 (讓你有載入的感覺)
  await new Promise((resolve) => setTimeout(resolve, 500))

  // 直接回傳假資料，而不是去呼叫 API
  // 因為這是一個 async 函式，它會自動把結果包成 Promise
  return MOCK_RESTAURANTS
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
*/
