from typing import List
from app.interfaces.map_interface import IMapRepository, IMapService
from app.schemas.map_schema import RestaurantItem
from app.interfaces.queue_interface import IQueueRepository,IQueueRuntimeRepository

class MapService(IMapService):
    def __init__(self, map_repo: IMapRepository,queue_repo: IQueueRepository, queue_runtime_repo: IQueueRuntimeRepository):
        # 依賴注入：這裡只認得 IMapRepository 定義過的 function
        self.map_repo = map_repo
        self.queue_repo = queue_repo
        self.queue_runtime_repo = queue_runtime_repo

    def get_restaurants(self) -> List[RestaurantItem]:
        # 1. 從 Repo 撈取原始資料 (List[MapEntity])
        restaurants = self.map_repo.get_all_restaurants()
        
        # 3. 資料轉換 (List[MapEntity] -> List[RestaurantItem])
        result = []
        for item in restaurants:
            status = "green"
            total_waiting = self.queue_repo.get_total_waiting(item.restaurant_id)
            table_number = (self.queue_runtime_repo.get_metrics(item.restaurant_id)).table_number
            if table_number >= total_waiting*0.9:
                status="red"
            elif table_number >= total_waiting*0.7:
                status="yellow"
            else:
                status="green"
                

            restaurant = RestaurantItem(        
                restaurant_id=item.restaurant_id,
                restaurant_name=item.restaurant_name,
                lat=item.lat,
                lng=item.lng,
                image_url=item.image_url,
                average_price=item.average_price,
                specialties=item.specialties,
                status=status
            )
            result.append(restaurant)
            
        return result