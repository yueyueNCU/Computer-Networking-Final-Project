from abc import ABC, abstractmethod
from app.schemas.map_schema import RestaurantItem  
from typing import List, Optional

class IQueueRepository(ABC):
    @abstractmethod
    def get_current_restaurant_queue(self,restaurant_id:int) -> int:
        pass
