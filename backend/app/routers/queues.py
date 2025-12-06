from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.schemas.queue_schema import (
    JoinQueueRequest,
    JoinQueueResponse,
    LeaveQueueRequest,
    QueueStatusResponse,
    QueueNextResponse
)
from app.interfaces.queue_interface import IQueueService
from app.domain.errors import (
    QueueAlreadyJoinedError,
    RestaurantNotFoundError,
    NotInQueueError
)

queue_router = APIRouter(
    prefix="/api/restaurants",
    tags=["Queue"]
)

# Dependency Stub
def get_queue_service() -> IQueueService:
    raise NotImplementedError("Dependency 'get_queue_service' not overridden")

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

@queue_router.post("/{restaurant_id}/queue", response_model=JoinQueueResponse, status_code=status.HTTP_201_CREATED)
def join_queue(
    restaurant_id: int, 
    request: JoinQueueRequest, 
    service: IQueueService = Depends(get_queue_service)
):
    try:
        return service.join_restaurant_waiting_queue(restaurant_id, request.user_id)
    except QueueAlreadyJoinedError as e:
        return error_response(status.HTTP_409_CONFLICT, e.code, e.message)
    except RestaurantNotFoundError as e:
        return error_response(status.HTTP_404_NOT_FOUND, e.code, e.message)

@queue_router.delete("/{restaurant_id}/queue", status_code=status.HTTP_204_NO_CONTENT)
def leave_queue(
    restaurant_id: int, 
    request: LeaveQueueRequest, 
    service: IQueueService = Depends(get_queue_service)
):
    try:
        service.leave_restaurant_waiting_queue(restaurant_id, request.user_id)
    except NotInQueueError as e:
        return error_response(status.HTTP_400_BAD_REQUEST, e.code, e.message)
    except RestaurantNotFoundError as e:
        return error_response(status.HTTP_404_NOT_FOUND, e.code, e.message)

@queue_router.get("/{restaurant_id}/queue/status", response_model=QueueStatusResponse)
def get_queue_status(
    restaurant_id: int, 
    service: IQueueService = Depends(get_queue_service)
):
    try:
        return service.get_queue_status(restaurant_id)
    except RestaurantNotFoundError as e:
        return error_response(status.HTTP_404_NOT_FOUND, e.code, e.message)

@queue_router.get("/{restaurant_id}/queue/next", response_model=QueueNextResponse)
def get_queue_next(
    restaurant_id: int, 
    service: IQueueService = Depends(get_queue_service)
):
    try:
        return service.get_queue_next(restaurant_id)
    except RestaurantNotFoundError as e:
        return error_response(status.HTTP_404_NOT_FOUND, e.code, e.message)