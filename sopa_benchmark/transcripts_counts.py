import argparse

from sopa.segmentation import aggregate
from sopa.utils import data
from spatialdata import SpatialData

from .timing import timer


@timer
def sopa_count(sdata: SpatialData):
    aggregate.count_transcripts(sdata, gene_column="gene")


@timer
def normal_count(sdata: SpatialData):
    sdata.aggregate(
        values="transcripts",
        by="cells",
        value_key="gene",
        agg_func="count",
    )


def main(args):
    sdata = data.uniform(args.length)

    if args.mode == "normal":
        normal_count(sdata)
    elif args.mode == "sopa":
        sopa_count(sdata)
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
