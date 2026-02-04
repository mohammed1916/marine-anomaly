import pyarrow.parquet as pq

PARQUET_FILE = "./marine_backend/unipi_ais_dynamic_may2017.parquet"

pq_file = pq.ParquetFile(PARQUET_FILE)
num_rows = pq_file.metadata.num_rows
