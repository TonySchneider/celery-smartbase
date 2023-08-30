from celery import shared_task
from celery_smartbase import SmartBase
from django_celery_results.models import TaskResult

SmartBase.db_model = TaskResult


@shared_task(base=SmartBase, name='tasks.add')
def add(x: int, y: int) -> int:
    """
    A task that adds two numbers.

    :param x: The first number.
    :param y: The second number.
    :return: The sum of x and y.
    """
    return x + y


@shared_task(base=SmartBase, name='tasks.mul')
def mul(x: int, y: int) -> int:
    """
    A task that multiplies two numbers.

    :param x: The first number.
    :param y: The second number.
    :return: The product of x and y.
    """
    return x * y
