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
    st.plotly_chart(fig_sales, width="stretch")

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
        st.plotly_chart(fig_cohort, width="stretch")
    else:
        st.dataframe(
            cohort_retention.style.background_gradient(cmap='Blues', axis=1).format("{:.1f}%", na_rep="-"),
            width="stretch"
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
        st.plotly_chart(fig_tree, width="stretch")
        
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
        st.plotly_chart(fig_bar, width="stretch")

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
        
    st.dataframe(df_cust_segment, width="stretch")
    
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
            st.dataframe(cust_tx, width="stretch")
        else:
            st.error(f"No profile records found for Customer ID {search_id}")
