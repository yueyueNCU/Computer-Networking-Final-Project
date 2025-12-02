from abc import ABC, abstractmethod
from app.schemas.map_schema import RestaurantItem  
from typing import List, Optional

class IMapService(ABC):
    @abstractmethod
    def get_nearby_markers(self, lat:float, lng:float, radius:float) -> List[RestaurantItem]:
        """取得半徑內的餐廳"""
        pass


class IMapRepository(ABC):
    @abstractmethod
    def find_restaurant_in_range(self, lat:float, lng:float, radius:float) -> List[dict]:
        pass

