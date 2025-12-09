import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock
from app.routers import map as map_router_module 
from app.routers.map import get_map_service
from app.services.map_service import MapService
from app.interfaces.map_interface import IMapRepository

# 1. 建立測試用的 FastAPI App 並掛載 Router
app = FastAPI()
app.include_router(map_router_module.router)

client = TestClient(app)

# --- Fixtures (測試前置準備) ---

@pytest.fixture
def mock_map_repo():
    """模擬 Map Repository (介面層)"""
    return MagicMock(spec=IMapRepository)

@pytest.fixture
def map_service_override(mock_map_repo):
    """建立注入了 Mock Repo 的 Service"""
    return MapService(map_repo=mock_map_repo)

@pytest.fixture
def app_with_map_override(map_service_override):
    """
    覆寫 FastAPI 的依賴注入 (Dependency Injection)
    讓 /api/restaurants 執行時，使用的是假的 Service，而不是真的 fake_all_repo
    """
    app.dependency_overrides[get_map_service] = lambda: map_service_override
    yield app
    # 測試結束後還原，避免汙染其他測試
    app.dependency_overrides = {}

# --- Test Cases (測試案例) ---

def test_get_restaurants_success(app_with_map_override, mock_map_repo):
    """
    測試 GET /api/restaurants 是否成功回傳 200 以及正確的資料格式
    """
    # 1. Arrange (準備假資料)
    # 模擬 Repository 從資料庫撈出的原始資料 (List of Dicts)
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
    
    # 設定 Mock Repo 的行為：當被呼叫 get_all_restaurants 時，回傳上面的假資料
    mock_map_repo.get_all_restaurants.return_value = fake_db_data

    # 2. Act (執行請求)
    # 這裡的網址必須對應 router 設定的 prefix + path
    response = client.get("/api/restaurants")

    # 3. Assert (驗證結果)
    # 驗證狀態碼
    assert response.status_code == 200
    
    # 驗證回傳的 JSON 內容
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["restaurant_name"] == "麥克小姐"
    assert data[1]["status"] == "red"

    # 驗證 Service 是否真的有去呼叫 Repository
    mock_map_repo.get_all_restaurants.assert_called_once()