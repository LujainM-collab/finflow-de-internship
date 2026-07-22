erDiagram
    fact_transactions ||--o{ transaction_type : uses
    fact_transactions ||--o{ dim_account : sends
    fact_transactions ||--o{ dim_account : receives
    dim_account ||--o{ dim_time : tracks
    fact_transactions ||--o{ complaints : reports

    fact_transactions {
        int transaction_id PK
        int step
        int transaction_type_id FK
        decimal amount
        decimal log_amount
        decimal balance_drain
        int sender_account_id PK
        int receiver_account_id PK
        boolean is_fraud
        boolean is_flagged_fraud
        decimal old_balance_sender
        decimal new_balance_sender
        decimal old_balance_receiver
        decimal new_balance_receiver
    }

    transaction_type {
        int id PK
        string type_name
    }

    dim_account {
        int id PK
        string name
    }

    dim_time {
        int step
        string sim_day
        string sim_week
        int hour_of_day
    }

    complaints {
        int complaint_id PK
        date date_received
        string product
        string sub_product
        string issue
        string company
        string state
        string resolution
    }
