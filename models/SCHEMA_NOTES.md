Choice: Pure Star Schema

I chose Pure star Schema because it is simnple and efficint and matches the structure of the Paysim Datasel. The dataset is transaction-centered, so having a single fact table with a few dimension tables makes the schema easy to understand and query.
A star schema also requires fewer joins than a snowflake schema, which improves query performance for analytical workloads in DuckDB.

Fact Table

The fact_transactions table stores one row for each transaction. includes the transaction measures: 

amount
log_amount
balance_drain
fraud indicators (is_fraud, is_flagged_fraud)
sender and receiver balances

It also contains foreign keys that reference the dimension tables.

Dimension Tables
dim_transaction_type

Stores the transaction type names (such as PAYMENT, TRANSFER, and CASH_OUT). Using a lookup table avoids storing the same text repeatedly in the fact table.

dim_account

Stores account IDs used by both sender and receiver accounts. The fact table references this table through sender_account_id and receiver_account_id.

dim_time

The PaySim dataset uses a simulation step instead of real dates. The time dimension stores the simulation step along with derived values such as:

sim_day
sim_week
hour_of_day

The snowflake option would split the account dimension into additional tables, such as dim_account and dim_account_type. This creates more joins and increases schema complexity.

The PaySim dataset does not provide a true account type attribute, so creating additional account dimension tables would add complexity without providing significant analytical value.



