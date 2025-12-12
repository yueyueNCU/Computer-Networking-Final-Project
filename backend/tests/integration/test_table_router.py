import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock
from app.routers import table as table_router_module
from app.routers.table import get_table_service
from app.services.table_service import TableService
from app.schemas.table_schema import RestaurantSeatsResponse, TableDetail

# 建立測試用的 FastAPI App
app = FastAPI()
app.include_router(table_router_module.table_router)

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service_override(mock_repo):
    """初始化 Service 時，只傳入 repo"""
    return TableService(repo=mock_repo)

@pytest.fixture
def app_with_override(service_override):
    # 覆寫依賴注入
    app.dependency_overrides[get_table_service] = lambda: service_override
    yield app
    app.dependency_overrides = {}


# --- 1. GET /api/restaurants/{id}/table (取得座位表) ---

def test_get_tables_success(app_with_override, mock_repo):
    """測試成功取得餐廳座位表"""
    restaurant_id = 2
    
    # 模擬 Repo 回傳 Layout 物件
    mock_layout = RestaurantSeatsResponse(
        restaurant_id=restaurant_id,
        restaurant_name="整合測試餐廳",
        seats=[
            TableDetail(table_id=101, label="A1", x=1, y=1, status="eating"),
            TableDetail(table_id=102, label="A2", x=2, y=1, status="empty")
        ]
    )
    mock_repo.get_layout.return_value = mock_layout

    # Act
    response = client.get(f"/api/restaurants/{restaurant_id}/table")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == restaurant_id
    assert data["restaurant_name"] == "整合測試餐廳"
    assert len(data["seats"]) == 2
    assert data["seats"][0]["label"] == "A1"


# --- 2. POST /api/tables/{id}/status (更新狀態) ---

def test_update_status_success(app_with_override, mock_repo):
    """測試成功更新狀態"""
    table_id = 101
    
    # 模擬: 找到桌子 (原本是 empty)
    mock_seat = TableDetail(table_id=table_id, label="A1", x=1, y=1, status="empty")
    mock_repo.get_seat_by_id.return_value = mock_seat

    # Act
    payload = {"action": "eating", "queue_ticket_number": 106}
    response = client.post(f"/api/tables/{table_id}/status", json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["table_id"] == table_id
    assert data["new_status"] == "eating"
    assert "updated_at" in data
    
    # 驗證 Mock 物件狀態被修改
    assert mock_seat.status == "eating"

def test_update_status_table_not_found(app_with_override, mock_repo):
    """測試錯誤 1: Table 不存在 (404)"""
    # 模擬找不到 Table
    mock_repo.get_seat_by_id.return_value = None

    payload = {"action": "eating", "queue_ticket_number": 106}
    response = client.post("/api/tables/999/status", json=payload)
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TABLE_NOT_FOUND"

def test_update_status_invalid_action(app_with_override, mock_repo):
    """測試錯誤 2: 狀態相同 (400)"""
    # 模擬原本就是 empty
    mock_seat = TableDetail(table_id=101, label="A1", x=1, y=1, status="empty")
    mock_repo.get_seat_by_id.return_value = mock_seat

    # 嘗試再設為 empty
    payload = {"action": "empty", "queue_ticket_number": 106}
    response = client.post("/api/tables/101/status", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "TABLE_INVALID_ACTION"

def test_update_status_not_in_queue(app_with_override, mock_repo):
    """測試錯誤 3: 票號錯誤"""
    # Table 存在且是 empty
    mock_seat = TableDetail(table_id=101, label="A1", x=1, y=1, status="empty")
    mock_repo.get_seat_by_id.return_value = mock_seat

    payload = {"action": "eating", "queue_ticket_number": 999}
    response = client.post("/api/tables/101/status", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "NOT_IN_QUEUE"