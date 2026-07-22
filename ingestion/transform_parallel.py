import pandas as pd
import numpy as np
import os
import time
from concurrent.futures import ProcessPoolExecutor


# set up file to be used and chunck size 
# use the csv one 
file_used= "data/processed/transactions.parquet"
file_done= "data/processed/transactions_transformed.parquet"

def transform_chunk(df):
    # create 2 new columns log_amount and balance_drain
    df["balance_drain"] = df["old_balance_org"] - df["new_balance_orig"] - df["amount"]
    df["log_amount"]= np.log(df["amount"] + 1)
    # make sure amount and =is_fraud are correct data types-> changed columns 
    df["amount"] = df["amount"].astype("float64")
    df["is_fraud"] = df["is_fraud"].astype(bool)
    # return transformed datsaframe
    return df

def transform_sequential(n_rows):
    # read parket file and keep only the first n_rows
    
    df = pd.read_parquet(file_used).head(n_rows)
    # in one process transform hole dataframe
    result = transform_chunk(df)
    # create an output folder if doesn;t already exixst 
    os.makedirs("data/processed", exist_ok=True)
    # save transformed data frame as a nes parquet file
    result.to_parquet(file_done)
    return result

def transform_parallel(n_rows, chunk_size=500_000, n_workers=4):    # since huge dataset read the required number of rows 
    df = pd.read_parquet(file_used).head(n_rows)
    # split data frame into smaller chunks
    # iloc slices rows using row positions 
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    # create a pool of worker processes
    #up to n workers processes can run at the same time
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        # store submited tasks
        futures = []
        # send each chunk to a seperate process
        for chunk in chunks:
            #executor.submit() tells another process to execute transform_chunk
            # returns fututre object
            futures.append(executor.submit(transform_chunk, chunk))
        # stpre the completed transformed chunks 
        results = []
        # wait for every process to finish
        for future in futures:
            # future.result() waits until that worker finishes
            # Then it returns the transformed chunk
            results.append(future.result())
    
    # Combine all transformed chunks into one DataFrame
    final_df = pd.concat(results)
    final_df.to_parquet(file_done)
    return final_df

def benchmark(n_rows, chunk_size, n_workers=8):    
    
    t1 = time.perf_counter()
    transform_sequential(n_rows)
    t2 = time.perf_counter()
    duration_sequential = t2 - t1

    t3 = time.perf_counter()
    transform_parallel(n_rows, chunk_size, n_workers)
    t4 = time.perf_counter()
    duration_parallel = t4 - t3

    speedup = duration_sequential / duration_parallel

    print("rows:", n_rows)
    print("Chunk size:", chunk_size)
    print("Workers:", n_workers)
    print("Sequential:", duration_sequential)
    print("Parallel:", duration_parallel)
    print()

if __name__ == "__main__":
    benchmark(6_362_620, chunk_size=1_000_000)
    benchmark(6_362_620, chunk_size=500_000)



