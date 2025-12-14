import pytest
from unittest.mock import MagicMock
from app.services.map_service import MapService
from app.interfaces.map_interface import IMapRepository
from app.interfaces.queue_interface import IQueueRepository,IQueueRuntimeRepository
from app.interfaces.table_interface import ITableRepository
from app.domain.entities import MapEntity
from typing import Tuple
from app.domain.value_objects import RestaurantMetrics


@pytest.fixture
def mock_repos():
    """
    負責建立所有需要的 Mock Repository。
    回傳 Tuple: (mock_queue_repo, mock_runtime_repo, mock_map_repo)
    """
    queue_repo = MagicMock(spec=IQueueRepository)
    queue_runtime_repo = MagicMock(spec=IQueueRuntimeRepository)
    map_repo = MagicMock(spec=IMapRepository)
    table_repo = MagicMock(spec=ITableRepository)
    return map_repo, table_repo, queue_repo, queue_runtime_repo

@pytest.fixture
def map_service(mock_repos):
    """
    負責初始化 Service，並自動注入 mock_repos。
    測試函式只需要請求這個 fixture，就可以拿到已經裝好 Mock 的 Service。
    """
    map_repo, table_repo, queue_repo, queue_runtime_repo = mock_repos
    return MapService(
        map_repo=map_repo,
        table_repo=table_repo,
        queue_repo=queue_repo,
        queue_runtime_repo=queue_runtime_repo
    )



def test_get_restaurants(map_service, mock_repos):
    # --- 1. Arrange (準備環境) ---
    mock_map_repo, mock_table_repo, mock_queue_repo, mock_queue_runtime_repo = mock_repos
    # 假資料 (模擬 Repository 從資料庫撈出來的原始 Dict)
    fake_db_data = [
        MapEntity(
            restaurant_id = 2,
            restaurant_name = "麥克小姐",
            lat = 24.968, 
            lng = 121.192,
            image_url = "https://example.com/burger.jpg",
            average_price = (150,300),
            specialties = "義大利麵、漢堡",
        ),
        MapEntity(
            restaurant_id = 3,
            restaurant_name = "歐姆萊斯",
            lat = 24.970, 
            lng = 121.195,
            image_url = "https://example.com/rice.jpg",
            average_price = (80,150),
            specialties = "咖哩、豬排飯",
        )
    ]

    # 設定 Mock 行為
    mock_map_repo.get_all_restaurants.return_value = fake_db_data
    mock_queue_repo.get_total_waiting.return_value = 3
    mock_table_repo.get_restaurant_remaining_table.return_value = 8
    mock_queue_runtime_repo.get_metrics.return_value = RestaurantMetrics(average_wait_time=15, table_number=10)

    # --- 2. Act (執行測試) ---
    result = map_service.get_restaurants()

    # --- 3. Assert (驗證結果) ---
    assert len(result) == 2
    assert result[0].restaurant_name == "麥克小姐"
    assert result[1].status == "yellow"

    # 驗證 Service 是否呼叫了正確的 Repo 方法
    mock_map_repo.get_all_restaurants.assert_called_once()