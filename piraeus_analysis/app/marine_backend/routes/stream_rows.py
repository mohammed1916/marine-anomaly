from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

from marine_backend.core.readers import read_row
from marine_backend.utils.data_process import sanitize_row

router = APIRouter()

@router.get("/rows/stream")
def stream_rows(start: int = 0, end: int = 100):
    total = max(end - start, 1)

    def generator():
        for idx, i in enumerate(range(start, end), 1):
            row = read_row(i)
            d = sanitize_row(row.to_dict())
            yield json.dumps({
                "progress": int(idx * 100 / total),
                "row": d
            }) + "\n"

    return StreamingResponse(generator(), media_type="text/plain")
