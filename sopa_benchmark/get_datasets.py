import argparse

from .utils import get_benchmark_data, get_uniform

START_DIM = 1024


def main(args):
    if args.mode == "uniform":
        for scale in range(args.scales):
            print(f"Saving scale {scale}")
            get_uniform(START_DIM * 2**scale)
    else:
        for scale in range(args.scales):
            print(f"Saving scale {scale}")
            get_benchmark_data(START_DIM * 2**scale)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="benchmark",
        help="Mode: uniform or benchmark",
    )
    parser.add_argument(
        "-s",
        "--scales",
        type=int,
        default=8,
        help="Number of scales",
    )

    main(parser.parse_args())
