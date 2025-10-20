import time

from decorator import decorator
from loguru import logger as local_logger


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@decorator
def log_func_time(func, *args, **kwargs):
    """记录函数运行时间"""

    t0 = time.perf_counter()
    r = func(*args, **kwargs)
    t1 = time.perf_counter()
    local_logger.debug(f"{func.__name__} run time: {t1 - t0:.4f}s")
    return r
