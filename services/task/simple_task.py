import uuid
from typing import List
from services.task.task import Task

class SimpleTask(Task):
    def __init__(self, id: uuid.UUID, description: str, task_command: str, nodes: List[str], remote_path: str=None, local_path: str=None):
        super().__init__(id, description, task_command, nodes, remote_path, local_path)

    def get_additional_info(self) -> List[str]:
        return []