from typing import Optional, List, Dict, Tuple
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.services.queue_service import QueueService

# --- 1. 模擬 Map Repository (餐廳資訊) ---
class MemoryMapRepository(IMapRepository):
    def check_exists(self, restaurant_id: int) -> bool:
        return restaurant_id < 100

    def get_restaurant_basic_info(self, restaurant_id: int) -> dict:
        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": f"測試餐廳 No.{restaurant_id}",
            "address": "虛擬記憶體路 123 號"
        }

    def get_all_restaurants(self) -> list:
        return [
            {
                "restaurant_id": 2,
                "restaurant_name": "麥克小姐",
                "lat": 24.968,
                "lng": 121.192,
                "image_url": "https://example.com/burger.jpg",
                "average_price": "150-300",
                "specialties": "義大利麵、漢堡",
                "status": "green"
            },
            {
                "restaurant_id": 3,
                "restaurant_name": "歐姆萊斯",
                "lat": 24.970,
                "lng": 121.195,
                "image_url": "https://example.com/rice.jpg",
                "average_price": "80-150",
                "specialties": "咖哩、豬排飯",
                "status": "red"
            }
        ]

# --- 2. 模擬 Queue Repository (排隊資料) ---
class MemoryQueueRepository(IQueueRepository):
    def __init__(self):
        # key: restaurant_id, value: list of user_ids
        self.queues: Dict[int, List[int]] = {}
        # key: user_id, value: restaurant_id (反向查詢)
        self.user_status: Dict[int, int] = {}

    def add_to_queue(self, restaurant_id: int, user_id: int, ticket_number: int) -> bool:
        """
        修正 1: 補上 ticket_number 參數以符合介面定義
        雖然記憶體模擬版可能暫時用不到 ticket_number (因為是用 list 順序)，
        但必須維持介面一致性。
        """
        if restaurant_id not in self.queues:
            self.queues[restaurant_id] = []
        self.queues[restaurant_id].append(user_id)
        self.user_status[user_id] = restaurant_id
        return True

    def get_user_current_queue(self, user_id: int) -> Optional[int]:
        return self.user_status.get(user_id)

    def get_total_waiting(self, restaurant_id: int) -> int:
        return len(self.queues.get(restaurant_id, []))

    def remove_from_queue(self, restaurant_id: int, user_id: int) -> bool:
        """
        修正: 回傳型別改為 bool 以符合介面定義
        """
        if restaurant_id in self.queues and user_id in self.queues[restaurant_id]:
            self.queues[restaurant_id].remove(user_id)
        if user_id in self.user_status:
            del self.user_status[user_id]
        return True
            
    def get_next_queue_to_call(self, restaurant_id: int) -> Optional[int]:
        # 簡單模擬：這裡回傳的是排在第一位的 user_id (或對應的號碼邏輯)
        # 實際依您的業務邏輯調整
        queue = self.queues.get(restaurant_id, [])
        return queue[0] if queue else None

# --- 3. 模擬 Runtime Repository (號碼牌與指標) ---
class MemoryQueueRuntimeRepository(IQueueRuntimeRepository):
    def __init__(self):
        # key: restaurant_id, value: int
        self.next_numbers: Dict[int, int] = {}
        self.current_numbers: Dict[int, int] = {}

    def get_next_ticket_number(self, restaurant_id: int) -> int:
        return self.next_numbers.get(restaurant_id, 1)

    def increment_next_ticket_number(self, restaurant_id: int):
        current = self.next_numbers.get(restaurant_id, 1)
        self.next_numbers[restaurant_id] = current + 1

    def get_current_ticket_number(self, restaurant_id: int) -> int:
        # 這裡模擬目前叫到的號碼，預設比下一張號碼小 5 號 (製造排隊感)
        next_num = self.next_numbers.get(restaurant_id, 1)
        return max(1, next_num - 5)

    def get_metrics(self, restaurant_id: int) -> Tuple[int, int]:
        # 固定回傳 (平均用餐時間 15 分鐘, 總座位 10)
        return (15, 10)

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