import dask.array as da
import numpy as np


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
