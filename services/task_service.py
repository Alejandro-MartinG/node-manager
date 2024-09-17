import uuid
from threading import Lock
from typing import Dict, List
from registry import Registry
from services.task.task_factory import TaskFactory
from services.task.task_status import TaskStatus
from services.task.task import Task
from services.task.simple_task import SimpleTask
from services.task.scheduled_task import ScheduledTask
from services.task.periodic_task import PeriodicTask


class TaskService:
    def __init__(self):
        self.tasks: Dict[uuid.UUID, SimpleTask]= {}
        self.task_factory = TaskFactory()
        self.task_scheduler = Registry.get('task_scheduler')
        self.lock = Lock()

    def create_task(self, description: str, command: str, node_ids: List[str], **kwargs) -> Task:
        task_id = uuid.uuid4()
        task = self.task_factory.create_task(task_id, description, command, node_ids, **kwargs)
        task_scheduler = Registry.get('task_scheduler')
        task_scheduler.add_task([task])
        with self.lock:
            self.tasks[task_id] = task
        return task

    def get_task(self, task_id: uuid.UUID):
        return self.tasks.get(task_id)

    def get_task_status(self, task_id: uuid.UUID):
        return self.tasks.get(task_id).status

    def get_task_results(self, task_id: uuid.UUID):
        return self.tasks.get(task_id).results

    def list_tasks(self):
        for task_id, task in self.tasks.items():
            print(f"Task ID: {task_id}, Description: {task.description}, Status: {task.status}")

    def get_simple_tasks(self) -> List[SimpleTask]:
        return [task for task in self.tasks.values() if isinstance(task, SimpleTask)]

    def get_scheduled_tasks(self) -> List[ScheduledTask]:
        return [task for task in self.tasks.values() if isinstance(task, ScheduledTask)]

    def get_periodic_tasks(self) -> List[PeriodicTask]:
        return [task for task in self.tasks.values() if isinstance(task, PeriodicTask)]

    def get_pending_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.status is TaskStatus.PENDING]

    def get_completed_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.status is TaskStatus.COMPLETED]

    def stop_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if task:
            task.stop()

    def update_task_status(self, task_id: uuid.UUID, status: TaskStatus):
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                task.status = status

    def update_task_result(self, task: Task, node_id: str, result: str):
        if task:
            task.add_result(node_id, result)

    def get_pending_tasks_info(self) -> List[str]:
        pending_tasks = self.get_pending_tasks()
        return self._format_tasks(pending_tasks, "Pending Tasks")

    def get_scheduled_tasks_info(self) -> List[str]:
        scheduled_tasks = self.get_scheduled_tasks()
        periodic_tasks = self.get_periodic_tasks()
        all_scheduled = scheduled_tasks + periodic_tasks
        return self._format_tasks(all_scheduled, "Scheduled Tasks")

    def _format_tasks(self, tasks: List[Task], title: str) -> List[str]:
        result = [f"{title}:"]
        if not tasks:
            result.append("No tasks found.")
            return result

        for task in tasks:
            task_info = task.to_string().split("\n")
            task_info.extend(task.get_additional_info())
            result.append("\n".join(task_info))
            result.append("-" * 40)

        return result
