from abc import ABC, abstractmethod
from typing import Optional,Tuple
from app.schemas.queue_schema import QueueStatusResponse,JoinQueueResponse

class IQueueService(ABC):
    @abstractmethod
    def join_restaurant_waiting_queue(self, restaurant_id: int, user_id: int) -> JoinQueueResponse:
        """
        使用者加入排隊
        Raises:
            QueueAlreadyJoinedError: 使用者已經在其他隊伍中
            RestaurantNotFoundError: 餐廳不存在
        """
        pass
    @abstractmethod
    def leave_restaurant_waiting_queue(self, restaurant_id: int, user_id: int) -> None:
        """
        使用者離開排隊
        Raises:
            NotInQueueError: 使用者不在排隊中
            RestaurantNotFoundError: 餐廳不存在
        """
        pass
    @abstractmethod
    def get_queue_status(self, restaurant_id: int) -> QueueStatusResponse:
        """
        取得餐廳排隊狀態
        Raises:
            RestaurantNotFoundError: 餐廳不存在
        """
        pass

class IQueueRepository(ABC):
    @abstractmethod
    def add_to_queue(self, restaurant_id: int, user_id: int, ticket_number: int) -> bool:
        """
        將使用者加入排隊列表。
        Returns:
            bool: 成功加入排隊與否
        """
        pass

    @abstractmethod
    def remove_from_queue(self, restaurant_id: int, user_id: int) -> bool:
        """
        將使用者從排隊中移除 
        Returns:
            bool: 是否更新成功
        """
        pass

    # --- 2. 查詢狀態 (對應 Validation) ---

    @abstractmethod
    def get_user_current_queue(self, user_id: int) -> Optional[int]:
        """
        檢查使用者目前是否正在排任何隊伍。
        用於 Service 檢查 QueueAlreadyJoinedError。
        Returns:
            Optional[int]: 若有排隊則回傳 restaurant_id，否則回傳 None
        """
        pass

"""
以下是Queue表格，可參考

queue_id | restaurant_id | user_id | ticket_number
1        | 2             | 25      | 15
2        | 2             | 28      | 16
3        | 3             | 28      | 6
"""


class IQueueRuntimeRepository(ABC):
    @abstractmethod
    def get_current_ticket_number(self, restaurant_id: int) -> int:
        """
        取得目前叫號叫到幾號 (用來顯示目前進度)。
        """
        pass
    @abstractmethod
    def get_next_ticket_number(self, restaurant_id: int) -> int:
        """
        取得目前號碼牌發到幾號 (排隊人要看)。
        """
        pass
    @abstractmethod
    def increment_next_ticket_number(self, restaurant_id: int) -> int:
        """
        讓下一的拿到票的數字 + 1
        """
        pass
    @abstractmethod
    def get_metrics(self, restaurant_id: int) -> Tuple[int , int]: #[average_wait_time, table_number]
        """
        取得平均等待時間及餐廳座位數
        """
        pass
    @abstractmethod
    def get_waiting_count(self, restaurant_id: int) -> int:
        """
        取得目前該餐廳的等待組數 (N)。
        """
        pass
    @abstractmethod
    def increment_waiting_count(self, restaurant_id: int) -> int:
        """
        讓等待人數 + 1
        """
        pass
    @abstractmethod
    def decrement_waiting_count(self, restaurant_id: int) -> int:
        """
        讓等待人數 - 1
        """
        pass

"""
以下是QueueRuntion表格，可參考
metrics 是 [average_wait_time, table_number]

restaurant_id | current_number | next_ticket_number | metrics
2             | 14             | 17                 | [8, 6]
3             | 5              | 7                  | [10, 5]
"""