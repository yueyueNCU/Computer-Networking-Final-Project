from typing import Optional, List, Dict, Tuple
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.services.queue_service import QueueService
from app.services.map_service import MapService
from app.domain.entities import MapEntity, QueueEntity

# --- 1. 模擬 Map Repository (餐廳資訊) ---
class MemoryMapRepository(IMapRepository):
    def get_restaurant_basic_info(self, restaurant_id: int) -> Optional[MapEntity]:
        if restaurant_id==1:
            return MapEntity(
                restaurant_id=1,
                restaurant_name="麥克小姐",
                lat= 24.968,
                lng= 21.192,
                image_url="https://example.com/burger.jpg",
                average_price= (150,300),
                specialties="義大利麵、漢堡"
            )
        elif restaurant_id==2:
            return MapEntity(
                restaurant_id=2,
                restaurant_name="歐姆萊斯",
                lat= 24.970,
                lng= 121.195,
                image_url="https://example.com/rice.jpg",
                average_price= (150,300),
                specialties="義大利麵、漢堡"
            )
        else:
            return None
        

    def get_all_restaurants(self) ->  List[MapEntity]:
        return [
            MapEntity(
                restaurant_id=1,
                restaurant_name="麥克小姐",
                lat= 24.968,
                lng= 21.192,
                image_url="https://example.com/burger.jpg",
                average_price= (150,300),
                specialties="義大利麵、漢堡"
            ),
            MapEntity(
                restaurant_id=2,
                restaurant_name="歐姆萊斯",
                lat= 24.970,
                lng= 121.195,
                image_url="https://example.com/rice.jpg",
                average_price= (150,300),
                specialties="義大利麵、漢堡"
            )
        ]
# --- 2. 模擬 Queue Repository (排隊資料) ---
class MemoryQueueRepository(IQueueRepository):
    def __init__(self):
        pass
class MemoryQueueRuntimeRepository(IQueueRuntimeRepository):
    def __init__(self):
        pass
# --- 4. 組合包：產生 Fake Service 的工廠函數 ---
# 這些變數放在全域，確保所有 Request 共用同一份記憶體資料
_mock_map_repo = MemoryMapRepository()
_mock_queue_repo = MemoryQueueRepository()
_mock_runtime_repo = MemoryQueueRuntimeRepository()

def get_memory_queue_service() -> QueueService:
    """
    這就是我們要在 main.py 裡用來替換真實依賴的函數
    """
    return QueueService(
        queue_repo=_mock_queue_repo,
        queue_runtime_repo=_mock_runtime_repo,
        map_repo=_mock_map_repo
    )
def get_memory_map_service() -> MapService:
    """
    這就是我們要在 main.py 裡用來替換真實依賴的函數
    """
    return MapService(
        map_repo=_mock_map_repo,
        queue_repo=_mock_queue_repo,
        queue_runtime_repo=_mock_runtime_repo
    )