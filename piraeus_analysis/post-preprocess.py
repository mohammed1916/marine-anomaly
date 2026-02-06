import numpy as np
import tensorstore as ts
from pathlib import Path
from typing import Tuple


from pathlib import Path
import tensorstore as ts

root = Path(r"/mnt/c/Users/BBBS-AI-01/d/anomaly/dataset/piraeus/processed")
path = root / "windows_2019_dec.zarr"

# Open TensorStore
windows = ts.open(
    {
        "driver": "zarr",
        "kvstore": {"driver": "file", "path": str(path)},
    },
    open=True,
).result()

# Inspect
print("TensorStore shape:", windows.shape)
print("TensorStore dtype:", windows.dtype)

# Optionally, read the first window to confirm
first_window = windows[0].read().result()
print("First window shape:", first_window.shape)
print("First window data (timestamps in last column):", first_window[:, 4])


def open_windows_store(path: Path) -> ts.TensorStore:
    """
    Open a Zarr TensorStore containing AIS windows.

    Parameters
    ----------
    path : Path
        Path to windows_YYYY_mon.zarr

    Returns
    -------
    ts.TensorStore
        Opened TensorStore object
    """
    return ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": str(path),
            },
        },
        open=True,
    ).result()


def sample_timestamp_gaps(
    windows: ts.TensorStore,
    max_windows: int = 10_000,
) -> np.ndarray:
    """
    Sample timestamp gaps from AIS windows.

    Parameters
    ----------
    windows : ts.TensorStore
        AIS windows of shape (N, window_size, 5)
    max_windows : int
        Maximum number of windows to sample

    Returns
    -------
    np.ndarray
        Flattened array of timestamp gaps (seconds)
    """
    n = windows.shape[0]
    sample_n = min(n, max_windows)

    idx = np.random.choice(n, size=sample_n, replace=False)

    # Read the full sampled windows
    sampled_windows = windows[idx, :, :].read().result()  # shape: (sample_n, window_size, 5)

    # Extract the timestamp column (last column)
    ts_data = sampled_windows[:, :, 4]  # shape: (sample_n, window_size)

    # Compute differences along each window
    gaps = np.diff(ts_data, axis=1)

    # Flatten to 1D array
    return gaps.reshape(-1)


def summarize_gaps(gaps: np.ndarray) -> Tuple[float, float, float]:
    """
    Compute summary statistics for timestamp gaps.

    Parameters
    ----------
    gaps : np.ndarray
        Timestamp gaps in seconds

    Returns
    -------
    tuple
        (mean, median, p90)
    """
    gaps = gaps[gaps > 0]

    return (
        float(np.mean(gaps)),
        float(np.median(gaps)),
        float(np.percentile(gaps, 90)),
    )


def main():
    """
    Entry point: sample timestamp gaps for a single month.
    """
    root = Path(
        r"/mnt/c/Users/BBBS-AI-01/d/anomaly/dataset/piraeus/processed"
    )

    # Single month
    path = root / "windows_2019_dec.zarr"
    windows = open_windows_store(path)

    gaps = sample_timestamp_gaps(windows)
    mean_g, med_g, p90_g = summarize_gaps(gaps)

    print(
        f"{path.name}: mean={mean_g:.2f}s "
        f"median={med_g:.2f}s p90={p90_g:.2f}s"
    )


if __name__ == "__main__":
    # main()
    pass
