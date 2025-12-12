import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock

from app.routers.table import table_router, get_table_service

from app.services.table_service import TableService
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.interfaces.table_interface import ITableRepository
from app.domain.entities import QueueEntity, MapEntity, TableEntity

# 建立測試用的 FastAPI App
app = FastAPI()
app.include_router(table_router)

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture
def mock_repos():
    table_repo = MagicMock(spec=ITableRepository)
    map_repo = MagicMock(spec=IMapRepository)
    queue_repo = MagicMock(spec=IQueueRepository)
    queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)
    return table_repo, map_repo, queue_repo, queue_runtime_repo

@pytest.fixture
def service_override(mock_repos):
    table_repo, map_repo, queue_repo, queue_runtime_repo = mock_repos
    return TableService(
        table_repo=table_repo,
        map_repo=map_repo,
        queue_repo=queue_repo,
        queue_runtime_repo=queue_runtime_repo,
    )

@pytest.fixture
def app_with_override(service_override):
    # 覆寫依賴注入
    app.dependency_overrides[get_table_service] = lambda: service_override
    yield app
    app.dependency_overrides = {}



def test_get_restaurant_seats_Success(app_with_override, mock_repos):
    """測試成功取得餐廳座位表"""
    # Arrange
    table_repo, map_repo, queue_repo, queue_runtime_repo = mock_repos

    map_repo.get_restaurant_basic_info.return_value= MapEntity(
                                                                restaurant_id = 2,
                                                                restaurant_name = "麥克小姐",
                                                                lat = 24.968, 
                                                                lng = 121.192,
                                                                image_url = "https://example.com/burger.jpg",
                                                                average_price = (150,300),
                                                                specialties = "義大利麵、漢堡",
                                                            ) 
    table_repo.get_tables_by_restaurant.return_value=[
        TableEntity(
            table_id=1,
            restaurant_id=2,
            label="1桌",
            x=2,
            y=5,
            status="empty"
        ),
        TableEntity(
            table_id=2,
            restaurant_id=2,
            label="2桌",
            x=1,
            y=4,
            status="eating"
        )
    ]
    # Act 
    restaurant_id=2
    response = client.get(f"/api/restaurants/{restaurant_id}/table")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == restaurant_id
    assert data["restaurant_name"] == "麥克小姐"
    assert len(data["seats"]) == 2
    assert data["seats"][0]["label"] == "1桌"


def test_get_restaurant_seats_RestaurantNotFoundError(app_with_override, mock_repos):
    """測試成功更新狀態"""
    # Arrange
    table_repo, map_repo, _, _ = mock_repos
    map_repo.get_restaurant_basic_info.return_value = None # 模擬找不到餐廳

    # Act
    restaurant_id=2
    response = client.get(f"/api/restaurants/{restaurant_id}/table")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    
    # 驗證格式
    assert "error" in data
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"
    assert data["error"]["message"] == "Restaurant does not exist."






def test_update_table_status_TableNotFoundError(app_with_override, mock_repos):
    """測試錯誤 1: Table 不存在 (404)"""
    # Arrange
    table_repo, _, _, _ = mock_repos
    table_repo.get_table_by_id.return_value = None # 模擬找不到桌子

    # Act
    restaurant_id=2
    table_id = 999
    response = client.post(f"/api/restaurant/{restaurant_id}/tables/{table_id}", json={ "action": "eating","queue_ticket_number": 106})
    
    assert response.status_code == 404
    data = response.json()
    
    # 驗證格式
    assert "error" in data
    assert data["error"]["code"] == "TABLE_NOT_FOUND"
    assert data["error"]["message"] == "Table does not exist."

def test_update_table_status_SecurityCheckFailed(app_with_override, mock_repos):
    # Arrange
    table_repo, _, _, _ = mock_repos
    
    # 桌子實際上屬於 restaurant_id=1
    existing_table = TableEntity(
        table_id=10, restaurant_id=1, label="A1", x=0, y=0, status="empty"
    )
    table_repo.get_table_by_id.return_value = existing_table
    # Act
    restaurant_id=2
    table_id = 10
    response = client.post(f"/api/restaurant/{restaurant_id}/tables/{table_id}", json={ "action": "eating","queue_ticket_number": 106})

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TABLE_NOT_FOUND"
    assert data["error"]["message"] == "Table does not exist."

def test_update_table_status_TableInvalidActionError(app_with_override, mock_repos):
    # Arrange
    table_repo, _, _, _ = mock_repos
    
    # 桌子已經是 eating 狀態
    existing_table = TableEntity(
        table_id=10, restaurant_id=2, label="A1", x=0, y=0, status="eating"
    )
    table_repo.get_table_by_id.return_value = existing_table

    restaurant_id=2
    table_id = 10
    response = client.post(f"/api/restaurant/{restaurant_id}/tables/{table_id}", json={ "action": "eating","queue_ticket_number": 106})

    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TABLE_INVALID_ACTION"

def test_update_table_status_CheckIn_Success(app_with_override, mock_repos):
    # Arrange
    table_repo, _, queue_repo, queue_runtime_repo = mock_repos
    
    restaurant_id = 2
    table_id = 10
    ticket_number = 50
    user_id = 100
    
    # 1. 模擬桌子存在且為 empty
    table_repo.get_table_by_id.return_value = TableEntity(
        table_id=table_id, restaurant_id=restaurant_id, label="A1", x=0, y=0, status="empty"
    )
    
    # 2. 模擬排隊資料存在 (使用 QueueEntity)
    queue_repo.get_user_current_queue_by_restaurantId_and_ticketNumber.return_value = QueueEntity(
        queue_id=1, restaurant_id=restaurant_id, user_id=user_id, ticket_number=ticket_number
    )

    restaurant_id=2
    table_id = 10
    response = client.post(f"/api/restaurant/{restaurant_id}/tables/{table_id}", json={ "action": "eating","queue_ticket_number": ticket_number})

    assert response.status_code == 200
    data = response.json()
    assert data["table_id"] == table_id
    assert data["new_status"] == "eating"

def test_update_table_status_CheckIn_NotInQueueError(app_with_override, mock_repos):
    # Arrange
    table_repo, _, queue_repo, _ = mock_repos
    
    restaurant_id = 2
    
    # 1. 桌子存在
    table_repo.get_table_by_id.return_value = TableEntity(
        table_id=10, restaurant_id=restaurant_id, label="A1", x=0, y=0, status="empty"
    )
    
    # 2. 排隊資料不存在 (None)
    queue_repo.get_user_current_queue_by_restaurantId_and_ticketNumber.return_value = None

    restaurant_id=2
    table_id = 10
    response = client.post(f"/api/restaurant/{restaurant_id}/tables/{table_id}", json={ "action": "eating","queue_ticket_number": 103})

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "NOT_IN_QUEUE"

def test_update_table_status_CheckOut_Success(app_with_override, mock_repos):
    # Arrange
    table_repo, _, queue_repo, queue_runtime_repo = mock_repos
    
    restaurant_id = 2
    table_id = 10
    
    # 模擬桌子正在使用中
    table_repo.get_table_by_id.return_value = TableEntity(
        table_id=table_id, restaurant_id=restaurant_id, label="A1", x=0, y=0, status="eating"
    )

    restaurant_id=2
    table_id = 10
    response = client.post(f"/api/restaurant/{restaurant_id}/tables/{table_id}", json={ "action": "empty","queue_ticket_number": 103})

    assert response.status_code == 200
    data = response.json()
    assert data["table_id"] == table_id
    assert data["new_status"] == "empty"