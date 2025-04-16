import pandas as pd
import os

def load_csv(file_path, **kwargs):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing {file_path}")
    return pd.read_csv(file_path, **kwargs)