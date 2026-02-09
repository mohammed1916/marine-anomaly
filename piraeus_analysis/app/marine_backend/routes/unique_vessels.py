from fastapi import APIRouter, Query
from marine_backend.core.readers import read_time_window

router = APIRouter()

unique_vessel_cache = {}


@router.get("/unique-vessels")
def unique_vessels_graph(
    file: str,
    start_ts: int = Query(-10**18),
    end_ts: int = Query(10**18),
):
    """
    Return unique vessel count for a single file.
    Suitable for graph visualisation.
    """
    file = file.replace("\\", "/")

    cache_key = f"{file}_{start_ts}_{end_ts}"
    if cache_key in unique_vessel_cache:
        return unique_vessel_cache[cache_key]

    df = read_time_window(file, start_ts, end_ts)
    if df.empty:
        result = {"file": file, "unique_vessels": 0}
        unique_vessel_cache[cache_key] = result
        return result

    result = {
        "file": file,
        "unique_vessels": int(df["vessel_id"].nunique()),
    }

    unique_vessel_cache[cache_key] = result
    return result
