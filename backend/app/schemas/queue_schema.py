from pydantic import BaseModel, Field

# --- 3. 排隊服務 ---

class JoinQueueRequest(BaseModel):
    """POST /api/restaurants/{restaurant_id}/queue 請求體"""
    user_id: int

class JoinQueueResponse(BaseModel):
    """POST /api/restaurants/{restaurant_id}/queue 回應"""
    ticket_number: int
    people_ahead: int 
    estimated_wait_time: int 

class LeaveQueueRequest(BaseModel):
    """DELETE /api/restaurants/{restaurant_id}/queue 請求體"""
    user_id: int

class QueueStatusResponse(BaseModel):
    """GET /api/restaurants/{restaurant_id}/queue/status 回應"""
    restaurant_id: int 
    restaurant_name: str
    current_number: int
    total_waiting: int = Field(..., description="總排隊組數 (N)")
    avg_wait_time: int

class QueueNextResponse(BaseModel):
    """GET /api/restaurants/{restaurant_id}/queue/next 回應"""
    current_number: int
    next_queue_to_call: int
    total_waiting: int 

class UserQueueStatusRequest(BaseModel):
    """POST api/user/{user_id}/queue 請求體"""
    user_id: int

class UserQueueStatusResponse(BaseModel):
    "Get /api/user/{user_id}/queue 回應"
    restaurant_id: int
    restaurant_name: str
    ticket_number: int       # 你的號碼牌
    people_ahead: int        # 前面還有幾組人 (這就是 N)
    estimated_wait_time: int # 根據公式算出來的時間 (分鐘)