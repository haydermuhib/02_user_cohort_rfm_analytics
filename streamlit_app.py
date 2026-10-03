import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Import core processing functions
try:
    from src.data_processing import calculate_cohort_retention, calculate_rfm_profiles
except ImportError:
    SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    from data_processing import calculate_cohort_retention, calculate_rfm_profiles

# Page Config
st.set_page_config(
    page_title="User Cohorts and RFM Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphism Styling
st.html("""
<style>
.stApp {
    background: linear-gradient(135deg, #0E111D 0%, #101424 100%) !important;
}

div[data-testid="stMetricValue"] {
    font-size: 2.0rem !important;
    font-weight: 700 !important;
    color: #EAEAEA !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #A0A5B5 !important;
}

.glass-card {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 18px !important;
    margin-bottom: 16px !important;
}
</style>
""")

# Load Cleaned Data
@st.cache_data
def load_cached_data():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    tx_path = os.path.join(project_dir, "data", "processed", "transactions.parquet")
    cust_path = os.path.join(project_dir, "data", "processed", "customers.parquet")
    
    if not os.path.exists(tx_path):
        try:
            from src.data_prep import run_data_pipeline
        except ImportError:
            from data_prep import run_data_pipeline
        run_data_pipeline()
        
    df_tx = pd.read_parquet(tx_path)
    
    # Ensure full customer profiles are loaded or recomputed
    if os.path.exists(cust_path):
        df_cust = pd.read_parquet(cust_path)
        if len(df_cust) < 100:
            df_cust = calculate_rfm_profiles(df_tx)
    else:
        df_cust = calculate_rfm_profiles(df_tx)
        
    return df_tx, df_cust

df_tx, df_cust = load_cached_data()

st.title("User Cohort and RFM Analytics")
st.markdown("Customer purchasing patterns, monthly cohort retention matrices, and RFM behavioral segmentation.")

# Sidebar Filters
st.sidebar.header("Filter Settings")
countries = sorted(df_tx['Country'].unique())
selected_country = st.sidebar.selectbox("Select Country", ["All Countries"] + countries)

# Apply filters
if selected_country != "All Countries":
    df_tx_filtered = df_tx[df_tx['Country'] == selected_country].copy()
    country_cust_ids = df_tx_filtered[df_tx_filtered['CustomerID'] != 'Guest']['CustomerID'].unique()
    df_cust_filtered = df_cust[df_cust['CustomerID'].isin(country_cust_ids)].copy()
else:
    df_tx_filtered = df_tx.copy()
    df_cust_filtered = df_cust.copy()

# Layout Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Overview",
    "Cohort Retention Matrix",
    "RFM Marketing Segments",
    "Customer Profiler and Lookup"
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
        avg_frequency = df_cust_filtered['Frequency'].mean() if not df_cust_filtered.empty else 0.0
        st.metric("Avg Orders / Customer", f"{avg_frequency:.1f}")
    with col4:
        total_orders = df_tx_filtered[~df_tx_filtered['IsCancelled']]['InvoiceNo'].nunique()
        st.metric("Total Invoices", f"{total_orders:,}")
        
    st.markdown("### Monthly Sales Trend")
    df_valid_tx = df_tx_filtered[~df_tx_filtered['IsCancelled']].copy()
    df_valid_tx['YearMonth'] = df_valid_tx['InvoiceDate'].dt.to_period('M').astype(str)
    df_monthly = df_valid_tx.groupby('YearMonth')['TotalSales'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 4.2))
    fig.patch.set_facecolor("#0E111D")
    ax.set_facecolor("#101424")
    
    if not df_monthly.empty:
        x_vals = range(len(df_monthly))
        ax.plot(x_vals, df_monthly['TotalSales'], color="#1856FF", linewidth=2.5, marker="o", markersize=4)
        ax.fill_between(x_vals, df_monthly['TotalSales'], color="#1856FF", alpha=0.25)
        ax.set_xticks(list(x_vals))
        ax.set_xticklabels(df_monthly['YearMonth'], rotation=40, ha="right", fontsize=9, color="#A0A5B5")
    
    ax.set_title("Monthly Gross Sales Revenue", fontsize=12, fontweight="bold", color="#EAEAEA", pad=12)
    ax.set_ylabel("Revenue (USD)", fontsize=10, color="#A0A5B5")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
    ax.grid(True, linestyle="--", alpha=0.15, color="#FFFFFF")
    ax.tick_params(colors="#A0A5B5", labelsize=9)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#2A2E3D")
        
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

# Tab 2: Cohort Retention Matrix
with tab2:
    st.markdown("### Monthly Cohort Retention Heatmap")
    cohort_counts, cohort_retention = calculate_cohort_retention(df_tx_filtered)
    
    view_mode = st.radio("Display Format", ["Heatmap Visualization", "Styled Data Grid"])
    
    if view_mode == "Heatmap Visualization":
        if not cohort_retention.empty:
            fig_h, ax_h = plt.subplots(figsize=(11, 5.8))
            fig_h.patch.set_facecolor("#0E111D")
            ax_h.set_facecolor("#101424")
            
            sns.heatmap(
                cohort_retention,
                annot=True,
                fmt=".1f",
                cmap="YlGnBu",
                linewidths=0.5,
                linecolor="#0E111D",
                cbar_kws={"label": "Retention Rate (%)"},
                ax=ax_h
            )
            
            ax_h.set_title("Monthly Cohort Retention Rate (%)", fontsize=12, fontweight="bold", color="#EAEAEA", pad=12)
            ax_h.set_xlabel("Cohort Period (Months Since First Purchase)", fontsize=10, color="#A0A5B5")
            ax_h.set_ylabel("Acquisition Cohort", fontsize=10, color="#A0A5B5")
            ax_h.tick_params(colors="#A0A5B5", labelsize=9)
            
            # Colorbar tick styling
            cbar = ax_h.collections[0].colorbar
            cbar.ax.yaxis.set_tick_params(color="#A0A5B5")
            plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#A0A5B5")
            cbar.set_label("Retention Rate (%)", color="#A0A5B5", fontsize=10)
            
            fig_h.tight_layout()
            st.pyplot(fig_h, width="stretch")
            plt.close(fig_h)
        else:
            st.info("Insufficient customer cohort volume to construct retention matrix for this selection.")
    else:
        st.dataframe(
            cohort_retention.style.background_gradient(cmap='Blues', axis=1).format("{:.1f}%", na_rep="-"),
            width="stretch"
        )

# Tab 3: RFM Marketing Segments
with tab3:
    st.markdown("### Customer Distribution and Spend by RFM Segment")
    
    if not df_cust_filtered.empty:
        df_seg = df_cust_filtered.groupby('Segment').agg(
            CustomerCount=('CustomerID', 'count'),
            AvgMonetary=('Monetary', 'mean'),
            TotalMonetary=('Monetary', 'sum')
        ).reset_index().sort_values('CustomerCount', ascending=True)
        
        fig_rfm, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
        fig_rfm.patch.set_facecolor("#0E111D")
        
        # Panel 1: Customer Count by Segment
        ax1.set_facecolor("#101424")
        bars1 = ax1.barh(df_seg['Segment'], df_seg['CustomerCount'], color="#1856FF", alpha=0.85, height=0.6)
        ax1.set_title("Customers per Segment", fontsize=11, fontweight="bold", color="#EAEAEA", pad=10)
        ax1.set_xlabel("Customer Count", fontsize=9, color="#A0A5B5")
        ax1.grid(True, linestyle="--", alpha=0.15, color="#FFFFFF", axis="x")
        ax1.tick_params(colors="#A0A5B5", labelsize=9)
        for spine in ["top", "right"]:
            ax1.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax1.spines[spine].set_color("#2A2E3D")
            
        # Add labels
        for bar in bars1:
            w = bar.get_width()
            ax1.text(w + max(df_seg['CustomerCount']) * 0.02, bar.get_y() + bar.get_height() / 2,
                     f"{int(w):,}", va="center", ha="left", color="#EAEAEA", fontsize=8.5, fontweight="bold")
        
        # Panel 2: Average Spend per Segment
        ax2.set_facecolor("#101424")
        bars2 = ax2.barh(df_seg['Segment'], df_seg['AvgMonetary'], color="#00ADB5", alpha=0.85, height=0.6)
        ax2.set_title("Average Spend per Customer", fontsize=11, fontweight="bold", color="#EAEAEA", pad=10)
        ax2.set_xlabel("Average Revenue (USD)", fontsize=9, color="#A0A5B5")
        ax2.xaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}"))
        ax2.grid(True, linestyle="--", alpha=0.15, color="#FFFFFF", axis="x")
        ax2.tick_params(colors="#A0A5B5", labelsize=9)
        for spine in ["top", "right"]:
            ax2.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax2.spines[spine].set_color("#2A2E3D")
            
        for bar in bars2:
            w = bar.get_width()
            ax2.text(w + max(df_seg['AvgMonetary']) * 0.02, bar.get_y() + bar.get_height() / 2,
                     f"${w:,.0f}", va="center", ha="left", color="#EAEAEA", fontsize=8.5, fontweight="bold")
                     
        fig_rfm.tight_layout()
        st.pyplot(fig_rfm, width="stretch")
        plt.close(fig_rfm)
        
        # Summary metrics table
        st.markdown("#### Segment Revenue Contribution Summary")
        df_summary = df_seg.copy().sort_values('TotalMonetary', ascending=False)
        df_summary['ShareOfRevenue'] = (df_summary['TotalMonetary'] / df_summary['TotalMonetary'].sum()) * 100
        df_summary['TotalMonetary'] = df_summary['TotalMonetary'].apply(lambda x: f"${x:,.2f}")
        df_summary['AvgMonetary'] = df_summary['AvgMonetary'].apply(lambda x: f"${x:,.2f}")
        df_summary['ShareOfRevenue'] = df_summary['ShareOfRevenue'].apply(lambda x: f"{x:.1f}%")
        df_summary.columns = ["Segment", "Customers", "Avg Spend / Customer", "Total Revenue", "Revenue Share"]
        st.dataframe(df_summary, width="stretch")
    else:
        st.info("No customer profiles available for the selected filter.")

# Tab 4: Customer Profiler and Lookup
with tab4:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        segment_list = sorted(df_cust_filtered['Segment'].unique()) if not df_cust_filtered.empty else []
        selected_segment = st.selectbox("Filter Segment Profiles", ["All Segments"] + segment_list)
        
    df_cust_segment = df_cust_filtered.copy()
    if selected_segment != "All Segments":
        df_cust_segment = df_cust_segment[df_cust_segment['Segment'] == selected_segment]
        
    st.dataframe(df_cust_segment, width="stretch")
    
    st.markdown("---")
    st.markdown("### Customer Transaction Search")
    
    search_id = st.text_input("Enter Customer ID to look up (e.g. 12347, 12769)")
    if search_id:
        cust_profile = df_cust_filtered[df_cust_filtered['CustomerID'] == search_id]
        if not cust_profile.empty:
            st.markdown(f"#### Profile Details for Customer {search_id}")
            c_row = cust_profile.iloc[0]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Recency", f"{c_row['Recency']} days ago")
            m2.metric("Order Frequency", f"{c_row['Frequency']} orders")
            m3.metric("Total Spend", f"${c_row['Monetary']:,.2f}")
            m4.metric("Segment Group", f"{c_row['Segment']}")
            
            st.markdown("#### Transaction Logs")
            cust_tx = df_tx[df_tx['CustomerID'] == search_id]
            st.dataframe(cust_tx, width="stretch")
        else:
            st.error(f"No profile records found for Customer ID {search_id} in active selection.")
