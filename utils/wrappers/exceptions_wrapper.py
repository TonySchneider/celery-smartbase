from helpers.loggers import get_logger

logger = get_logger(__file__)


class ExceptionDecorator(object):
    """
    This class is being used as a class decorator for exceptions handling.
    """

    def __init__(self, exceptions):
        """
        :param exceptions: list of exceptions that we want to monitor while we decorate a method
        """
        self.tuple_of_exceptions = exceptions

    def __call__(self, func, *args, **kwargs):
        def inner_func(*args, **kwargs):
            error_message = f"Got exception while trying to execute method '{func.__name__}' with params {kwargs if kwargs else args[1:]}"
            try:
                return func(*args, **kwargs)
            except tuple(self.tuple_of_exceptions) as e:
                logger.error(f"{error_message}. Exception - {type(e)}")
                logger.error(f"Exception message : {e}")
                return False
        return inner_func
