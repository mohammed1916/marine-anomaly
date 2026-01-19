import pandas as pd
import numpy as np
import os

# path to the GNSS dataset
data_path = "C:\\Users\\BBBS-AI-01\\d\\anomaly\\dataset\\GNSS\\GNSS Dataset (with Interference and Spoofing) Part III\\1221\\Processed data"

# List files for demonstration
print('Files in GNSS data directory:')
print(os.listdir(data_path))

# Try loading a sample JSON file (update filename as needed)
sample_file = None
for fname in os.listdir(data_path):
    if fname.startswith('observation') and fname.endswith('.json'):
        sample_file = os.path.join(data_path, fname)
        break
if sample_file:
    import json
    with open(sample_file, 'r') as f:
        data = json.load(f)
    print(f'Loaded {sample_file}')
    print('Type:', type(data))
    if isinstance(data, dict):
        print('Keys:', list(data.keys()))
    elif isinstance(data, list) and len(data) > 0:
        print('First item keys:', list(data[0].keys()))
    # Convert to DataFrame
    df = pd.DataFrame(data if isinstance(data, list) else [data])
    print('DataFrame shape:', df.shape)
    print('Columns:', list(df.columns))
    print(df.head())
else:
    print('No observation JSON file found.')
