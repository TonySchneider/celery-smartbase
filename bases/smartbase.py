import logging
from kombu import uuid
from datetime import datetime

from celery import Task as BaseTask
from celery.result import AsyncResult

from django_celery_results.models import TaskResult

import django.db.models
from django.db.models import Q
from django.db import ProgrammingError


class SmartBase(BaseTask):
    def __init__(self, db_model=TaskResult):
        logging.info("Initializing SmartBaseTask celery base ...")
        super(SmartBase, self).__init__()
        self.task_id = None
        self.db_model = db_model

    def __call__(self, *args, **kwargs):
        logging.info("Doing __call__ ...")
        self.task_id = self.request.id
        job = self.db_model.objects.get(task_id=self.task_id)
        job.date_started = datetime.now()
        logging.info(f"Task ({self.task_id}) Starting at {self.name} [{job.date_started}]")
        job.save()
        return super(SmartBase, self).__call__(*args, **kwargs)

    def run(self, *args, **kwargs):
        logging.error(f'Task tried to run: {self.name}[{self.request.id}]')
        raise NotImplementedError()

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, shadow=None, **options):
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

        return super(SmartBase, self).apply_async(args, kwargs, task_id, producer, link, link_error, shadow, **options)

    def before_start(self, task_id, args, kwargs):
        """Handler called before the task starts.

        .. versionadded:: 5.2

        Arguments:
            task_id (str): Unique id of the task to execute.
            args (Tuple): Original arguments for the task to execute.
            kwargs (Dict): Original keyword arguments for the task to execute.

        Returns:
            None: The return value of this handler is ignored.
        """
        logging.info(f"Task ({task_id}) doing before_start...")

    def on_success(self, retval, task_id, args, kwargs):
        """Success handler.

        Run by the worker if the task executes successfully.

        Arguments:
            retval (Any): The return value of the task.
            task_id (str): Unique id of the executed task.
            args (Tuple): Original arguments for the executed task.
            kwargs (Dict): Original keyword arguments for the executed task.

        Returns:
            None: The return value of this handler is ignored.
        """
        logging.info(f"Task ({task_id}) doing on_success...")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry handler.

        This is run by the worker when the task is to be retried.

        Arguments:
            exc (Exception): The exception sent to :meth:`retry`.
            task_id (str): Unique id of the retried task.
            args (Tuple): Original arguments for the retried task.
            kwargs (Dict): Original keyword arguments for the retried task.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        logging.info(f"Task ({task_id}) doing Retry...")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error handler.

        This is run by the worker when the task fails.

        Arguments:
            exc (Exception): The exception raised by the task.
            task_id (str): Unique id of the failed task.
            args (Tuple): Original arguments for the task that failed.
            kwargs (Dict): Original keyword arguments for the task that failed.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        logging.info(f"Task ({task_id}) doing on_failure ...")

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Handler called after the task returns.

        Arguments:
            status (str): Current task state.
            retval (Any): Task return value/exception.
            task_id (str): Unique id of the task.
            args (Tuple): Original arguments for the task.
            kwargs (Dict): Original keyword arguments for the task.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        logging.info(f"Task ({self.task_id}) doing after_return ...")
        job = self.db_model.objects.get(task_id=self.task_id)
        job.date_finished = datetime.now()
        job.save()
