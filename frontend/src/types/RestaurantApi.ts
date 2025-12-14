// src/types/RestaurantApi.ts

/**
 * 餐廳基本資訊 (GET /api/restaurants)
 */
export interface RestaurantItem {
  restaurant_id: number
  restaurant_name: string
  lat: number
  lng: number
  image_url: string
  average_price: string
  specialties: string
  // 狀態顏色，用於前端顯示忙碌程度
  status: 'green' | 'red' | 'yellow'
}

// GET /api/restaurants 的回應類型
export type RestaurantListResponse = RestaurantItem[]

/**
 * 單一座位/桌子資訊
 */
export interface SeatDetail {
  table_id: number
  label: string
  // CSS Grid 座標
  x: number
  y: number
  // 座位狀態
  status: 'empty' | 'eating'
}

/**
 * 店家座位佈局與狀態 (GET /api/restaurants/{restaurant_id}/seats)
 */
export interface RestaurantSeatsResponse {
  restaurant_id: number
  seats: SeatDetail[]
}

/**
 * 更新桌子狀態的請求 (POST /api/tables/{table_id}/status)
 */
export interface UpdateTableStatusRequest {
  action: 'eating' | 'empty'
}

/**
 * 更新桌子狀態的回應 (POST /api/tables/{table_id}/status)
 */
export interface UpdateTableStatusResponse {
  success: boolean
  table_id: number
  new_status: 'eating' | 'empty'
  updated_at: string // ISO 8601 格式的日期時間字串
}

// 加入排隊的請求 (POST /api/restaurants/{restaurant_id}/queue)
export interface JoinQueueRequest {
  user_id: number
}

// 加入排隊，且成功的回應
export interface JoinQueueResponse {
  ticket_number: number
  people_ahead: number
  estimated_wait_time: number // 分鐘
}

// 排隊狀態查詢 (GET /api/restaurants/{restaurant_id}/queue/status)
export interface QueueStatusResponse {
  restaurant_id: number
  restaurant_name: string
  current_number: number // 目前叫號
  total_waiting: number // 總排隊組數 (N)
  avg_wait_time: number // 平均等待時間 (分鐘)
}

// 使用者個人的排隊狀態 (對應 /api/user/{user_id}/queue)
export interface UserQueueStatusResponse {
  restaurant_id: number
  restaurant_name: string
  ticket_number: number // 你的號碼牌
  people_ahead: number // 前面還有幾組人
  estimated_wait_time: number // 預估等待時間 (分鐘)
}
