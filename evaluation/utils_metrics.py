import pandas as pd
import numpy as np


def compute_hit_percentage(df):
    return df["hits"] / (df["hits"] + df["misses"]) * 100

def compute_cost_per_gain(runtime_series, hit_percentage_series):
    runtime_gain = runtime_series.diff().fillna(0)
    hit_gain = hit_percentage_series.diff().replace(0, np.nan)
    return runtime_gain / hit_gain