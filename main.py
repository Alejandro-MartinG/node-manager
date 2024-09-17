import logging
import os
import sys
import traceback
from dotenv import load_dotenv
from bots.quilibrium import QuilibriumBot
from registry import Registry
from services.task.task_manager import TaskManager
from services.task.task_scheduler import TaskScheduler
from services.db.db_service import DBService
from services.node_service import NodeService
from services.task_service import TaskService

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
BLOCKCHAIN = 'quilibrium'
DB_EXPANDED_PATH = os.path.expanduser(DB_PATH)
__version__ = "0.1.0"


def run_task_manager():
    try:
        db_service = DBService(DB_EXPANDED_PATH)
        Registry.register('db_service', db_service)

        node_service = NodeService()
        Registry.register('node_service', node_service)

        task_service = TaskService()
        Registry.register('task_service', task_service)

        task_manager = TaskManager(blockchain=BLOCKCHAIN)
        Registry.register('task_manager', task_manager)

        task_scheduler = TaskScheduler()
        Registry.register('task_scheduler', task_scheduler)
        task_scheduler.start()

        quililibrium_bot = QuilibriumBot()
        Registry.register('quililibrium_bot', quililibrium_bot)

        quililibrium_bot.run()

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected, exiting.")
        sys.exit(0)
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(f"Unhandled exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_task_manager()