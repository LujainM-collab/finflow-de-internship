CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY,
    step INTEGER,
    transaction_type_id INTEGER,
    amount FLOAT,
    log_amount FLOAT,
    balance_drain FLOAT,
    sender_account_id INTEGER,
    receiver_account_id INTEGER,
    is_fraud BOOLEAN,
    is_flagged_fraud BOOLEAN,
    old_balance_sender FLOAT,
    new_balance_sender FLOAT,
    old_balance_receiver FLOAT,
    new_balance_receiver FLOAT
);

CREATE TABLE dim_transaction_type (
    id INTEGER PRIMARY KEY,
    type_name TEXT
);

CREATE TABLE dim_account (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE dim_time (
    step INTEGER PRIMARY KEY,
    sim_day INTEGER,
    sim_week INTEGER,
    hour_of_day INTEGER
);

CREATE TABLE complaints (
    complaint_id INTEGER PRIMARY KEY,
    date_received DATE,
    product TEXT,
    sub_product TEXT,
    issue TEXT,
    company TEXT,
    state TEXT,
    resolution TEXT
);