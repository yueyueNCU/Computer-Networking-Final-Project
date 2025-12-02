import pytest
from unittest.mock import MagicMock
from app.services.map_service import MapService
from app.interface.map_interface import IMapRepository
from app.interface.queue_interface import IQueueRepository

def test_get_nearby_markers_status_logic():
    # Arrange
    mock_map_repository=MagicMock(spec=IMapRepository)
    mock_queue_repository=MagicMock(spec=IQueueRepository)

    mock_map_repository.find_restaurant_in_range.return_value = [
        {"restaurant_id": 1, "restaurant_name":"麥克小姐", "lat":24.1, "lng":121.1, "image_url":"http://text.png", "average_price":"150-300", "specialties":"義大利麵、漢堡"},
        {"restaurant_id": 2, "restaurant_name":"寶咖咖", "lat":24.2, "lng":121.2, "image_url":"http://text2.png", "average_price":"95-150", "specialties":"雞排飯"}
    ]
    mock_queue_repository.get_current_restaurant_queue.side_effect = lambda id: 16 if id == 1 else 0

    service= MapService(map_repo=mock_map_repository, queue_repo=mock_queue_repository)
    # Act
    markers = service.get_nearby_markers(24, 121, 10)
    # Assert
    assert len(markers) == 2

    assert markers[0].restaurant_id == 1
    assert markers[0].status == "red"

    assert markers[1].restaurant_id == 2
    assert markers[1].status == "green"

