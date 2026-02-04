import pandas as pd
from marine_backend.core.parquet_store import pq_file, num_rows

def read_row(row_idx: int) -> pd.Series:
    if row_idx < 0 or row_idx >= num_rows:
        raise IndexError("Row index out of bounds")

    cum = 0
    for g in range(pq_file.num_row_groups):
        rg = pq_file.metadata.row_group(g).num_rows
        if row_idx < cum + rg:
            table = pq_file.read_row_group(g)
            return table.to_pandas().iloc[row_idx - cum]
        cum += rg
