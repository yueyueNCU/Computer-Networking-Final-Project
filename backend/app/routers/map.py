from fastapi import APIRouter, Depends
from typing import List
from app.schemas.map_schema import RestaurantItem
from app.services.map_service import MapService

from app.repositories.fake_all_repo import _mock_map_repo

router = APIRouter(prefix="/api/map", tags=["Map"])

def get_map_service():
    return MapService(repo=_mock_map_repo)
# yueyue 
# 這邊我們設計的是 GET /api/restaurants 是要使用者(前端)送任何lat,lng ，這裡不需要參數
# 我理解你這樣設計是為了使用者用gps，但是我們沒有這樣設定，如果使用的話，會增加我們的複雜度
@router.get("/restaurants", response_model=List[RestaurantItem])
def get_restaurants(
    lat: float, 
    lng: float, 
    service: MapService = Depends(get_map_service)
):
    return service.get_restaurants(user_lat=lat, user_lng=lng)