import pytest
from unittest.mock import MagicMock
from app.services.table_service import TableService
from app.domain.errors import RestaurantNotFoundError, TableInvalidActionError, TableNotFoundError, NotInQueueError
from app.interfaces.map_interface import IMapRepository
from app.interfaces.queue_interface import IQueueRepository, IQueueRuntimeRepository
from app.interfaces.table_interface import ITableRepository
from app.domain.entities import MapEntity, TableEntity, QueueEntity
@pytest.fixture
def mock_repos():
    table_repo = MagicMock(spec=ITableRepository)
    map_repo = MagicMock(spec=IMapRepository)
    queue_repo = MagicMock(spec=IQueueRepository)
    queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)
    return table_repo, map_repo, queue_repo, queue_runtime_repo

@pytest.fixture
def table_service(mock_repos):
    table_repo, map_repo, queue_repo, queue_runtime_repo = mock_repos
    return TableService(
        table_repo=table_repo,
        map_repo=map_repo,
        queue_repo=queue_repo,
        queue_runtime_repo=queue_runtime_repo,
    )

def test_get_restaurant_seats_Success(table_service, mock_repos):
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
    response = table_service.get_restaurant_seats(restaurant_id=2)
    # Assert
    assert response.restaurant_id == 2
    assert response.restaurant_name == "麥克小姐"
    assert len(response.seats) == 2
    assert response.seats[0].label == "1桌"
# 2. 測試取得餐廳座位失敗 (餐廳不存在)
def test_get_restaurant_seats_RestaurantNotFoundError(table_service, mock_repos):
    # Arrange
    table_repo, map_repo, _, _ = mock_repos
    map_repo.get_restaurant_basic_info.return_value = None # 模擬找不到餐廳

    # Act & Assert
    with pytest.raises(RestaurantNotFoundError):
        table_service.get_restaurant_seats(restaurant_id=999)




# 3. 測試更新桌況失敗 (桌子不存在)
def test_update_table_status_TableNotFoundError(table_service, mock_repos):
    # Arrange
    table_repo, _, _, _ = mock_repos
    table_repo.get_table_by_id.return_value = None # 模擬找不到桌子

    # Act & Assert
    with pytest.raises(TableNotFoundError):
        table_service.update_table_status(restaurant_id=2, table_id=999, new_table_status="eating", queue_ticket_number=10)


# 4. 測試更新桌況失敗 (安全性檢查：桌子不屬於該餐廳)
def test_update_table_status_SecurityCheckFailed(table_service, mock_repos):
    # Arrange
    table_repo, _, _, _ = mock_repos
    
    # 桌子實際上屬於 restaurant_id=1
    existing_table = TableEntity(
        table_id=10, restaurant_id=1, label="A1", x=0, y=0, status="empty"
    )
    table_repo.get_table_by_id.return_value = existing_table

    # Act & Assert
    # 我們試圖用 restaurant_id=2 去更新它，應該要報錯
    with pytest.raises(TableNotFoundError):
        table_service.update_table_status(restaurant_id=2, table_id=10, new_table_status="eating", queue_ticket_number=10)


# 5. 測試更新桌況失敗 (狀態未改變)
def test_update_table_status_TableInvalidActionError(table_service, mock_repos):
    # Arrange
    table_repo, _, _, _ = mock_repos
    
    # 桌子已經是 eating 狀態
    existing_table = TableEntity(
        table_id=10, restaurant_id=2, label="A1", x=0, y=0, status="eating"
    )
    table_repo.get_table_by_id.return_value = existing_table

    # Act & Assert
    # 試圖再次設為 eating
    with pytest.raises(TableInvalidActionError):
        table_service.update_table_status(restaurant_id=2, table_id=10, new_table_status="eating", queue_ticket_number=10)


# 6. 情境 A: 顧客入座成功 (empty -> eating)
def test_update_table_status_CheckIn_Success(table_service, mock_repos):
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

    # Act
    response = table_service.update_table_status(
        restaurant_id=restaurant_id, 
        table_id=table_id, 
        new_table_status="eating", 
        queue_ticket_number=ticket_number
    )

    # Assert
    # 驗證回傳
    assert response.table_id == table_id
    assert response.new_status == "eating"
    
    # 驗證副作用 (Side Effects)
    queue_repo.remove_from_queue.assert_called_once_with(restaurant_id=restaurant_id, user_id=user_id)
    queue_runtime_repo.set_current_ticket_number.assert_called_once_with(restaurant_id=restaurant_id, ticket_number=ticket_number)
    table_repo.update_status.assert_called_once_with(table_id=table_id, new_table_status="eating", queue_ticket_number=ticket_number)


# 7. 情境 A 失敗: 顧客入座但找不到排隊資料 (NotInQueueError)
def test_update_table_status_CheckIn_NotInQueueError(table_service, mock_repos):
    # Arrange
    table_repo, _, queue_repo, _ = mock_repos
    
    restaurant_id = 2
    
    # 1. 桌子存在
    table_repo.get_table_by_id.return_value = TableEntity(
        table_id=10, restaurant_id=restaurant_id, label="A1", x=0, y=0, status="empty"
    )
    
    # 2. 排隊資料不存在 (None)
    queue_repo.get_user_current_queue_by_restaurantId_and_ticketNumber.return_value = None

    # Act & Assert
    with pytest.raises(NotInQueueError):
        table_service.update_table_status(
            restaurant_id=restaurant_id, 
            table_id=10, 
            new_table_status="eating", 
            queue_ticket_number=50
        )


# 8. 情境 B: 顧客離座/清桌成功 (eating -> empty)
def test_update_table_status_CheckOut_Success(table_service, mock_repos):
    # Arrange
    table_repo, _, queue_repo, queue_runtime_repo = mock_repos
    
    restaurant_id = 2
    table_id = 10
    
    # 模擬桌子正在使用中
    table_repo.get_table_by_id.return_value = TableEntity(
        table_id=table_id, restaurant_id=restaurant_id, label="A1", x=0, y=0, status="eating"
    )

    # Act
    # 離座時，ticket_number 通常不重要 (或是傳 0)
    response = table_service.update_table_status(
        restaurant_id=restaurant_id, 
        table_id=table_id, 
        new_table_status="empty", 
        queue_ticket_number=0
    )

    # Assert
    assert response.new_status == "empty"
    
    # 關鍵驗證：離座不應該去動排隊系統
    queue_repo.remove_from_queue.assert_not_called()
    queue_runtime_repo.set_current_ticket_number.assert_not_called()
    
    # 驗證桌況更新被呼叫
    table_repo.update_status.assert_called_once_with(table_id=table_id, new_table_status="empty", queue_ticket_number=0)