import os
import pandas as pd
import numpy as np

# Paths
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
RAW_CSV_PATH = os.path.join(PROJECT_DIR, "data", "raw", "online_retail.csv")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
OUTPUT_PARQUET_PATH = os.path.join(PROCESSED_DIR, "transactions.parquet")

def run_data_pipeline():
    print("Loading raw CSV transactions...")
    df = pd.read_csv(RAW_CSV_PATH)
    
    # Parse dates
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Drop rows with negative quantities or prices that represent cancellations
    # Handle cancellations separately via boolean column
    df['IsCancelled'] = df['InvoiceNo'].astype(str).str.startswith('C') | (df['Quantity'] < 0)
    
    # Fill missing Customer IDs
    df['CustomerID'] = df['CustomerID'].fillna(-1).astype(int).astype(str)
    df['CustomerID'] = df['CustomerID'].replace('-1', 'Guest')
    
    # Fill missing descriptions
    df['Description'] = df['Description'].fillna('Unknown Product').str.strip()
    
    # Engineering metrics
    df['TotalSales'] = df['Quantity'] * df['UnitPrice']
    df['COGS'] = df['Quantity'] * (df['UnitPrice'] * 0.60)
    df['Profit'] = df['TotalSales'] - df['COGS']
    
    # Outlier Capping at 99.9th percentile on absolute values
    q_limit = df[df['Quantity'] > 0]['Quantity'].quantile(0.999)
    p_limit = df[df['UnitPrice'] > 0]['UnitPrice'].quantile(0.999)
    
    df['Quantity'] = np.clip(df['Quantity'], -q_limit, q_limit)
    df['UnitPrice'] = np.clip(df['UnitPrice'], 0, p_limit)
    df['TotalSales'] = df['Quantity'] * df['UnitPrice']
    df['COGS'] = df['Quantity'] * (df['UnitPrice'] * 0.60)
    df['Profit'] = df['TotalSales'] - df['COGS']
    
    # Hemisphere Classification
    southern_countries = ["Australia", "New Zealand", "South Africa", "Brazil"]
    df['Hemisphere'] = np.where(df['Country'].isin(southern_countries), 'Southern', 'Northern')
    
    # Save to Parquet
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"Saving {len(df):,} transactions to Parquet...")
    df.to_parquet(OUTPUT_PARQUET_PATH, index=False, engine='pyarrow')
    
    # Calculate and save global customer RFM profiles to Parquet
    print("Calculating and saving global customer RFM profiles...")
    from data_processing import calculate_rfm_profiles
    df_cust = calculate_rfm_profiles(df)
    cust_parquet_path = os.path.join(PROCESSED_DIR, "customers.parquet")
    df_cust.to_parquet(cust_parquet_path, index=False, engine='pyarrow')
    
    print("ETL complete.")

if __name__ == "__main__":
    run_data_pipeline()
