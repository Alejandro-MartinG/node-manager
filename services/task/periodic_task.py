import threading
from datetime import datetime, timedelta
from typing import List, Optional
from services.task.task import Task


class PeriodicTask(Task):
    def __init__(self, task_id: str, description: str, command: str, node_ids: List[str], interval: timedelta, start_time: datetime, end_time: Optional[datetime] = None):
        super().__init__(task_id, description, command, node_ids)
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.thread = threading.Thread(target=self.run)
        self.running = False
        self.last_execution = None

    def get_additional_info(self) -> List[str]:
        return [
            f"Interval: {self.interval}",
            f"Next Execution: {self.next_execution_time}",
            f"End Time: {self.end_time or 'Not set'}"
        ]