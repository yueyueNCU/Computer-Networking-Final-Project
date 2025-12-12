from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List
from app.schemas.map_schema import RestaurantItem
from app.services.map_service import MapService
from app.interfaces.map_interface import IMapService

map_router = APIRouter(
    prefix="/api",
    tags=["Restaurant"]
)

# Dependency Stub
def get_map_service() -> IMapService:
    raise NotImplementedError("Dependency 'get_map_service' not overridden")

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


@map_router.get("/restaurants", response_model=List[RestaurantItem])
def get_restaurants(
    service: MapService = Depends(get_map_service)
):
    # 取得所有餐廳列表，直接呼叫 Service
    return service.get_restaurants()