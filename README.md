# User Cohort and RFM Analytics Dashboard
## Executive Technical Portfolio Presentation

**Live Application:** https://02usercohortrfmanalytics.streamlit.app/  
**Duration:** 10 minutes review  
**Audience:** Technical Recruiters and Hiring Managers  
**Date:** 2026-10-03  

---

## Executive Summary and Key Takeaways

1. Retention Cliff Identification: Customer retention drops from 100% in acquisition month to approximately 20% to 25% by month 1. The first 30 days represent the highest-leverage retention window for automated onboarding and re-engagement workflows.
2. Revenue Concentration: Champions and Loyal Customers constitute roughly 40% of the customer base but drive over 75% of cumulative sales revenue. Protecting high-tier buyers from attrition delivers disproportionate financial impact.
3. Clean Data Architecture: Over 24% of transactions represent guest checkouts. These are retained in top-line retail sales metrics but isolated from individual customer cohort matrices to maintain retention integrity.

---

## Timed 10-Minute Presentation Agenda

1. Executive Overview and Problem Framing (0:00 - 2:00)
2. Data Pipeline, Cleansing, and Schemas (2:00 - 4:00)
3. Technology Architecture and Package Management (4:00 - 5:00)
4. Interactive Dashboard Walkthrough (5:00 - 8:00)
5. Local Setup, Reproducibility, and Verification (8:00 - 10:00)

---

## 1. Project Overview and Features

This project provides an end-to-end customer analytics suite evaluating retail purchasing patterns across multiple international markets.

### Analytical Scope and Business Discipline
This project represents a dedicated **Customer Lifecycle Diagnostics and Retention Marketing (CRM)** analytics solution. Rather than focusing on predictive churn classification, this system analyzes empirical historical purchasing behavior to track post-acquisition retention decay and construct behavioral customer segments.

- **Analytical Discipline:** Descriptive and Diagnostic Behavioral Analytics, Cohort Retention Modeling, Quantile RFM Clustering.
- **Core Business Questions Answered:**
  1. How rapidly does customer retention degrade month-over-month following initial acquisition across international markets?
  2. Which customer groups represent the core financial foundation of the business versus those requiring active win-back intervention?
  3. How should marketing budgets and personalized promotions be allocated based on objective purchase recency, order frequency, and monetary contribution?
- **Target Stakeholders:** Retention Marketing Managers, CRM Strategy Leads, Growth Marketing Directors, and Executive Leadership.

### Analytical Capabilities
- Executive Overview: Tracks gross revenue, order volume, unique customer headcount, and monthly sales trends using custom Matplotlib filled area plots.
- Cohort Retention Matrix: Groups buyers by initial purchase period and evaluates lifecycle decay across 12+ months using an annotated Seaborn heatmap.
- RFM Marketing Segmentation: Applies quintile scoring across Recency, Frequency, and Monetary dimensions to classify customers into actionable segments (Champions, Loyal Customers, New/Promising, At Risk, Hibernating/Lost).
- Customer Profiler and Lookup: Provides instant lookup by Customer ID to inspect individual purchase history, spend tiers, and transaction logs.
- Exploratory Analysis: Features a dedicated Jupyter notebook detailing missing value treatment, return order isolation, and segmentation math.

### Visualization Design Rationale: Bar Charts vs. Treemaps
For RFM segment analysis, dual-panel horizontal bar charts were selected over nested 2D treemaps based on the **Cleveland and McGill Graphical Perception Hierarchy**:
1. **Perceptual Accuracy:** Human vision evaluates positions along an aligned common scale with the lowest judgment error. In contrast, evaluating 2D area (treemaps) introduces high cognitive estimation variance.
2. **Decoupled Volume vs. Value:** A single treemap conflates customer headcount with monetary spend. Dual aligned bars decouple the two metrics: Panel 1 shows customer density per segment, while Panel 2 shows average spend per customer in dollars. This immediately reveals that high-value "Champions" represent modest headcount but massive individual spend.

---

## 2. Data Dictionary and Variables

Processed data is stored as columnar Parquet files for fast query execution:

<details>
<summary><b>Click to expand transactions schema variables</b></summary>

- `InvoiceNo`: Unique 6-digit transaction identifier (cancellations prefixed with 'C').
- `StockCode`: Unique product SKU identifier.
- `Description`: Clean product description string.
- `Quantity`: Number of units purchased (outliers capped at 99.9th percentile).
- `InvoiceDate`: Timestamp of transaction.
- `UnitPrice`: Unit price in sterling/USD (outliers capped at 99.9th percentile).
- `CustomerID`: Unique 5-digit buyer identifier (unregistered guest transactions assigned 'Guest').
- `Country`: Customer country of residence.
- `TotalSales`: Engineered revenue calculated as `Quantity * UnitPrice`.
- `IsCancelled`: Boolean indicator flagging cancellations or negative quantities.
- `Hemisphere`: Geographic classification for seasonal demand analysis.

</details>

<details>
<summary><b>Click to expand customer RFM schema variables</b></summary>

- `CustomerID`: Unique customer identifier.
- `Recency`: Days elapsed between reference date and customer last purchase.
- `Frequency`: Total distinct invoice orders placed.
- `Monetary`: Cumulative sales revenue generated across customer lifecycle.
- `R_Score`: Recency quintile score from 1 (dormant) to 5 (recent).
- `F_Score`: Frequency quintile score from 1 (single order) to 5 (frequent buyer).
- `M_Score`: Monetary quintile score from 1 (low spend) to 5 (top tier spend).
- `RFM_Score`: Combined 3-digit score string (e.g. 555, 111).
- `Segment`: Behavioral category classification based on quintile combinations.

</details>

---

## 3. Technology Stack

- **Package Management:** Pixi (Conda-forge ecosystem for reproducible cross-platform environments)
- **Runtime:** Python 3.10+
- **Data Engineering:** Pandas, NumPy, PyArrow
- **Visualization:** Matplotlib and Seaborn Object-Oriented API
- **Web Interface:** Streamlit (Glassmorphism Dark Theme configured via `.streamlit/config.toml`)
- **Version Control:** Git, GitHub

---

## 4. System Architecture and Codebase Layout

The pipeline isolates ingestion, data transformation, exploratory notebook analysis, and web dashboard presentation:

```text
[Raw Retail Transactions CSV]
              │
              ▼ (data/download_data.py)
         [data/raw/]
              │
              ▼ (src/data_prep.py ETL)
   ┌───────────────────────────────────────────────┐
   ▼                                               ▼
[data/processed/transactions.parquet]    [data/processed/customers.parquet]
   │                                               │
   ├───────────────────────────────┬───────────────┘
   ▼                               ▼
(notebooks/01_cohort_retention...) (streamlit_app.py / app.py Bridge)
```

<details>
<summary><b>Click to expand codebase directory structure</b></summary>

- `data/download_data.py`: Downloads online retail CSV source files.
- `src/data_prep.py`: Cleans raw records, removes anomalies, caps outliers, and writes Parquet tables.
- `src/data_processing.py`: Core mathematical logic for cohort pivots and RFM scoring.
- `notebooks/01_cohort_retention_and_rfm_eda.ipynb`: Fully executed exploratory notebook with narrative takeaways.
- `streamlit_app.py`: Main dashboard implementation using Matplotlib and Seaborn Object-Oriented charts.
- `app.py`: Backwards-compatible entrypoint forwarding to `streamlit_app.py` for cloud deployments.
- `pixi.toml`: Explicit dependency specifications and executable task commands.
- `requirements.txt`: Streamlit Community Cloud package manifest.
- `.streamlit/config.toml`: Enforces default dark mode (`#0E111D` background, `#1856FF` primary accent).

</details>

---

## 5. Local Setup and Execution

### Prerequisites
Install Pixi on your machine:
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

### Setup Commands
1. Navigate to the project directory:
   ```bash
   cd 02_user_cohort_rfm_analytics
   ```

2. Install dependencies:
   ```bash
   pixi install
   ```

3. Run data preparation ETL pipeline:
   ```bash
   pixi run data-prep
   ```

4. Launch local Streamlit analytics dashboard:
   ```bash
   pixi run app
   ```
   The application will open at `http://localhost:8501`.

---

## Quick Reference Task Table

| Action | Command | Output |
| :--- | :--- | :--- |
| Ingest Raw Data | `pixi run download-data` | `data/raw/online_retail.csv` |
| Execute ETL Pipeline | `pixi run data-prep` | `data/processed/*.parquet` |
| Launch Dashboard | `pixi run app` | Streamlit Dashboard Server |
| Run Exploratory Notebook | Open Jupyter in Pixi env | `notebooks/*.ipynb` |
