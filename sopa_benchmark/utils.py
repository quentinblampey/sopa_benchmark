from functools import wraps
from pathlib import Path
from time import time

import dask.array as da
import numpy as np
import spatialdata
from sopa.utils.data import uniform


def timer(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print(f"func:{f.__name__} args:[{args, kwargs}] took: {te-ts} sec")
        return result

    return wrap


def _get_start(image: da.Array, axis: int, width: int) -> int:
    x0 = (image.shape[axis] - width) // 2
    return min(np.array(image.chunks[axis]).cumsum(), key=lambda x: abs(x - x0))


def crop_image(image: da.Array, width: int, compute: bool = False):
    assert width <= image.shape[1] and width <= image.shape[2]

    y0 = _get_start(image, 1, width)
    x0 = _get_start(image, 2, width)

    image = image[:, y0 : y0 + width, x0 : x0 + width]

    if compute:
        return image.values

    return image


def _get_data_dir():
    DATA_DIRS = [
        "/mnt/beegfs/userdata/q_blampey/sopa_benchmark/data",
        "/Users/quentinblampey/dev/sopa_benchmark/data",
        "~/sopa_benchmark/data",
    ]
    for data_dir in DATA_DIRS:
        path = Path(data_dir)
        if path.exists():
            return path

    raise ValueError(
        f"Data directory {DATA_DIRS[-1]} is not existing. Create it before continuing."
    )


def get_uniform(length: int):
    path = _get_data_dir() / f"uniform_{length}.zarr"

    if not path.exists():
        sdata = uniform(length)
        sdata.write(path)

    return spatialdata.read_zarr(path)
