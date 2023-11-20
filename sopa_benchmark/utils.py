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


def _get_start(image: da.Array, axis: int, length: int) -> int:
    x0 = (image.shape[axis] - length) // 2
    chunks_starts = np.array(image.chunks[axis])
    if x0 <= 0 or len(chunks_starts) == 1:
        return 0
    return min(chunks_starts.cumsum(), key=lambda x: abs(x - x0))


def crop_image(image: da.Array, length: int, compute: bool = False):
    assert length <= image.shape[1] and length <= image.shape[2]

    y0 = _get_start(image, 1, length)
    x0 = _get_start(image, 2, length)

    image = image[:, y0 : y0 + length, x0 : x0 + length]

    if compute:
        return image.values

    return image


def crop_sdata(sdata: SpatialData, length: int):
    image = get_spatial_image(sdata)

    y0 = _get_start(image, 1, length)
    x0 = _get_start(image, 2, length)

    return sdata.query.bounding_box(
        axes=["x", "y"],
        min_coordinate=[x0, y0],
        max_coordinate=[x0 + length, y0 + length],
        target_coordinate_system=get_intrinsic_cs(sdata, image),
    )


def _get_benchmark_data(length: int | None = None):
    suffix = "" if length is None else f"_{length}"
    DATA_DIRS = [
        f"/mnt/beegfs/merfish/data/liver/public",
        f"/Users/quentinblampey/dev/sopa_benchmark/data",
        f"~/sopa_benchmark/data",
    ]
    FILENAMES = [
        f"patient_1{suffix}.zarr",
        f"uniform_4096{suffix}.zarr",
        f"liver{suffix}.zarr",
    ]
    for data_dir, filename in zip(DATA_DIRS, FILENAMES):
        path = Path(data_dir) / filename
        if path.exists():
            return spatialdata.read_zarr(path)

    if length is not None:
        sdata = crop_sdata(_get_benchmark_data(), length)

        image_key, image = get_spatial_image(sdata, return_key=True)
        image.data.rechunk(image.data.chunksize)

        for data_dir, filename in zip(DATA_DIRS, FILENAMES):
            if Path(data_dir).exists():
                path = Path(data_dir) / filename
                sdata.write(path)

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


def _get_baysor_dirs(name: str) -> Path:
    path = _get_data_dir() / "baysor_dirs" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_uniform(length: int):
    path = _get_data_dir() / f"uniform_{length}.zarr"

    if not path.exists():
        sdata = uniform(length=length, cell_density=5e-5)
        sdata.write(path)

    return spatialdata.read_zarr(path)
