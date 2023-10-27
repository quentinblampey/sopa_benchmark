from functools import wraps
from time import time


def time(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print(f"func:{f.__name__} args:[{args, kwargs}] took: {te-ts} sec")
        return result

    return wrap
