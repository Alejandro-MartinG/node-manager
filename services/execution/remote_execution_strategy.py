from services.ssh_service import SSHService
from services.execution.execution_strategy import ExecutionStrategy

class RemoteExecutionStrategy(ExecutionStrategy):
    def execute_command(self, command: str, ip: str, username: str, password: str) -> str:
        try:
            client = SSHService(ip, username, password)
            output = client.execute_command(command)
            return output
        except Exception as e:
            print(f"REMOTE execution failed: {str(e)}")
        finally:
            client.close()
