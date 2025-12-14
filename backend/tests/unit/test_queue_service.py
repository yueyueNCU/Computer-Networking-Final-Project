import pytest
from unittest.mock import MagicMock
from app.services.queue_service import QueueService
from app.interfaces.queue_interface import IQueueRepository,IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.domain.errors import QueueAlreadyJoinedError,NotInQueueError, RestaurantNotFoundError
from app.domain.value_objects import RestaurantMetrics
from app.domain.entities import QueueEntity, MapEntity
@pytest.fixture
def mock_repos():
    """
    負責建立所有需要的 Mock Repository。
    回傳 Tuple: (mock_queue_repo, mock_runtime_repo, mock_map_repo)
    """
    queue_repo = MagicMock(spec=IQueueRepository)
    queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)
    map_repo = MagicMock(spec=IMapRepository)
    return queue_repo, queue_runtime_repo, map_repo

@pytest.fixture
def queue_service(mock_repos):
    """
    負責初始化 Service，並自動注入 mock_repos。
    測試函式只需要請求這個 fixture，就可以拿到已經裝好 Mock 的 Service。
    """
    queue_repo, queue_runtime_repo, map_repo = mock_repos
    return QueueService(
        queue_repo=queue_repo,
        queue_runtime_repo=queue_runtime_repo,
        map_repo=map_repo
    )

# 測試加入排隊成功案例
def test_join_restaurant_waiting_queue_Success(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    waiting_count=3
    obtain_ticket_number=12
    metrics=RestaurantMetrics(average_wait_time=8,table_number=10) 

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    mock_map_repo.get_restaurant_basic_info.return_value = True # 餐廳存在
    mock_queue_repo.get_total_waiting.return_value = waiting_count
    mock_queue_runtime_repo.get_next_ticket_number.return_value = obtain_ticket_number
    mock_queue_runtime_repo.get_metrics.return_value = metrics
    mock_queue_repo.add_to_queue.return_value = True

    # Act
    join_response = queue_service.join_restaurant_waiting_queue(restaurant_id=5, user_id= 25)
    # Assert
    assert join_response.ticket_number == obtain_ticket_number
    assert join_response.people_ahead == waiting_count
    assert join_response.estimated_wait_time == int(waiting_count* (metrics.average_wait_time/metrics.table_number))
    mock_queue_runtime_repo.increment_next_ticket_number.assert_called_once_with(restaurant_id=5)
    
# 測試加入排隊因 餐廳找不到 而失敗
def test_join_restaurant_waiting_queue_RestaurantNotFoundError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    mock_map_repo.get_restaurant_basic_info.return_value = None  # 餐廳不存在

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        queue_service.join_restaurant_waiting_queue(restaurant_id=999, user_id=25)
    mock_queue_runtime_repo.increment_next_ticket_number.assert_not_called()

# 測試加入排隊因 已經在排隊隊伍中 而失敗
def test_join_restaurant_waiting_queue_AlreadyJoinQueueError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30) # 使用者有排隊

    # Act & Assert
    with pytest.raises(QueueAlreadyJoinedError):
        queue_service.join_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_runtime_repo.increment_next_ticket_number.assert_not_called()
        


""""""
# 測試離開排隊成功案例
def ttest_leave_restaurant_waiting_queue_Success(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30)      # 使用者有排隊
    mock_map_repo.get_restaurant_basic_info.return_value = True     # 餐廳存在

    # Act
    queue_service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)

    # Assert
    mock_queue_repo.get_user_current_queue.assert_called_once_with(user_id=25)
    mock_map_repo.get_restaurant_basic_info.assert_called_once_with(restaurant_id=5)
    mock_queue_repo.remove_from_queue.assert_called_once_with(restaurant_id=5, user_id=25)
    
# 測試離開排隊因 不在排隊隊伍中 而失敗
def test_leave_restaurant_waiting_queue_NotInQueueError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊

    # Act & Assert
    with pytest.raises(NotInQueueError):
        queue_service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_repo.remove_from_queue.assert_not_called()

# 測試離開排隊因 排隊的隊伍與要退出的隊伍不一致 而失敗
def test_leave_restaurant_waiting_queue_NotInCorrectQueueError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30) # 使用者排餐廳5的隊伍


    # Act & Assert
    with pytest.raises(NotInQueueError):
        queue_service.leave_restaurant_waiting_queue(restaurant_id=2, user_id=25) #但是卻要離開餐廳2
    mock_queue_repo.remove_from_queue.assert_not_called()

# 測試離開排隊因 餐廳找不到 而失敗
def test_leave_restaurant_waiting_queue_RestaurantNotFoundError(queue_service, mock_repos):
    # Act & Assert
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, restaurant_id=5, user_id=25, ticket_number=30) # 使用者有排隊
    mock_map_repo.get_restaurant_basic_info.return_value = None     # 餐廳不存在

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        queue_service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_repo.remove_from_queue.assert_not_called()





""""""
# 測試取得排隊狀態成功案例
def test_get_queue_status_Success(queue_service, mock_repos):
    # Arrange
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

    # Act
    result = queue_service.get_queue_status(restaurant_id=4)

    # Assert
    assert result.restaurant_id == 4
    assert result.restaurant_name == "麥克小姐"
    assert result.current_number == 105
    assert result.total_waiting == 5
    assert result.avg_wait_time == int(5 * (10/2))  # = 25

# 測試取得排隊狀態因 餐廳找不到 而失敗
def test_get_queue_status_RestaurantNotFoundError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = None # 餐廳不存在

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        queue_service.get_queue_status(999)




""""""
# 測試取得餐廳叫號資訊成功案例--隊伍中 有人 在排這家餐廳
def test_get_queue_next_Success(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = True # 餐廳不存在

    mock_queue_runtime_repo.get_current_ticket_number.return_value=20
    mock_queue_repo.get_next_queue_to_call.return_value= 22
    mock_queue_repo.get_total_waiting.return_value=5
    # Act
    response= queue_service.get_queue_next(restaurant_id= 2)
    # Assert
    assert response.current_number == 20
    assert response.next_queue_to_call == 22
    assert response.total_waiting == 5

# 測試取得餐廳叫號資訊成功案例--隊伍中 沒人 在排這家餐廳
def test_get_queue_next_NoOneInQueSuccess(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = True # 餐廳存在

    mock_queue_runtime_repo.get_current_ticket_number.return_value= 20
    mock_queue_repo.get_next_queue_to_call.return_value= None
    mock_queue_repo.get_total_waiting.return_value=0
    # Act
    response= queue_service.get_queue_next(restaurant_id= 2)
    # Assert
    assert response.current_number == 20
    assert response.next_queue_to_call == 20
    assert response.total_waiting == 0

# 測試取得餐廳叫號因 餐廳找不到 而失敗
def test_get_queue_next_RestaurantNotFoundError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_map_repo.get_restaurant_basic_info.return_value = None # 餐廳不存在

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        queue_service.get_queue_next(999)




""""""
# 測試取得使用者排隊資訊成功案例
def test_get_user_queue_status_Success(queue_service, mock_repos):
    # Arrange
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
    # Act
    response= queue_service.get_user_queue_status(user_id=123)
    # Assert
    assert response.ticket_number == 30
    assert response.estimated_wait_time == 6*(10/2)
    assert response.restaurant_name == "麥克小姐"

def test_get_user_queue_status_NotInQueueError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = None    # 使用者有排隊
    # Act & Assert
    with pytest.raises(NotInQueueError):
        queue_service.get_user_queue_status(user_id=123)

def test_get_user_queue_status_RestaurantNotFoundError(queue_service, mock_repos):
    # Arrange
    mock_queue_repo, mock_queue_runtime_repo, mock_map_repo = mock_repos

    mock_queue_repo.get_user_current_queue.return_value = QueueEntity(queue_id=1, 
                                                                      restaurant_id=1, 
                                                                      user_id=123, 
                                                                      ticket_number=30)   # 使用者沒排隊
    mock_map_repo.get_restaurant_basic_info.return_value = None #餐廳找不到
    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        queue_service.get_user_queue_status(user_id=123)