from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class IMapRepository(ABC):
    @abstractmethod
    def check_exists(self, restaurant_id: int) -> bool:
        """
        檢查餐廳是否存在 (對應 restaurant table)
        """
        pass

    @abstractmethod
    def get_restaurant_basic_info(self, restaurant_id: int) -> Optional[Dict]:
        """
        取得單一餐廳所有資訊
        # SQL: SELECT * FROM restaurants WHERE id = ?
        """
        pass

    @abstractmethod
    def get_all_restaurants(self) -> List[Dict]:
        """
        取得所有餐廳列表 (不需 lat, lng 參數)
        用於 API: GET /api/restaurants
        """
        pass

"""
以下是Restaurant表格，可參考
restaurant_id | restaurant_name | lat  | lng   | img_url                         | average_price | specialties
2             | 麥麥小館         | 24.1 | 121.1 | https://example.com/burger.jpg  | [150, 300]    | 義大利麵、漢堡
3             | 歐姆瑞斯         | 24.2 | 24.2  | https://example.com/rice.jpg    | [80, 150]     | 咖哩、焗烤飯
"""