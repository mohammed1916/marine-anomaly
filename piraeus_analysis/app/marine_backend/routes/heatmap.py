# marine_backend/routes/heatmap.py
from fastapi import APIRouter, Query
from marine_backend.core.readers import read_time_window
import numpy as np
import json

router = APIRouter()

@router.get("/heatmap")
def heatmap(
    file: str,
    start_ts: int = Query(-10**18),
    end_ts: int = Query(10**18),
    cell_size: float = Query(0.001)
):
    """
    Return grid-based heatmap of AIS points for a file and time range.
    Sends JSON: list of [lat, lon, normalized_count]
    """
    df = read_time_window(file, start_ts, end_ts)
    if df.empty:
        return []

    # compute bounds with a small epsilon to include max
    eps = 1e-9
    min_lat, max_lat = df['lat'].min(), df['lat'].max() + eps
    min_lon, max_lon = df['lon'].min(), df['lon'].max() + eps

    lat_bins = np.arange(min_lat, max_lat + cell_size, cell_size)
    lon_bins = np.arange(min_lon, max_lon + cell_size, cell_size)

    heatmap_grid = np.zeros((len(lat_bins)-1, len(lon_bins)-1), dtype=int)

    # bin points efficiently
    lat_idx = np.clip(np.searchsorted(lat_bins, df['lat'].values, side='right') - 1, 0, heatmap_grid.shape[0]-1)
    lon_idx = np.clip(np.searchsorted(lon_bins, df['lon'].values, side='right') - 1, 0, heatmap_grid.shape[1]-1)

    np.add.at(heatmap_grid, (lat_idx, lon_idx), 1)

    # convert to points for frontend
    points = []
    max_count = heatmap_grid.max()
    if max_count == 0:
        return []

    for i in range(heatmap_grid.shape[0]):
        for j in range(heatmap_grid.shape[1]):
            count = heatmap_grid[i, j]
            if count > 0:
                lat = (lat_bins[i] + lat_bins[i+1]) / 2
                lon = (lon_bins[j] + lon_bins[j+1]) / 2
                points.append([lat, lon, count / max_count])

    return points
