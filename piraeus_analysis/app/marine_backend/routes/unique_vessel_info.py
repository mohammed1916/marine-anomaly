# marine_backend/routes/unique_vessel_info.py
from fastapi import APIRouter, Query
from marine_backend.core.readers import read_time_window

router = APIRouter()

@router.get("/unique-vessels")
def unique_vessels(file: str, start_ts: int = -10**18, end_ts: int = 10**18):
    """
    Return list of unique vessel IDs in a file/time window.
    """
    df = read_time_window(file, start_ts, end_ts)
    vessels = df.index.get_level_values(0).unique().tolist()
    return vessels
