import pytest
from unittest.mock import MagicMock
from app.services.table_service import TableService
from app.schemas.table_schema import TableDetail, UpdateTableStatusRequest, RestaurantSeatsResponse
from fastapi import HTTPException

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def table_service(mock_repo):
    return TableService(repo=mock_repo)

# --- 1. 取得餐廳座位表測試 ---

def test_get_restaurant_seats_success(table_service, mock_repo):
    # Arrange
    restaurant_id = 2
    # 模擬 Repo 回傳 Layout 物件 (因為你的 Service 呼叫 .get_layout)
    mock_layout = RestaurantSeatsResponse(
        restaurant_id=restaurant_id,
        restaurant_name="寶咖咖",
        seats=[
            TableDetail(table_id=101, label="A1", x=1, y=1, status="eating"),
            TableDetail(table_id=102, label="A2", x=2, y=1, status="empty")
        ]
    )
    mock_repo.get_layout.return_value = mock_layout

    # Act
    result = table_service.get_restaurant_seats(restaurant_id)

    # Assert
    assert result.restaurant_id == restaurant_id
    assert result.restaurant_name == "寶咖咖"
    assert len(result.seats) == 2
    mock_repo.get_layout.assert_called_once_with(restaurant_id)

def test_get_restaurant_seats_not_found(table_service, mock_repo):
    # Arrange: 找不到餐廳 (回傳 None)
    mock_repo.get_layout.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        table_service.get_restaurant_seats(999)
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Restaurant not found"


# --- 2. 更新座位狀態測試 ---

def test_update_status_eating_success(table_service, mock_repo):
    """測試成功更新狀態：入座"""
    # Arrange
    table_id = 101
    mock_seat = TableDetail(table_id=table_id, label="A1", x=1, y=1, status="empty")
    mock_repo.get_seat_by_id.return_value = mock_seat
    
    request = UpdateTableStatusRequest(action="eating", queue_ticket_number=100)

    # Act
    result = table_service.update_table_status(table_id, request)

    # Assert
    assert result.new_status == "eating"
    assert mock_seat.status == "eating" # 驗證物件屬性被修改了

def test_update_status_table_not_found(table_service, mock_repo):
    """測試錯誤：Table 不存在"""
    # Arrange
    mock_repo.get_seat_by_id.return_value = None
    request = UpdateTableStatusRequest(action="eating", queue_ticket_number=100)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        table_service.update_table_status(999, request)
    
    assert exc.value.status_code == 404
    assert exc.value.detail["code"] == "TABLE_NOT_FOUND"

def test_update_status_invalid_action(table_service, mock_repo):
    """測試錯誤：狀態重複 (原本 empty 又要設 empty)"""
    # Arrange
    # 模擬: 原本就是 empty
    mock_seat = TableDetail(table_id=101, label="A1", x=1, y=1, status="empty")
    mock_repo.get_seat_by_id.return_value = mock_seat
    
    request = UpdateTableStatusRequest(action="empty", queue_ticket_number=100)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        table_service.update_table_status(101, request)
    
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "TABLE_INVALID_ACTION"

def test_update_status_not_in_queue(table_service, mock_repo):
    """測試錯誤：票號錯誤"""
    # Arrange
    mock_seat = TableDetail(table_id=101, label="A1", x=1, y=1, status="empty")
    mock_repo.get_seat_by_id.return_value = mock_seat
    
    request = UpdateTableStatusRequest(action="eating", queue_ticket_number=999)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        table_service.update_table_status(101, request)
    
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "NOT_IN_QUEUE"