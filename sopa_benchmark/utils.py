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


def crop_image(image: da.Array, length: int, compute: bool = False):
    assert length <= image.shape[1] and length <= image.shape[2]

    image = image[:, :length, :length]

    if compute:
        return image.values

    return image


def crop_sdata(sdata: SpatialData, length: int):
    return sdata.query.bounding_box(
        axes=["x", "y"],
        min_coordinate=[0, 0],
        max_coordinate=[length, length],
        target_coordinate_system="microns",
    )


def get_benchmark_data(length: int | None = None):
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
        sdata = crop_sdata(get_benchmark_data(), length)

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
        sdata = uniform(
            length=length,
            cell_density=5e-5,
            apply_blur=False,
            save_vertices=True,
            n_points_per_cell=100,
        )
        sdata.write(path)

    return spatialdata.read_zarr(path)
