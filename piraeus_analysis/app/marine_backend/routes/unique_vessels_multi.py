# marine_backend/routes/unique_vessels_multi.py
from fastapi import APIRouter, Request
from marine_backend.core.readers import read_time_window
import json
import time
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/unique-vessels-multi")
async def unique_vessels_multi(request: Request):
    """
    Stream unique vessel counts for multiple files.
    """
    data = await request.json()
    files = data.get("files", [])

    async def streamer():
        total_files = len(files)
        for i, file in enumerate(files):
            df = read_time_window(file, -10**18, 10**18)
            unique_count = int(df["vessel_id"].nunique()) if not df.empty else 0
            progress = int(((i + 1) / total_files) * 100)
            yield json.dumps({"file": file, "unique_vessels": unique_count, "progress": progress}) + "\n"
            time.sleep(0.1)  # optional: simulate delay / allow frontend to see progress

    return StreamingResponse(streamer(), media_type="text/plain")
