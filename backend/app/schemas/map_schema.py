from pydantic import BaseModel
from typing import List

class RestaurantItem(BaseModel):
    """GET /api/restaurants 回應中的單一餐廳物件"""
    restaurant_id: int
    restaurant_name: str
    lat: float
    lng: float
    image_url: str
    average_price: str
    specialties: str
    status: str  # "green", "red", "yellow"

class RestaurantListResponse(BaseModel):
    restaurants: List[RestaurantItem]