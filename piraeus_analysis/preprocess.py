import cudf
import rmm
import numpy as np
import cupy as cp
from numba import cuda
import math
import tensorstore as ts
from pathlib import Path

# ------------------------------
# Config
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

rmm.reinitialize(pool_allocator=True, managed_memory=False)

class AISConfig:
    def __init__(self, root, chunk_size, window_size):
        self.root = root
        self.chunk_size = chunk_size   # windows per batch
        self.window_size = window_size

# ------------------------------
# CUDA kernel (batch-local)
# ------------------------------
@cuda.jit
def fused_mask_clamp_window_kernel(
    vessel_id, lat, lon, speed, course, ts,
    start_idx, N, window_size,
    out_windows, out_vids
):
    i = cuda.grid(1)
    if i >= out_vids.size:
        return

    idx = start_idx + i
    if idx + window_size > N:
        return

    vid = vessel_id[idx]
    if vessel_id[idx + window_size - 1] != vid:
        out_vids[i] = -1
        return

    base = i * window_size * 5

    for j in range(window_size):
        r = idx + j
        s = speed[r]
        c = course[r]

        if math.isnan(s) or math.isnan(c):
            out_vids[i] = -1
            return

        if s < 0.0:
            s = 0.0
        elif s > 100.0:
            s = 100.0

        if c < 0.0:
            c = 0.0
        elif c > 360.0:
            c = 360.0

        out_windows[base + j*5 + 0] = lat[r]
        out_windows[base + j*5 + 1] = lon[r]
        out_windows[base + j*5 + 2] = s
        out_windows[base + j*5 + 3] = c
        out_windows[base + j*5 + 4] = ts[r]

    out_vids[i] = vid

# ------------------------------
# RMM → CuPy helper
# ------------------------------
def rmm_to_memptr(buf):
    return cp.cuda.MemoryPointer(
        cp.cuda.UnownedMemory(buf.ptr, buf.size, buf), 0
    )

# ------------------------------
# Main processing
# ------------------------------
def process_month_gpu(year, month, cfg):
    file_path = (
        f"{cfg.root}/unipi_ais_dynamic_{year}/"
        f"unipi_ais_dynamic_{MONTH_ABBR[month]}{year}.csv"
    )

    print(f"Processing {MONTH_ABBR[month]} {year}")

    df = cudf.read_csv(file_path)
    df = df.rename(columns={"t": "timestamp"})
    df["timestamp"] = df["timestamp"].astype("float32")
    df["vessel_id"], _ = df["vessel_id"].factorize()

    gathered = df[
        ["vessel_id", "lat", "lon", "speed", "course", "timestamp"]
    ].sort_values(["vessel_id", "timestamp"])

    N = len(gathered)
    total_windows = N - cfg.window_size + 1
    if total_windows <= 0:
        return

    # ------------------------------
    # TensorStore (CREATE OUTPUT)
    # ------------------------------
    out_root = Path(cfg.root) / "processed"
    out_root.mkdir(parents=True, exist_ok=True)

    windows_store = ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": str(out_root / f"windows_{year}_{MONTH_ABBR[month]}.zarr"),
            },
        },
        create=True,
        open=True,
        dtype=ts.float32,
        shape=[total_windows, cfg.window_size, 5],
        chunk_layout=ts.ChunkLayout(
            chunk_shape=[1024, cfg.window_size, 5]
        ),
    ).result()

    vids_store = ts.open(
        {
            "driver": "zarr",
            "kvstore": {
                "driver": "file",
                "path": str(out_root / f"vids_{year}_{MONTH_ABBR[month]}.zarr"),
            },
        },
        create=True,
        open=True,
        dtype=ts.int32,
        shape=[total_windows],
        chunk_layout=ts.ChunkLayout(
            chunk_shape=[1024]
        ),
    ).result()

    vessel_id = gathered["vessel_id"].to_cupy()
    lat = gathered["lat"].to_cupy()
    lon = gathered["lon"].to_cupy()
    speed = gathered["speed"].to_cupy()
    course = gathered["course"].to_cupy()
    ts_col = gathered["timestamp"].to_cupy()

    threads = 256
    write_offset = 0

    # ------------------------------
    # STREAMING LOOP
    # ------------------------------
    for start in range(0, total_windows, cfg.chunk_size):
        batch = min(cfg.chunk_size, total_windows - start)

        win_buf = rmm.DeviceBuffer(
            size=batch * cfg.window_size * 5 * 4
        )
        vid_buf = rmm.DeviceBuffer(size=batch * 4)

        win_dev = cp.ndarray(
            (batch * cfg.window_size * 5,),
            dtype=cp.float32,
            memptr=rmm_to_memptr(win_buf),
        )
        vid_dev = cp.ndarray(
            (batch,),
            dtype=cp.int32,
            memptr=rmm_to_memptr(vid_buf),
        )

        blocks = (batch + threads - 1) // threads

        fused_mask_clamp_window_kernel[blocks, threads](
            vessel_id, lat, lon, speed, course, ts_col,
            start, N, cfg.window_size,
            win_dev, vid_dev
        )
        cuda.synchronize()

        win_host = cp.asnumpy(
            win_dev.reshape(batch, cfg.window_size, 5)
        )
        vid_host = cp.asnumpy(vid_dev)

        windows_store[
            write_offset:write_offset + batch
        ].write(win_host).result()

        vids_store[
            write_offset:write_offset + batch
        ].write(vid_host).result()

        write_offset += batch

        del win_dev, vid_dev, win_buf, vid_buf
        cp.get_default_memory_pool().free_all_blocks()

    print(
        f"Done {MONTH_ABBR[month]} {year} | windows={total_windows}"
    )

# ------------------------------
# Main
# ------------------------------
cfg = AISConfig(
    root=r"/mnt/c/Users/BBBS-AI-01/d/anomaly/dataset/piraeus",
    chunk_size=500_000,
    window_size=128,
)

for year, months in DATA_PERIODS:
    for month in months:
        process_month_gpu(year, month, cfg)

print("GPU preprocessing completed.")
