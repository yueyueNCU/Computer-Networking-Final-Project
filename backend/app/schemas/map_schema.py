from pydantic import BaseModel, Field
from typing import List, Literal, Union
from datetime import datetime

# 餐廳列表服務 (/api/restaurants)

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