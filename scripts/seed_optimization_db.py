import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def seed_db():
    print("Seeding optimization database...")
    engine = create_engine('sqlite:///optimization.db')
    
    np.random.seed(42)
    
    # 1. Customers Table (Lots of unused columns to demonstrate SELECT *)
    customers = pd.DataFrame({
        'id': range(1, 1001),
        'customer_name': [f"Cust_{i}" for i in range(1, 1001)],
        'country': np.random.choice(['USA', 'UK', 'CA', 'AU', 'FR'], 1000),
        'customer_segment': np.random.choice(['Enterprise', 'SMB', 'Startup'], 1000),
        'account_type': np.random.choice(['Premium', 'Standard'], 1000),
        'unused_col_1': np.random.randn(1000),
        'unused_col_2': np.random.randn(1000),
        'unused_col_3': np.random.randn(1000),
        'unused_col_4': np.random.randn(1000),
        'unused_col_5': np.random.randn(1000)
    })
    
    # 2. Products Table
    products = pd.DataFrame({
        'id': range(1, 11),
        'product_name': [f"Product_{i}" for i in range(1, 11)],
        'category': np.random.choice(['Software', 'Hardware', 'Service'], 10)
    })
    
    # 3. Transactions Table (10,000 rows to show filtering reductions)
    transactions = pd.DataFrame({
        'transaction_id': range(100001, 110001),
        'customer_id': np.random.randint(1, 1001, 10000),
        'product_id': np.random.randint(1, 11, 10000),
        'transaction_date': pd.date_range(start='2023-01-01', periods=10000, freq='4h'),
        'amount': np.random.uniform(10, 500, 10000)
    })
    
    customers.to_sql('customers', engine, if_exists='replace', index=False)
    products.to_sql('products', engine, if_exists='replace', index=False)
    transactions.to_sql('transactions', engine, if_exists='replace', index=False)
    
    print(f"Seeded 10,000 transactions, 1,000 customers, and 10 products.")

if __name__ == "__main__":
    seed_db()