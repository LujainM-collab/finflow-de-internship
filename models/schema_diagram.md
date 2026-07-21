# FinFlow Schema Diagram

```mermaid
erDiagram
    fact_transactions }o--|| dim_transaction_type : is
    fact_transactions }o--|| dim_account : "sent by"
    fact_transactions }o--|| dim_time : "occurred at"
```