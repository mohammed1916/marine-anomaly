# marine_backend/core/parquet_store.py
import pyarrow.parquet as pq
from pathlib import Path

PARQUET_DIR = Path("./marine_backend/parquet")

parquet_files = list(PARQUET_DIR.glob("*.parquet"))

for f in parquet_files:
    pq_file = pq.ParquetFile(f)
    print(f"{f.name}: {pq_file.metadata.num_rows} rows")
