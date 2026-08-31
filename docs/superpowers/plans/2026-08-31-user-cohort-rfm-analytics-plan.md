# User cohort and RFM analytics implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a user cohort retention and RFM segmentation Streamlit dashboard with a Glassmorphism theme, using Parquet files for data storage.

**Architecture:** A modular Python backend containing an ETL prep script (`src/data_prep.py`) and calculations helper (`src/data_processing.py`) loading flat Parquet tables into a Streamlit frontend layer (`app.py`).

**Tech Stack:** `python`, `pandas`, `numpy`, `pyarrow`, `scikit-learn`, `plotly`, `streamlit`, `uv`

**Spec:** [`docs/superpowers/specs/2026-08-31-user-cohort-rfm-analytics-design.md`](file:///home/haider/Desktop/job_prep/docs/superpowers/specs/2026-08-31-user-cohort-rfm-analytics-design.md)

## Global Constraints
- Do not use emojis anywhere in code comments, print logs, or UI labels.
- Implement the Glassmorphism visual theme as the default design language.
- Separate calculation logic into `src/` and keep `app.py` reserved strictly for layout rendering.
- Exclude raw data directories (`data/raw/`) from Git tracking.

---

### Task 1: Scaffolding and environment setup

**Files:**
- Create: `02_user_cohort_rfm_analytics/pyproject.toml`
- Create: `02_user_cohort_rfm_analytics/.gitignore`
- Create: `02_user_cohort_rfm_analytics/project_design_rules.md`

**Interfaces:**
- Produces: Base project structure and dependency package locks.

- [ ] **Step 1: Create project directory and initialize Git**

Run:
```bash
mkdir -p 02_user_cohort_rfm_analytics
cd 02_user_cohort_rfm_analytics
git init
```

- [ ] **Step 2: Create .gitignore file**

Write to `02_user_cohort_rfm_analytics/.gitignore`:
```text
.venv/
data/raw/
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 3: Create pyproject.toml**

Write to `02_user_cohort_rfm_analytics/pyproject.toml`:
```toml
[project]
name = "user-cohort-rfm-analytics"
version = "0.1.0"
description = "User Cohort and RFM Analytics Dashboard"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "streamlit>=1.35.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pyarrow>=12.0.0",
    "scikit-learn>=1.2.0",
    "plotly>=5.15.0",
]
```

- [ ] **Step 4: Copy project design rules**

Write to `02_user_cohort_rfm_analytics/project_design_rules.md`:
```markdown
# Project Design Rules

This document outlines the visual, styling, and coding design rules for the cohort and RFM analytics project.

## 1. Typography and Interface
- No emojis may be used anywhere in the source code, logging statements, print statements, or user-facing Streamlit dashboard interface.
- Implement the Glassmorphism Theme as the core aesthetic.

## 2. Codebase Architecture and Directory Structure
- **app.py (Presentation Layer):** Reserved strictly for Streamlit UI rendering, tab configurations, sidebars, input widgets, and Plotly visualization renders. No raw database mapping, heavy feature engineering, outlier capping, cohort grouping math, or machine learning training logic is allowed directly inside this file.
- **src/ (Core Logic Layer):** All data cleaning, ETL pipelines, raw CSV parsing, database feature engineering, and mathematical helpers must live inside modular python scripts within the `src/` directory.
- **data/ (Data & Ingestion Layer):** Holds raw dataset files (git-ignored under `data/raw/`) and processed Parquet files (`data/processed/`). Ingestion or download-only scripts (e.g., `data/download_data.py`) must reside directly inside the `data/` folder, not in `src/`.
- **Data Preservation:** Raw transactional data must be processed via the ETL scripts in `src/` and stored in the `data/processed/` directory. The presentation layer must only load prepared datasets from Parquet files.
```

- [ ] **Step 5: Synchronize dependencies**

Run:
```bash
cd 02_user_cohort_rfm_analytics
uv sync
```
Expected: Succeeds and creates `.venv/` and `uv.lock`.

- [ ] **Step 6: Commit**

Run:
```bash
git add pyproject.toml .gitignore project_design_rules.md
git commit -m "chore: scaffold project structure and dependencies"
```

---

### Task 2: Data ingestion script

**Files:**
- Create: `02_user_cohort_rfm_analytics/data/download_data.py`

**Interfaces:**
- Produces: `02_user_cohort_rfm_analytics/data/raw/online_retail.csv` raw source file.

- [ ] **Step 1: Write raw data downloader script**

Write to `02_user_cohort_rfm_analytics/data/download_data.py`:
```python
import os
import requests
import pandas as pd

# Define paths relative to this file
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(DATA_DIR, "raw")
CSV_PATH = os.path.join(RAW_DIR, "online_retail.csv")
URL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"

def download_dataset():
    os.makedirs(RAW_DIR, exist_ok=True)
    print("Starting download of Online Retail dataset...")
    try:
        response = requests.get(URL, stream=True)
        response.raise_for_status()
        
        with open(CSV_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print(f"Dataset saved to: {CSV_PATH}")
        
        # Verify
        df = pd.read_csv(CSV_PATH)
        print(f"Verified dataset: {df.shape[0]:,} rows loaded.")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    download_dataset()
```

- [ ] **Step 2: Run download script to verify Ingestion**

Run:
```bash
uv run python data/download_data.py
```
Expected: Prints verification with approximately 541,909 rows loaded.

- [ ] **Step 3: Commit**

Run:
```bash
git add data/download_data.py
git commit -m "feat: add download script for online retail dataset"
```

---

### Task 3: ETL data preparation and Parquet export

**Files:**
- Create: `02_user_cohort_rfm_analytics/src/data_prep.py`

**Interfaces:**
- Consumes: `02_user_cohort_rfm_analytics/data/raw/online_retail.csv`
- Produces: `02_user_cohort_rfm_analytics/data/processed/transactions.parquet`

- [ ] **Step 1: Write ETL pipeline script**

Write to `02_user_cohort_rfm_analytics/src/data_prep.py`:
```python
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
    print("ETL complete.")

if __name__ == "__main__":
    run_data_pipeline()
```

- [ ] **Step 2: Run ETL script to verify Parquet output**

Run:
```bash
uv run python src/data_prep.py
```
Expected: Output printed confirming saving to `transactions.parquet`.

- [ ] **Step 3: Commit**

Run:
```bash
git add src/data_prep.py
git commit -m "feat: implement ETL prep pipeline exporting transactions.parquet"
```

---

### Task 4: Analytical calculations and RFM segmentation

**Files:**
- Create: `02_user_cohort_rfm_analytics/src/data_processing.py`

**Interfaces:**
- Consumes: `transactions.parquet`
- Produces:
  - `calculate_cohort_retention(df_tx)` -> `pd.DataFrame`
  - `calculate_rfm_profiles(df_tx)` -> `pd.DataFrame`
  - Saves: `02_user_cohort_rfm_analytics/data/processed/customers.parquet`

- [ ] **Step 1: Write calculations module**

Write to `02_user_cohort_rfm_analytics/src/data_processing.py`:
```python
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
    
    # Save to Parquet
    df_rfm.to_parquet(CUSTOMERS_PARQUET_PATH, index=False, engine='pyarrow')
    
    return df_rfm
```

- [ ] **Step 2: Write test script to verify calculations module**

Write to `02_user_cohort_rfm_analytics/src/run_test_math.py`:
```python
import os
import pandas as pd
from data_processing import calculate_cohort_retention, calculate_rfm_profiles

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
TX_PATH = os.path.join(PROJECT_DIR, "data", "processed", "transactions.parquet")

def test():
    df_tx = pd.read_parquet(TX_PATH)
    print("Testing calculations...")
    cohort_sizes, retention = calculate_cohort_retention(df_tx)
    print(f"Cohort retention shapes: sizes={cohort_sizes.shape}, retention={retention.shape}")
    
    df_rfm = calculate_rfm_profiles(df_tx)
    print(f"RFM aggregated profiles: {len(df_rfm)} customers.")
    print("Sample segment distribution:")
    print(df_rfm['Segment'].value_counts())

if __name__ == "__main__":
    test()
```

- [ ] **Step 3: Execute test script**

Run:
```bash
uv run python src/run_test_math.py
```
Expected: Prints shapes and segment distribution (e.g. Champions, Loyal, Hibernating).

- [ ] **Step 4: Clean up test script and commit**

Run:
```bash
rm src/run_test_math.py
git add src/data_processing.py
git commit -m "feat: add calculations module for cohort matrices and RFM segments"
```

---

### Task 5: Streamlit frontend and Glassmorphism styling

**Files:**
- Create: `02_user_cohort_rfm_analytics/.streamlit/config.toml`
- Create: `02_user_cohort_rfm_analytics/app.py`

**Interfaces:**
- Consumes:
  - `data/processed/transactions.parquet`
  - `data/processed/customers.parquet`
  - `calculate_cohort_retention(df_tx)`
  - `calculate_rfm_profiles(df_tx)`

- [ ] **Step 1: Configure Streamlit dark configuration**

Write to `02_user_cohort_rfm_analytics/.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1856FF"
backgroundColor = "#0e111d"
secondaryBackgroundColor = "#101424"
textColor = "#EAEAEA"
font = "sans serif"
```

- [ ] **Step 2: Implement Glassmorphism styling and tabs**

Write to `02_user_cohort_rfm_analytics/app.py`:
```python
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add src folder to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from data_processing import calculate_cohort_retention, calculate_rfm_profiles

# Page Config
st.set_page_config(
    page_title="User Cohorts & RFM Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphism Styling
st.html("""
<style>
/* Background overlay */
.stApp {
    background: linear-gradient(135deg, #0e111d 0%, #101424 100%) !important;
}

/* Glassmorphism Card Wrapper */
div[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #EAEAEA !important;
}

/* Custom card container styling */
.glass-card {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    margin-bottom: 20px !important;
}
</style>
""")

# Load Cleaned Data
@st.cache_data
def load_cached_data():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    tx_path = os.path.join(project_dir, "data", "processed", "transactions.parquet")
    cust_path = os.path.join(project_dir, "data", "processed", "customers.parquet")
    
    # Check if files exist, if not run pipeline
    if not os.path.exists(tx_path):
        from data_prep import run_data_pipeline
        run_data_pipeline()
        
    df_tx = pd.read_parquet(tx_path)
    
    if not os.path.exists(cust_path):
        df_cust = calculate_rfm_profiles(df_tx)
    else:
        df_cust = pd.read_parquet(cust_path)
        
    return df_tx, df_cust

df_tx, df_cust = load_cached_data()

st.title("User Cohort & RFM Analytics")
st.markdown("Analyzing customer purchasing behavior, cohort retention trends, and RFM marketing segments.")

# Sidebar Filters
st.sidebar.header("Filter settings")
countries = sorted(df_tx['Country'].unique())
selected_country = st.sidebar.selectbox("Select Country", ["All Countries"] + countries)

# Apply filters
df_tx_filtered = df_tx.copy()
if selected_country != "All Countries":
    df_tx_filtered = df_tx_filtered[df_tx_filtered['Country'] == selected_country]
    # Re-calculate customer metrics for active country selection
    df_cust_filtered = calculate_rfm_profiles(df_tx_filtered)
else:
    df_cust_filtered = df_cust.copy()

# Layout Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Overview",
    "Cohort Retention Matrix",
    "RFM Marketing Segments",
    "Customer Profiler & Lookup"
])

# Tab 1: Executive Overview
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df_tx_filtered[~df_tx_filtered['IsCancelled']]['TotalSales'].sum()
        st.metric("Gross Revenue", f"${total_sales:,.2f}")
    with col2:
        active_customers = df_cust_filtered['CustomerID'].nunique()
        st.metric("Unique Customers", f"{active_customers:,}")
    with col3:
        avg_frequency = df_cust_filtered['Frequency'].mean()
        st.metric("Avg Orders/Cust", f"{avg_frequency:.1f}")
    with col4:
        total_orders = df_tx_filtered[~df_tx_filtered['IsCancelled']]['InvoiceNo'].nunique()
        st.metric("Total Invoices", f"{total_orders:,}")
        
    st.markdown("### Monthly Sales Trend")
    df_monthly = df_tx_filtered[~df_tx_filtered['IsCancelled']].groupby(df_tx_filtered['InvoiceDate'].dt.to_period('M').astype(str))['TotalSales'].sum().reset_index()
    fig_sales = px.area(
        df_monthly, x='InvoiceDate', y='TotalSales',
        labels={'InvoiceDate': 'Month', 'TotalSales': 'Sales Revenue ($)'},
        color_discrete_sequence=['#1856FF']
    )
    fig_sales.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EAEAEA'
    )
    st.plotly_chart(fig_sales, use_container_width=True)

# Tab 2: Cohort Retention Matrix
with tab2:
    st.markdown("### Monthly Cohort Retention Heatmap")
    cohort_counts, cohort_retention = calculate_cohort_retention(df_tx_filtered)
    
    view_mode = st.radio("Display Format", ["Interactive Heatmap Plot", "Styled Data Grid Table"])
    
    if view_mode == "Interactive Heatmap Plot":
        fig_cohort = px.imshow(
            cohort_retention,
            labels=dict(x="Months Active", y="Acquisition Cohort", color="Retention (%)"),
            x=cohort_retention.columns,
            y=cohort_retention.index,
            color_continuous_scale="blues",
            text_auto=".1f"
        )
        fig_cohort.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#EAEAEA'
        )
        st.plotly_chart(fig_cohort, use_container_width=True)
    else:
        st.dataframe(
            cohort_retention.style.background_gradient(cmap='Blues', axis=1).format("{:.1f}%", na_rep="-"),
            use_container_width=True
        )

# Tab 3: RFM Marketing Segments
with tab3:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### RFM Segment Distribution Treemap")
        df_treemap = df_cust_filtered.groupby('Segment').agg(
            CustomerCount=('CustomerID', 'count'),
            AvgMonetary=('Monetary', 'mean')
        ).reset_index()
        
        fig_tree = px.treemap(
            df_treemap,
            path=['Segment'],
            values='CustomerCount',
            color='AvgMonetary',
            color_continuous_scale='blues',
            labels={'CustomerCount': 'Customers Count', 'AvgMonetary': 'Avg Spend ($)'}
        )
        fig_tree.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#EAEAEA'
        )
        st.plotly_chart(fig_tree, use_container_width=True)
        
    with col_right:
        st.markdown("### Customer Segment Counts")
        segment_counts = df_cust_filtered['Segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        fig_bar = px.bar(
            segment_counts, x='Count', y='Segment', orientation='h',
            color_discrete_sequence=['#1856FF']
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#EAEAEA'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# Tab 4: Customer Profiler & Lookup
with tab4:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        # Segment filter
        segment_list = sorted(df_cust_filtered['Segment'].unique())
        selected_segment = st.selectbox("Filter Segment Profiles", ["All Segments"] + segment_list)
        
    df_cust_segment = df_cust_filtered.copy()
    if selected_segment != "All Segments":
        df_cust_segment = df_cust_segment[df_cust_segment['Segment'] == selected_segment]
        
    st.dataframe(df_cust_segment, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Customer Transaction Search")
    
    # Text input search
    search_id = st.text_input("Enter Customer ID to look up")
    if search_id:
        cust_profile = df_cust_filtered[df_cust_filtered['CustomerID'] == search_id]
        if not cust_profile.empty:
            st.markdown(f"#### Profile details for customer {search_id}")
            c_row = cust_profile.iloc[0]
            st.write(f"- **Recency:** {c_row['Recency']} days since last order")
            st.write(f"- **Frequency:** {c_row['Frequency']} orders placed")
            st.write(f"- **Monetary value:** ${c_row['Monetary']:,.2f} total spend")
            st.write(f"- **Marketing Segment Group:** {c_row['Segment']}")
            
            st.markdown("#### Transaction logs")
            cust_tx = df_tx[df_tx['CustomerID'] == search_id]
            st.dataframe(cust_tx, use_container_width=True)
        else:
            st.error(f"No profile records found for Customer ID {search_id}")
```

- [ ] **Step 3: Run local dashboard server**

Run:
```bash
uv run streamlit run app.py --server.port 8502
```
Expected: Dashboard launches successfully on local port 8502.

- [ ] **Step 4: Commit**

Run:
```bash
git add app.py .streamlit/config.toml
git commit -m "feat: implement Glassmorphism Streamlit UI pages and Plotly visual layouts"
```

---

### Task 6: Project documentation and presentation README

**Files:**
- Create: `02_user_cohort_rfm_analytics/README.md`

**Interfaces:**
- Produces: Project presentation cover page.

- [ ] **Step 1: Write slide-formatted README**

Write to `02_user_cohort_rfm_analytics/README.md`:
```markdown
# User Cohort & RFM Analytics Dashboard
## Technical portfolio presentation

**Duration:** 10 minutes review
**Audience:** Technical Recruiters and Hiring Managers
**Date:** 2026-08-31

---

## Agenda

1. Project overview and features (2 min)
2. Data dictionary and variables (2 min)
3. Tech stack (1 min)
4. System architecture and codebase layout (3 min)
5. Installation and verification (2 min)

---

## 1. Project overview and features

This application calculates monthly user cohort retention rates and performs quantile-based RFM (Recency, Frequency, Monetary) value clustering on retail transaction datasets.

### Core modules
- The Executive Overview tracks total gross revenue, transaction volumes, unique buyer counts, and average order counts.
- The Cohort Retention Matrix computes monthly signup cohorts and visualizes their retention cycles using heatmaps and styled grids.
- The RFM Marketing Segments partition customer value scores into quintiles and represent counts on interactive treemaps.
- The Customer Profiler lookup drill-down pulls detailed transaction logs and segment metrics for specific customers.

---

## 2. Data dictionary and variables

The system uses flat Parquet files to organize processed transactional tables and customer metrics:

<details>
<summary><b>Click to expand transactions schema variables</b></summary>

- `InvoiceNo` represents the unique transaction code (cancellations prefixed with 'C').
- `StockCode` represents the unique item code.
- `Description` represents the item name.
- `Quantity` represents transaction volume (capped at the 99.9th percentile outlier limit).
- `InvoiceDate` represents transaction timestamp.
- `UnitPrice` represents item price (capped at the 99.9th percentile outlier limit).
- `CustomerID` represents buyer profile ID (guest checkout transactions mapped to 'Guest').
- `Country` represents user residence.
- `TotalSales` represents engineered revenue (`Quantity * UnitPrice`).
- `IsCancelled` represents returns check flag.
- `Hemisphere` represents country location used for season mappings.

</details>

---

## 3. Tech stack

- **Tools:** VS Code, Git
- **Language:** Python
- **Libraries:**
  - `pandas`, `numpy`, `pyarrow`, `plotly`, `streamlit`

---

## 4. System architecture and codebase layout

The project uses a modular folder layout, executing data preparation pipelines separately from the display layers:

```text
[Raw Dataset] ──► (data/download_data.py) ──► [data/raw/]
                        │
                        ▼ (src/data_prep.py ETL)
          [data/processed/transactions.parquet] ──┐
          [data/processed/customers.parquet] ────┼──► (app.py Streamlit UI)
```

<details>
<summary><b>Click to expand file layout details</b></summary>

- `data/download_data.py` pulls the online retail transaction CSV logs from the remote databricks repository.
- `src/data_prep.py` runs ETL cleaning, resolves returns, handles guest tags, caps anomalies, and exports Parquet tables.
- `src/data_processing.py` calculates cohort pivots, computes customer RFM quantiles, and classifies segments.
- `app.py` renders the Glassmorphic layout UI and runs the Plotly visualizations.

</details>

---

## 5. Installation and verification

You need Python 3.10 or newer and the `uv` package manager installed.

### Setup commands
1. Navigate to the project directory:
   ```bash
   cd 02_user_cohort_rfm_analytics
   ```
2. Synchronize dependencies:
   ```bash
   uv sync
   ```
3. Fetch raw data, compile ETL tables, and write processed Parquet files:
   ```bash
   uv run python data/download_data.py
   uv run python src/data_prep.py
   ```
4. Launch the local Streamlit dashboard server:
   ```bash
   uv run streamlit run app.py --server.port 8502
   ```

---

## Quick reference card

### Execution scripts
| Step | Command |
|------|---------|
| Ingestion | `uv run python data/download_data.py` |
| ETL Pipeline | `uv run python src/data_prep.py` |
| Dashboard App | `uv run streamlit run app.py` |

### Processed Parquet paths
- Transactions: `data/processed/transactions.parquet`
- Customers: `data/processed/customers.parquet`
```

- [ ] **Step 2: Commit**

Run:
```bash
git add README.md
git commit -m "docs: add technical presentation README walkthrough"
```
