from fastapi import FastAPI, HTTPException
import pyarrow.parquet as pq
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from marine_backend.utils.data_process import sanitize_row

app = FastAPI()

origin = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load Parquet metadata once
PARQUET_FILE = "./marine_backend/unipi_ais_dynamic_may2017.parquet"
pq_file = pq.ParquetFile(PARQUET_FILE)
num_rows = pq_file.metadata.num_rows
rows_per_group = pq_file.metadata.row_group(0).num_rows 

def read_row(row_idx: int) -> pd.Series:
    if row_idx < 0 or row_idx >= num_rows:
        raise IndexError("Row index out of bounds")

    # Find which row group contains the row
    cum_rows = 0
    for group_idx in range(pq_file.num_row_groups):
        rg_rows = pq_file.metadata.row_group(group_idx).num_rows
        if row_idx < cum_rows + rg_rows:
            local_idx = row_idx - cum_rows
            table = pq_file.read_row_group(group_idx)
            df = table.to_pandas()
            return df.iloc[local_idx]
        cum_rows += rg_rows

@app.get("/rows")
def get_rows(start: int = 0, end: int = 100):
    # print("start: ", start)
    # print("end: ", end)
    rows =[]
    for i in range(start, end):
        try:
            row = read_row(i)
            d = sanitize_row(row.to_dict())
            rows.append(d)
        except IndexError as e:
            raise HTTPException(status_code=404, detail=str(e))
    return rows

if __name__ == "__main__":
    rows =[]
    for i in range(0, 100):
        try:
            row = read_row(i)
            d = sanitize_row(row.to_dict())
            rows.append(d)
        except IndexError as e:
            print(e)
    print(rows)