import cudf
import rmm
import numpy as np
import numba
from numba import cuda

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

class AISConfig:
    def __init__(self, root, chunk_size, window_size):
        self.root = root
        self.chunk_size = chunk_size
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

        if np.isnan(s) or np.isnan(c):
            valid_window = False
            break

        s = min(max(s, 0.0), 100.0)
        c = min(max(c, 0.0), 360.0)

        speed[r] = s
        course[r] = c

        out_windows[base + j*5 + 0] = lat[r]
        out_windows[base + j*5 + 1] = lon[r]
        out_windows[base + j*5 + 2] = s
        out_windows[base + j*5 + 3] = c
        out_windows[base + j*5 + 4] = ts[r]

    out_vids[idx] = vid if valid_window else -1

# ------------------------------
# Save .npy helpers
# ------------------------------
def save_npy(filename, data, num_windows, window_size, features):
    arr = np.array(data).reshape(num_windows, window_size, features)
    np.save(filename, arr)

def save_vids(filename, vids):
    np.save(filename, np.array(vids))

# ------------------------------
# Main GPU processing
# ------------------------------
def process_month_gpu(year, month, cfg):
    file_path = f"{cfg.root}/unipi_ais_dynamic_{year}/unipi_ais_dynamic_{MONTH_ABBR[month]}{year}.csv"

    df = cudf.read_csv(file_path, usecols=COLS_ALIAS, byte_range_size=cfg.chunk_size)
    df = df.rename(columns={"t": "timestamp"})
    df["timestamp"] = df["timestamp"].astype("float32")

    df["vessel_id"], _ = df["vessel_id"].factorize()

    gathered = df[["vessel_id", "lat", "lon", "speed", "course", "timestamp"]]
    gathered = gathered.sort_values(["vessel_id", "timestamp"])

    N = len(gathered)
    num_windows = N - cfg.window_size + 1
    if num_windows <= 0:
        return

    windows = rmm.device_array(num_windows * cfg.window_size * 5, dtype=np.float32)
    vids = rmm.device_array(num_windows, dtype=np.int32)

    threads = 256
    blocks = (num_windows + threads - 1) // threads

    fused_mask_clamp_window_kernel[blocks, threads](
        gathered["vessel_id"].to_array(),
        gathered["lat"].to_array(),
        gathered["lon"].to_array(),
        gathered["speed"].to_array(),
        gathered["course"].to_array(),
        gathered["timestamp"].to_array(),
        N,
        cfg.window_size,
        windows,
        vids
    )
    cuda.synchronize()

    save_npy(f"{cfg.root}/windows_{year}_{MONTH_ABBR[month]}.npy",
             windows.copy_to_host(),
             num_windows, cfg.window_size, 5)
    save_vids(f"{cfg.root}/vids_{year}_{MONTH_ABBR[month]}.npy",
              vids.copy_to_host())

    print(f"Processed month {MONTH_ABBR[month]} {year} | Generated windows: {num_windows}")

# ------------------------------
# Main
# ------------------------------
cfg = AISConfig(root="../dataset/piraeus", chunk_size=500_000, window_size=128)

for year, months in DATA_PERIODS:
    for month in months:
        process_month_gpu(year, month, cfg)

print("GPU preprocessing completed.")
