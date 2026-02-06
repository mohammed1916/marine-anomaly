# marine_backend/routes/stream_rows_time.py
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import json

from marine_backend.core.readers import read_time_window
from marine_backend.utils.data_process import sanitize_row

router = APIRouter()

@router.get("/rows/stream_time")
def stream_rows_time(
    file: str = Query(...),
    start_ts: int = Query(...),
    end_ts: int = Query(...),
):
    """
    Stream AIS rows filtered by timestamp window.
    """
    def generator():
        df = read_time_window(file, start_ts, end_ts)
        total = len(df)

        for i, (_, row) in enumerate(df.iterrows()):
            d = sanitize_row(row.to_dict())
            yield json.dumps(
                {
                    "progress": int((i + 1) * 100 / max(total, 1)),
                    "row": d,
                },
                allow_nan=False,
            ) + "\n"

    return StreamingResponse(generator(), media_type="text/plain")
