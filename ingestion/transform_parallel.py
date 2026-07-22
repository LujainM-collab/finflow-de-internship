import pandas as pd
import numpy as np
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed


# set up file to be used and chunck size 
# use the csv one 
file_used= "data/processed/transactions.parquet"
file_done= "data/processed/transactions_transformed.parquet"

def transform_chunk(df):
    df["balance_drain"] = df["old_balance_org"] - df["new_balance_orig"] - df["amount"]
    df["log_amount"]= np.log(df["amount"] + 1)
    df["amount"] = df["amount"].astype("float64")
    df["is_fraud"] = df["is_fraud"].astype(bool)
    return df

def transform_sequential(n_rows):
    df = pd.read_parquet(file_used).head(n_rows)
    result = transform_chunk(df)
    os.makedirs("data/processed", exist_ok=True)
    result.to_parquet(file_done)
    return result

def transform_parallel(n_rows, n_workers=8):
    df = pd.read_parquet(file_used).head(n_rows)
    chunk_size = len(df) // n_workers
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for chunk in chunks:
            futures.append(executor.submit(transform_chunk, chunk))

        results = []
        for future in futures:
            results.append(future.result())

    final_df = pd.concat(results)
    final_df.to_parquet(file_done)
    return final_df

def benchmark(n_rows, n_workers=4):
    t1 = time.perf_counter()
    transform_sequential(n_rows)
    t2 = time.perf_counter()
    duration_sequential = t2 - t1

    t3 = time.perf_counter()
    transform_parallel(n_rows, n_workers)
    t4 = time.perf_counter()
    duration_parallel = t4 - t3

    speedup = duration_sequential / duration_parallel

    print("rows:", n_rows)
    print("Sequential:", duration_sequential)
    print("Parallel:", duration_parallel)

if __name__ == "__main__":
    benchmark(500_000)
    benchmark(1_000_000)



