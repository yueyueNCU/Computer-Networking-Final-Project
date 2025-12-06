from fastapi import APIRouter, Depends
from typing import List
from app.schemas.map_schema import RestaurantItem
from app.services.map_service import MapService

from app.repositories.fake_all_repo import _mock_map_repo

router = APIRouter(prefix="/api/map", tags=["Map"])

def get_map_service():
    return MapService(repo=_mock_map_repo)

@router.get("/restaurants", response_model=List[RestaurantItem])
def get_restaurants(
    lat: float, 
    lng: float, 
    service: MapService = Depends(get_map_service)
):
    return service.get_restaurants(user_lat=lat, user_lng=lng)