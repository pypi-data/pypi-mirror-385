from time import perf_counter
from functools import wraps


def time_this(func):
    """
    This decorator can be used
    to count the execution time
    of a function, then print
    the elapsed time!
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        elapsed_time = end - start
        print(f"\n\n(Finished in: {elapsed_time:.4f} seconds.)")
        return result
    return wrapper
