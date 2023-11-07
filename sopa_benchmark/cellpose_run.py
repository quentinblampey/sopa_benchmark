import argparse

import geopandas as gpd
from shapely.geometry import Polygon
from sopa.segmentation.cellpose import cellpose_patch
from sopa.segmentation.stainings import StainingSegmentation
from spatialdata import SpatialData
from spatialdata.models import ShapesModel

from .utils import _get_liver


def _save_shapes(sdata: SpatialData, cells: list[Polygon], name: str) -> None:
    gdf = gpd.GeoDataFrame(geometry=cells)
    gdf = ShapesModel.parse(gdf)
    sdata.add_shapes(name, gdf)


def normal_cellpose(sdata: SpatialData, seg: StainingSegmentation):
    cells = seg.run_patches(10 ^ 10, 0)
    _save_shapes(sdata, cells, f"normal")


def sopa_cellpose(sdata: SpatialData, width, seg: StainingSegmentation):
    cells = seg.run_patches(width, 200)
    _save_shapes(sdata, cells, f"sopa_{width}")


def main(args):
    sdata = _get_liver()
    method = cellpose_patch(70, ["DAPI"])
    seg = StainingSegmentation(sdata, method, ["DAPI"])

    if args.mode == "normal":
        normal_cellpose(sdata, seg)
    elif args.mode == "sopa":
        sopa_cellpose(sdata, args.patch_width, seg)
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
        "-pw",
        "--patch_width",
        type=int,
        default=None,
        help="Sopa patch width",
    )

    main(parser.parse_args())
