
- ThreadPoolExecutor for Ingestion

If I used ProcessPoolExecutor in this situation, it wouldn't work well, since this exercise doesn't involve heavy computation (like math) and isn't CPU-bound. This is heavy I/O-bound work instead, since we're loading a file with a huge amount of data and converting it to a parquet file. There were also several different datasets to extract (API and web-heavy), which is why ThreadPoolExecutor was the right choice here.

A scenario where ProcessPoolExecutor would have been better suited is processing large files, like image or PDF extraction. For example, in Milestone 1.4, where there's more math and calculation involved, that's CPU work, so ProcessPoolExecutor belongs there instead.

- What I Expected, Got, and Concluded

 I. Sequential Ingestion

   1. ingest_paysim()

        This function reads a CSV file, fixes the column names (to snake_case), changes data types where needed, and saves the result as a parquet file (for easier querying in the future).


Expected:I expected that when I printed the output, the column names and data types would be changed: for example 0/1 becoming True/False since that makes more sense conceptually. I also expected to see the number of rows and columns, which would give me a good general sense of what the PaySim file and its variables/values actually look like.

Output: To check the different variables and get an overall view of the file, I used df.shape to see its shape, which returned: [6362620 rows x 11 columns]. To check what the first several rows looked like, I used df.head() to see the actual values. For example, this was the output(df.head()):

step  type      amount    name_orig     old_balance_org  new_balance_orig  name_dest     old_balance_dest  new_balance_dest  is_fraud  is_flagged_fraud
1     PAYMENT   9839.64   C1231006815   170136.00        160296.36         M1979787155   0.0               0.00              False     False
1     PAYMENT   1864.28   C1666544295   21249.00         19384.72          M2044282225   0.0               0.00              False     False
1     TRANSFER  181.00    C1305486145   181.00           0.00              C553264065    0.0               0.00              True      False
1     CASH_OUT  181.00    C840083671    181.00           0.00              C38997010     21182.0           0.00              True      False
1     PAYMENT   11668.14  C2048537720   41554.00         29885.86          M1230701703   0.0               0.00              False     False
1     PAYMENT   7817.71   C90045638     53860.00         46042.29          M573487274    0.0               0.00              False     False
1     PAYMENT   7107.77   C154988899    183195.00        176087.23         M408069119    0.0               0.00              False     False
1     PAYMENT   7861.64   C1912850431   176087.23        168225.59         M633326333    0.0               0.00              False     False
1     PAYMENT   4024.36   C1265012928   2671.00          0.00              M1176932104   0.0               0.00              False     False
1     DEBIT     5337.77   C712410124    41720.00         36382.23          C195600860    41898.0           40348.79          False     False

        2. ingest_fred():

                This function connects to the FRED API, downloads three macro series (inflation, unemployment, USD/EUR exchange rate), prints shape/head/info to validate each download, saves each series as a CSV under data/raw/macro/, stores them in a dictionary, and returns that dictionary. Errors like no internet connection are caught, so the pipeline can report the failure instead of crashing silently.

                Expected: I expected that it would extract the data for each series (UNRATE, CPI, DEXUSEU) and that they'd successfully show up, and the output showed exactly this.

                Output: 

CPIAUCSL (Consumer Price Index):

| Date       | Value   |
|------------|---------|
| 1947-01-01 | 21.480  |
| 1947-02-01 | 21.620  |
| 1947-03-01 | 22.000  |
| 1947-04-01 | 22.000  |
| 1947-05-01 | 21.950  |
| ...        | ...     |
| 2026-02-01 | 327.460 |
| 2026-03-01 | 330.293 |
| 2026-04-01 | 332.407 |
| 2026-05-01 | 333.979 |
| 2026-06-01 | 332.568 |

Length: 954, dtype: float64

UNRATE (Unemployment Rate):

| Date       | Value |
|------------|-------|
| 1948-01-01 | 3.4   |
| 1948-02-01 | 3.8   |
| 1948-03-01 | 4.0   |
| 1948-04-01 | 3.9   |
| 1948-05-01 | 3.5   |
| ...        | ...   |
| 2026-02-01 | 4.4   |
| 2026-03-01 | 4.3   |
| 2026-04-01 | 4.3   |
| 2026-05-01 | 4.3   |
| 2026-06-01 | 4.2   |

Length: 942, dtype: float64. 
DEXUSEU (USD/EUR Exchange Rate):

| Date       | Value  |
|------------|--------|
| 1999-01-04 | 1.1812 |
| 1999-01-05 | 1.1760 |
| 1999-01-06 | 1.1636 |
| 1999-01-07 | 1.1672 |
| 1999-01-08 | 1.1554 |
| ...        | ...    |
| 2026-07-06 | 1.1426 |
| 2026-07-07 | 1.1423 |
| 2026-07-08 | 1.1396 |
| 2026-07-09 | 1.1439 |
| 2026-07-10 | 1.1438 |

Length: 7180, dtype: float64. 

        3. run_sequential()

This function calls ingest_paysim(), ingest_fred(), and ingest_complaints() one after another sequentially,  and times the whole process using time.perf_counter().

Expected I expected run_sequential() to take a lot of time, since it's pulling in a large amount of data from both PaySim and FRED one task at a time, with zero overlap between them. Each function has to fully finish reading the file, calling the API, saving the result  before the next one starts, so I knew the total would basically be the sum of all three individual runtimes rather than anything faster.

Output: It took 10.32 seconds to run in total. This is normal to me, considering PaySim has 6.3 million rows being read and transformed, on top of three separate live API calls to FRED for CPI, unemployment, and the exchange rate. Given how much is actually happening behind that one number, 10 seconds doesn't feel slow at all it.

To resolve the fact that run_sequential() waits for ingest_paysim() to finish before running ingest_fred() (and so on), we can use ThreadPoolExecutor to solve this problem — threads let the functions run in parallel, meaning that while ingest_paysim() is running, ingest_fred()` can also be running on a different thread, at the same time.

        4. run_parallel()

opens a ThreadPoolExecutor with a number of workers (2), then submits (runs) ingest_fred() and ingest_paysim() to run at the same time (ingest_complaints() is commented out for now since I'm still waiting on the URL). It uses as_completed() to grab each result as soon as it's ready, and wraps each one in a try/except so if one fails, it doesn't crash the other. At the end, it returns whatever results came back successfully.

Expected: I expected this to let both functions run at the same time, and be faster than run_sequential(), so when comparing the two in the benchmark, I expected run_parallel()'s number to be lower than run_sequential()`'s.

Output: I got exactly what I expected but the difference is around 3seconds whoch for me isn't that high.


| Method     | Time (s) | Speedup |
|------------|----------|---------|
| Sequential | 9.93     | 1.0x    |
| Parallel   | 6.84     | 1.45x   |


- Transform Parallel

        1. transform_chunk() 

        Adds two new columns, balance_drain and log_amount, to a piece of the transaction data. It also makes sure amount is float64 and is_fraud is bool, then returns the chunk. Both sequential and parallel use this same function.

        2. transform_sequential(n_rows)

        Reads transactions.parquet, takes the first n_rows with .head(n_rows), runs transform_chunk() on the whole dataset at once in a single process, creates the output folder if needed, and saves to transactions_transformed.parquet. This is my comparison baseline.

        3. transform_parallel(n_rows, n_workers=8)

        Reads transactions.parquet and takes .head(n_rows). Then it splits the data into chunks using chunk_size = len(df) // n_workers and a list comprehension: [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]. I use for loops to submit each chunk to transform_chunk() with ProcessPoolExecutor, collect the results with future.result(), combine them with pd.concat(), and save to transactions_transformed.parquet.

        4. benchmark(n_rows, n_workers=4)

        Times both transform_sequential(n_rows) and transform_parallel(n_rows, n_workers), calculates speedup, and prints the row count plus both runtimes. In __main__ I run it for 500_000 and 1_000_000 rows. When benchmark runs, parallel uses 4 workers (not 8), because benchmark passes n_workers=4.

Chunk reasoning:
I split the data based on n_workers (chunk_size = total rows ÷ number of workers) using iloc instead of np.array_split. I stopped using np.array_split because it was turning the dataframe into numpy arrays and breaking column access when running in parallel. With 500k rows and 4 workers in the benchmark, each chunk is about 125k rows. I chose splitting by worker count because it directly matches the process pool — one chunk per worker, simple to implement, and easy to benchmark.

The tradeoff is that chunk size grows with the size of the dataset — at full PaySim scale (6.3M rows) with 8 workers, each chunk would be around 790k rows, which uses more memory per process than smaller fixed chunks would. A fixed chunk size like 500k would give better control over memory usage and load balancing on very large datasets, but splitting by worker count was simpler and matched my design more directly.

Benchmark results:

| Rows      | Sequential | Parallel |
|-----------|------------|----------|
| 500,000   | 0.67s      | 0.89s    |

The parallel version was slower than the sequential one for this amount of data. After thinking about it, it makes sense because transform_chunk() only does simple calculations, so it runs very quickly even with 500,000 rows. Using ProcessPoolExecutor also takes extra time because it has to start multiple processes and split the data between them. Since the calculations were already so fast, that extra time made the parallel version slower. This shows that ProcessPoolExecutor works better for more complex tasks, but for simple calculations like these, the sequential version can actually be faster.