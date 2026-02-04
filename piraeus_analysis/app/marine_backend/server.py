from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from marine_backend.routes.stream_rows import router as stream_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_router)

@app.get("/files")
def get_files():
    return [{"name": "unipi_ais_dynamic_may2017.parquet"}]
