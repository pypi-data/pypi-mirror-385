from functools import wraps
from itertools import product
from logging import DEBUG, getLevelName, getLevelNamesMapping, getLogger
from sys import modules

logger = getLogger(__name__)


def log_io(level=DEBUG, enter=False, exit=False):
    """
    Decorator factory that logs function input arguments and return values
    at the specified logging level.
    Usage:
        from logging import DEBUG, INFO

        debug = @log_io(DEBUG)
        info = @log_io(INFO)


        @debug
        def my_func(...):
            ...


        @info
        def more_important_func(...):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if enter:
                logger.log(
                    level,
                    "Calling %s with args=%s, kwargs=%s",
                    func.__name__,
                    args,
                    kwargs,
                    stacklevel=2,
                )
            result = func(*args, **kwargs)
            if exit:
                logger.log(level, "%s returned %r", func.__name__, result, stacklevel=2)
            return result

        return wrapper

    return decorator


level_names = getLevelNamesMapping().keys()

for level, direction in product(level_names, ("_in", "_out", "")):
    if direction == "_in":
        enter = True
        exit = False
    elif direction == "_out":
        enter = False
        exit = True
    else:
        enter = True
        exit = True
    setattr(
        modules[__name__],
        f"{level.lower()}{direction}",
        log_io(getLevelName(level), enter=enter, exit=exit),
    )
