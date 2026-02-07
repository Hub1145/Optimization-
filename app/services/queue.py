from celery import Celery
from app.config import settings

class QueueService:
    """Celery task queue service"""

    def __init__(self):
        self.celery = Celery(
            "worker",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND
        )

    def push_task(self, task_name: str, *args, **kwargs):
        return self.celery.send_task(task_name, args=args, kwargs=kwargs)

    def get_task_status(self, task_id: str):
        return self.celery.AsyncResult(task_id).status

    def get_task_result(self, task_id: str):
        return self.celery.AsyncResult(task_id).result
