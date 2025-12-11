from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

# 店家座位服務 (/api/restaurants/{restaurant_id}/seats) 

TableStatus = Literal["empty", "eating"]

class TableDetail(BaseModel):
    """座位/桌子資訊"""
    table_id: int
    label: str                      # 桌號顯示文字
    x: int                          # CSS Grid 的 Column 位置
    y: int                          # CSS Grid 的 Row 位置
    status: TableStatus

class RestaurantSeatsResponse(BaseModel):
    """GET /api/restaurants/{restaurant_id}/table 回應"""
    restaurant_id: int
    restaurant_name: str
    seats: List[TableDetail]


class UpdateTableStatusRequest(BaseModel):
    """POST /api/tables/{table_id}/status 請求體"""
    action: TableStatus # action 只能是 "eating" 或 "empty"
    queue_ticket_number: int #要帶位的號碼
    
class UpdateTableStatusResponse(BaseModel):
    """POST /api/tables/{table_id}/status 回應"""
    table_id: int 
    new_status: TableStatus
    updated_at: datetime # Pydantic 可以自動將 ISO 8601 字串解析為 datetime 物件