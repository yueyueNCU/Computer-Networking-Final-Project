from typing import List
from app.interface.map_interface import IMapRepository, IMapService
from app.interface.queue_interface import IQueueRepository
from app.schemas.map_schema import RestaurantStatus
from backend.app.schemas.map_schema import RestaurantItem

class MapService(IMapService):
    def __init__(self, map_repo: IMapRepository, queue_repo: IQueueRepository) -> None:
        self.map_repo= map_repo
        self.queue_repo= queue_repo
    def get_nearby_markers(self, lat: float, lng: float, radius: float) -> List[RestaurantItem]:

        restaurants = self.map_repo.find_restaurant_in_range(lat, lng, radius)
        markers=[]
        for r in restaurants:
            id = r["restaurant_id"]
            queue_count= self.queue_repo.get_current_restaurant_queue(id)

            status_color= "green"

            if queue_count>15:
                status_color="red"
            elif queue_count>10:
                status_color="yellow"
            
            markers.append(RestaurantItem(
                restaurant_id=r["restaurant_id"],
                restaurant_name=r["restaurant_name"],
                lat=r["lat"],
                lng=r["lng"],
                image_url=r["image_url"],
                average_price=r["average_price"],
                specialties=r["specialties"],
                status=status_color
            ))
        
                
        return markers