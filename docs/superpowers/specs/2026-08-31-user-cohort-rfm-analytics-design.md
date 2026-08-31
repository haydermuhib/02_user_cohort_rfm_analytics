# User cohort and RFM analytics design specification

This document defines the system design, dataset criteria, file organization, and visual layout parameters for the user cohort and RFM analytics dashboard.

---

## 1. System overview and data pipeline

The application processes raw retail transactions to group customers into purchase-frequency cohorts and RFM marketing segments. The system stores processed data in flat Parquet files rather than a database.

```text
[Raw Dataset]
      │
      ▼ (download_data.py)
[data/raw/online_retail.csv]
      │
      ▼ (src/data_prep.py ETL)
[data/processed/transactions.parquet] ──┐
[data/processed/customers.parquet] ────┼── (reads Parquet tables)
                                        ▼
                             (app.py Streamlit UI) ◄── (src/data_processing.py calculations)
```

---

## 2. Codebase architecture and layout

The codebase separates calculations and file operations from the visual rendering layer:

### Module responsibilities
- `data/download_data.py` pulls the raw UCI Online Retail CSV dataset from the remote source.
- `src/data_prep.py` runs the ETL cleaning logic, handles returns and guest accounts, caps quantity and price outliers at the 99.9th percentile, and writes the Parquet tables.
- `src/data_processing.py` contains standalone functions to compute monthly cohort retention matrices and run quantile-based RFM scoring.
- `app.py` serves the user interface, renders the Plotly treemaps and heatmaps, and displays the customer lookup tables.

---

## 3. Data processing and analytical logic

### Cohort retention analysis
1. Identify the acquisition month (first purchase date) for each unique customer.
2. Calculate the month distance index (0, 1, 2... 12+) for all subsequent customer orders.
3. Pivot transaction counts into a cohort matrix where rows represent acquisition months and columns represent index months.
4. Calculate retention percentages by dividing active counts in index months by the starting size (Month 0).

### RFM customer segmentation
1. Aggregate transaction records per customer to extract Recency (days since last purchase), Frequency (total unique invoices), and Monetary value (total sales).
2. Calculate quintiles (20th, 40th, 60th, 80th percentiles) for the three variables.
3. Assign scores from 1 to 5 for each metric (where 5 represents most active, frequent, or high-spending).
4. Combine scores and map customers to standard segments (Champions, Loyal, Promising, At Risk, Hibernating).

---

## 4. Visual design and styling

The application uses a Glassmorphism design system to present a modern, premium dark interface:

### Styling foundations
- **Colors:** Primary blue (`#1856FF`), background dark gradient canvas (`linear-gradient(135deg, #0e111d 0%, #101424 100%)`), text color (`#EAEAEA`), and frosted borders (`rgba(255, 255, 255, 0.1)`).
- **Cards:** Frosted containers with backdrop blur filter (`backdrop-filter: blur(12px)`).
- **Tabs:**
  - Executive Overview (KPI bento-cards and revenue line charts).
  - Cohort Retention (Plotly heatmap and toggled Pandas dataframe grid).
  - RFM Segmentation (customer treemap and segment count distributions).
  - Customer Search (drill-down lookups by segment or individual customer ID).
