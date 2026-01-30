import cudf
import rmm
import numpy as np
import cupy as cp
import numba
from numba import cuda
import math
import tensorstore as ts

# ------------------------------
# Config and metadata
# ------------------------------
MONTH_ABBR = {
    1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
    7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
}

DATA_PERIODS = [
    (2017, [5,6,7,8,9,10,11,12]),
    (2018, list(range(1,13))),
    (2019, list(range(1,13)))
]

COLS_ALIAS = ["t","timestamp","vessel_id","lon","lat","speed","course","heading"]

rmm.reinitialize(
    pool_allocator=True,
    managed_memory=False
)

class AISConfig:
    def __init__(self, root, chunk_size, window_size):
        self.root = root
        self.chunk_size = chunk_size  # max windows per batch
        self.window_size = window_size

# ------------------------------  
# CUDA kernel: sliding windows + clamp + NaN
# ------------------------------
@cuda.jit
def fused_mask_clamp_window_kernel(vessel_id, lat, lon, speed, course, ts,
                                   N, window_size, out_windows, out_vids):
    idx = cuda.grid(1)
    if idx >= N - window_size + 1:
        return

    vid = vessel_id[idx]
    if vessel_id[idx + window_size - 1] != vid:
        return

    base = idx * window_size * 5
    valid_window = True

    for j in range(window_size):
        r = idx + j
        s = speed[r]
        c = course[r]

        if math.isnan(s) or math.isnan(c):
            valid_window = False
            break

        # clamp values
        s = min(max(s, 0.0), 100.0)
        c = min(max(c, 0.0), 360.0)

        out_windows[base + j*5 + 0] = lat[r]
        out_windows[base + j*5 + 1] = lon[r]
        out_windows[base + j*5 + 2] = s
        out_windows[base + j*5 + 3] = c
        out_windows[base + j*5 + 4] = ts[r]

    out_vids[idx] = vid if valid_window else -1

# ------------------------------
# RMM → CuPy helper
# ------------------------------
def rmm_to_memptr(buf):
    """Converts an RMM DeviceBuffer to a CuPy MemoryPointer."""
    return cp.cuda.MemoryPointer(cp.cuda.UnownedMemory(buf.ptr, buf.size, buf), 0)

# ------------------------------
# Main GPU processing
# ------------------------------
def process_month_gpu(year, month, cfg):
    file_path = f"{cfg.root}/unipi_ais_dynamic_{year}/unipi_ais_dynamic_{MONTH_ABBR[month]}{year}.csv"

    df = cudf.read_csv(file_path)
    df = df.rename(columns={"t": "timestamp"})
    df["timestamp"] = df["timestamp"].astype("float32")
    df["vessel_id"], _ = df["vessel_id"].factorize()

    gathered = df[["vessel_id", "lat", "lon", "speed", "course", "timestamp"]]
    gathered = gathered.sort_values(["vessel_id", "timestamp"])

    N = len(gathered)
    num_windows = N - cfg.window_size + 1
    if num_windows <= 0:
        return

    # Allocate device memory
    windows_buf = rmm.DeviceBuffer(size=num_windows * cfg.window_size * 5 * np.dtype(np.float32).itemsize)
    vids_buf    = rmm.DeviceBuffer(size=num_windows * np.dtype(np.int32).itemsize)

    windows = cp.ndarray(shape=(num_windows * cfg.window_size * 5,), dtype=np.float32, memptr=rmm_to_memptr(windows_buf))
    vids    = cp.ndarray(shape=(num_windows,), dtype=np.int32, memptr=rmm_to_memptr(vids_buf))

    # Launch kernel
    threads = 256
    blocks = (num_windows + threads - 1) // threads
    fused_mask_clamp_window_kernel[blocks, threads](
        gathered["vessel_id"].to_cupy(),
        gathered["lat"].to_cupy(),
        gathered["lon"].to_cupy(),
        gathered["speed"].to_cupy(),
        gathered["course"].to_cupy(),
        gathered["timestamp"].to_cupy(),
        N,
        cfg.window_size,
        windows,
        vids
    )
    cuda.synchronize()

    # ------------------------------
    # TensorStore: chunked write to avoid OOM
    # ------------------------------
    store = ts.open({
        "driver": "zarr",
        "kvstore": {"driver": "file", "path": f"{cfg.root}/windows_{year}_{MONTH_ABBR[month]}.zarr"},
        "dtype": "float32",
        "shape": (num_windows, cfg.window_size, 5),
        "chunk_shape": (cfg.chunk_size, cfg.window_size, 5)
    }, create=True, open=True).result()

    vid_store = ts.open({
        "driver": "zarr",
        "kvstore": {"driver": "file", "path": f"{cfg.root}/vids_{year}_{MONTH_ABBR[month]}.zarr"},
        "dtype": "int32",
        "shape": (num_windows,),
        "chunk_shape": (cfg.chunk_size,)
    }, create=True, open=True).result()

    # batch sliding-window write
    stride = cfg.window_size * 5
    for start in range(0, num_windows, cfg.chunk_size):
        end = min(start + cfg.chunk_size, num_windows)
        batch_size = end - start

        windows_chunk = windows[start*stride:end*stride]
        vids_chunk = vids[start:end]

        windows_host = cp.asnumpy(windows_chunk).reshape(batch_size, cfg.window_size, 5)
        vids_host = cp.asnumpy(vids_chunk)

        store[start:end, :, :] = windows_host
        vid_store[start:end] = vids_host

    print(f"Processed month {MONTH_ABBR[month]} {year} | Generated windows: {num_windows}")

# ------------------------------
# Main
# ------------------------------
cfg = AISConfig(root="../dataset/piraeus", chunk_size=500_000, window_size=128)

for year, months in DATA_PERIODS:
    for month in months:
        process_month_gpu(year, month, cfg)

print("GPU preprocessing completed.")
