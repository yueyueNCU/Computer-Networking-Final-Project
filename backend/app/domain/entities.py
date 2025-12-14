from dataclasses import dataclass
from typing import Tuple
@dataclass
class QueueEntity:
    queue_id: int          
    restaurant_id: int
    user_id: int
    ticket_number: int

"""
以下是Queue表格，可參考

queue_id | restaurant_id | user_id | ticket_number
1        | 2             | 25      | 15
2        | 2             | 28      | 16
3        | 3             | 28      | 6
"""

@dataclass
class MapEntity:
    restaurant_id: int
    restaurant_name: str
    lat: float
    lng: float
    image_url: str
    average_price: Tuple[int, int]
    specialties: str

"""
    以下是Restaurant表格，可參考
    restaurant_id | restaurant_name | lat  | lng   | img_url                         | average_price | specialties
    2             | 麥麥小館         | 24.1 | 121.1 | https://example.com/burger.jpg  | [150, 300]    | 義大利麵、漢堡
    3             | 歐姆瑞斯         | 24.2 | 24.2  | https://example.com/rice.jpg    | [80, 150]     | 咖哩、焗烤飯
"""


@dataclass
class TableEntity:
    table_id: int
    restaurant_id: int
    label: str
    x: int
    y: int 
    status: str

"""
以下是Table表格，可參考

table_id | restaurant_id | label | x | y | status
5        | 2             | 1桌   | 1 | 1 | empty
6        | 3             | 1桌   | 1 | 2 | eating
7        | 2             | 5桌   | 1 | 5 | eating
8        | 3             | 2桌   | 1 | 4 | empty
"""