from typing import Optional
from app.interfaces.queue_interface import IQueueService,IQueueRepository,IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.domain.errors import NotInQueueError, QueueAlreadyJoinedError, RestaurantNotFoundError
from app.schemas.queue_schema import QueueStatusResponse,JoinQueueResponse

class QueueService(IQueueService):

    def __init__(self, queue_repo: IQueueRepository, queue_runtime_repo: IQueueRuntimeRepository, map_repo: IMapRepository):
        self.queue_repo=queue_repo
        self.queue_runtime_repo=queue_runtime_repo
        self.map_repo=map_repo

    def join_restaurant_waiting_queue(self, restaurant_id: int, user_id: int) -> JoinQueueResponse:
        # user 是否已在任何餐廳排隊
        already_in_queue = self.queue_repo.get_user_current_queue(user_id=user_id)
        if already_in_queue == True:
            raise QueueAlreadyJoinedError()
        # 餐廳是否存在
        exist_restaurant = self.map_repo.check_exists(restaurant_id=restaurant_id)   
        if exist_restaurant == False:
            raise RestaurantNotFoundError()
        # 排隊計數
        people_ahead = self.queue_runtime_repo.get_waiting_count(restaurant_id=restaurant_id)
        # 取得票號
        obtain_ticket_number = self.queue_runtime_repo.get_next_ticket_number(restaurant_id=restaurant_id)
        # 加入排隊
        self.queue_repo.add_to_queue(
            restaurant_id=restaurant_id, 
            user_id=user_id, 
            ticket_number=obtain_ticket_number
        )
        self.queue_runtime_repo.increment_next_ticket_number(restaurant_id=restaurant_id)
        self.queue_runtime_repo.increment_waiting_count(restaurant_id=restaurant_id)
        # 計算預估時間
        metrics= self.queue_runtime_repo.get_metrics(restaurant_id=restaurant_id)
        estimated_wait_time = int(people_ahead* (metrics[0]/metrics[1]))

        return JoinQueueResponse(
            ticket_number=obtain_ticket_number,
            people_ahead=people_ahead,
            estimated_wait_time=estimated_wait_time
        )
    
    def leave_restaurant_waiting_queue(self, restaurant_id: int, user_id: int) -> None:
        # user 是否已在任何餐廳排隊
        already_in_queue = self.queue_repo.get_user_current_queue(user_id=user_id)
        if already_in_queue == None:
            raise NotInQueueError()
        # 餐廳是否存在
        exist_restaurant = self.map_repo.check_exists(restaurant_id=restaurant_id)   
        if exist_restaurant == False:
            raise RestaurantNotFoundError()
        # 離開排隊
        self.queue_repo.remove_from_queue(restaurant_id=restaurant_id, user_id=user_id)
        self.queue_runtime_repo.decrement_waiting_count(restaurant_id=restaurant_id)

    def get_queue_status(self, restaurant_id: int) -> QueueStatusResponse:
        # 1. 檢查餐廳是否存在
        exist_restaurant = self.map_repo.check_exists(restaurant_id=restaurant_id)
        if exist_restaurant is False:
            raise RestaurantNotFoundError()

        # 2. 拿餐廳名稱
        restaurant = self.map_repo.get_restaurant_basic_info(restaurant_id)

        # 3. 取得目前叫到幾號
        current_number = self.queue_runtime_repo.get_current_ticket_number(restaurant_id)

        # 4. 取得等待組數 N
        total_waiting = self.queue_runtime_repo.get_waiting_count(restaurant_id)

        # 5. 計算平均等待時間
        # metrics: (avg_dining_time, total_seats)
        avg_dining_time, total_seats = self.queue_runtime_repo.get_metrics(restaurant_id)
        avg_wait_time = int(total_waiting * (avg_dining_time / total_seats))

        # 6. 回傳
        return QueueStatusResponse(
            restaurant_id=restaurant_id,
            restaurant_name=restaurant["restaurant_name"],
            current_number=current_number,
            total_waiting=total_waiting,
            avg_wait_time=avg_wait_time
        )
