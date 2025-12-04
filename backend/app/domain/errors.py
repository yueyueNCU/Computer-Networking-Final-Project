# app/domain/errors.py
class DomainError(Exception):
    """Base class for domain-level errors"""
    code: str
    message: str

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

class TableNotFoundError(DomainError):
    def __init__(self):
        super().__init__("TABLE_NOT_FOUND", "Table does not exist.")

class TableInvalidActionError(DomainError):
    def __init__(self, current_status: str):
        super().__init__("TABLE_INVALID_ACTION", f"Cannot set a table that is already {current_status}.")

class QueueAlreadyJoinedError(DomainError):
    def __init__(self):
        super().__init__("QUEUE_ALREADY_JOINED", "You are already in the queue.")

class RestaurantNotFoundError(DomainError):
    def __init__(self):
        super().__init__("RESTAURANT_NOT_FOUND", "Restaurant does not exist.")

class NotInQueueError(DomainError):
    def __init__(self, message: str = "User is not in queue."):
        super().__init__("NOT_IN_QUEUE", message)
