from datetime import datetime, timezone
from typing import List
from app.schemas.table_schema import UpdateTableStatusResponse, RestaurantSeatsResponse, TableDetail, TableStatus
from app.interfaces.table_interface import ITableService, ITableRepository
from app.interfaces.map_interface import IMapRepository
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.domain.errors import RestaurantNotFoundError, TableNotFoundError, TableInvalidActionError, NotInQueueError
class TableService(ITableService):
    def __init__(self, table_repo: ITableRepository, map_repo: IMapRepository, queue_repo: IQueueRepository, queue_runtime_repo: IQueueRuntimeRepository):
        self.table_repo = table_repo
        self.map_repo = map_repo
        self.queue_repo = queue_repo
        self.queue_runtime_repo = queue_runtime_repo

    def get_restaurant_seats(self, restaurant_id: int) -> RestaurantSeatsResponse:
        restaurant=self.map_repo.get_restaurant_basic_info(restaurant_id=restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError()
        layouts = self.table_repo.get_tables_by_restaurant(restaurant_id=restaurant_id)
        

        tables = []
        for layout in layouts:
            table = TableDetail(
                table_id=layout.table_id,
                label=layout.label,
                x=layout.x,
                y=layout.y,
                status=layout.status # type: ignore
            )
            tables.append(table)
        return RestaurantSeatsResponse(
            restaurant_id=restaurant_id,
            restaurant_name=restaurant.restaurant_name,
            seats=tables
        )
    
    def update_table_status(self, restaurant_id: int, table_id: int, new_table_status: str, queue_ticket_number: int) -> UpdateTableStatusResponse:
        # 1. 獲取桌子資訊
        table = self.table_repo.get_table_by_id(table_id=table_id)
        if table is None:
            raise TableNotFoundError()
            
        # 2. 安全性檢查：確保桌子屬於該餐廳
        if table.restaurant_id != restaurant_id:
            raise TableNotFoundError() 

        # 3. 狀態檢查
        # target_status = TableStatus(new_table_status) 
        if table.status == new_table_status:
            raise TableInvalidActionError(current_status=table.status)
        
        # 情境 A: 顧客入座 (empty -> eating)
        # 只有在「入座」時才需要處理排隊邏輯
        if new_table_status == "eating": # 建議使用 Enum: TableStatus.OCCUPIED.value
            queue_ticket = self.queue_repo.get_user_current_queue_by_restaurantId_and_ticketNumber(
                restaurant_id=restaurant_id, 
                ticket_number=queue_ticket_number
            )
            
            if queue_ticket is None:
                raise NotInQueueError()

            # 執行入座相關的排隊操作
            self.queue_repo.remove_from_queue(restaurant_id=restaurant_id, user_id=queue_ticket.user_id)
            self.queue_runtime_repo.set_current_ticket_number(restaurant_id=restaurant_id, ticket_number=queue_ticket.ticket_number)

            # 更新桌子狀態 (這裡需要帶入 ticket_number 嗎？視你的實作而定)
            self.table_repo.update_status(table_id=table_id, new_table_status=new_table_status, queue_ticket_number=queue_ticket_number)

        # 情境 B: 顧客離座/清桌 (eating -> empty)
        # 不需要檢查排隊號碼，也不需要操作 Queue Repo
        elif new_table_status == "empty":
            # 只單純更新桌子狀態
            # 這裡傳入 None 或 0 給 ticket_number，視你的 Repository 實作而定
            self.table_repo.update_status(table_id=table_id, new_table_status=new_table_status, queue_ticket_number=0)
        
        return UpdateTableStatusResponse(
            table_id=table_id,
            new_status=new_table_status, # type: ignore
            updated_at=datetime.now(timezone.utc)
        )