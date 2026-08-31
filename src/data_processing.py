import os
import pandas as pd
import numpy as np

# Paths
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
CUSTOMERS_PARQUET_PATH = os.path.join(PROJECT_DIR, "data", "processed", "customers.parquet")

def calculate_cohort_retention(df_tx):
    # Filter out guests and cancellations for retention calculations
    df = df_tx[(df_tx['CustomerID'] != 'Guest') & (~df_tx['IsCancelled'])].copy()
    
    # Find Cohort Month (first purchase month)
    df['OrderMonth'] = df['InvoiceDate'].dt.to_period('M')
    df['CohortMonth'] = df.groupby('CustomerID')['OrderMonth'].transform('min')
    
    # Calculate index distance
    df['CohortIndex'] = (df['OrderMonth'].dt.year - df['CohortMonth'].dt.year) * 12 + (df['OrderMonth'].dt.month - df['CohortMonth'].dt.month)
    
    # Group by cohort and index
    cohort_group = df.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
    
    # Pivot cohort table
    cohort_pivot = cohort_group.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
    
    # Convert index periods to strings for visualization
    cohort_pivot.index = cohort_pivot.index.astype(str)
    
    # Calculate retention percentages
    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_sizes, axis=0) * 100
    
    return cohort_pivot, retention

def calculate_rfm_profiles(df_tx):
    # Filter out guests and cancellations
    df = df_tx[(df_tx['CustomerID'] != 'Guest') & (~df_tx['IsCancelled'])].copy()
    
    max_date = df['InvoiceDate'].max()
    
    # Aggregate to customer level
    df_rfm = df.groupby('CustomerID').agg(
        Recency=('InvoiceDate', lambda x: (max_date - x.max()).days),
        Frequency=('InvoiceNo', 'nunique'),
        Monetary=('TotalSales', 'sum')
    ).reset_index()
    
    # RFM Scoring using quintiles
    # Recency: lower is better (receives score 5)
    r_labels = [5, 4, 3, 2, 1]
    # Frequency and Monetary: higher is better (receives score 5)
    f_labels = [1, 2, 3, 4, 5]
    m_labels = [1, 2, 3, 4, 5]
    
    # Check for rank duplication using rank method if data contains identical quantiles
    df_rfm['R_Score'] = pd.qcut(df_rfm['Recency'], q=5, labels=r_labels, duplicates='drop').astype(int)
    df_rfm['F_Score'] = pd.qcut(df_rfm['Frequency'].rank(method='first'), q=5, labels=f_labels).astype(int)
    df_rfm['M_Score'] = pd.qcut(df_rfm['Monetary'], q=5, labels=m_labels).astype(int)
    
    df_rfm['RFM_Score'] = df_rfm['R_Score'].astype(str) + df_rfm['F_Score'].astype(str) + df_rfm['M_Score'].astype(str)
    
    # Segment definitions
    def map_rfm_segment(row):
        r = row['R_Score']
        f = row['F_Score']
        m = row['M_Score']
        
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "New/Promising"
        elif r <= 2 and f >= 3:
            return "At Risk"
        else:
            return "Hibernating/Lost"
            
    df_rfm['Segment'] = df_rfm.apply(map_rfm_segment, axis=1)
    
    return df_rfm
