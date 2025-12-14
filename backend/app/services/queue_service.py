from typing import Optional
from app.interfaces.queue_interface import IQueueService,IQueueRepository,IQueueRuntimeRepository
from app.interfaces.map_interface import IMapRepository
from app.domain.errors import NotInQueueError, QueueAlreadyJoinedError, RestaurantNotFoundError
from app.schemas.queue_schema import QueueStatusResponse,JoinQueueResponse,QueueNextResponse, UserQueueStatusResponse

class QueueService(IQueueService):

    def __init__(self, queue_repo: IQueueRepository, queue_runtime_repo: IQueueRuntimeRepository, map_repo: IMapRepository):
        self.queue_repo=queue_repo
        self.queue_runtime_repo=queue_runtime_repo
        self.map_repo=map_repo

    def join_restaurant_waiting_queue(self, restaurant_id: int, user_id: int) -> JoinQueueResponse:
        # user 是否已在任何餐廳排隊
        queue_ticket = self.queue_repo.get_user_current_queue(user_id=user_id)
        if  queue_ticket is not None:
            raise QueueAlreadyJoinedError()
        # 餐廳是否存在
        restaurant = self.map_repo.get_restaurant_basic_info(restaurant_id=restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError()
        # 排隊計數
        people_ahead = self.queue_repo.get_total_waiting(restaurant_id=restaurant_id)
        # 取得票號
        obtain_ticket_number = self.queue_runtime_repo.get_next_ticket_number(restaurant_id=restaurant_id)
        # 加入排隊
        self.queue_repo.add_to_queue(
            restaurant_id=restaurant_id, 
            user_id=user_id, 
            ticket_number=obtain_ticket_number
        )
        self.queue_runtime_repo.increment_next_ticket_number(restaurant_id=restaurant_id)
        # 計算預估時間
        metrics= self.queue_runtime_repo.get_metrics(restaurant_id=restaurant_id)
        avg_dining_time= metrics.average_wait_time
        total_seats=metrics.table_number

        estimated_wait_time = int(people_ahead* (avg_dining_time/total_seats))

        return JoinQueueResponse(
            ticket_number=obtain_ticket_number,
            people_ahead=people_ahead,
            estimated_wait_time=estimated_wait_time
        )
    
    def leave_restaurant_waiting_queue(self, restaurant_id: int, user_id: int) -> None:
        # user 是否已在任何餐廳排隊
        queue_ticket = self.queue_repo.get_user_current_queue(user_id=user_id)
        if queue_ticket is None:
            raise NotInQueueError()
        # 餐廳是否存在
        restaurant = self.map_repo.get_restaurant_basic_info(restaurant_id=restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError()
        if queue_ticket.restaurant_id != restaurant_id:
            raise NotInQueueError("User is not in this restaurant's queue.")
        # 離開排隊
        self.queue_repo.remove_from_queue(restaurant_id=restaurant_id, user_id=user_id)

    def get_queue_status(self, restaurant_id: int) -> QueueStatusResponse:
        # 1. 檢查餐廳是否存在
        restaurant = self.map_repo.get_restaurant_basic_info(restaurant_id=restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError()

        # 2. 取得目前叫到幾號
        current_number = self.queue_runtime_repo.get_current_ticket_number(restaurant_id=restaurant_id)

        # 3. 取得等待組數 N
        total_waiting = self.queue_repo.get_total_waiting(restaurant_id=restaurant_id)

        # 4. 計算平均等待時間
        # metrics: (avg_dining_time, total_seats)
        metrics= self.queue_runtime_repo.get_metrics(restaurant_id=restaurant_id)
        # 避免除以零的錯誤 (防呆)
        avg_wait_time = 0
        if metrics.table_number > 0:
            avg_wait_time = int(total_waiting * (metrics.average_wait_time / metrics.table_number))
        # 5. 回傳
        return QueueStatusResponse(
            restaurant_id=restaurant_id,
            restaurant_name=restaurant.restaurant_name,
            current_number=current_number,
            total_waiting=total_waiting,
            avg_wait_time=avg_wait_time
        )
    
    def get_queue_next(self, restaurant_id: int) -> QueueNextResponse:
        # 1. 檢查餐廳是否存在
        restaurant = self.map_repo.get_restaurant_basic_info(restaurant_id=restaurant_id)
        if restaurant is None :
            raise RestaurantNotFoundError()
        # 3. 取得目前叫到幾號
        current_number = self.queue_runtime_repo.get_current_ticket_number(restaurant_id=restaurant_id)
        next_queue_to_call = self.queue_repo.get_next_queue_to_call(restaurant_id=restaurant_id)
        if next_queue_to_call is None:
            next_queue_to_call = current_number

        total_waiting = self.queue_repo.get_total_waiting(restaurant_id=restaurant_id)
        return QueueNextResponse(
            current_number=current_number,
            next_queue_to_call=next_queue_to_call,
            total_waiting=total_waiting
        )
    def get_user_queue_status(self, user_id: int) -> UserQueueStatusResponse:
        # user 是否已在任何餐廳排隊
        queue_ticket = self.queue_repo.get_user_current_queue(user_id=user_id)
        if queue_ticket is None:
            raise NotInQueueError()
        restaurant_id= queue_ticket.restaurant_id
        user_id = queue_ticket.user_id

        restaurant = self.map_repo.get_restaurant_basic_info(restaurant_id=restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError()
        people_ahead= self.queue_repo.get_people_ahead(restaurant_id=restaurant_id, user_id=user_id)

        metrics= self.queue_runtime_repo.get_metrics(restaurant_id=restaurant_id)
        # 避免除以零的錯誤 (防呆)
        estimated_wait_time = 0
        if metrics.table_number > 0:
            estimated_wait_time = int(people_ahead * (metrics.average_wait_time / metrics.table_number))

        return UserQueueStatusResponse(
            restaurant_id=queue_ticket.restaurant_id,
            restaurant_name=restaurant.restaurant_name,
            ticket_number=queue_ticket.ticket_number,
            people_ahead=people_ahead,
            estimated_wait_time=estimated_wait_time
        )
