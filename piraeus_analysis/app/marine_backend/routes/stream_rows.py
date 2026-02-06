# marine_backend/routes/stream_rows.py
from fastapi import APIRouter, Query
from marine_backend.core.readers import read_row
import json
from fastapi.responses import StreamingResponse
from marine_backend.utils.data_process import sanitize_row

router = APIRouter()

@router.get("/rows/stream")
def stream_rows(
    file: str,
    start: int = Query(0),
    end: int = Query(100),
):
    """
    Stream AIS rows by index range from a parquet file.
    """
    def generator():
        for idx in range(start, end):
            try:
                row = read_row(file, idx)
                row = sanitize_row(row)
            except IndexError:
                break

            yield json.dumps({
                "progress": int((idx - start + 1) * 100 / max(end - start, 1)),
                "row": row,
            }) + "\n"

    return StreamingResponse(generator(), media_type="text/plain")
