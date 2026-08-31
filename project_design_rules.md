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
