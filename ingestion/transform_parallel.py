import pandas as pd
import numpy as np
import os
import time
from ingest_all_sequential import ingest_paysim
from concurrent.futures import ProcessPoolExecutor, as_completed


# set up file to be used and chunck size 
# use the csv one 
file_used= "data/processed/transactions.parquet"
file_done= "data/processed/transactions_transformed.parquet"

def transform_chunk(df):
    df["balance_drain"] = df["old_balance_org"] - df["new_balance_orig"] - df["amount"]
    df["log_amount"]= np.log(df["amount"] + 1)
    return df


def transform_parallel(n_workers=8):
    
    df = pd.read_parquet(file_used).head(1000)
    chunks = np.array_split(df, n_workers)

    with ProcessPoolExecutor (max_workers= n_workers) as executor:
        results= list(executor.map(transform_chunk, chunks))

    final_df = pd.concat(results)
    final_df.to_parquet (file_done)
    return final_df

def transform_sequential():
    df = pd.read_parquet(file_used).head(1000)
    result = transform_chunk(df)
    return result

def benchmark():
    t1 = time.perf_counter()
    transform_sequential()
    t2 = time.perf_counter()
    duration_sequential = t2 - t1
    
    t3 = time.perf_counter()
    transform_parallel()
    t4 = time.perf_counter()
    duration_parallel = t4 - t3
    
    speedup = duration_sequential / duration_parallel
    
    print(f"Sequential | {duration_sequential:.2f}s")
    print(f"Parallel   | {duration_parallel:.2f}s | {speedup:.2f}x speedup")

if __name__ == "__main__":
    benchmark()



