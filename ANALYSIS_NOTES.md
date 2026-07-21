# ANALYSIS_NOTES — Milestone 1.3 Design Choice

## Design Choice A: why i used `ThreadPoolExecutor` for ingestion

Ingestion in FinFlow is I/O-bound, not CPU-bound. Most of the time each task is just waiting on:

- **Network**: FRED API calls (`fred.get_series`)
- **Disk**: reading `paysim.csv`, writing parquet and CSV files

While one thread waits on the network or disk, another thread can keep working. This works because threads are a good fit when you're waiting on I/O.

---

## what would happen if i used `ProcessPoolExecutor` instead?

If i swapped `ThreadPoolExecutor` for `ProcessPoolExecutor` in `ingest_all_parallel.py`:

### 1. Higher startup overhead
Each worker is a **separate Python process**. Processes take longer to create than threads and you have to **pickle** (serialize) function arguments and return values.

For short ingestion jobs, that overhead can eat into or even wipe out the speedup.

### 2. Much higher memory use
Processes do **not share memory**. With Paysim (~6.3M rows, ~621 MB in RAM), each process would load its own copy of the DataFrame.

Example with 2 processes both touching large data:
- Thread pool: one copy of shared memory in one process
- Process pool: potentially **2×+ RAM** for the same work

### 3. No real benefit from bypassing the GIL
Python's GIL limits parallel **CPU** work in threads. But ingestion isn't CPU-limited — it's waiting on I/O. Threads already overlap I/O waits, so bypassing the GIL with processes doesn't help much here.

### 4. Harder error handling and data sharing
Return values (DataFrames, dicts of Series) have to be pickled back to the parent process. Large objects make that slower and more fragile than returning them from threads in the same process.

### 5. Likely outcome for our pipeline
I'd probably see:
- Similar or **worse** wall-clock time (extra process/pickle cost)
- **Higher memory** pressure
- More complexity for little or no gain

**Conclusion:** `ProcessPoolExecutor` is the wrong default for this milestone's ingestion step.

---

## when would i switch to `ProcessPoolExecutor` for ingestion?

I'd switch to **processes** when ingestion becomes **CPU-bound**, for example:

| Scenario | Why processes help |
|----------|-------------------|
| Heavy pandas transforms on large files | CPU work (filters, joins, aggregations) |
| Compression / decompression at scale | CPU-intensive |
| Parsing many large JSON/XML files | CPU-bound parsing |
| Image/PDF extraction, OCR | CPU-bound |
| Per-row validation logic in pure Python | CPU-bound loops |

**Rule of thumb:**
- **I/O-bound** (network, disk, API) → `ThreadPoolExecutor`
- **CPU-bound** (transform, compute, encode) → `ProcessPoolExecutor`

Milestone 1.4 (Parallel Transformation) is where `ProcessPoolExecutor` makes sense — transformation is usually CPU-heavy, unlike raw ingestion.

---

## PPT talking points (short)

1. Ingestion waits on network and disk → threads overlap those waits.
2. Process pool adds spawn + pickle + duplicate memory → bad fit for large I/O jobs.
3. GIL isn't the bottleneck when code is waiting on FRED or disk.
4. Use process pool when transformation/compute dominates runtime (Milestone 1.4).
