from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.interfaces.table_interface import ITableService
from app.schemas.table_schema import RestaurantSeatsResponse, UpdateTableStatusRequest, UpdateTableStatusResponse
from app.domain.errors import RestaurantNotFoundError, NotInQueueError, TableInvalidActionError, TableNotFoundError

table_router = APIRouter(prefix="/api", tags=["Table"])

# Dependency Stub
def get_table_service() -> ITableService:
    raise NotImplementedError("Dependency 'get_table_service' not overridden")

def error_response(status_code: int, code: str, message: str):
    """輔助函式：產生符合格式的錯誤回應"""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )

# 1. GET 取得座位表
@table_router.get("/restaurants/{restaurant_id}/table", response_model=RestaurantSeatsResponse)
def get_table_layout(
    restaurant_id: int, 
    service: ITableService = Depends(get_table_service)
):
    try:
        return service.get_restaurant_seats(restaurant_id)
    except RestaurantNotFoundError as e:
        return error_response(status.HTTP_404_NOT_FOUND, e.code, e.message)

# 2. POST 更新狀態
@table_router.post("/restaurant/{restaurant_id}/tables/{table_id}", response_model=UpdateTableStatusResponse)
def update_table_status(
    restaurant_id: int,
    table_id: int,
    request: UpdateTableStatusRequest,
    service: ITableService = Depends(get_table_service)
):
    try:
        return service.update_table_status(restaurant_id, table_id, request.action, request.queue_ticket_number)
    except TableNotFoundError as e:
        return error_response(status.HTTP_404_NOT_FOUND, e.code, e.message)
    except TableInvalidActionError as e:
        return error_response(status.HTTP_400_BAD_REQUEST, e.code, e.message)
    except NotInQueueError as e:
        return error_response(status.HTTP_400_BAD_REQUEST, e.code, e.message)