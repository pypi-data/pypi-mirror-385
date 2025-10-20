import time
from typing import Optional, Callable,List
from .task_processor import TaskProcessor
from .infer_service import InferService

from .models import (
    PostAsyncInferRequest,
    PostAsyncInferResponse,
    TaskResponse,
)
from .constants import (
    DEFAULT_API_ENDPOINT,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_MAX_WAIT_TIME,
    DEFAULT_MAX_QUEUE_SIZE
)

class AsyncInfer:
    def __init__(
            self,
            token: str,
            endpoint: str = DEFAULT_API_ENDPOINT,
            worker_num: int = 100,
            polling_interval: int = DEFAULT_POLLING_INTERVAL,
            max_wait_time: int = DEFAULT_MAX_WAIT_TIME,
            max_queue_size: int = DEFAULT_MAX_QUEUE_SIZE,
            timeout: int = 3600,
            callback: Optional[Callable[[TaskResponse], None]] = None,
    ):

        self.start_time = time.time()
        self.infer_service = InferService(
            token=token,
            worker_num=worker_num,
            timeout=timeout,
            polling_interval=polling_interval,
            endpoint=endpoint,
            max_wait_time=max_wait_time,
            max_queue_size=max_queue_size
        )

        # 监听队列，处理数据
        self.processor = TaskProcessor(
            infer_service=self.infer_service,
            worker_num=worker_num,
            callback=callback
        )
        self.processor.start()

    def post_async_infer(self, request: PostAsyncInferRequest) -> PostAsyncInferResponse:
        return self.infer_service.post_async_infer(request)

    def post_async_infer_batch(self,requests: List[PostAsyncInferRequest],max_workers: int = 10) -> List[PostAsyncInferResponse]:
        return self.infer_service.post_async_infer_batch(requests, max_workers)

    def stop_processor(self):
        self.processor.stop()
