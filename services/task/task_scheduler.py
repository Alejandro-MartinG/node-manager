import os
import logging
from typing import List
from dotenv import load_dotenv
from pytz import utc
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from registry import Registry
from services.task.task_status import TaskStatus
from services.task.simple_task import SimpleTask
from services.task.periodic_task import PeriodicTask
from services.task.scheduled_task import ScheduledTask
from services.task.task_executor import TaskExecutor
from services.task.task import Task


load_dotenv()

class TaskScheduler:
    DEFAULT_MAX_THREADS = 3

    def __init__(self):
        pid = os.getpid()
        logging.debug(f"Task Scheduler PID: {pid}")

        self.task_service = Registry.get('task_service')
        self.node_service = Registry.get('node_service')
        self.task_executor = TaskExecutor()
        self.is_running = False
        self.max_threads = int(os.getenv('MAX_THREADS', self.DEFAULT_MAX_THREADS))

        jobstores = {'default': MemoryJobStore()}
        executors = { 'default': ThreadPoolExecutor(self.max_threads) }
        job_defaults = { 'coalesce': False, 'max_instances': self.max_threads }

        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=utc
        )

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.is_running = False

    def add_task(self, tasks: List[Task]):
        for task in tasks:
            if isinstance(task, SimpleTask):
                self.run_task(task)
            elif isinstance(task, ScheduledTask) and task.scheduled_time and task.status is TaskStatus.PENDING:
                self.add_scheduled_task(self.run_task, task.scheduled_time, task)
            elif isinstance(task, PeriodicTask) and task.next_execution_time and task.status is TaskStatus.PENDING:
                self.add_daily_task(self.run_task, task)

    def add_immediate_task(self, func, *args, **kwargs):
        return self.scheduler.add_job(
            func,
            trigger=DateTrigger(run_date=datetime.now()),
            args=args,
            kwargs=kwargs
        )

    def add_scheduled_task(self, func, run_date, *args, **kwargs):
        return self.scheduler.add_job(
            func,
            trigger=DateTrigger(run_date=run_date),
            args=args,
            kwargs=kwargs
        )

    def add_recurring_task(self, func, interval, *args, **kwargs):
        return self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=interval),
            args=args,
            kwargs=kwargs
        )

    def add_daily_task(self, func):
        return self.scheduler.add_job(func, 'cron', hour=12, minute=0)

    def remove_task(self, job_id):
        self.scheduler.remove_job(job_id)

    def get_tasks(self):
        return self.scheduler.get_jobs()

    def run_task(self, task: Task):
        self.task_executor.execute(task)
