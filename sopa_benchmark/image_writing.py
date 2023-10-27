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

from .utils import crop_image


def _prepare_image(sdata: SpatialData, width: int, compute: bool = False):
    image = get_spatial_image(sdata)
    image = crop_image(image, width, compute=compute)
    print(f"Image of shape {image.shape}")
    return image


def sopa_write(sdata: SpatialData, width: int):
    image = _prepare_image(sdata, width)
    image: MultiscaleSpatialImage = to_multiscale(image, [])

    with tempfile.NamedTemporaryFile() as tmp:
        image_writer = MultiscaleImageWriter(image, pixelsize=0.2125, tile_width=1024)
        with tf.TiffWriter(tmp, bigtiff=True) as tif:
            image_writer._write_image_level(tif, scale_index=0)


def normal_write(sdata: SpatialData, width: int):
    image = _prepare_image(sdata, width, compute=True)
    image = scale_dtype(image, np.int8)

    with tempfile.NamedTemporaryFile() as tmp:
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
