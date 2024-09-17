from typing import List
from services.task.task import Task
from datetime import datetime

class ScheduledTask(Task):
    def __init__(self, task_id: str, description: str, command: str, node_ids: List[str], scheduled_time: datetime):
        super().__init__(task_id, description, command, node_ids)
        self.scheduled_time = scheduled_time

    def get_additional_info(self) -> List[str]:
        return [f"Scheduled Time: {self.scheduled_time}"]