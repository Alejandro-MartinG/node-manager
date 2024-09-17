from abc import ABC, abstractmethod


class ExecutionStrategy(ABC):
    @abstractmethod
    def execute_command(self, command: str) -> str:
        pass
