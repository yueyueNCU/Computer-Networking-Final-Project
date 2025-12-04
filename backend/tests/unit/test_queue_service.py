import pytest
from unittest.mock import MagicMock
from app.services.queue_service import QueueService
from app.interfaces.queue_interface import IQueueRepository,IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.domain.errors import QueueAlreadyJoinedError,NotInQueueError, RestaurantNotFoundError
# 測試加入排隊成功案例
def test_join_restaurant_waiting_queue_success():
    waiting_count=3
    obtain_ticket_number=12
    metrics=[8,10] # Tuple[int, int]: (avg_dining_time, total_seats)
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo= MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    mock_map_repo.check_exists.return_value = True # 餐廳存在
    mock_queue_repo.get_total_waiting.return_value = waiting_count
    mock_queue_runtime_repo.get_next_ticket_number.return_value = obtain_ticket_number
    mock_queue_runtime_repo.get_metrics.return_value = metrics
    mock_queue_repo.add_to_queue.return_value = True

    service = QueueService(queue_repo=mock_queue_repo, queue_runtime_repo=mock_queue_runtime_repo, map_repo=mock_map_repo)
    # Act
    join_response = service.join_restaurant_waiting_queue(restaurant_id=5, user_id= 25)
    # Assert
    assert join_response.ticket_number == obtain_ticket_number
    assert join_response.people_ahead == waiting_count
    assert join_response.estimated_wait_time == int(waiting_count* (metrics[0]/metrics[1]))
    mock_queue_runtime_repo.increment_next_ticket_number.assert_called_once_with(restaurant_id=5)
    
# 測試加入排隊因 餐廳找不到 而失敗
def test_join_restaurant_waiting_queue_notFound():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊
    mock_map_repo.check_exists.return_value = False  # 餐廳不存在

    service = QueueService(
        queue_repo=mock_queue_repo,
        queue_runtime_repo=mock_queue_runtime_repo,
        map_repo=mock_map_repo
    )

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        service.join_restaurant_waiting_queue(restaurant_id=999, user_id=25)
    mock_queue_runtime_repo.increment_next_ticket_number.assert_not_called()

# 測試加入排隊因 已經在排隊隊伍中 而失敗
def test_join_restaurant_waiting_queue_alreadyInQueue():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = True # 使用者有排隊

    service = QueueService(
        queue_repo=mock_queue_repo,
        queue_runtime_repo=mock_queue_runtime_repo,
        map_repo=mock_map_repo
    )

    # Act & Assert
    with pytest.raises(QueueAlreadyJoinedError):
        service.join_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_runtime_repo.increment_next_ticket_number.assert_not_called()
        


""""""
# 測試離開排隊成功案例
def test_leave_restaurant_waiting_queue_success():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = 5 # 使用者排餐廳5的隊伍
    mock_map_repo.check_exists.return_value = True     # 餐廳存在

    service = QueueService(
        queue_repo=mock_queue_repo,
        queue_runtime_repo=mock_queue_runtime_repo,
        map_repo=mock_map_repo
    )

    # Act
    service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)

    # Assert
    mock_queue_repo.get_user_current_queue.assert_called_once_with(user_id=25)
    mock_map_repo.check_exists.assert_called_once_with(restaurant_id=5)
    mock_queue_repo.remove_from_queue.assert_called_once_with(restaurant_id=5, user_id=25)
    
# 測試離開排隊因 不在排隊隊伍中 而失敗
def test_leave_queue_notInAnyQueue():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = None # 使用者沒排隊

    service = QueueService(
        queue_repo=mock_queue_repo,
        queue_runtime_repo=mock_queue_runtime_repo,
        map_repo=mock_map_repo
    )

    # Act & Assert
    with pytest.raises(NotInQueueError):
        service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_repo.remove_from_queue.assert_not_called()

# 測試離開排隊因 排隊的隊伍與要退出的隊伍不一致 而失敗
def test_leave_queue_notInCorrectQueue():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = 2 # 使用者排餐廳2的隊伍

    service = QueueService(
        queue_repo=mock_queue_repo,
        queue_runtime_repo=mock_queue_runtime_repo,
        map_repo=mock_map_repo
    )

    # Act & Assert
    with pytest.raises(NotInQueueError):
        service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_repo.remove_from_queue.assert_not_called()

# 測試離開排隊因 餐廳找不到 而失敗
def test_leave_queue_restaurant_notFound():
    # Act & Assert
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_queue_repo.get_user_current_queue.return_value = True # 使用者有排隊
    mock_map_repo.check_exists.return_value = False     # 餐廳不存在

    service = QueueService(
        queue_repo=mock_queue_repo,
        queue_runtime_repo=mock_queue_runtime_repo,
        map_repo=mock_map_repo
    )

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        service.leave_restaurant_waiting_queue(restaurant_id=5, user_id=25)
    mock_queue_repo.remove_from_queue.assert_not_called()





""""""
# 測試取得排隊狀態成功案例
def test_get_queue_status_success():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_map_repo.check_exists.return_value = True # 使用者有排隊
    mock_map_repo.get_restaurant_basic_info.return_value = {
        "restaurant_name": "麥克小姐"
    }

    mock_runtime_repo.get_current_ticket_number.return_value = 105
    mock_queue_repo.get_total_waiting.return_value = 5
    mock_runtime_repo.get_metrics.return_value = (10, 2)  # avg_dining_time, total_seats

    service = QueueService(mock_queue_repo, mock_runtime_repo, mock_map_repo)

    # Act
    result = service.get_queue_status(restaurant_id=4)

    # Assert
    assert result.restaurant_id == 4
    assert result.restaurant_name == "麥克小姐"
    assert result.current_number == 105
    assert result.total_waiting == 5
    assert result.avg_wait_time == int(5 * (10/2))  # = 25

# 測試取得排隊狀態因 餐廳找不到 而失敗
def test_get_queue_status_restaurant_not_found():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_map_repo.check_exists.return_value = False # 餐廳不存在

    service = QueueService(mock_queue_repo, mock_runtime_repo, mock_map_repo)

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        service.get_queue_status(999)



""""""
# 測試取得餐廳叫號資訊成功案例--隊伍中 有人 在排這家餐廳
def test_get_queue_next_success():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_map_repo.check_exists.return_value = True # 餐廳不存在

    mock_runtime_repo.get_current_ticket_number.return_value= 20
    mock_queue_repo.get_next_queue_to_call.return_value= 22
    mock_queue_repo.get_total_waiting.return_value=5
    service = QueueService(mock_queue_repo, mock_runtime_repo, mock_map_repo)
    # Act
    response= service.get_queue_next(restaurant_id= 2)
    # Assert
    assert response.current_number == 20
    assert response.next_queue_to_call == 22
    assert response.total_waiting == 5

# 測試取得餐廳叫號資訊成功案例--隊伍中 沒人 在排這家餐廳
def test_get_queue_next_NoOneInQueSuccess():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_map_repo.check_exists.return_value = True # 餐廳不存在

    mock_runtime_repo.get_current_ticket_number.return_value= 20
    mock_queue_repo.get_next_queue_to_call.return_value= None
    mock_queue_repo.get_total_waiting.return_value=0
    service = QueueService(mock_queue_repo, mock_runtime_repo, mock_map_repo)
    # Act
    response= service.get_queue_next(restaurant_id= 2)
    # Assert
    assert response.current_number == 20
    assert response.next_queue_to_call == 20
    assert response.total_waiting == 0

# 測試取得餐廳叫號因 餐廳找不到 而失敗
def test_get_queue_next_restaurant_not_found():
    # Arrange
    mock_queue_repo = MagicMock(spec=IQueueRepository)
    mock_map_repo = MagicMock(spec=IMapRepository)
    mock_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)

    mock_map_repo.check_exists.return_value = False # 餐廳不存在

    service = QueueService(mock_queue_repo, mock_runtime_repo, mock_map_repo)

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        service.get_queue_next(999)
