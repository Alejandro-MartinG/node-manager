import os
import uuid
from dotenv import load_dotenv
from typing import Any, Callable, Dict, List
from munch import Munch
from services.node.node import Node
from services.node_service import NodeService
from services.task.task import Task
from services.task.task_status import TaskStatus
from services.task_service import TaskService
from registry import Registry

load_dotenv()

class TaskManager:
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    NODES_WITH_BLOCKCHAIN = "all_nodes_with_blockchain"

    def __init__(self, blockchain: str=None):
        self.blockchain = blockchain
        self.task_service = Registry.get('task_service')
        self.node_service = Registry.get('node_service')
        self.node_service.load_nodes_from_seeds()
        self.bot = Registry.get('quilibrium_bot')

    def create_task(self, command: Munch, node_names: List[str], **kwargs) -> Dict[Task, Node]:
        nodes = self.get_nodes_for_task(node_names=node_names)
        task = self.task_service.create_task(
            command=command.command,
            description=command.description,
            node_ids=nodes,
            **kwargs
        )
        return task

    def get_nodes_for_task(self, node_names: List[str], blockchain: str=None) -> List[Node]:
        if not blockchain:
            blockchain = self.blockchain

        if len(node_names) == 1 and self.NODES_WITH_BLOCKCHAIN in node_names:
            return self.node_service.get_nodes_with_blockchain(blockchain)
        else:
            return self.node_service.get_nodes_by_name(node_names)

    def show_pending_tasks(self) -> List[str]:
        return self.task_service.get_pending_tasks_info()

    def show_scheduled_tasks(self) -> List[str]:
        return self.task_service.get_scheduled_tasks_info()

    def get_task_status(self, task_id: uuid.UUID) -> str:
        return self.task_service.get_task_status(task_id)

    def get_task_results(self, task_id: uuid.UUID) -> Dict[str, Any]:
        task = self.task_service.get_task(task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")
        
        if task.status != TaskStatus.COMPLETED:
            raise ValueError(f"Task with ID {task_id} is not completed. Current status: {task.status.name}")
        
        return task.results

    def register_callback(self, task_id: uuid.UUID, callback: Callable):
        self.callbacks[task_id] = callback

    def ping_task_completion(self, task_id: uuid.UUID):
        callback = self.callbacks.pop(task_id, None)
        if callback:
            results = self.task_service.get_task_results(task_id)
            callback(results)

    def notify_task_completion(self, task_id):
        result = self.task_service.get_task_results(task_id)
        message = f"Task {task_id} completed. Result: {result}"
        self.bot.send_message(chat_id=self.CHAT_ID, text=message)