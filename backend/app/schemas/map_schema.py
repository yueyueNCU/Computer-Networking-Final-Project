from pydantic import BaseModel
from typing import Tuple


class RestaurantItem(BaseModel):
    """GET /api/restaurants 回應中的單一餐廳物件"""
    restaurant_id: int
    restaurant_name: str
    lat: float
    lng: float
    image_url: str
    average_price: Tuple[int, int]
    specialties: str
    status: str  # "green", "red", "yellow"