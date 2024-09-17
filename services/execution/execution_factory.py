from importlib import import_module
from services.node.node import Node

class ExecutionFactory:
    @staticmethod
    def get_execution_strategy(execution_mode="remote"):
        module_name = f".{execution_mode}_execution_strategy"
        module = import_module(module_name, package='services.execution')
        print(f"Module loaded from Execution Strategy: {module}")
        
        strategy_class = getattr(module, f'{execution_mode.capitalize()}ExecutionStrategy')
        return strategy_class()