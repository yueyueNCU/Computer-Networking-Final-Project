from typing import List
from app.interfaces.map_interface import IMapRepository 
from app.schemas.map_schema import RestaurantItem

class MapService:
    def __init__(self, repo: IMapRepository):
        self.repo = repo
    ##  yueyue
    ##　這個function 可讀性太差了，我完全看不懂(已哭死廁所)
    ##  以及一樣問題，我們設計是GET /api/restaurants，所以不需要任何變數
    def get_restaurants(self, user_lat: float, user_lng: float) -> List[RestaurantItem]:

        ## yueyue
        ## 這邊你有沒有發現你這邊的et_nearby_restaurants 是紅字的(有錯)，這邊的self.repo會去對照IMapRepository 的定義，
        #  IMapRepository 沒有，這裡面沒辦法用
        raw_data = self.repo.get_nearby_restaurants(lat=user_lat, lng=user_lng, radius=1000)
        
        # 把字典 (dict) 轉換成 Pydantic 物件 (RestaurantItem)
        return [RestaurantItem(**item) for item in raw_data]