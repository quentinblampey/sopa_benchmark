from .utils import _get_benchmark_data, get_uniform

if __name__ == "__main__":
    for scale in range(8):
        get_uniform(1024 * 2**scale)

    for scale in range(8):
        _get_benchmark_data(1024 * 2**scale)
