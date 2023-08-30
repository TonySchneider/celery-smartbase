import logging
from datetime import datetime
from django.db.models import Q
from kombu.utils.uuid import uuid
from typing import Any, Dict, Tuple
from celery.app.task import BaseTask
from celery.result import AsyncResult

from django_celery_results.models import TaskResult


class SmartBase(BaseTask):
    """
    SmartBase is an extension of the Celery BaseTask class that provides features to avoid duplicates
    for tasks that are pending or running, and to see the "pending" tasks as well in the "jobs" Django model
    when you integrate Celery with Django.
    """

    def __init__(self, db_model=TaskResult):
        """
        Initialize SmartBaseTask celery base.

        :param db_model: The database model to use for storing task results.
        """
        logging.info("Initializing SmartBaseTask celery base ...")
        super().__init__()
        self.task_id = None
        self.db_model = db_model

    def __call__(self, *args, **kwargs):
        """
        Handler called when the task is called.

        :param args: Positional arguments passed to the task.
        :param kwargs: Keyword arguments passed to the task.
        :return: The return value of the task.
        """
        logging.info("Doing __call__ ...")
        self.task_id = self.request.id
        job = self.db_model.objects.get(task_id=self.task_id)
        job.date_started = datetime.now()
        logging.info(f"Task ({self.task_id}) Starting at {self.name} [{job.date_started}]")
        job.save()
        return super().__call__(*args, **kwargs)

    def run(self, *args, **kwargs):
        """
        The body of the task.

        :param args: Positional arguments passed to the task.
        :param kwargs: Keyword arguments passed to the task.
        :raise NotImplementedError: This method must be implemented in subclasses.
        """
        logging.error(f'Task tried to run: {self.name}[{self.request.id}]')
        raise NotImplementedError()

    def apply_async(self, args: Tuple = None, kwargs: Dict = None, task_id: str = None, producer=None,
                    link=None, link_error=None, shadow=None, **options) -> AsyncResult:
        """
        Send task message.

        :param args: Positional arguments passed to the task.
        :param kwargs: Keyword arguments passed to the task.
        :param task_id: Unique id of the task.
        :param producer: Message producer.
        :param link: A callback to apply if the task completes successfully.
        :param link_error: A callback to apply if an error occurs while executing the task.
        :param shadow: The name of the task to use in logs and monitoring tools.
        :param options: Additional options passed to the task.
        :return: AsyncResult instance.
        """
        task_id = task_id or uuid()
        logging.info(f"Task {task_id} running apply_async method...")

        pending_tasks = self.db_model.objects.filter(
            Q(task_name=self.name, status='PENDING', task_args=args if args is None else f"{args}",
              task_kwargs=kwargs if kwargs is None else f"{kwargs}") |
            Q(task_name=self.name, status='STARTED', task_args=args if args is None else f"\"{args}\"",
              task_kwargs=kwargs if kwargs is None else f"\"{kwargs}\""))

        if pending_tasks:
            logging.info(
                f"Will not send this task (task_id={task_id}|task_name={self.name}) due to a similar task that already running/pending.")
            return AsyncResult(id=task_id)

        job = self.db_model.objects.create(task_id=task_id, status='PENDING', task_name=self.name, task_args=args,
                                           task_kwargs=kwargs)
        job.save()

        return super().apply_async(args, kwargs, task_id, producer, link, link_error, shadow, **options)

    def before_start(self, task_id: str, args: Tuple, kwargs: Dict):
        """
        Handler called before the task starts.

        :param task_id: Unique id of the task to execute.
        :param args: Original arguments for the task to execute.
        :param kwargs: Original keyword arguments for the task to execute.
        """
        logging.info(f"Task ({task_id}) doing before_start...")

    def on_success(self, retval: Any, task_id: str, args: Tuple, kwargs: Dict):
        """
        Success handler. Run by the worker if the task executes successfully.

        :param retval: The return value of the task.
        :param task_id: Unique id of the executed task.
        :param args: Original arguments for the executed task.
        :param kwargs: Original keyword arguments for the executed task.
        """
        logging.info(f"Task ({task_id}) doing on_success...")

    def on_retry(self, exc: Exception, task_id: str, args: Tuple, kwargs: Dict, einfo):
        """
        Retry handler. This is run by the worker when the task is to be retried.

        :param exc: The exception sent to :meth:`retry`.
        :param task_id: Unique id of the retried task.
        :param args: Original arguments for the retried task.
        :param kwargs: Original keyword arguments for the retried task.
        :param einfo: Exception information.
        """
        logging.info(f"Task ({task_id}) doing Retry...")

    def on_failure(self, exc: Exception, task_id: str, args: Tuple, kwargs: Dict, einfo):
        """
        Error handler. This is run by the worker when the task fails.

        :param exc: The exception raised by the task.
        :param task_id: Unique id of the failed task.
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: Exception information.
        """
        logging.info(f"Task ({task_id}) doing on_failure ...")

    def after_return(self, status: str, retval: Any, task_id: str, args: Tuple, kwargs: Dict, einfo):
        """
        Handler called after the task returns.

        :param status: Current task state.
        :param retval: Task return value/exception.
        :param task_id: Unique id of the task.
        :param args: Original arguments for the task.
        :param kwargs: Original keyword arguments for the task.
        :param einfo: Exception information.
        """
        logging.info(f"Task ({self.task_id}) doing after_return ...")
        job = self.db_model.objects.get(task_id=self.task_id)
        job.date_finished = datetime.now()
        job.save()
