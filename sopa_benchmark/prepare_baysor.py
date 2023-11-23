import argparse
from pathlib import Path

import pandas as pd
from sopa._constants import SopaFiles
from sopa.segmentation.baysor.prepare import to_toml
from sopa.segmentation.patching import Patches2D
from spatialdata import SpatialData

from .utils import _get_baysor_dirs, get_uniform, timer

baysor_config = {
    "data": {
        "exclude_genes": "Blank*",
        "force_2d": True,
        "min_molecules_per_cell": 10,
        "x": "x",
        "y": "y",
        "z": "z",
        "gene": "gene",
        "min_molecules_per_gene": 0,
        "min_molecules_per_segment": 3,
        "confidence_nn_id": 6,
    },
    "segmentation": {
        "scale": 6.25,
        "scale_std": "25%",
        "prior_segmentation_confidence": 0.75,
        "estimate_scale_from_centers": False,
        "n_clusters": 4,
        "iters": 500,
        "n_cells_init": 0,
        "nuclei_genes": "",
        "cyto_genes": "",
        "new_component_weight": 0.2,
        "new_component_fraction": 0.3,
    },
}


@timer
def normal_baysor(sdata: SpatialData, length: int):
    df: pd.DataFrame = sdata["transcripts"].compute()

    path = _get_baysor_dirs(f"normal_{length}")

    df.to_csv(path / "transcripts.csv")
    to_toml(path / SopaFiles.BAYSOR_CONFIG, baysor_config)


@timer
def sopa_baysor(sdata: SpatialData, length: int, width):
    assert width is not None

    df_key = "transcripts"
    baysor_temp_dir = _get_baysor_dirs(f"sopa_{length}_{width}")
    patches = Patches2D(sdata, df_key, width, 20)
    valid_indices = patches.patchify_transcripts(baysor_temp_dir)

    for i in range(len(patches)):
        path = Path(baysor_temp_dir) / str(i) / SopaFiles.BAYSOR_CONFIG
        to_toml(path, baysor_config)

    with open(baysor_temp_dir / SopaFiles.PATCHES_DIRS_BAYSOR, "w") as f:
        f.write("\n".join(map(str, valid_indices)))


def main(args):
    sdata = get_uniform(args.length)
    print(sdata)

    length = "full" if args.length is None else args.length

    if args.mode == "normal":
        normal_baysor(sdata, length)
    elif args.mode == "sopa":
        sopa_baysor(sdata, length, args.patch_width)
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
        help="Sopa patch width in microns",
    )

    main(parser.parse_args())
