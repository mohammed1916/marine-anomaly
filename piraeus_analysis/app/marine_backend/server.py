# marine_backend/server.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from marine_backend.routes.stream_rows import router as stream_router
from marine_backend.routes.stream_rows_time import router as stream_router_time
from marine_backend.routes.heatmap import router as heatmap_router
from marine_backend.routes.unique_vessels_multi import router as unique_vessels_multi
from marine_backend.routes.predict_trajectory import router as predict_trajectory_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_router)
app.include_router(stream_router_time)
app.include_router(heatmap_router)
app.include_router(unique_vessels_multi)
app.include_router(predict_trajectory_router)

PARQUET_DIR = Path("./marine_backend/parquet")  

@app.get("/files")
def get_files():
    files = []
    for pq_file in sorted(PARQUET_DIR.rglob("*.parquet")):
        # optional: include relative path so frontend can identify year
        files.append({"name": str(pq_file.relative_to(PARQUET_DIR))})
    return files

if __name__ == "__main__":
    files = []
    for pq_file in sorted(PARQUET_DIR.rglob("*.parquet")):
        # optional: include relative path so frontend can identify year
        files.append({"name": str(pq_file.relative_to(PARQUET_DIR))})
    print(files)