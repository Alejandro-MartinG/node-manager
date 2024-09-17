import uuid
from abc import ABC, abstractmethod
from typing import Dict, List
from services.task.task_status import TaskStatus

class Task(ABC):
    def __init__(self, id: uuid.UUID, description: str, task_command: str, nodes: List[object], remote_path: str=None, local_path: str=None):
        self._task_id = id
        self.description = description
        self._task_command = task_command
        self.status = TaskStatus.PENDING
        self._nodes = nodes
        self._results: Dict[str, str] = {}
        self.remote_path = remote_path
        self.local_path = local_path

    def __repr__(self):
        return f"Task({self._task_id}, {self._task_command}, '{self.description}', {self.status}, nodes: {self.nodes}, results: {self._results})"

    @property
    def id(self):
        return self._task_id

    @property
    def task_command(self):
        return self._task_command

    @task_command.setter
    def task_command(self, value):
        if not value:
            raise ValueError("Command cannot be empty")
        self._task_command = value

    @property
    def nodes(self):
        return self._nodes.copy()

    @nodes.setter
    def nodes(self, value: List[str]):
        self._nodes = value

    @property
    def results(self):
        return self._results.copy()

    def add_result(self, node_id, result):
        self._results[node_id] = result

    def to_string(self) -> str:
        task_info = [
            f"ID: {self._task_id}",
            f"Type: {self.__class__.__name__}",
            f"Status: {self.status.name}",
            f"Description: {self.description}",
            f"Nodes: {', '.join(str(node) for node in self.nodes)}",
        ]
        return "\n".join(task_info)

    @abstractmethod
    def get_additional_info(self) -> List[str]:
        pass