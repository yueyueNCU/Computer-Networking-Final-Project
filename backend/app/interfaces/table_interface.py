from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from app.schemas.table_schema import RestaurantSeatsResponse, UpdateTableStatusResponse, UpdateTableStatusRequest

class ITableService(ABC):
    @abstractmethod
    def get_restaurant_seats(self, restaurant_id: int) -> RestaurantSeatsResponse:
        """
        取得特定餐廳的座位表 (Layout)
        
        Raises:
            RestaurantNotFoundError: 餐廳不存在
        """
        pass

    @abstractmethod
    def update_table_status(self, table_id: int, request: UpdateTableStatusRequest) -> UpdateTableStatusResponse:
        """
        更新座位狀態 (入座/離座)
        
        Raises:
            TableNotFoundError: 桌子不存在 (404)
            TableInvalidActionError: 狀態重複 (400)
            NotInQueueError: 使用者不在排隊中 (400)
        """
        pass


class ITableRepository(ABC):
    @abstractmethod
    def get_tables_by_restaurant(self, restaurant_id: int) -> List[Dict]:
        """
        取得特定餐廳的所有座位資訊。

        SQL 指令:
            SELECT table_id, label, x, y, status
            FROM seat
            WHERE restaurant_id = ?;

        Returns:
            List[Dict]: 包含該餐廳所有座位資料的列表
        """
        pass

    @abstractmethod
    def get_table_by_id(self, table_id: int) -> Optional[Dict]:
        """
        透過 ID 取得單一座位資訊。

        SQL 指令:
            SELECT *
            FROM seat
            WHERE table_id = ?;

        Returns:
            Optional[Dict]: 若存在回傳座位資料(包含 status, restaurant_id)，否則 None
        """
        pass

    @abstractmethod
    def update_status(self, table_id: int, new_status: str) -> Dict:
        """
        更新座位狀態。

        SQL 指令:
            UPDATE seat
            SET status = ?
            WHERE table_id = ?;
        
        (注意：通常會再執行一次 SELECT 回傳更新後的資料)

        Returns:
            Dict: 更新後的座位資料
        """
        pass

"""
以下是Seat表格，可參考

table_id | restaurant_id | label | x | y | status
5        | 2             | 1桌   | 1 | 1 | empty
6        | 3             | 1桌   | 1 | 2 | eating
7        | 2             | 5桌   | 1 | 5 | eating
8        | 3             | 2桌   | 1 | 4 | empty
"""