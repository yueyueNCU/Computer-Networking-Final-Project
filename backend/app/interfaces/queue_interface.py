from abc import ABC, abstractmethod
from typing import Optional,Tuple
from app.schemas.queue_schema import QueueStatusResponse,JoinQueueResponse, QueueNextResponse

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
            讓使用者 取得餐廳排隊狀態
            Raises:
                RestaurantNotFoundError: 餐廳不存在
        """
        pass
    @abstractmethod
    def get_queue_next(self, restaurant_id: int) -> QueueNextResponse:
        """
            讓餐廳方 取得餐廳排隊狀態
            Raises:
                RestaurantNotFoundError: 餐廳不存在
        """
        pass

class IQueueRepository(ABC):
    @abstractmethod
    def add_to_queue(self, restaurant_id: int, user_id: int, ticket_number: int) -> bool:
        """
            將使用者加入排隊列表。

            SQL 指令:
                INSERT INTO queue (restaurant_id, user_id, ticket_number)
                VALUES (?, ?, ?);

            Returns:
                bool: 成功加入排隊與否
        """
        pass

    @abstractmethod
    def remove_from_queue(self, restaurant_id: int, user_id: int) -> bool:
        """
            將使用者從排隊中移除。

            SQL 指令:
                DELETE FROM queue
                WHERE restaurant_id = ?
                AND user_id = ?;

            Returns:
                bool: 是否刪除成功 (影響到 1 row 以上)
        """
        pass

    @abstractmethod
    def get_user_current_queue(self, user_id: int) -> Optional[int]:
        """
            檢查使用者目前是否正在排任何隊伍。
            若有排隊，回傳 restaurant_id，否則回傳 None。

            SQL 指令:
                SELECT restaurant_id
                FROM queue
                WHERE user_id = ?
                LIMIT 1;

            Returns:
                Optional[int]: 若有排隊則回傳 restaurant_id，否則 None
        """
        pass
    @abstractmethod
    def get_total_waiting(self, restaurant_id: int) -> int:
        """
            取得目前該餐廳的等待組數 (N)。

            SQL 指令:
                SELECT COUNT(*) AS total
                FROM queue
                WHERE restaurant_id = ?;

            Returns:
                int: 排隊中的總組數
        """
        pass
    @abstractmethod
    def get_next_queue_to_call(self, restaurant_id: int) -> Optional[int]:
        """
            取得該餐廳排隊隊伍中下一個叫號。
            下一個叫號 = 該餐廳 queue 中 ticket_number 最小值。

            SQL 指令:
                SELECT MIN(ticket_number) AS next_queue_to_call
                FROM queue
                WHERE restaurant_id = ?;

            若結果為 NULL，表示目前該餐廳沒有排隊的人。

            Returns:
                Optional[int]: 
                    - 若有排隊 → 回傳最小 ticket_number
                    - 若無排隊 → 回傳 None
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
        SQL指令:
            SELECT current_ticket_number
            FROM queue_runtime
            WHERE restaurant_id = ?;
        """
        pass
    @abstractmethod
    def get_next_ticket_number(self, restaurant_id: int) -> int:
        """
        取得目前號碼牌發到幾號 (排隊人要看)。
        SQL指令:
            SELECT next_ticket_number
            FROM queue_runtime
            WHERE restaurant_id = ?;
        """
        pass
    @abstractmethod
    def increment_next_ticket_number(self, restaurant_id: int) -> None:
        """
        讓下一的拿到票的數字 + 1
        SQL指令:
            UPDATE queue_runtime
            SET next_ticket_number = next_ticket_number + 1
            WHERE restaurant_id = ?;    
        """
        pass
    @abstractmethod
    def get_metrics(self, restaurant_id: int) -> Tuple[int , int]: #[average_wait_time, table_number]
        """
        取得平均等待時間及餐廳座位數
        SQL指令:
            SELECT
                JSON_EXTRACT(metrics, '$[0]') AS average_wait_time,
                JSON_EXTRACT(metrics, '$[1]') AS table_number
            FROM queue_runtime
            WHERE restaurant_id = ?;
        """
        pass

"""
以下是QueueRuntion表格，可參考
metrics 是 [average_wait_time, table_number]
注意這裡的next_ticket是下一個分配的號碼，並非下一個排隊中的叫號

restaurant_id | current_ticket_number | next_ticket_number | metrics
2             | 14             | 17                 | [8, 6]
3             | 5              | 7                  | [10, 5]
"""