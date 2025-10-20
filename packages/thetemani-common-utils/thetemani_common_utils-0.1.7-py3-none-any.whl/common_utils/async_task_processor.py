import asyncio
import queue
import threading
from typing import Callable


class AsyncTaskProcessor:
    def __init__(self):
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self._process_queue, daemon=True)
        self.worker.start()
    
    def _process_queue(self):
        while True:
            try:
                task_func, args, kwargs = self.queue.get()
                asyncio.run(task_func(*args, **kwargs))
                self.queue.task_done()
            except Exception as e:
                pass
    
    def add_task(self, async_func: Callable, *args, **kwargs):
        """Add an async task to the queue"""
        try:
            self.queue.put_nowait((async_func, args, kwargs))
        except Exception as e:
            pass


# Global async task processor
task_processor = AsyncTaskProcessor()