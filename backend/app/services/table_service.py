from datetime import datetime
from fastapi import HTTPException
from app.repositories.fake_all_repo import _mock_table_repo
from app.schemas.table_schema import UpdateTableStatusRequest, UpdateTableStatusResponse

class TableService:
    def __init__(self, repo=_mock_table_repo):
        self.repo = repo

    def get_restaurant_seats(self, restaurant_id: int):
        layout = self.repo.get_layout(restaurant_id)
        if not layout:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return layout

    def update_table_status(self, table_id: int, request: UpdateTableStatusRequest):
        # 1. 找桌子
        seat = self.repo.get_seat_by_id(table_id)
        
        # 錯誤情境 1: Table 不存在 -> 404
        if not seat:
            raise HTTPException(
                status_code=404,
                detail={"code": "TABLE_NOT_FOUND", "message": "Table does not exist."}
            )

        # 錯誤情境 2: 狀態相同 (重複入座或重複離座) -> 400
        if seat.status == request.action:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "TABLE_INVALID_ACTION", 
                    "message": f"Cannot set a table that is already {seat.status}."
                }
            )

        # 錯誤情境 3: 驗證排隊號碼 (User is not in queue)
        # 這裡暫時模擬：如果 action 是 eating 且 票號是 999 則報錯
        if request.action == "eating" and request.queue_ticket_number == 999:
             raise HTTPException(
                status_code=400,
                detail={"code": "NOT_IN_QUEUE", "message": "User is not in queue."}
            )

        # 通過檢查，更新狀態
        seat.status = request.action
        
        return UpdateTableStatusResponse(
            table_id=seat.table_id,
            new_status=seat.status,
            updated_at=datetime.now()
        )