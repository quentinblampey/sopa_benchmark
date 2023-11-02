import numpy as np
import spatialdata
from sopa.segmentation.aggregate import Aggregator

from .timing import timer


@timer
def sopa_average(sdata_path: str):
    sdata = spatialdata.read_zarr(sdata_path)

    aggregrator = Aggregator(sdata)
    aggregrator.average_channels()


@timer
def normal_average(sdata_path: str):
    sdata = spatialdata.read_zarr(sdata_path)

    image = ...
    cell_mask = sdata["cellpose_masks"]

    average_intensities = []

    for cell_id in np.unique(cell_mask):
        cell_id_mask = cell_mask == cell_id
        average_intensity = np.sum(image * cell_id_mask, axis=(1, 2)) / np.sum(
            cell_id_mask
        )
        average_intensities.append(average_intensity)

    average_intensities = np.stack(average_intensities)
