from registry import Registry
from services.task.task import Task
from services.execution.execution_factory import ExecutionFactory
from services.node.node import Node
from services.task.task_status import TaskStatus


class TaskExecutor:
    def __init__(self):
        self.task_service = Registry.get('task_service')
        self.node_service = Registry.get('node_service')
        self.task_manager = Registry.get('task_manager')
        self.macro = "$NODE_ID"

    def execute(self, task: Task):
        self.task_service.update_task_status(task.id, TaskStatus.RUNNING)

        def execute_task(self, task: Task, node: Node):
            ip, username, password = node.get_ssh_login_params()
            strategy = ExecutionFactory.get_execution_strategy(node.execution_type)

            command = task.task_command
            if self.macro in command:
                command = command.replace(self.macro, node.id)

            result = strategy.execute_command(command, ip, username, password)
            self.task_service.update_task_result(task, node.id, result)

        try:
            for node in task.nodes:
                if node:
                    execute_task(self, task=task, node=node)
            self.task_service.update_task_status(task.id, TaskStatus.COMPLETED)
            self.task_manager.notify_task_completion(task.id)
        except Exception as e:
            self.task_service.update_task_status(task.id, TaskStatus.FAILED)
            print(f"Task execution failed: {str(e)}")
