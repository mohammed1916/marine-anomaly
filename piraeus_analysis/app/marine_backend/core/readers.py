# marine_backend/core/readers.py
import pandas as pd
from marine_backend.core.parquet_store import PARQUET_DIR
import pyarrow.parquet as pq
from marine_backend.utils.data_process import sanitize_row

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

def read_time_window(file: str, start_ts: int, end_ts: int) -> list[dict]:
    """
    Return rows with t in [start_ts, end_ts] from a single parquet file.
    Avoids pandas conversion.
    """
    pq_file = pq.ParquetFile(PARQUET_DIR / file)
    rows = []

    for g in range(pq_file.num_row_groups):
        table = pq_file.read_row_group(g)

        # Determine timestamp column
        col_name = "t" if "t" in table.column_names else "timestamp"
        col_data = table[col_name].to_numpy()

        # Mask rows in the time range
        mask = (col_data >= start_ts) & (col_data <= end_ts)

        if mask.any():
            # Slice the table with PyArrow
            selected_table = table.filter(pa.compute.field(col_name).ge(start_ts)
                                          & pa.compute.field(col_name).le(end_ts))
            # Convert to dict directly
            rows.extend([sanitize_row(r) for r in selected_table.to_pylist()])

    return rows

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

