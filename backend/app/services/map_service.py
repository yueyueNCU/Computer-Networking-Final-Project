from typing import List
from app.interfaces.map_interface import IMapRepository 
from app.schemas.map_schema import RestaurantItem

class MapService:
    def __init__(self, repo: IMapRepository):
        self.repo = repo

    def get_restaurants(self, user_lat: float, user_lng: float) -> List[RestaurantItem]:
        raw_data = self.repo.get_nearby_restaurants(lat=user_lat, lng=user_lng, radius=1000)
        
        # 把字典 (dict) 轉換成 Pydantic 物件 (RestaurantItem)
        return [RestaurantItem(**item) for item in raw_data]