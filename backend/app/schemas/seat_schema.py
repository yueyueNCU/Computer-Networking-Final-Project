from pydantic import BaseModel, Field
from typing import List, Literal, Union
from datetime import datetime

# 店家座位服務 (/api/restaurants/{restaurant_id}/seats) 

SeatStatus = Literal["empty", "eating"]

class SeatDetail(BaseModel):
    """座位/桌子資訊"""
    table_id: int
    label: str                      # 桌號顯示文字
    x: int                          # CSS Grid 的 Column 位置
    y: int                          # CSS Grid 的 Row 位置
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
    table_id: int 
    new_status: SeatStatus
    updated_at: datetime # Pydantic 可以自動將 ISO 8601 字串解析為 datetime 物件