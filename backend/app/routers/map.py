from fastapi import APIRouter, Depends
from typing import List
from app.schemas.map_schema import RestaurantItem
from app.services.map_service import MapService
from app.repositories.fake_all_repo import _mock_map_repo 

router = APIRouter(prefix="/api", tags=["Restaurants"])

def get_map_service():
    return MapService(map_repo=_mock_map_repo)

@router.get("/restaurants", response_model=List[RestaurantItem])
def get_restaurants(
    service: MapService = Depends(get_map_service)
):
    # 取得所有餐廳列表，直接呼叫 Service
    return service.get_restaurants()