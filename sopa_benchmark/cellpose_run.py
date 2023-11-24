import argparse

import geopandas as gpd
from shapely.geometry import Polygon
from sopa._sdata import get_spatial_image, get_transformation
from sopa.segmentation.cellpose import cellpose_patch
from sopa.segmentation.patching import Patches2D
from sopa.segmentation.stainings import StainingSegmentation
from spatialdata import SpatialData
from spatialdata.models import ShapesModel
from tqdm import tqdm

from .utils import get_benchmark_data, timer


def _save_shapes(
    sdata: SpatialData, cells: list[Polygon], name: str, overwrite: bool = False
) -> None:
    image = get_spatial_image(sdata)
    gdf = gpd.GeoDataFrame(geometry=cells)
    gdf = ShapesModel.parse(
        gdf, transformations=get_transformation(image, get_all=True)
    )
    sdata.add_shapes(name, gdf, overwrite=overwrite)


@timer
def normal_cellpose(sdata: SpatialData, length: int, seg: StainingSegmentation):
    cells = seg.run_patches(10**10, 0)
    _save_shapes(sdata, cells, f"normal_{length}")


@timer
def sopa_cellpose(sdata: SpatialData, length: int, width, seg: StainingSegmentation):
    assert width is not None

    seg.patches = Patches2D(seg.sdata, seg.image_key, width, 100)
    cells = [
        cell
        for patch in tqdm(seg.patches.polygons, desc="Run on patches")
        for cell in seg._run_patch(patch)
    ]
    _save_shapes(sdata, cells, f"sopa_{length}_{width}")


def main(args):
    sdata = get_benchmark_data(args.length)
    print(sdata)

    method = cellpose_patch(70, ["DAPI"], flow_threshold=2, cellprob_threshold=-6)
    seg = StainingSegmentation(sdata, method, ["DAPI"])

    length = "full" if args.length is None else args.length

    if args.mode == "normal":
        normal_cellpose(sdata, length, seg)
    elif args.mode == "sopa":
        sopa_cellpose(sdata, length, args.patch_width, seg)
    else:
        raise ValueError(f"Invalid mode {args.mode}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="normal",
        help="Either 'normal' or 'sopa'",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=None,
        help="Image width",
    )
    parser.add_argument(
        "-pw",
        "--patch_width",
        type=int,
        default=None,
        help="Sopa patch width",
    )

    main(parser.parse_args())
