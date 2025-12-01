from pydantic import BaseModel, Field
from typing import List, Literal, Union
from datetime import datetime

# --- 1. 餐廳列表服務 (/api/restaurants) ---

# 使用 Literal 來限制 status 只能是特定字符串之一
RestaurantStatus = Literal["green", "red", "yellow"] 

class RestaurantItem(BaseModel):
    """GET /api/restaurants 回應中的單一餐廳物件"""
    restaurant_id: int
    restaurant_name: str
    lat: float
    lng: float
    image_url: str
    average_price: str
    specialties: str
    status: RestaurantStatus

# 回應是一個包含多個 RestaurantItem 的列表
RestaurantListResponse = List[RestaurantItem]


# --- 2. 店家座位服務 (/api/restaurants/{restaurant_id}/seats) ---

SeatStatus = Literal["empty", "eating"]

class SeatDetail(BaseModel):
    """座位/桌子資訊"""
    table_id: int
    label: str = Field(..., description="桌號顯示文字")
    x: int = Field(..., description="CSS Grid 的 Column 位置")
    y: int = Field(..., description="CSS Grid 的 Row 位置")
    status: SeatStatus

class RestaurantSeatsResponse(BaseModel):
    """GET /api/restaurants/{restaurant_id}/seats 回應"""
    restaurant_id: int
    seats: List[SeatDetail]


class UpdateTableStatusRequest(BaseModel):
    """POST /api/tables/{table_id}/status 請求體"""
    action: SeatStatus # action 只能是 "eating" 或 "empty"

class UpdateTableStatusResponse(BaseModel):
    """POST /api/tables/{table_id}/status 回應"""
    success: bool
    table_id: int 
    new_status: SeatStatus
    updated_at: datetime # Pydantic 可以自動將 ISO 8601 字串解析為 datetime 物件


# --- 3. 排隊服務 ---

class JoinQueueRequest(BaseModel):
    """POST /api/restaurants/{restaurant_id}/queue 請求體"""
    user_id: int

class JoinQueueResponse(BaseModel):
    """POST /api/restaurants/{restaurant_id}/queue 回應"""
    ticket_number: int
    people_ahead: int = Field(..., description="前面還有幾組人 (N)")
    estimated_wait_time: int = Field(..., description="根據公式算出來的時間 (分鐘)")

class QueueStatusResponse(BaseModel):
    """GET /api/restaurants/{restaurant_id}/queue/status 回應"""
    restaurant_id: int 
    restaurant_name: str
    current_number: int
    total_waiting: int = Field(..., description="總排隊組數 (N)")
    avg_wait_time: int