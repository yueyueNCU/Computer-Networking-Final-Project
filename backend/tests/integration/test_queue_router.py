import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock

# Import 你的模組
from app.routers.queues import queue_router, get_queue_service
from app.services.queue_service import QueueService
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository

# 建立測試用的 FastAPI App
app = FastAPI()
app.include_router(queue_router)

client = TestClient(app)

# --- Fixtures ---
@pytest.fixture
def mock_repos():
    queue_repo = MagicMock(spec=IQueueRepository)
    queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)
    map_repo = MagicMock(spec=IMapRepository)
    return queue_repo, queue_runtime_repo, map_repo

@pytest.fixture
def service_override(mock_repos):
    queue_repo, queue_runtime_repo, map_repo = mock_repos
    return QueueService(queue_repo, queue_runtime_repo, map_repo)

@pytest.fixture
def app_with_override(service_override):
    app.dependency_overrides[get_queue_service] = lambda: service_override
    yield app
    app.dependency_overrides = {}


""""""
def test_join_queue_success(app_with_override, mock_repos):
    queue_repo, queue_runtime_repo, map_repo = mock_repos
    
    # 模擬正常流程
    queue_repo.get_user_current_queue.return_value = None
    map_repo.check_exists.return_value = True
    queue_repo.get_total_waiting.return_value = 2
    queue_runtime_repo.get_next_ticket_number.return_value = 10
    queue_runtime_repo.get_metrics.return_value = (10, 5) # wait_time = 2 * (10/5) = 4
    queue_repo.add_to_queue.return_value = True

    response = client.post("/api/restaurants/1/queue", json={"user_id": 123})
    
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_number"] == 10
    assert data["estimated_wait_time"] == 4

def test_join_queue_restaurant_not_found_returns_custom_error(app_with_override, mock_repos):
    """驗證回傳的錯誤格式是否符合 {error: {code: ..., message: ...}}"""
    queue_repo, _, map_repo = mock_repos
    
    # 模擬餐廳不存在
    queue_repo.get_user_current_queue.return_value = None
    map_repo.check_exists.return_value = False 

    response = client.post("/api/restaurants/999/queue", json={"user_id": 123})
    
    assert response.status_code == 404
    data = response.json()
    
    # 驗證格式
    assert "error" in data
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"
    assert data["error"]["message"] == "Restaurant does not exist."

def test_join_queue_already_joined_returns_custom_error(app_with_override, mock_repos):
    queue_repo, _, _ = mock_repos
    
    # 模擬使用者已經在排隊
    queue_repo.get_user_current_queue.return_value = 1 

    response = client.post("/api/restaurants/2/queue", json={"user_id": 123})
    
    assert response.status_code == 409
    data = response.json()
    
    assert "error" in data
    assert data["error"]["code"] == "QUEUE_ALREADY_JOINED"
    assert data["error"]["message"] == "You are already in the queue."




""""""
def test_leave_queue_success(app_with_override, mock_repos):
    queue_repo, _, map_repo = mock_repos
    
    # 模擬使用者正在排該餐廳
    queue_repo.get_user_current_queue.return_value = 1
    map_repo.check_exists.return_value = True

    response = client.request("DELETE", "/api/restaurants/1/queue", json={"user_id": 123})
    
    assert response.status_code == 204
    # 驗證有呼叫移除
    queue_repo.remove_from_queue.assert_called_with(restaurant_id=1, user_id=123)

def test_leave_queue_not_in_queue_error(app_with_override, mock_repos):
    """測試離開排隊時，使用者根本沒在排隊"""
    queue_repo, _, map_repo = mock_repos
    
    # 使用者沒在排任何隊
    queue_repo.get_user_current_queue.return_value = None
    
    response = client.request("DELETE", "/api/restaurants/1/queue", json={"user_id": 123})
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "NOT_IN_QUEUE"
    assert data["error"]["message"] == "User is not in queue."

def test_leave_queue_restaurant_not_found(app_with_override, mock_repos):
    """測試離開排隊時，餐廳不存在"""
    queue_repo, _, map_repo = mock_repos
    
    queue_repo.get_user_current_queue.return_value = 999
    map_repo.check_exists.return_value = False 

    response = client.request("DELETE", "/api/restaurants/999/queue", json={"user_id": 123})
    
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"




""""""
# --- 3. 取得排隊狀態 (Queue Status) 測試 ---
def test_get_queue_status_success(app_with_override, mock_repos):
    queue_repo, queue_runtime_repo, map_repo = mock_repos
    
    map_repo.check_exists.return_value = True
    map_repo.get_restaurant_basic_info.return_value = {"restaurant_name": "My Rest"}
    queue_runtime_repo.get_current_ticket_number.return_value = 5
    queue_repo.get_total_waiting.return_value = 3
    queue_runtime_repo.get_metrics.return_value = (20, 10) 

    response = client.get("/api/restaurants/1/queue/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_name"] == "My Rest"
    assert data["current_number"] == 5

def test_get_queue_status_restaurant_not_found(app_with_override, mock_repos):
    _, _, map_repo = mock_repos
    map_repo.check_exists.return_value = False

    response = client.get("/api/restaurants/999/queue/status")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"



# --- 4. 取得下一個叫號 (Queue Next) 測試 ---
""""""
def test_get_queue_next_success(app_with_override, mock_repos):
    """測試餐廳端取得下一個叫號"""
    queue_repo, queue_runtime_repo, map_repo = mock_repos
    
    map_repo.check_exists.return_value = True
    queue_runtime_repo.get_current_ticket_number.return_value = 10
    # 下一個要叫的號碼是 12
    queue_repo.get_next_queue_to_call.return_value = 12
    queue_repo.get_total_waiting.return_value = 5

    response = client.get("/api/restaurants/1/queue/next")
    
    assert response.status_code == 200
    data = response.json()
    assert data["current_number"] == 10
    assert data["next_queue_to_call"] == 12
    assert data["total_waiting"] == 5

def test_get_queue_next_restaurant_not_found(app_with_override, mock_repos):
    """測試餐廳端取得叫號時，餐廳不存在"""
    _, _, map_repo = mock_repos
    map_repo.check_exists.return_value = False

    response = client.get("/api/restaurants/999/queue/next")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"