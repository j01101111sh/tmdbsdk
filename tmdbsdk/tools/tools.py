import logging
from functools import wraps


def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug('{} called\n\targs: {}\n\tkwargs: {}'.format(
            func.__name__,
            '\n\t\t'.join([str(s) for s in args]),
            '\n\t\t'.join([f'{key}: {value}' for key, value in kwargs.items()])
        ))
        return func(*args, **kwargs)
    return wrapper
