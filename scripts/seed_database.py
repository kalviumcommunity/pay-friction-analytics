import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///analytics.db')

customers_df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4],
    'customer_type': ['Enterprise', 'SMB', 'Enterprise', 'Startup']
})

transactions_df = pd.DataFrame({
    'order_id': [101, 102, 103, 104, 105],
    'customer_id': [1, 2, 1, 3, 4],
    'transaction_date': ['2026-01-15', '2026-02-20', '2026-03-10', '2026-04-05', '2026-04-10'],
    'amount': [1500.0, 300.0, 1200.0, 2500.0, 100.0]
})

users_df = pd.DataFrame({
    'user_id': [1, 2, 3],
    'created_at': ['2026-03-01', '2026-03-05', '2026-03-10'],
    'email_verified_at': ['2026-03-01', '2026-03-06', None],
    'first_purchase_at': ['2026-03-02', None, None]
})

customers_df.to_sql('customers', engine, if_exists='replace', index=False)
transactions_df.to_sql('transactions', engine, if_exists='replace', index=False)
users_df.to_sql('users', engine, if_exists='replace', index=False)

print("✓ Database seeded successfully with customers, transactions, and users tables.")