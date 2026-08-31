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
