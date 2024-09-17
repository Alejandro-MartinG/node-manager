import subprocess
from services.execution.execution_strategy import ExecutionStrategy


class LocalExecutionStrategy(ExecutionStrategy):
    def execute_command(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error executing local command: {e.stderr}")
