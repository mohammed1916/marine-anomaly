# marine_backend/routes/stream_rows.py
from fastapi import APIRouter, Query
from marine_backend.core.readers import read_row
import json
from fastapi.responses import StreamingResponse
from marine_backend.utils.data_process import sanitize_row
from typing import Optional
from marine_backend.core.parquet_store import PARQUET_DIR
import pyarrow.parquet as pq

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

@router.get("/analysis-multi/stream")
def analysis_multi_stream(
    files: list[str] = Query(...),
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None
):
    def generator():
        total_rows = 0
        # count total rows (optional, for progress)
        for file in files:
            pq_file = pq.ParquetFile(PARQUET_DIR / file)
            for g in range(pq_file.num_row_groups):
                df = pq_file.read_row_group(g).to_pandas()
                if start_ts is not None:
                    df = df[df["t"] >= start_ts]
                if end_ts is not None:
                    df = df[df["t"] <= end_ts]
                total_rows += len(df)
        sent = 0
        # yield rows one by one
        for file in files:
            pq_file = pq.ParquetFile(PARQUET_DIR / file)
            for g in range(pq_file.num_row_groups):
                df = pq_file.read_row_group(g).to_pandas()
                if start_ts is not None:
                    df = df[df["t"] >= start_ts]
                if end_ts is not None:
                    df = df[df["t"] <= end_ts]
                for r in df.to_dict(orient="records"):
                    sent += 1
                    yield json.dumps({
                        "progress": int(sent * 100 / max(total_rows, 1)),
                        "row": sanitize_row(r),
                    }) + "\n"
    return StreamingResponse(generator(), media_type="text/plain")

