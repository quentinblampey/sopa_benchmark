import argparse

import numpy as np
from sopa._sdata import get_spatial_image
from sopa.segmentation import aggregate
from sopa.utils.data import _to_mask
from spatialdata import SpatialData
from tqdm import tqdm

from .utils import get_uniform, timer


@timer
def sopa_average(sdata: SpatialData):
    aggregate.average_channels(sdata)


@timer
def normal_average(sdata: SpatialData, cell_mask: np.array):
    image = get_spatial_image(sdata)

    average_intensities = []

    for cell_id in tqdm(np.unique(cell_mask)):
        if cell_id == 0:
            continue

        cell_id_mask = cell_mask == cell_id
        average_intensity = np.sum(image * cell_id_mask, axis=(1, 2)) / np.sum(
            cell_id_mask
        )
        average_intensities.append(average_intensity)

    average_intensities = np.stack(average_intensities)


def main(args):
    sdata = get_uniform(args.length)

    if args.mode == "sopa":
        sopa_average(sdata)
    elif args.mode == "normal":
        gdf = sdata["cells"]
        radius = np.sqrt(gdf.area / np.pi).mean()
        xy = sdata["vertices"].compute().values
        cell_mask = _to_mask(args.length, xy, radius)
        normal_average(sdata, cell_mask)
    else:
        raise ValueError(f"Invalid mode {args.mode}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        required=True,
        help="Width in pixels of the square",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="normal",
        help="Either 'normal' or 'sopa'",
    )

    main(parser.parse_args())
