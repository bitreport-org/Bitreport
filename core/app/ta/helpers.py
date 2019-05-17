import logging
import traceback
from functools import wraps


def empty(keys: list) -> dict:
    d = {k: [] for k in keys}
    d['info'] = []
    return d


def indicator(name: str, default: list) -> callable:
    def decorator(func: callable):
        @wraps(func)
        def wraped_function(*args, **kwargs) -> dict:
            try:
                return {name: func(*args, **kwargs)}
            # Broad exception because TA-Lib has low level
            # errors and because there's a lot of magic...
            except:
                logging.error(f'Indicator {name}, error: /n {traceback.format_exc()}')
                return {name: empty(default)}
        return wraped_function
    return decorator
