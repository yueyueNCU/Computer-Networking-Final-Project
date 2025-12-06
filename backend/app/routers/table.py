from fastapi import APIRouter, Depends
from app.services.table_service import TableService
from app.schemas.table_schema import RestaurantSeatsResponse, UpdateTableStatusRequest, UpdateTableStatusResponse

router = APIRouter(prefix="/api", tags=["Table"])

def get_table_service():
    return TableService()

# 1. GET 取得座位表
@router.get("/restaurants/{restaurant_id}/table", response_model=RestaurantSeatsResponse)
def get_table_layout(
    restaurant_id: int, 
    service: TableService = Depends(get_table_service)
):
    return service.get_restaurant_seats(restaurant_id)

# 2. POST 更新狀態
@router.post("/tables/{table_id}/status", response_model=UpdateTableStatusResponse)
def update_table_status(
    table_id: int,
    request: UpdateTableStatusRequest,
    service: TableService = Depends(get_table_service)
):
    return service.update_table_status(table_id, request)