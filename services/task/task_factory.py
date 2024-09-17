from typing import Dict, List
import uuid
from services.task.task import Task
from services.task.simple_task import SimpleTask
from services.task.scheduled_task import ScheduledTask
from services.task.periodic_task import PeriodicTask
from importlib import import_module

class TaskFactory:
    @staticmethod
    def create_task(task_id: uuid.UUID, description: str, command: Dict, node_ids: List[str], **kwargs) -> Task:
            if not kwargs:
                return SimpleTask(task_id, description, command, node_ids, **kwargs)
            elif 'scheduled_time' in kwargs and len(kwargs) == 1:
                scheduled_time = kwargs['scheduled_time']
                return ScheduledTask(task_id, description, command, node_ids, scheduled_time, **kwargs)
            elif 'interval' in kwargs and 'start_time' in kwargs:
                interval = kwargs['interval']
                start_time = kwargs['start_time']
                end_time = kwargs.get('end_time')
                return PeriodicTask(task_id, description, command, node_ids, interval, start_time, end_time, **kwargs)
            else:
                return SimpleTask(task_id, description, command, node_ids, **kwargs)
