# marine_backend/core/readers.py
import pandas as pd
from marine_backend.core.parquet_store import PARQUET_DIR
from marine_backend.utils.data_process import sanitize_row
import pyarrow.parquet as pq 
import pyarrow.compute as pc
import pyarrow as pa

# Load all Parquet files
parquet_files = list(PARQUET_DIR.glob("*.parquet"))

# Preload all rows into memory (optional, only if dataset fits in RAM)
_all_rows: list[dict] = []

for f in parquet_files:
    pq_file = pq.ParquetFile(f)
    for g in range(pq_file.num_row_groups):
        table = pq_file.read_row_group(g)
        df = table.to_pandas()
        _all_rows.extend(df.to_dict(orient="records"))

def read_time_window(file_path: str, start_ts: int, end_ts: int) -> pa.Table:
    """
    Read a parquet file and filter rows within a time window.

    Parameters
    ----------
    file_path : str
        Path to the parquet file.
    start_ts : int
        Start timestamp (inclusive).
    end_ts : int
        End timestamp (inclusive).

    Returns
    -------
    filtered_table : pyarrow.Table
        Table filtered to rows where 't' is in [start_ts, end_ts].
    """
    # Load parquet file as table
    table = pq.read_table(PARQUET_DIR / file_path)

    # Combine chunks for the 't' column to avoid ChunkedArray errors
    col = table["t"].combine_chunks()

    # Create mask using pyarrow.compute functions
    mask = pc.and_(
        pc.greater_equal(col, start_ts),
        pc.less_equal(col, end_ts)
    )

    # Filter table by mask
    filtered_table = table.filter(mask)

    return filtered_table


# def read_time_window(file: str, start_ts: int, end_ts: int) -> pd.DataFrame:
#     """
#     Return rows with t in [start_ts, end_ts] from a single parquet file.
#     """
#     pq_file = pq.ParquetFile(PARQUET_DIR / file)
#     frames = []

#     for g in range(pq_file.num_row_groups):
#         table = pq_file.read_row_group(g)
#         df = table.to_pandas()

#         col = "t" if "t" in df.columns else "timestamp"
#         mask = (df[col] >= start_ts) & (df[col] <= end_ts)

#         if mask.any():
#             frames.append(df.loc[mask])

#     if frames:
#         return pd.concat(frames, ignore_index=True)

#     return pd.DataFrame()

# def read_multiple_files(files: list[str], start_ts: int = None, end_ts: int = None) -> list[dict]:
#     frames = []

#     for file in files:
#         pq_file = pq.ParquetFile(PARQUET_DIR / file)
#         for g in range(pq_file.num_row_groups):
#             df = pq_file.read_row_group(g).to_pandas()

#             if start_ts is not None and end_ts is not None:
#                 col = "t" if "t" in df.columns else "timestamp"
#                 df = df[(df[col] >= start_ts) & (df[col] <= end_ts)]

#             if not df.empty:
#                 frames.extend([sanitize_row(r) for r in df.to_dict(orient="records")])

#     return frames


def read_row(file: str, idx: int) -> dict:
    """
    Read a single row by index from a parquet file.
    """
    pq_file = pq.ParquetFile(PARQUET_DIR / file)

    offset = 0
    for g in range(pq_file.num_row_groups):
        rg = pq_file.metadata.row_group(g)
        n = rg.num_rows

        if offset + n > idx:
            table = pq_file.read_row_group(g)
            df = table.to_pandas()
            return df.iloc[idx - offset].to_dict()

        offset += n

    raise IndexError("Row index out of range")

