import numpy as np
from fastapi import APIRouter, Query
from marine_backend.core.readers import read_time_window

router = APIRouter()

# simple in-memory cache
heatmap_cache = {}

FIXED_BOUNDS = {
    "min_lat": 37.45947, "max_lat": 38.03808166666671,
    "min_lon": 23.0350833333333, "max_lon": 23.8806466666667
}

@router.get("/heatmap")
def heatmap(file: str, start_ts: int = Query(-10**18), end_ts: int = Query(10**18), cell_size: float = Query(0.001)):
    cache_key = f"{file}_{cell_size}"
    
    # check cache
    if cache_key in heatmap_cache:
        return heatmap_cache[cache_key]

    df = read_time_window(file, start_ts, end_ts)
    if df.empty:
        return []

    lat_bins = np.arange(FIXED_BOUNDS["min_lat"], FIXED_BOUNDS["max_lat"] + cell_size, cell_size)
    lon_bins = np.arange(FIXED_BOUNDS["min_lon"], FIXED_BOUNDS["max_lon"] + cell_size, cell_size)
    heatmap_grid = np.zeros((len(lat_bins)-1, len(lon_bins)-1), dtype=int)

    lat_idx = np.searchsorted(lat_bins, df['lat'].values, side='right') - 1
    lon_idx = np.searchsorted(lon_bins, df['lon'].values, side='right') - 1
    mask = (lat_idx >= 0) & (lat_idx < heatmap_grid.shape[0]) & (lon_idx >= 0) & (lon_idx < heatmap_grid.shape[1])
    np.add.at(heatmap_grid, (lat_idx[mask], lon_idx[mask]), 1)

    max_count = heatmap_grid.max()
    points = [
        [(lat_bins[i]+lat_bins[i+1])/2, (lon_bins[j]+lon_bins[j+1])/2, heatmap_grid[i,j]/max_count]
        for i in range(heatmap_grid.shape[0]) 
        for j in range(heatmap_grid.shape[1]) 
        if heatmap_grid[i,j] > 0
    ]

    # store in cache
    heatmap_cache[cache_key] = points
    return points
