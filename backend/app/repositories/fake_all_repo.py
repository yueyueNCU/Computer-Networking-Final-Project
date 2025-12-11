from typing import Optional, List, Dict, Tuple
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.services.queue_service import QueueService
from app.services.map_service import MapService
from app.domain.entities import MapEntity, QueueEntity
from app.domain.value_objects import RestaurantMetrics
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
        # 使用 List 來模擬資料庫的 Table
        self._queue_data: List[QueueEntity] = []
        # 模擬 Auto Increment 的 Primary Key
        self._id_counter = 1

    def add_to_queue(self, restaurant_id: int, user_id: int, ticket_number: int) -> bool:
        """
        模擬 INSERT INTO queue ...
        """
        new_entry = QueueEntity(
            queue_id=self._id_counter,
            restaurant_id=restaurant_id,
            user_id=user_id,
            ticket_number=ticket_number
        )
        self._queue_data.append(new_entry)
        self._id_counter += 1
        return True

    def remove_from_queue(self, restaurant_id: int, user_id: int) -> bool:
        """
        模擬 DELETE FROM queue WHERE ...
        """
        original_count = len(self._queue_data)
        # 過濾掉符合條件的項目 (相當於刪除)
        self._queue_data = [
            q for q in self._queue_data 
            if not (q.restaurant_id == restaurant_id and q.user_id == user_id)
        ]
        # 如果長度有變少，代表刪除成功
        return len(self._queue_data) < original_count

    def get_user_current_queue(self, user_id: int) -> Optional[QueueEntity]:
        """
        模擬 SELECT * FROM queue WHERE user_id = ?
        """
        for q in self._queue_data:
            if q.user_id == user_id:
                return q
        return None

    def get_total_waiting(self, restaurant_id: int) -> int:
        """
        模擬 SELECT COUNT(*) ...
        """
        count = 0
        for q in self._queue_data:
            if q.restaurant_id == restaurant_id:
                count += 1
        return count

    def get_next_queue_to_call(self, restaurant_id: int) -> Optional[int]:
        """
        模擬 SELECT MIN(ticket_number) ...
        """
        tickets = [
            q.ticket_number 
            for q in self._queue_data 
            if q.restaurant_id == restaurant_id
        ]
        if not tickets:
            return None
        return min(tickets)

# --- 3. 模擬 Queue Runtime Repository (叫號狀態) ---
class MemoryQueueRuntimeRepository(IQueueRuntimeRepository):
    def __init__(self):
        # 使用 Dict 模擬不同餐廳的狀態表
        # Key: restaurant_id
        # Value: 包含 current_ticket_number, next_ticket_number, metrics 的字典
        self._runtime_data = {
            1: {
                "current_ticket_number": 0,
                "next_ticket_number": 1,
                "metrics": RestaurantMetrics(average_wait_time=10, table_number=5)
            },
            2: {
                "current_ticket_number": 14,
                "next_ticket_number": 17,
                "metrics": RestaurantMetrics(average_wait_time=8, table_number=6)
            }
        }

    def _ensure_restaurant_exists(self, restaurant_id: int):
        """輔助函數：如果請求的餐廳不在記憶體中，初始化一組預設值"""
        if restaurant_id not in self._runtime_data:
            self._runtime_data[restaurant_id] = {
                "current_ticket_number": 0,
                "next_ticket_number": 1,
                "metrics": RestaurantMetrics(average_wait_time=15, table_number=4)
            }

    def get_current_ticket_number(self, restaurant_id: int) -> int:
        self._ensure_restaurant_exists(restaurant_id)
        return self._runtime_data[restaurant_id]["current_ticket_number"]

    def get_next_ticket_number(self, restaurant_id: int) -> int:
        self._ensure_restaurant_exists(restaurant_id)
        return self._runtime_data[restaurant_id]["next_ticket_number"]

    def increment_next_ticket_number(self, restaurant_id: int) -> None:
        self._ensure_restaurant_exists(restaurant_id)
        self._runtime_data[restaurant_id]["next_ticket_number"] += 1

    def get_metrics(self, restaurant_id: int) -> RestaurantMetrics:
        self._ensure_restaurant_exists(restaurant_id)
        return self._runtime_data[restaurant_id]["metrics"]
    
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