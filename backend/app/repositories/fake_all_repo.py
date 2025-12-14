from typing import Optional, List, Dict, Tuple
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.interfaces.table_interface import ITableRepository
from app.domain.entities import MapEntity, QueueEntity, TableEntity
from app.domain.value_objects import RestaurantMetrics
from app.schemas.table_schema import RestaurantSeatsResponse, TableDetail
# --- 1. 模擬 Map Repository (餐廳資訊) ---
class MemoryMapRepository(IMapRepository):
    def get_restaurant_basic_info(self, restaurant_id: int) -> Optional[MapEntity]:
        if restaurant_id==1:
            return MapEntity(
                restaurant_id=1,
                restaurant_name="麥克小姐",
                lat= 24.963068,
                lng= 121.190522,
                image_url="https://lh3.googleusercontent.com/gps-cs-s/AG0ilSx8y-lVonUobgUnS75Yz8rUT0mRzZDS78r4zbMmmbZHQXgIw-1HfXL2p_GJRamtS7MhYJw-05yaTUhubUx43izoWW6jTH8fyahL5tsGlQsnZUe_eVqqtkc8IZmyMarMpm0K9hI_=w243-h304-n-k-no-nu",
                average_price= (150,300),
                specialties="義大利麵、漢堡"
            )
        elif restaurant_id==2:
            return MapEntity(
                restaurant_id=2,
                restaurant_name="歐姆萊斯",
                lat= 24.964267,
                lng= 121.190726,
                image_url="https://lh3.googleusercontent.com/gps-cs-s/AG0ilSw1Zrdd2LRVUmlcJC0t8oeK7W5x7s9s0zTk15nHp5rSiGuhCsloCDXgzpU3ZcHkgaRuelR1yM4KIu6BXnNaS3BmLgGavEdLW_mXYOCJ-Y_dmN7PIeLC8vVa3GZzLKq-RuF8e3lkFqqMn4Gt=s1360-w1360-h1020-rw",
                average_price= (85,165),
                specialties="咖哩、豬排飯"
            )
        elif restaurant_id==3:
            return MapEntity(
                restaurant_id=3,
                restaurant_name="香城燒臘",
                lat= 24.964879,
                lng= 121.193531,
                image_url="https://lh3.googleusercontent.com/gps-cs-s/AG0ilSw_0mtAZviH08orlPwOS9LzMfgbqvV22-6HvmS3IATLMUbBMbxkBFqSKbeZM72AKHz8VHt5eYyPqv8b6z0JiZmV4c77RRyUhTcvi7ahUcRpYOyUUfppeen9RjOlcH6r1HC5rodoewqhKxY=w408-h306-k-no",
                average_price= (80,130),
                specialties="蜜汁叉燒、燒肉、香腸"
            )
        else:
            return None
        

    def get_all_restaurants(self) ->  List[MapEntity]:
        return [
            MapEntity(
                restaurant_id=1,
                restaurant_name="麥克小姐",
                lat= 24.963068,
                lng= 121.190522,
                image_url="https://lh3.googleusercontent.com/gps-cs-s/AG0ilSx8y-lVonUobgUnS75Yz8rUT0mRzZDS78r4zbMmmbZHQXgIw-1HfXL2p_GJRamtS7MhYJw-05yaTUhubUx43izoWW6jTH8fyahL5tsGlQsnZUe_eVqqtkc8IZmyMarMpm0K9hI_=w243-h304-n-k-no-nu",
                average_price= (150,300),
                specialties="義大利麵、漢堡"
            ),
            MapEntity(
                restaurant_id=2,
                restaurant_name="歐姆萊斯",
                lat= 24.964267,
                lng= 121.190726,
                image_url="https://lh3.googleusercontent.com/gps-cs-s/AG0ilSw1Zrdd2LRVUmlcJC0t8oeK7W5x7s9s0zTk15nHp5rSiGuhCsloCDXgzpU3ZcHkgaRuelR1yM4KIu6BXnNaS3BmLgGavEdLW_mXYOCJ-Y_dmN7PIeLC8vVa3GZzLKq-RuF8e3lkFqqMn4Gt=s1360-w1360-h1020-rw",
                average_price= (85,165),
                specialties="咖哩、豬排飯"
            ),
            MapEntity(
                restaurant_id=3,
                restaurant_name="香城燒臘",
                lat= 24.964879,
                lng= 121.193531,
                image_url="https://lh3.googleusercontent.com/gps-cs-s/AG0ilSw_0mtAZviH08orlPwOS9LzMfgbqvV22-6HvmS3IATLMUbBMbxkBFqSKbeZM72AKHz8VHt5eYyPqv8b6z0JiZmV4c77RRyUhTcvi7ahUcRpYOyUUfppeen9RjOlcH6r1HC5rodoewqhKxY=w408-h306-k-no",
                average_price= (80,130),
                specialties="蜜汁叉燒、燒肉、香腸"
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
    def get_user_current_queue_by_restaurantId_and_ticketNumber(self, restaurant_id: int, ticket_number: int) -> Optional[QueueEntity]:
        """
        模擬 SELECT * FROM queue WHERE restaurant_id = ? AND ticket_number = ?
        """
        for q in self._queue_data:
            if q.restaurant_id == restaurant_id and q.ticket_number == ticket_number:
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
    def get_people_ahead(self, restaurant_id: int, user_id: int) -> int:
        """
        取得排在特定使用者前面的人數。
        
        SQL 邏輯 (概念):
            SELECT COUNT(*) 
            FROM queue 
            WHERE restaurant_id = ? 
              AND ticket_number < (
                  SELECT ticket_number 
                  FROM queue 
                  WHERE restaurant_id = ? AND user_id = ?
              )
        """
        # 1. 先找到該使用者的 ticket_number
        target_ticket = None
        for q in self._queue_data:
            if q.restaurant_id == restaurant_id and q.user_id == user_id:
                target_ticket = q.ticket_number
                break
        
        # 如果使用者不在該餐廳的隊伍中，回傳 0 (或是您可以選擇拋出 NotInQueueError)
        if target_ticket is None:
            return 0

        # 2. 計算同一間餐廳中，ticket_number 小於 target_ticket 的人數
        count = 0
        for q in self._queue_data:
            if q.restaurant_id == restaurant_id and q.ticket_number < target_ticket:
                count += 1
        
        return count
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
            },
            3: {
                "current_ticket_number": 5,
                "next_ticket_number": 8,
                "metrics": RestaurantMetrics(average_wait_time=100, table_number=12)
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

    def set_current_ticket_number(self, restaurant_id: int, ticket_number: int) -> None:
        self._ensure_restaurant_exists(restaurant_id)
        self._runtime_data[restaurant_id]["current_ticket_number"] = ticket_number

    def get_next_ticket_number(self, restaurant_id: int) -> int:
        self._ensure_restaurant_exists(restaurant_id)
        return self._runtime_data[restaurant_id]["next_ticket_number"]

    def increment_next_ticket_number(self, restaurant_id: int) -> None:
        self._ensure_restaurant_exists(restaurant_id)
        self._runtime_data[restaurant_id]["next_ticket_number"] += 1

    def get_metrics(self, restaurant_id: int) -> RestaurantMetrics:
        self._ensure_restaurant_exists(restaurant_id)
        return self._runtime_data[restaurant_id]["metrics"]
    
class MemoryTableRepository(ITableRepository):
    def __init__(self):
        # 模擬資料庫
        # key: table_id, value: TableEntity
        self._tables: Dict[int, TableEntity] = {
            # 餐廳 1 的桌子
            101: TableEntity(table_id=101, restaurant_id=1, label="A1", x=1, y=1, status="eating"),
            102: TableEntity(table_id=102, restaurant_id=1, label="A2", x=2, y=1, status="empty"),
            103: TableEntity(table_id=103, restaurant_id=1, label="A3", x=3, y=1, status="eating"),
            104: TableEntity(table_id=104, restaurant_id=1, label="A4", x=1, y=2, status="eating"),
            105: TableEntity(table_id=105, restaurant_id=1, label="A5", x=2, y=2, status="eating"),
            
            # 餐廳 2 的桌子
            201: TableEntity(table_id=201, restaurant_id=2, label="VIP1", x=1, y=1, status="empty"),
            202: TableEntity(table_id=202, restaurant_id=2, label="VIP2", x=3, y=1, status="eating"),
            203: TableEntity(table_id=203, restaurant_id=2, label="VIP3", x=5, y=1, status="empty"),
            204: TableEntity(table_id=204, restaurant_id=2, label="VIP4", x=1, y=3, status="eating"),
            205: TableEntity(table_id=205, restaurant_id=2, label="VIP5", x=3, y=3, status="eating"),
            206: TableEntity(table_id=206, restaurant_id=2, label="VIP6", x=5, y=3, status="eating"),

            # 餐廳 3 的桌子
            301: TableEntity(table_id=301, restaurant_id=3, label="1桌", x=1, y=1, status="empty"),
            302: TableEntity(table_id=302, restaurant_id=3, label="2桌", x=3, y=1, status="eating"),
            303: TableEntity(table_id=303, restaurant_id=3, label="3桌", x=5, y=1, status="empty"),
            304: TableEntity(table_id=304, restaurant_id=3, label="4桌", x=7, y=1, status="eating"),
            305: TableEntity(table_id=305, restaurant_id=3, label="5桌", x=1, y=3, status="empty"),
            306: TableEntity(table_id=306, restaurant_id=3, label="6桌", x=3, y=3, status="empty"),
            307: TableEntity(table_id=307, restaurant_id=3, label="7桌", x=5, y=3, status="empty"),
            308: TableEntity(table_id=308, restaurant_id=3, label="8桌", x=7, y=3, status="empty"),
            309: TableEntity(table_id=309, restaurant_id=3, label="9桌", x=1, y=5, status="empty"),
            310: TableEntity(table_id=310, restaurant_id=3, label="10桌", x=3, y=5, status="eating"),
            311: TableEntity(table_id=311, restaurant_id=3, label="11桌", x=5, y=6, status="empty"),
            312: TableEntity(table_id=312, restaurant_id=3, label="12桌", x=7, y=6, status="empty"),
        }

    def get_tables_by_restaurant(self, restaurant_id: int) -> List[TableEntity]:
        """
        取得特定餐廳的所有座位資訊。
        """
        # 回傳 TableEntity 的列表
        return [t for t in self._tables.values() if t.restaurant_id == restaurant_id]

    def get_table_by_id(self, table_id: int) -> Optional[TableEntity]:
        """
        透過 ID 取得單一座位資訊。
        """
        table = self._tables.get(table_id)
        if table:
            # 回傳副本避免直接修改
            return TableEntity(
                table_id=table.table_id,
                restaurant_id=table.restaurant_id,
                label=table.label,
                x=table.x,
                y=table.y,
                status=table.status
            )
        return None

    def update_status(self, table_id: int, new_table_status: str, queue_ticket_number: int) -> bool:
        """
        更新座位狀態。
        """
        if table_id in self._tables:
            self._tables[table_id].status = new_table_status
            return True
        return False
    def get_restaurant_remaining_table(self, restaurant_id: int) -> int:
        count = 0
        for table in self._tables.values():
            if table.restaurant_id == restaurant_id and table.status == "empty":
                count += 1
        return count
# --- 4. 組合包：產生 Fake Service 的工廠函數 ---
# 這些變數放在全域，確保所有 Request 共用同一份記憶體資料
_mock_map_repo = MemoryMapRepository()
_mock_queue_repo = MemoryQueueRepository()
_mock_runtime_repo = MemoryQueueRuntimeRepository()
_mock_table_repo = MemoryTableRepository()

def get_memory_queue_service():
    """
    這就是我們要在 main.py 裡用來替換真實依賴的函數
    """
    from app.services.queue_service import QueueService
    return QueueService(
        queue_repo=_mock_queue_repo,
        queue_runtime_repo=_mock_runtime_repo,
        map_repo=_mock_map_repo
    )
def get_memory_map_service():
    from app.services.map_service import MapService
    """
    這就是我們要在 main.py 裡用來替換真實依賴的函數
    """
    return MapService(
        map_repo=_mock_map_repo,
        table_repo=_mock_table_repo,
        queue_repo=_mock_queue_repo,
        queue_runtime_repo=_mock_runtime_repo
    )

def get_memory_table_service():
    from app.services.table_service import TableService
    return TableService(
        table_repo=_mock_table_repo, 
        map_repo=_mock_map_repo, 
        queue_repo=_mock_queue_repo, 
        queue_runtime_repo=_mock_runtime_repo
    )