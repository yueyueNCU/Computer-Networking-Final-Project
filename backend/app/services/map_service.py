from typing import List
from app.interfaces.map_interface import IMapRepository 
from app.schemas.map_schema import RestaurantItem

class MapService:
    def __init__(self, map_repo: IMapRepository):
        # 依賴注入：這裡只認得 IMapRepository 定義過的 function
        self.map_repo = map_repo

    def get_restaurants(self) -> List[RestaurantItem]:
        """
        對應 GET /api/restaurants
        """
        # 1. 從 Repo 撈取原始資料 (List[Dict])
        raw_data = self.map_repo.get_all_restaurants()
        
        # 2. 資料轉換 (Dict -> Pydantic Schema)
        result = []
        for item in raw_data:
            restaurant = RestaurantItem(**item)
            result.append(restaurant)
            
        return result