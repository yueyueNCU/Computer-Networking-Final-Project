import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock

# Import 你的模組
from app.routers.queues import queue_router, get_queue_service
from app.services.queue_service import QueueService
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.domain.value_objects import RestaurantMetrics
from app.domain.entities import QueueEntity, MapEntity
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
def test_join_restaurant_waiting_queue_Success(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    waiting_count=2
    obtain_ticket_number=10
    metrics=RestaurantMetrics(average_wait_time=10,table_number=5) 

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    mock_map_repo.get_restaurant_basic_info.return_value = True # 餐廳存在
    mock_queue_repo.get_total_waiting.return_value = waiting_count
    mock_queue_runtime_repo.get_next_ticket_number.return_value = obtain_ticket_number
    mock_queue_runtime_repo.get_metrics.return_value = metrics
    mock_queue_repo.add_to_queue.return_value = True 

    response = client.post("/api/restaurants/1/queue", json={"user_id": 123})
    
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_number"] == 10
    assert data["estimated_wait_time"] == 4

def test_join_restaurant_waiting_queue_RestaurantNotFoundError(app_with_override, mock_repos):
    """驗證回傳的錯誤格式是否符合 {error: {code: ..., message: ...}}"""
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    mock_map_repo.get_restaurant_basic_info.return_value = None  # 餐廳不存在

    response = client.post("/api/restaurants/999/queue", json={"user_id": 123})
    
    assert response.status_code == 404
    data = response.json()
    
    # 驗證格式
    assert "error" in data
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"
    assert data["error"]["message"] == "Restaurant does not exist."

def test_join_restaurant_waiting_queue_AlreadyJoinQueueError(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30) # 使用者有排隊

    response = client.post("/api/restaurants/2/queue", json={"user_id": 123})
    
    assert response.status_code == 409
    data = response.json()
    
    assert "error" in data
    assert data["error"]["code"] == "QUEUE_ALREADY_JOINED"




""""""
def test_leave_restaurant_waiting_queue_Success(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=1, user_id=123, ticket_number=30)      # 使用者有排隊
    mock_map_repo.get_restaurant_basic_info.return_value = True     # 餐廳存在

    response = client.request("DELETE", "/api/restaurants/1/queue", json={"user_id": 123})
    
    assert response.status_code == 204
    # 驗證有呼叫移除
    mock_queue_repo.remove_from_queue.assert_called_with(restaurant_id=1, user_id=123)

def test_leave_restaurant_waiting_queue_NotInQueueError(app_with_override, mock_repos):
    """測試離開排隊時，使用者根本沒在排隊"""
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    
    response = client.request("DELETE", "/api/restaurants/1/queue", json={"user_id": 123})
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "NOT_IN_QUEUE"
    assert data["error"]["message"] == "User is not in queue."

def test_leave_restaurant_waiting_queue_NotInCorrectQueueError(app_with_override, mock_repos):
    """測試離開排隊時，使用者根本沒在排隊"""
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30) # 使用者排餐廳5的隊伍
    
    response = client.request("DELETE", "/api/restaurants/2/queue", json={"user_id": 123})
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "NOT_IN_QUEUE"
    assert data["error"]["message"] == "User is not in this restaurant's queue."

def test_leave_restaurant_waiting_queue_RestaurantNotFoundError(app_with_override, mock_repos):
    """測試離開排隊時，餐廳不存在"""
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30) # 使用者有排隊
    mock_map_repo.get_restaurant_basic_info.return_value = None     # 餐廳不存在

    response = client.request("DELETE", "/api/restaurants/999/queue", json={"user_id": 123})
    
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"




""""""
# --- 3. 取得排隊狀態 (Queue Status) 測試 --- 查詢排隊概況 (給考慮排隊的顧客看)
def test_get_queue_status_Success(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = MapEntity(
                                                                restaurant_id = 2,
                                                                restaurant_name = "麥克小姐",
                                                                lat = 24.968, 
                                                                lng = 121.192,
                                                                image_url = "https://example.com/burger.jpg",
                                                                average_price = (150,300),
                                                                specialties = "義大利麵、漢堡",
                                                            ) 
    
    mock_queue_runtime_repo.get_current_ticket_number.return_value = 105
    mock_queue_repo.get_total_waiting.return_value = 5
    mock_queue_runtime_repo.get_metrics.return_value = RestaurantMetrics(average_wait_time=10,table_number=2)  # avg_dining_time, total_seats

    response = client.get("/api/restaurants/1/queue/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_name"] == "麥克小姐"
    assert data["current_number"] == 105

def test_get_queue_status_RestaurantNotFoundError(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = None # 餐廳不存在

    response = client.get("/api/restaurants/999/queue/status")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"



# --- 4. 取得下一個叫號 (Queue Next) 測試 --- 查詢下組叫號資訊 (給店家)
""""""
def test_get_queue_next_Success(app_with_override, mock_repos):
    """測試餐廳端取得下一個叫號"""
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = True # 餐廳不存在

    mock_queue_runtime_repo.get_current_ticket_number.return_value=20
    mock_queue_repo.get_next_queue_to_call.return_value= 22
    mock_queue_repo.get_total_waiting.return_value=5

    response = client.get("/api/restaurants/1/queue/next")
    
    assert response.status_code == 200
    data = response.json()
    assert data["current_number"] == 20
    assert data["next_queue_to_call"] == 22
    assert data["total_waiting"] == 5
def test_get_queue_next_NoOneInQueSuccess(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = True # 餐廳存在

    mock_queue_runtime_repo.get_current_ticket_number.return_value= 20
    mock_queue_repo.get_next_queue_to_call.return_value= None
    mock_queue_repo.get_total_waiting.return_value=0

    response = client.get("/api/restaurants/1/queue/next")

    assert response.status_code == 200
    data = response.json()
    assert data["current_number"] == 20
    assert data["next_queue_to_call"] == 20
    assert data["total_waiting"] == 0

def test_get_queue_next_RestaurantNotFoundError(app_with_override, mock_repos):
    """測試餐廳端取得叫號時，餐廳不存在"""
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = None # 餐廳不存在

    response = client.get("/api/restaurants/999/queue/next")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"




# --- 5. 取得下一個叫號 (User queue test) 測試 ---  查詢個人排隊概況 (給已經排隊的顧客看) 測試
def test_get_user_queue_status_Success(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, 
                                                                      restaurant_id=1, 
                                                                      user_id=123, 
                                                                      ticket_number=30)      # 使用者有排隊
    mock_map_repo.get_restaurant_basic_info.return_value = MapEntity(
                                                                restaurant_id = 2,
                                                                restaurant_name = "麥克小姐",
                                                                lat = 24.968, 
                                                                lng = 121.192,
                                                                image_url = "https://example.com/burger.jpg",
                                                                average_price = (150,300),
                                                                specialties = "義大利麵、漢堡",
                                                            ) 
    mock_queue_repo.get_people_ahead.return_value = 6
    mock_queue_runtime_repo.get_metrics.return_value = RestaurantMetrics(average_wait_time=10,
                                                                         table_number=2) 

    response = client.get("/api/user/123/queue")

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_number"] == 30
    assert data["people_ahead"] == 6
    assert data["estimated_wait_time"] == 6*(10/2)

def test_get_user_queue_status_NotInQueueError(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = None   # 使用者沒排隊

    response = client.get("/api/user/123/queue")

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "NOT_IN_QUEUE"
    assert data["error"]["message"] == "User is not in queue."

def test_get_user_queue_status_RestaurantNotFoundError(app_with_override, mock_repos):
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, 
                                                                      restaurant_id=1, 
                                                                      user_id=123, 
                                                                      ticket_number=30)   # 使用者沒排隊
    mock_map_repo.get_restaurant_basic_info.return_value = None #餐廳找不到

    response = client.get("/api/user/123/queue")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"
    