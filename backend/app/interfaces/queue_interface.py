from abc import ABC, abstractmethod
from typing import Optional,Tuple
from app.schemas.queue_schema import QueueStatusResponse,JoinQueueResponse, QueueNextResponse, UserQueueStatusResponse
from app.domain.entities import QueueEntity
from app.domain.value_objects import RestaurantMetrics

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
    @abstractmethod
    def get_user_queue_status(self, user_id: int) -> UserQueueStatusResponse:
        """
            讓已經排隊的人取得排隊狀況
            Raises:
                NotInQueueError: 使用者不在排隊中
        """

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
    def get_user_current_queue(self, user_id: int) -> Optional[QueueEntity]:
        """
            檢查使用者目前是否正在排任何隊伍。

            SQL 指令:
                SELECT *
                FROM queue
                WHERE user_id = ?;

            Returns:
                Optional[QueueEntity]: 
                    - 若使用者在排隊中，回傳 QueueEntity 物件 
                    - 若使用者未排隊，回傳 None
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
    @abstractmethod
    def get_people_ahead(self, restaurant_id: int, user_id: int) -> int:
        """
            取得特定使用者在該餐廳排隊隊伍中前面還有多少人。
            
            前面的人數 = 該使用者在隊伍中的順位 (Row Number) 減去 1。
            順位計算規則：根據 `restaurant_id` 分區，並按照 `ticket_number` 遞增排序。

            SQL 指令:
                WITH UserRank AS (
                    -- 1. 計算所有人在各自餐廳隊伍中的順序 (row_num)
                    SELECT
                        user_id,
                        restaurant_id,
                        ticket_number,
                        ROW_NUMBER() OVER (
                            PARTITION BY restaurant_id
                            ORDER BY ticket_number ASC
                        ) as row_num
                    FROM
                        queue
                )
                -- 2. 查詢特定使用者 (user_id = ?) 和餐廳 (restaurant_id = ?) 的順序，並計算前面人數
                SELECT
                    (row_num - 1) AS people_ahead
                FROM
                    UserRank
                WHERE
                    user_id = ? AND restaurant_id = ?;

            若結果為空 (No rows returned)，表示該使用者不在該餐廳的排隊隊伍中。
            
            Returns:
                Optional[int]: 
                    - 若使用者在隊伍中 → 回傳前面排隊的人數 (int >= 0)
                    - 若使用者不在隊伍中 → 回傳 None (或空集/No rows returned)
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
    def get_metrics(self, restaurant_id: int) -> RestaurantMetrics: #[average_wait_time, table_number]
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