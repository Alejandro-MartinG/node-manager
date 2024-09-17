import logging
import threading
import queue
import os
from typing import Callable, Any

class ThreadService:
    default_threads = 8

    def __init__(self):
        self.max_threads = int(os.environ.get('MAX_THREADS', self.default_threads))
        self.semaphore = threading.Semaphore(self.max_threads)
        self.task_queue = queue.Queue()
        self.results = {}
        self.lock = threading.Lock()

    def worker(self):
        while True:
            task_id, func, args, kwargs = self.task_queue.get()
            with self.semaphore:
                try:
                    result = func(*args, **kwargs)
                    with self.lock:
                        self.results[task_id] = result
                except Exception as e:
                    with self.lock:
                        self.results[task_id] = e
                finally:
                    self.task_queue.task_done()

    def run_workers(self):
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

    def run_in_background_thread(self):
        """
        Starts a worker in a separate background thread.
        This is useful for non-blocking operations.
        """
        if not self.is_running:
            logging.debug("Starting worker in background thread.")
            self.should_exit = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            logging.debug("Started")

    def submit_task(self, func: Callable[..., Any], *args, **kwargs) -> int:
        task_id = len(self.results)
        self.task_queue.put((task_id, func, args, kwargs))
        return task_id

    def get_result(self, task_id: int) -> Any:
        while True:
            with self.lock:
                if task_id in self.results:
                    result = self.results[task_id]
                    del self.results[task_id]
                    if isinstance(result, Exception):
                        raise result
                    return result
            threading.Event().wait(0.1)  # Small delay to prevent busy waiting

    def wait_all(self):
        self.task_queue.join()

# Usage example
if __name__ == "__main__":
    import time

    def example_task(x):
        time.sleep(1)  # Simulate some work
        return x * x

    # Set the MAX_THREADS environment variable (you would typically do this outside the script)
    os.environ['MAX_THREADS'] = '8'

    manager = ThreadService()
    manager.start_workers()

    # Submit tasks
    task_ids = [manager.submit_task(example_task, i) for i in range(10)]

    # Get results
    for task_id in task_ids:
        result = manager.get_result(task_id)
        print(f"Result for task {task_id}: {result}")

    # Wait for all tasks to complete
    manager.wait_all()
