# marine_backend/routes/stream_rows_time.py
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import json

from marine_backend.core.readers import read_time_window
from marine_backend.utils.data_process import sanitize_row
import pyarrow.compute as pc

router = APIRouter()

@router.get("/rows/stream_time")
def stream_rows_time(
    file: str = Query(...),
    start_ts: int = Query(...),
    end_ts: int = Query(...),
):
    """
    Stream AIS rows filtered by timestamp window using PyArrow directly.
    """
    def generator():
        table: pa.Table = read_time_window(file, start_ts, end_ts)
        columns = table.column_names
        col_values = [table.column(c).to_pylist() for c in columns]
        total = table.num_rows

        for i in range(total):
            row = {col: col_values[j][i] for j, col in enumerate(columns)}
            d = sanitize_row(row)
            yield json.dumps(
                {
                    "progress": int((i + 1) * 100 / max(total, 1)),
                    "row": d,
                },
                allow_nan=False,
            ) + "\n"

    return StreamingResponse(generator(), media_type="text/plain")

@router.get("/rows/time_bounds")
def time_bounds(file: str):
    table = read_time_window(file, -10**18, 10**18)

    # pick first column (or 't'/'timestamp' if you prefer)
    col_name = table.schema.names[0]

    # get the column as a single ChunkedArray
    arr = table.column(col_name).combine_chunks()

    # compute min and max using pyarrow.compute
    min_val = pc.min(arr).as_py()
    max_val = pc.max(arr).as_py()

    return {
        "min": int(min_val),
        "max": int(max_val)
    }

