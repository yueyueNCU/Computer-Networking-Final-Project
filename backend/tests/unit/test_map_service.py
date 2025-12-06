# 檔案: tests/test_map_service.py
import pytest
from unittest.mock import MagicMock
from app.services.map_service import MapService
from app.repositories.map_repo import MapRepository
from app.schemas.map_schema import RestaurantItem

def test_get_restaurants():
    # 1. Arrange (準備假資料)
    mock_repo = MagicMock()
    
    # 假裝資料庫裡有這兩間餐廳
    fake_data = [
        RestaurantItem(
            restaurant_id=1, restaurant_name="Yueyue Burger", 
            lat=25.0, lng=121.0, image_url="img1.jpg", 
            average_price="$$", specialties="Burger", status="green"
        ),
        RestaurantItem(
            restaurant_id=2, restaurant_name="Hxy Pizza", 
            lat=25.01, lng=121.01, image_url="img2.jpg", 
            average_price="$", specialties="Pizza", status="yellow"
        )
    ]
    
    # 設定 Mock 行為：當呼叫 get_nearby_restaurants 時，回傳上面的假資料
    mock_repo.get_nearby_restaurants.return_value = fake_data
    
    # 初始化 Service
    service = MapService(repo=mock_repo)

    # 2. Act (執行測試)
    # 假設使用者位置在 (25.0, 121.0)
    result = service.get_restaurants(user_lat=25.0, user_lng=121.0)

    # 3. Assert (驗證結果)
    assert len(result) == 2
    assert result[0].restaurant_name == "Yueyue Burger"
    assert result[1].status == "yellow"
    
    # 驗證 Service 是否有正確呼叫 Repository
    mock_repo.get_nearby_restaurants.assert_called_once()