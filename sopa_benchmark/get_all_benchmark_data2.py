from .utils import _get_benchmark_data

if __name__ == "__main__":
    for scale in range(8):
        print(1024 * 2**scale)
        _get_benchmark_data(1024 * 2**scale)
