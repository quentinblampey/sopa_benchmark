import argparse
import tempfile

import numpy as np
import tifffile as tf
from sopa._sdata import get_spatial_image
from sopa.io.explorer.images import (
    MultiscaleImageWriter,
    MultiscaleSpatialImage,
    scale_dtype,
    to_multiscale,
)
from spatialdata import SpatialData

from .utils import crop_image, get_benchmark_data, timer


def _prepare_image(sdata: SpatialData, length: int, compute: bool = False):
    image = get_spatial_image(sdata)
    image = crop_image(image, length, compute=compute)
    print(f"Image of shape {image.shape}")
    return image


@timer
def sopa_write(sdata: SpatialData, length: int):
    image = _prepare_image(sdata, length)
    image: MultiscaleSpatialImage = to_multiscale(image, [])

    with tempfile.NamedTemporaryFile() as tmp:
        print(f"Writing to {tmp}")
        image_writer = MultiscaleImageWriter(image, pixelsize=0.2125, tile_width=1024)
        image_writer.lazy = True
        image_writer.ram_threshold_gb = None
        with tf.TiffWriter(tmp, bigtiff=True) as tif:
            image_writer._write_image_level(tif, scale_index=0)


@timer
def normal_write(sdata: SpatialData, length: int):
    image = _prepare_image(sdata, length, compute=True)
    image = scale_dtype(image, np.int8)

    with tempfile.NamedTemporaryFile() as tmp:
        print(f"Writing to {tmp}")
        with tf.TiffWriter(tmp, bigtiff=True) as tif:
            resolution = 1e4 / 0.2125
            tif.write(
                image,
                tile=(1024, 1024),
                resolution=(resolution, resolution),
                shape=image.shape,
                dtype=image.dtype,
                photometric="minisblack",
                compression="jpeg2000",
                resolutionunit="CENTIMETER",
            )


def main(args):
    print("Running:", __name__, "with args:\n", args)
    sdata = get_benchmark_data()

    if args.mode == "normal":
        normal_write(sdata, args.length)
    elif args.mode == "sopa":
        sopa_write(sdata, args.length)
    else:
        raise ValueError(f"Invalid mode {args.mode}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        required=True,
        help="Patch width",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="normal",
        help="Either 'normal' or 'sopa'",
    )

    main(parser.parse_args())
