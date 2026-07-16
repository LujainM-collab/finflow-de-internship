import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from ingest_all_sequential import (ingest_fred,ingest_paysim, run_sequential)


def run_parallel():
    results = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        temp = [
            executor.submit(ingest_fred),
            #executor.submit(ingest_complaints),
            executor.submit(ingest_paysim),
        ]
        for future in as_completed(temp):
            try:
                results.append(future.result())
            except Exception as error:
                print(f"failed: {error}")

    return results

def benchmark_ingestion():

    start = time.perf_counter()
    run_sequential()
    end= time.perf_counter()
    duration= end- start

    s= time.perf_counter()
    run_parallel()
    e= time.perf_counter()
    period= e-s

    speedup= duration/period

    # printing in table form 
    print(f"{'Method':<16}| {'Time(s)':<20}| {'Speedup'}")
    print("-" * 50)
    print(f"{'Sequential':<16}| {duration:<20}| 1.0x")
    print(f"{'Parallel':<16}| {period:<20}| {speedup}x")

benchmark_ingestion()



