from functools import wraps
from pathlib import Path
from time import time

import dask.array as da
import numpy as np
import spatialdata
from sopa._sdata import get_intrinsic_cs, get_spatial_image
from sopa.utils.data import uniform
from spatialdata import SpatialData


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
    chunks_starts = np.array(image.chunks[axis])
    if x0 <= 0 or len(chunks_starts) == 1:
        return 0
    return min(chunks_starts.cumsum(), key=lambda x: abs(x - x0))


def crop_image(image: da.Array, width: int, compute: bool = False):
    assert width <= image.shape[1] and width <= image.shape[2]

    y0 = _get_start(image, 1, width)
    x0 = _get_start(image, 2, width)

    image = image[:, y0 : y0 + width, x0 : x0 + width]

    if compute:
        return image.values

    return image


def crop_sdata(sdata: SpatialData, width: int):
    image = get_spatial_image(sdata)

    y0 = _get_start(image, 1, width)
    x0 = _get_start(image, 2, width)

    return sdata.query.bounding_box(
        axes=["x", "y"],
        min_coordinate=[x0, y0],
        max_coordinate=[x0 + width, y0 + width],
        target_coordinate_system=get_intrinsic_cs(sdata, image),
    )


def _get_liver():
    DATA_DIRS = [
        "/mnt/beegfs/merfish/data/liver/public/patient_1.zarr",
        "~/sopa_benchmark/data/liver.zarr",
    ]
    for data_dir in DATA_DIRS:
        path = Path(data_dir)
        if path.exists():
            return spatialdata.read_zarr(path)

    raise ValueError(
        f"Data directory {DATA_DIRS[-1]} is not existing. Create it before continuing."
    )


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


def get_liver_cropped(length: int = None):
    path = _get_data_dir() / f"patient_1{'' if length is None else f'_{length}'}.zarr"

    if not path.exists():
        sdata = crop_sdata(_get_liver(), length)
        sdata.write(path)

    return spatialdata.read_zarr(path)
