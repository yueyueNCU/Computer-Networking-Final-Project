import pytest
from unittest.mock import MagicMock
from app.services.map_service import MapService
from app.interfaces.map_interface import IMapRepository

def test_get_restaurants():
    # --- 1. Arrange (準備環境) ---
    mock_repo = MagicMock(spec=IMapRepository)
    
    # 假資料 (模擬 Repository 從資料庫撈出來的原始 Dict)
    fake_db_data = [
        {
            "restaurant_id": 2,
            "restaurant_name": "麥克小姐",
            "lat": 24.968,
            "lng": 121.192,
            "image_url": "https://example.com/burger.jpg",
            "average_price": "150-300",
            "specialties": "義大利麵、漢堡",
            "status": "green",
        },
        {
            "restaurant_id": 3,
            "restaurant_name": "歐姆萊斯",
            "lat": 24.970,
            "lng": 121.195,
            "image_url": "https://example.com/rice.jpg",
            "average_price": "80-150",
            "specialties": "咖哩、豬排飯",
            "status": "red",
        }
    ]

    # 設定 Mock 行為
    mock_repo.get_all_restaurants.return_value = fake_db_data
    
    # 初始化 Service
    service = MapService(map_repo=mock_repo)

    # --- 2. Act (執行測試) ---
    result = service.get_restaurants()

    # --- 3. Assert (驗證結果) ---
    assert len(result) == 2
    assert result[0].restaurant_name == "麥克小姐"
    assert result[1].status == "red"
    
    # 驗證 Service 是否呼叫了正確的 Repo 方法
    mock_repo.get_all_restaurants.assert_called_once()