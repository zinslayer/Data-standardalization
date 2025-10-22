import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit_agraph import agraph, Node, Edge, Config
import json
import uuid
from datetime import datetime
import zipfile
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import requests

# Page configuration
st.set_page_config(
    page_title="Aarti Industries - Trade Data Cleaner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Aarti Industries branding
st.markdown("""
<style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', 'Roboto', sans-serif;
    }
    
    /* Main background - Aarti blue theme */
    .stApp {
        background: linear-gradient(135deg, #0a2463 0%, #1e3a8a 30%, #2563eb 70%, #3b82f6 100%);
        background-attachment: fixed;
    }
    
    /* Top header bar with logo */
    .aarti-header {
        background: linear-gradient(90deg, #fb923c 0%, #f97316 50%, #ea580c 100%);
        padding: 1.5rem 2rem;
        margin: -5rem -5rem 2rem -5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        border-bottom: 4px solid #ffffff;
    }
    
    .aarti-logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .aarti-logo-circle {
        width: 60px;
        height: 60px;
        background: #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .aarti-title {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        letter-spacing: 0.5px;
    }
    
    .aarti-subtitle {
        color: #fef3c7;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: -5px;
    }
    
    /* Header styling */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.4);
        margin-bottom: 0.5rem !important;
        letter-spacing: 1px;
    }
    
    h2 {
        color: #fbbf24 !important;
        font-weight: 600 !important;
        font-size: 1.7rem !important;
        margin-top: 2rem !important;
        border-bottom: 3px solid #f97316;
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    h3 {
        color: #fde68a !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
    }
    
    /* Content containers - Bold white text */
    .stMarkdown p, .stMarkdown li {
        color: #ffffff !important;
        font-size: 1.1rem;
        line-height: 1.7;
        font-weight: 600 !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
    }
    
    /* Strong text */
    strong {
        color: #fbbf24 !important;
        font-weight: 600;
    }
    
    /* Input fields */
    .stTextInput input, .stMultiSelect, .stSelectbox {
        background-color: rgba(255, 255, 255, 0.98) !important;
        color: #0a2463 !important;
        border: 2px solid #f97316 !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        padding: 0.7rem !important;
    }
    
    .stTextInput input:focus, .stMultiSelect:focus-within, .stSelectbox:focus-within {
        border-color: #fb923c !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2) !important;
    }
    
    /* Labels - Enhanced visibility */
    .stTextInput label, .stMultiSelect label, .stSelectbox label, [data-testid="stFileUploader"] label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
    }
    
    /* Info text and help text */
    .stTextInput > div > div > div, 
    .stMultiSelect > div > div > div,
    .stSelectbox > div > div > div,
    [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.4);
    }
    
    /* Success/Info messages - High contrast */
    .element-container .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Make all status text visible */
    .stMarkdown, .stText {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Buttons - Aarti orange theme */
    .stButton button {
        background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fdba74 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2.5rem !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%) !important;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.7);
        transform: translateY(-3px) scale(1.02);
    }
    
    .stButton button:disabled {
        background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%) !important;
        opacity: 0.5;
        box-shadow: none;
    }
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        padding: 0.7rem 2.5rem !important;
        font-size: 1.05rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%) !important;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.7);
    }
    
    /* Metrics - Aarti orange accent */
    [data-testid="stMetricValue"] {
        color: #fb923c !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: #fef3c7 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Info/Success/Warning boxes - High contrast white text */
    .stAlert {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.3) 0%, rgba(251, 146, 60, 0.25) 100%) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border-left: 5px solid #f97316 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 1rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-size: 1.1rem !important;
    }
    
    .stAlert > div {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border-radius: 12px;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.3);
        border: 2px solid #f97316;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(251, 146, 60, 0.1) 100%);
        padding: 15px;
        border-radius: 12px;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        color: #fef3c7;
        font-weight: 600;
        padding: 14px 28px;
        border: 2px solid transparent;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f97316 0%, #fb923c 100%) !important;
        border-color: #fdba74;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.5);
        transform: scale(1.05);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(249, 115, 22, 0.3);
        border-color: #fb923c;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(251, 146, 60, 0.15) 100%) !important;
        border-radius: 10px !important;
        color: #fef3c7 !important;
        font-weight: 600 !important;
        border: 1px solid rgba(249, 115, 22, 0.3);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(251, 146, 60, 0.05) 100%);
        border-radius: 12px;
        border: 3px dashed rgba(249, 115, 22, 0.6);
        padding: 25px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #fb923c;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(251, 146, 60, 0.1) 100%);
    }
    
    /* Columns */
    [data-testid="column"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(249, 115, 22, 0.05) 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(249, 115, 22, 0.2);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #f97316 !important;
    }
    
    /* Multiselect dropdown */
    [data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border-radius: 10px;
    }
    
    /* Success message */
    .success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(52, 211, 153, 0.15) 100%) !important;
        color: #ffffff !important;
        border-left-color: #10b981 !important;
    }
    
    /* Section dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #f97316 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
    }
</style>
""", unsafe_allow_html=True)

# Aarti Industries Header with custom logo
st.markdown("""
<div class="aarti-header">
    <div class="aarti-logo">
        <svg width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <!-- Orange circle background -->
            <circle cx="50" cy="50" r="48" fill="#FFFFFF"/>
            <!-- Globe icon in Aarti blue -->
            <g transform="translate(50, 50)">
                <!-- Outer circle -->
                <circle cx="0" cy="0" r="35" fill="none" stroke="#0a2463" stroke-width="4"/>
                <!-- Vertical lines -->
                <line x1="0" y1="-35" x2="0" y2="35" stroke="#0a2463" stroke-width="3"/>
                <ellipse cx="0" cy="0" rx="15" ry="35" fill="none" stroke="#0a2463" stroke-width="3"/>
                <!-- Horizontal lines -->
                <line x1="-35" y1="0" x2="35" y2="0" stroke="#0a2463" stroke-width="3"/>
                <ellipse cx="0" cy="0" rx="35" ry="15" fill="none" stroke="#0a2463" stroke-width="3"/>
            </g>
        </svg>
        <div>
            <div class="aarti-title">AARTI INDUSTRIES</div>
            <div class="aarti-subtitle">Trade Data Standardization System</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'current_mappings' not in st.session_state:
    st.session_state.current_mappings = {}
if 'current_files_hash' not in st.session_state:
    st.session_state.current_files_hash = None
if 'selected_data_type' not in st.session_state:
    st.session_state.selected_data_type = None

# Initialize session state for value chain
if 'value_chain_nodes' not in st.session_state:
    st.session_state.value_chain_nodes = []
if 'value_chain_edges' not in st.session_state:
    st.session_state.value_chain_edges = []
if 'node_counter' not in st.session_state:
    st.session_state.node_counter = 0
if 'selected_node_id' not in st.session_state:
    st.session_state.selected_node_id = None

# Initialize session state for saved datasets
if 'saved_datasets' not in st.session_state:
    st.session_state.saved_datasets = {}
if 'temp_cleaned_data' not in st.session_state:
    st.session_state.temp_cleaned_data = None
if 'temp_data_type' not in st.session_state:
    st.session_state.temp_data_type = None

# Initialize relation mappings in session state
if 'product_relations' not in st.session_state:
    st.session_state.product_relations = {}

def load_and_merge_files(uploaded_files):
    """Load and merge multiple Excel files into a single DataFrame"""
    dfs = []
    for file in uploaded_files:
        try:
            df = pd.read_excel(file, engine='openpyxl')
            dfs.append(df)
        except Exception as e:
            st.error(f"Error loading {file.name}: {str(e)}")
    
    if dfs:
        merged = pd.concat(dfs, ignore_index=True)
        return merged
    return None

def extract_commercial_name_import_export(description):
    """Extract commercial name from Import/Export Commercial Description field"""
    if pd.isna(description):
        return "Unknown"
    return str(description).strip()

def extract_commercial_name_global(description):
    """Extract commercial name from Global Trade Product Description field"""
    if pd.isna(description):
        return "Unknown"
    return str(description).strip()

def apply_mappings_import_export(df, mappings):
    """Apply name mappings and filter the DataFrame for Import/Export data"""
    if 'Commercial Description' not in df.columns:
        st.error("'Commercial Description' column not found in the data")
        return df
    
    df['Commercial Name'] = df['Commercial Description'].apply(extract_commercial_name_import_export)
    df['Standardized Name'] = df['Commercial Name'].map(mappings)
    filtered_df = df[df['Standardized Name'].notna()].copy()
    
    return filtered_df

def apply_mappings_global(df, mappings):
    """Apply name mappings and filter the DataFrame for Global Trade data"""
    if 'Product Description' not in df.columns:
        st.error("'Product Description' column not found in the data")
        return df
    
    df['Commercial Name'] = df['Product Description'].apply(extract_commercial_name_global)
    df['Standardized Name'] = df['Commercial Name'].map(mappings)
    filtered_df = df[df['Standardized Name'].notna()].copy()
    
    return filtered_df

def get_financial_year_quarter(date_val):
    """Convert date to FY Quarter (April-March cycle)"""
    try:
        if pd.isna(date_val):
            return None
        
        if isinstance(date_val, str):
            date_obj = pd.to_datetime(date_val, dayfirst=True, errors='coerce')
        else:
            date_obj = pd.to_datetime(date_val)
        
        if pd.isna(date_obj):
            return None
        
        year = date_obj.year
        month = date_obj.month
        
        # Determine FY and Quarter
        if month >= 4:  # April onwards
            fy_start = year
            fy_end = year + 1
        else:  # Jan-March
            fy_start = year - 1
            fy_end = year
        
        # Determine quarter (Q1=Apr-Jun, Q2=Jul-Sep, Q3=Oct-Dec, Q4=Jan-Mar)
        if month in [4, 5, 6]:
            quarter = "Q1"
        elif month in [7, 8, 9]:
            quarter = "Q2"
        elif month in [10, 11, 12]:
            quarter = "Q3"
        else:  # [1, 2, 3]
            quarter = "Q4"
        
        return f"FY{fy_start}-{str(fy_end)[2:]} {quarter}"
    except:
        return None

def process_dataset_for_analytics(df):
    """Process dataset: filter units, convert to MT, compute quarters"""
    # Find required columns
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'period' in col.lower():
            date_col = col
            break
    
    qty_col = None
    for col in df.columns:
        if 'quantity' in col.lower() or 'qty' in col.lower() or 'weight' in col.lower():
            qty_col = col
            break
    
    unit_col = None
    for col in df.columns:
        if 'unit' in col.lower() or 'uqc' in col.lower():
            unit_col = col
            break
    
    value_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'unit value' in col_lower and 'usd' in col_lower:
            value_col = col
            break
        elif 'unit price' in col_lower or 'price' in col_lower:
            value_col = col
            break
    
    if not value_col:
        for col in df.columns:
            col_lower = col.lower()
            if 'value' in col_lower or 'amount' in col_lower or 'fob' in col_lower or 'cif' in col_lower:
                value_col = col
                break
    
    # Find country/origin columns
    country_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'country' in col_lower or 'origin' in col_lower or 'destination' in col_lower:
            country_col = col
            break
    
    # Find supplier/buyer columns
    supplier_col = None
    buyer_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'supplier' in col_lower or 'exporter' in col_lower:
            supplier_col = col
        if 'buyer' in col_lower or 'importer' in col_lower or 'consignee' in col_lower:
            buyer_col = col
    
    if not all([date_col, qty_col, unit_col, value_col]):
        return None, f"Missing required columns. Found: Date={date_col}, Qty={qty_col}, Unit={unit_col}, Value={value_col}"
    
    # Create working copy
    df_work = df.copy()
    
    # Filter valid units (MT or KG only)
    df_work['Unit_Upper'] = df_work[unit_col].astype(str).str.upper().str.strip()
    valid_mask = df_work['Unit_Upper'].str.contains('METRIC TON|KILOGRAMS?|^MTS?$|^KGS?$', regex=True, na=False)
    df_work = df_work[valid_mask].copy()
    
    if len(df_work) == 0:
        return None, "No valid MT or KG rows found after filtering"
    
    # Convert all to MT
    df_work['Quantity_MT'] = np.where(
        df_work['Unit_Upper'].str.contains('KILOGRAM|^KGS?$', regex=True),
        df_work[qty_col].astype(float) / 1000,
        df_work[qty_col].astype(float)
    )
    
    # Convert price to $/kg
    df_work['Price_USD_per_kg'] = np.where(
        df_work['Unit_Upper'].str.contains('KILOGRAM|^KGS?$', regex=True),
        df_work[value_col].astype(float),
        df_work[value_col].astype(float) / 1000
    )
    
    # Add quarter column
    df_work['Quarter'] = df_work[date_col].apply(get_financial_year_quarter)
    df_work = df_work[df_work['Quarter'].notna()].copy()
    
    # Store column names for later use
    df_work.attrs['country_col'] = country_col
    df_work.attrs['supplier_col'] = supplier_col
    df_work.attrs['buyer_col'] = buyer_col
    
    return df_work, None

# Create tabs - NOW WITH 4 TABS
tab1, tab3, tab4, tab5, tab6 = st.tabs(["📊 Data Processing",  "🔬 Value Chain Builder", "📈 Analytics & Insights", "Market Estimation", "EC analysis"])

with tab1:
    st.header("📦 Trade Data Processing")
    
    # Data type selector
    data_type = st.selectbox(
        "Select Data Type",
        options=["Import", "Export", "Global"],
        help="Choose the type of trade data you want to process",
        key="data_type_selector"
    )
    
    # Get icon based on data type
    data_type_icon = {
        "Import": "📥",
        "Export": "📤",
        "Global": "🌍"
    }
    
    st.markdown(f"### {data_type_icon[data_type]} Processing {data_type} Trade Data")
    
    # Check if data type changed
    if st.session_state.selected_data_type != data_type:
        st.session_state.selected_data_type = data_type
        st.session_state.current_df = None
        st.session_state.current_mappings = {}
        st.session_state.current_files_hash = None
    
    # Determine the description column based on data type
    desc_column = 'Product Description' if data_type == 'Global' else 'Commercial Description'
    apply_func = apply_mappings_global if data_type == 'Global' else apply_mappings_import_export
    extract_func = extract_commercial_name_global if data_type == 'Global' else extract_commercial_name_import_export
    
    # File uploader
    files = st.file_uploader(
        f"Select {data_type} Excel files (.xlsx)",
        type=['xlsx'],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if files:
        # Create a hash of uploaded files to detect changes
        files_hash = hash(tuple(f.name for f in files))
        
        # Reset mappings if new files are uploaded
        if files_hash != st.session_state.current_files_hash:
            st.session_state.current_mappings = {}
            st.session_state.current_files_hash = files_hash
        
        # Load and merge files
        if st.button(f"Load and Merge {data_type} Files", key="load_button") or st.session_state.current_df is not None:
            if st.session_state.current_df is None:
                with st.spinner(f"Loading and merging {data_type.lower()} files..."):
                    st.session_state.current_df = load_and_merge_files(files)
            
            if st.session_state.current_df is not None:
                df = st.session_state.current_df
                
                # Check if required column exists
                if desc_column in df.columns:
                    
                    # Add pre-filtering section
                    st.subheader("🔍 Pre-Filter Data (Optional)")
                    st.write("Filter out unwanted entries before extracting unique names")
                    
                    col_filter1, col_filter2 = st.columns(2)
                    with col_filter1:
                        exclude_keywords = st.text_input(
                            "🚫 Exclude entries containing (comma-separated)",
                            placeholder="e.g., TESTING, SAMPLE, TRIAL",
                            key="pre_exclude",
                            help="Remove rows where description contains any of these keywords"
                        )
                    with col_filter2:
                        include_keywords = st.text_input(
                            "✓ Include only entries containing (comma-separated)",
                            placeholder="e.g., ANILINE, CHEMICAL",
                            key="pre_include",
                            help="Keep only rows where description contains any of these keywords (leave empty to include all)"
                        )
                    
                    # Apply pre-filtering
                    filtered_df = df.copy()
                    original_count = len(filtered_df)
                    
                    # Exclude filter
                    if exclude_keywords:
                        exclude_list = [kw.strip().upper() for kw in exclude_keywords.split(',') if kw.strip()]
                        for keyword in exclude_list:
                            filtered_df = filtered_df[~filtered_df[desc_column].astype(str).str.upper().str.contains(keyword, na=False)]
                    
                    # Include filter
                    if include_keywords:
                        include_list = [kw.strip().upper() for kw in include_keywords.split(',') if kw.strip()]
                        mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                        for keyword in include_list:
                            mask = mask | filtered_df[desc_column].astype(str).str.upper().str.contains(keyword, na=False)
                        filtered_df = filtered_df[mask]
                    
                    rows_removed = original_count - len(filtered_df)
                    
                    if exclude_keywords or include_keywords:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Original Rows", original_count)
                        with col2:
                            st.metric("Filtered Rows", len(filtered_df))
                        with col3:
                            st.metric("Removed", rows_removed, delta=f"-{rows_removed}")
                    
                    # Extract unique names from filtered data
                    filtered_df['Commercial Name'] = filtered_df[desc_column].apply(extract_func)
                    unique_names = sorted(filtered_df['Commercial Name'].unique())
                    
                    st.success(f"✅ Loaded {len(filtered_df)} rows from {len(files)} file(s)")
                    st.info(f"Found {len(unique_names)} unique commercial names")
                    
                    # Update the working dataframe to filtered version
                    df = filtered_df
                    
                    # Display sample data
                    with st.expander(f"📊 Preview {data_type} Data"):
                        st.dataframe(df.head(20))
                    
                    # Commercial Name Standardization
                    st.subheader(f"🔄 {data_type} Name Standardization")
                    
                    # Display current mappings
                    if st.session_state.current_mappings:
                        st.write("**Current Mappings:**")
                        mapping_df = pd.DataFrame([
                            {"Source Name": k, "→ Target Name": v}
                            for k, v in st.session_state.current_mappings.items()
                        ])
                        st.dataframe(mapping_df, use_container_width=True)
                        
                        if st.button(f"🗑️ Clear All {data_type} Mappings", key="clear_button"):
                            st.session_state.current_mappings = {}
                            st.experimental_rerun()
                    
                    # Get unmapped names
                    unmapped_names = [name for name in unique_names 
                                     if name not in st.session_state.current_mappings]
                    
                    if unmapped_names:
                        st.write("**Create New Mapping:**")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Add Select All checkbox
                            select_all = st.checkbox(
                                "Select All Unmapped Names",
                                key="select_all_checkbox",
                                help="Select all unmapped names at once"
                            )
                            
                            selected_names = st.multiselect(
                                "Select Source Names (original names to standardize)",
                                options=unmapped_names,
                                default=unmapped_names if select_all else [],
                                help="Select one or more names to map to a standardized name",
                                key="sources"
                            )
                        
                        with col2:
                            target_name = st.text_input(
                                "Target Name (standardized name)",
                                help="Enter the generalized/standardized name",
                                key="target"
                            )
                        
                        if st.button(f"➕ Add {data_type} Mapping", 
                                   disabled=not (selected_names and target_name),
                                   key="add_button"):
                            for name in selected_names:
                                st.session_state.current_mappings[name] = target_name
                            st.success(f"Added mapping: {len(selected_names)} name(s) → {target_name}")
                            st.experimental_rerun()
                    else:
                        st.success(f"✅ All unique {data_type.lower()} names have been mapped!")
                    
                    # Show mapping statistics
                    st.metric(f"Mapped {data_type} Names", f"{len(st.session_state.current_mappings)} / {len(unique_names)}")
                    
                    # Apply mappings and generate output
                    if st.session_state.current_mappings:
                        st.subheader(f"📥 Generate Cleaned {data_type} Data")
                        
                        if st.button(f"🔄 Apply {data_type} Mappings and Filter Data", key="apply_button"):
                            with st.spinner("Processing..."):
                                cleaned_df = apply_func(df.copy(), st.session_state.current_mappings)
                                
                                # Store cleaned data in session state temporarily
                                st.session_state.temp_cleaned_data = cleaned_df
                                st.session_state.temp_data_type = data_type
                                
                                st.success(f"✅ Processed! {len(cleaned_df)} rows retained (filtered from {len(df)} original rows)")
                                
                                # Display results
                                st.write(f"**Cleaned {data_type} Data Preview:**")
                                st.dataframe(cleaned_df.head(20))
                                
                                # Download button
                                output = BytesIO()
                                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                    cleaned_df.to_excel(writer, index=False, sheet_name='Cleaned Data')
                                output.seek(0)
                                
                                st.download_button(
                                    label=f"📥 Download Cleaned {data_type} Data",
                                    data=output,
                                    file_name=f"cleaned_{data_type.lower()}_trade_data.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="download_button"
                                )
                                
                                # Statistics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Original Rows", len(df))
                                with col2:
                                    st.metric("Cleaned Rows", len(cleaned_df))
                                with col3:
                                    st.metric("Removed Rows", len(df) - len(cleaned_df))
                        
                        # Save Dataset Section
                        if st.session_state.temp_cleaned_data is not None:
                            st.markdown("---")
                            st.subheader("💾 Save Cleaned Dataset")
                            st.write("Save this cleaned dataset for future analytics and processing")
                            
                            col_name, col_save = st.columns([3, 1])
                            
                            with col_name:
                                dataset_name = st.text_input(
                                    "Enter Dataset Name",
                                    placeholder=f"e.g., {data_type}_Q1_2024_Cleaned",
                                    key="dataset_name_input",
                                    help="Give this dataset a unique, descriptive name"
                                )
                            
                            with col_save:
                                st.write("")  # Spacing
                                st.write("")  # Spacing
                                if st.button("💾 Save Dataset", key="save_dataset_button", disabled=not dataset_name):
                                    if dataset_name in st.session_state.saved_datasets:
                                        st.warning(f"⚠️ Dataset '{dataset_name}' already exists! Choose a different name.")
                                    else:
                                        # Save dataset with metadata
                                        st.session_state.saved_datasets[dataset_name] = {
                                            'data': st.session_state.temp_cleaned_data.copy(),
                                            'type': st.session_state.temp_data_type,
                                            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'rows': len(st.session_state.temp_cleaned_data),
                                            'columns': list(st.session_state.temp_cleaned_data.columns)
                                        }
                                        
                                        st.success(f"✅ Dataset '{dataset_name}' saved successfully!")
                                        st.balloons()
                                        
                                        # Clear temp data
                                        st.session_state.temp_cleaned_data = None
                                        st.experimental_rerun()
                else:
                    st.error(f"'{desc_column}' column not found in the uploaded files")
    else:
        st.info(f"👆 Upload {data_type} Excel files to begin")
    
    # Display Saved Datasets
    if st.session_state.saved_datasets:
        st.markdown("---")
        st.subheader("📚 Saved Datasets")
        st.write(f"Total saved datasets: **{len(st.session_state.saved_datasets)}**")
        
        # Create a summary table
        saved_summary = []
        for name, info in st.session_state.saved_datasets.items():
            saved_summary.append({
                "Dataset Name": name,
                "Type": info['type'],
                "Rows": info['rows'],
                "Saved On": info['date']
            })
        
        summary_df = pd.DataFrame(saved_summary)
        st.dataframe(summary_df, use_container_width=True)
        
        # Dataset management
        col_manage1, col_manage2 = st.columns(2)
        
        with col_manage1:
            selected_dataset = st.selectbox(
                "Select dataset to manage:",
                options=list(st.session_state.saved_datasets.keys()),
                key="manage_dataset_select"
            )
        
        with col_manage2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            col_view, col_delete = st.columns(2)
            
            with col_view:
                if st.button("👁️ View", key="view_dataset_button"):
                    if selected_dataset:
                        dataset_info = st.session_state.saved_datasets[selected_dataset]
                        st.write(f"**Dataset: {selected_dataset}**")
                        st.write(f"Type: {dataset_info['type']} | Rows: {dataset_info['rows']} | Date: {dataset_info['date']}")
                        st.dataframe(dataset_info['data'].head(50))
            
            with col_delete:
                if st.button("🗑️ Delete", key="delete_dataset_button"):
                    if selected_dataset:
                        del st.session_state.saved_datasets[selected_dataset]
                        st.success(f"Deleted dataset: {selected_dataset}")
                        st.experimental_rerun()
        
        # Bulk download option
        if st.button("📦 Download All Datasets as ZIP", key="download_all_button"):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for name, info in st.session_state.saved_datasets.items():
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        info['data'].to_excel(writer, index=False, sheet_name='Data')
                    excel_buffer.seek(0)
                    zip_file.writestr(f"{name}.xlsx", excel_buffer.read())
            
            zip_buffer.seek(0)
            st.download_button(
                label="📥 Download ZIP",
                data=zip_buffer,
                file_name="all_saved_datasets.zip",
                mime="application/zip",
                key="download_zip_button"
            )



with tab3:
    st.markdown("""
    ### 🔬 Chemical Value Chain Builder
    Build interactive value chains for chemical molecules and their relationships.
    """)
    
    # Create two columns for controls and visualization
    col_controls, col_viz = st.columns([1, 2])
    
    with col_controls:
        st.markdown("#### 🎛️ Controls")
        
        # Add new node section
        with st.expander("➕ Add New Molecule", expanded=True):
            new_molecule_name = st.text_input(
                "Molecule Name",
                placeholder="e.g., Aniline, Benzene, etc.",
                key="new_molecule_input"
            )
            
            molecule_type = st.selectbox(
                "Molecule Type",
                ["Raw Material", "Intermediate", "Target Product", "By-Product"],
                key="molecule_type_select"
            )
            
            # Color mapping for different types
            color_map = {
                "Raw Material": "#3b82f6",      # Blue
                "Intermediate": "#f59e0b",      # Amber
                "Target Product": "#ef4444",    # Red
                "By-Product": "#8b5cf6",        # Purple
            }
            
            if st.button("➕ Add Molecule", disabled=not new_molecule_name):
                node_id = f"node_{st.session_state.node_counter}"
                st.session_state.node_counter += 1
                
                new_node = {
                    'id': node_id,
                    'label': new_molecule_name,
                    'type': molecule_type,
                    'color': color_map[molecule_type],
                    'size': 30 if molecule_type == "Target Product" else 25,
                    'font': {'size': 14, 'color': '#ffffff'}
                }
                st.session_state.value_chain_nodes.append(new_node)
                st.success(f"Added {new_molecule_name} as {molecule_type}")
                st.experimental_rerun()
        
        # Upload downstream applications
        with st.expander("📤 Upload Downstream Applications", expanded=False):
            st.markdown("""
            **Excel Format Expected:**
            - Category name in first column
            - Empty row (separator)
            - Category name in first column
            - Chemical names in rows below
            - Empty row (separator)
            - Next category name...
            
            The application categories will be automatically detected and visualized!
            """)
            
            applications_file = st.file_uploader(
                "Select Excel file (.xlsx, .xls)",
                type=['xlsx', 'xls'],
                key="applications_uploader"
            )
            
            if applications_file:
                try:
                    # Read Excel file
                    if applications_file.name.endswith('.xls'):
                        apps_df = pd.read_excel(applications_file, engine='xlrd', header=None)
                    else:
                        apps_df = pd.read_excel(applications_file, engine='openpyxl', header=None)
                    
                    # Extract categories and their chemicals
                    # Logic: After every empty row, first non-empty row is category name
                    # Subsequent rows until next empty row are chemicals
                    categories_dict = {}
                    current_category = None
                    prev_row_empty = True  # Start as if we just saw an empty row (for first category)
                    
                    for idx, row in apps_df.iterrows():
                        # Check if entire row is empty
                        row_is_empty = all(pd.isna(val) or str(val).strip() == '' for val in row)
                        
                        if row_is_empty:
                            prev_row_empty = True
                            continue
                        
                        first_col = row[0]
                        if pd.isna(first_col) or str(first_col).strip() == '':
                            continue
                        
                        first_col_str = str(first_col).strip()
                        
                        # Skip header row
                        if first_col_str.upper() in ['CHEMICAL_NAME', 'NAME', 'MOLECULE', 'SYNONYM', 'CAS_NO', 'MOLECULAR_FORMULA']:
                            prev_row_empty = False
                            continue
                        
                        # If previous row was empty, this is a category name
                        if prev_row_empty:
                            current_category = first_col_str
                            if current_category not in categories_dict:
                                categories_dict[current_category] = []
                            prev_row_empty = False
                        else:
                            # This is a chemical under current category
                            if current_category:
                                categories_dict[current_category].append(first_col_str)
                    
                    # Remove empty categories
                    categories_dict = {k: v for k, v in categories_dict.items() if v}
                    
                    if categories_dict:
                        st.success(f"✅ Found {len(categories_dict)} application categories")
                        
                        # Display found categories with counts in a scrollable container
                        st.write("**Detected Categories:**")
                        
                        # Create a summary view
                        category_summary = []
                        for cat, chemicals in categories_dict.items():
                            category_summary.append(f"• **{cat}**: {len(chemicals)} chemicals")
                        
                        st.markdown("\n".join(category_summary))
                        
                        # Predefined colors for different industry categories
                        category_color_mapping = {
                            'pharmaceutical': '#fbbf24',    # Yellow
                            'agrochemical': '#10b981',      # Green
                            'rubber': '#ec4899',            # Pink
                            'plastic': '#8b5cf6',           # Purple
                            'specialty': '#06b6d4',         # Cyan
                            'speciality': '#06b6d4',        # Cyan (alternative spelling)
                            'cosmetic': '#f97316',          # Orange
                            'veterinary': '#84cc16',        # Lime
                            'food': '#14b8a6',              # Teal
                            'intermediate': '#6366f1',      # Indigo
                            'colorant': '#ef4444',          # Red
                            'dye': '#d946ef',               # Fuchsia
                            'photochemical': '#0ea5e9',     # Sky blue
                        }
                        
                        # Assign colors to categories
                        default_colors = ['#10b981', '#fbbf24', '#ec4899', '#8b5cf6', '#06b6d4', 
                                        '#f97316', '#84cc16', '#14b8a6', '#6366f1', '#ef4444', '#d946ef', '#0ea5e9']
                        
                        category_colors = {}
                        color_idx = 0
                        
                        for cat in categories_dict.keys():
                            cat_lower = cat.lower()
                            color_assigned = False
                            
                            # Try to match with predefined colors
                            for keyword, color in category_color_mapping.items():
                                if keyword in cat_lower:
                                    category_colors[cat] = color
                                    color_assigned = True
                                    break
                            
                            # If no match, use default colors
                            if not color_assigned:
                                category_colors[cat] = default_colors[color_idx % len(default_colors)]
                                color_idx += 1
                        
                        if st.button("🔗 Create Value Chain with Categories"):
                            # Find target product nodes
                            target_products = [node for node in st.session_state.value_chain_nodes 
                                             if node['type'] == 'Target Product']
                            
                            if not target_products:
                                st.error("❌ No Target Product found! Please add a Target Product first.")
                            else:
                                target_node = target_products[0]
                                target_id = target_node['id']
                                
                                # Remove old group nodes and their edges
                                st.session_state.value_chain_nodes = [
                                    node for node in st.session_state.value_chain_nodes 
                                    if not node.get('is_group', False)
                                ]
                                st.session_state.value_chain_edges = [
                                    edge for edge in st.session_state.value_chain_edges
                                    if not any(node.get('is_group', False) 
                                             for node in st.session_state.value_chain_nodes 
                                             if node['id'] in [edge['from'], edge['to']])
                                ]
                                
                                # Create group nodes for each category
                                for category, chemicals in categories_dict.items():
                                    cat_id = f"group_{category.replace(' ', '_').replace('/', '_').lower()}"
                                    
                                    # Create label with count
                                    group_label = f"{category}\n({len(chemicals)} chemicals)"
                                    
                                    # Create tooltip with chemical names
                                    tooltip_chemicals = "\n".join(chemicals[:10])  # Show first 10
                                    if len(chemicals) > 10:
                                        tooltip_chemicals += f"\n... +{len(chemicals) - 10} more"
                                    
                                    # Create group node
                                    group_node = {
                                        'id': cat_id,
                                        'label': group_label,
                                        'type': 'Application Group',
                                        'color': category_colors[category],
                                        'size': 35,
                                        'font': {'size': 12, 'color': '#ffffff'},
                                        'is_group': True,
                                        'shape': 'box',
                                        'title': f"{category}:\n{tooltip_chemicals}"
                                    }
                                    st.session_state.value_chain_nodes.append(group_node)
                                    
                                    # Create edge from target to group
                                    new_edge = {
                                        'from': target_id,
                                        'to': cat_id,
                                        'width': 3,
                                        'color': category_colors[category],
                                        'dashes': False,
                                        'arrows': {'to': {'enabled': True, 'scaleFactor': 1.2}}
                                    }
                                    st.session_state.value_chain_edges.append(new_edge)
                                
                                st.success(f"✅ Created value chain with {len(categories_dict)} application categories connected to {target_node['label']}")
                                st.experimental_rerun()
                    else:
                        st.warning("⚠️ No categories found. Make sure your Excel follows the expected format.")
                        
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
                    st.info("💡 **Tip:** Make sure your Excel file has category names followed by chemical names, separated by empty rows")
        
        # Show detected categories details (outside expander)
        if 'categories_dict' in locals() and categories_dict:
            st.markdown("---")
            st.markdown("#### 📋 Category Details")
            
            # Allow users to select a category to view details
            selected_category = st.selectbox(
                "Select category to view chemicals:",
                options=list(categories_dict.keys()),
                key="category_detail_select"
            )
            
            if selected_category:
                chemicals = categories_dict[selected_category]
                st.write(f"**{selected_category}** ({len(chemicals)} chemicals):")
                
                # Show chemicals in a scrollable text area
                chemicals_text = "\n".join([f"{i+1}. {chem}" for i, chem in enumerate(chemicals)])
                st.text_area(
                    "Chemicals list:",
                    value=chemicals_text,
                    height=200,
                    key="chemicals_display"
                )
        
        # Edit existing nodes
        if st.session_state.value_chain_nodes:
            with st.expander("✏️ Edit Molecules"):
                # Filter out group nodes from editing
                editable_nodes = [node for node in st.session_state.value_chain_nodes 
                                 if not node.get('is_group', False)]
                
                if editable_nodes:
                    node_to_edit = st.selectbox(
                        "Select Node to Edit",
                        options=[node['label'] for node in editable_nodes],
                        key="edit_node_select"
                    )
                    
                    if node_to_edit:
                        # Find the node
                        node_idx = next(i for i, node in enumerate(st.session_state.value_chain_nodes) 
                                      if node['label'] == node_to_edit and not node.get('is_group', False))
                        current_node = st.session_state.value_chain_nodes[node_idx]
                        
                        # Edit fields
                        edited_name = st.text_input(
                            "Edit Name",
                            value=current_node['label'],
                            key=f"edit_name_{node_idx}"
                        )
                        
                        color_map = {
                            "Raw Material": "#3b82f6",
                            "Intermediate": "#f59e0b",
                            "Target Product": "#ef4444",
                            "By-Product": "#8b5cf6",
                        }
                        
                        edited_type = st.selectbox(
                            "Edit Type",
                            ["Raw Material", "Intermediate", "Target Product", "By-Product"],
                            index=["Raw Material", "Intermediate", "Target Product", "By-Product"].index(current_node['type']),
                            key=f"edit_type_{node_idx}"
                        )
                        
                        col_update, col_delete = st.columns(2)
                        with col_update:
                            if st.button("💾 Update", key=f"update_{node_idx}"):
                                st.session_state.value_chain_nodes[node_idx]['label'] = edited_name
                                st.session_state.value_chain_nodes[node_idx]['type'] = edited_type
                                st.session_state.value_chain_nodes[node_idx]['color'] = color_map[edited_type]
                                st.session_state.value_chain_nodes[node_idx]['size'] = 30 if edited_type == "Target Product" else 25
                                st.success("✅ Updated!")
                                st.experimental_rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Delete", key=f"delete_{node_idx}"):
                                # Remove node and its edges
                                node_id = current_node['id']
                                st.session_state.value_chain_nodes.pop(node_idx)
                                st.session_state.value_chain_edges = [
                                    edge for edge in st.session_state.value_chain_edges 
                                    if edge['from'] != node_id and edge['to'] != node_id
                                ]
                                st.success("✅ Deleted!")
                                st.experimental_rerun()
                else:
                    st.info("No editable molecules. Add molecules first.")
        
        # Add connections - simplified with only arrow direction
        if len([n for n in st.session_state.value_chain_nodes if not n.get('is_group', False)]) >= 2:
            with st.expander("🔗 Add Connections"):
                # Only show non-group nodes for manual connections
                connectable_nodes = [node['label'] for node in st.session_state.value_chain_nodes 
                                    if not node.get('is_group', False)]
                
                col_from, col_to = st.columns(2)
                
                with col_from:
                    from_molecule = st.selectbox(
                        "From (Upstream)",
                        options=connectable_nodes,
                        key="from_molecule"
                    )
                
                with col_to:
                    to_molecule = st.selectbox(
                        "To (Downstream)",
                        options=connectable_nodes,
                        key="to_molecule"
                    )
                
                if st.button("🔗 Add Connection"):
                    if from_molecule != to_molecule:
                        # Find node IDs
                        from_id = next(node['id'] for node in st.session_state.value_chain_nodes 
                                     if node['label'] == from_molecule and not node.get('is_group', False))
                        to_id = next(node['id'] for node in st.session_state.value_chain_nodes 
                                   if node['label'] == to_molecule and not node.get('is_group', False))
                        
                        # Check if edge already exists
                        edge_exists = any(
                            edge['from'] == from_id and edge['to'] == to_id
                            for edge in st.session_state.value_chain_edges
                        )
                        
                        if not edge_exists:
                            # Create simple arrow connection
                            new_edge = {
                                'from': from_id,
                                'to': to_id,
                                'width': 2,
                                'color': '#4ade80',
                                'dashes': False,
                                'arrows': {'to': {'enabled': True, 'scaleFactor': 1}}
                            }
                            st.session_state.value_chain_edges.append(new_edge)
                            st.success(f"✅ Connected {from_molecule} → {to_molecule}")
                            st.experimental_rerun()
                        else:
                            st.warning("⚠️ Connection already exists!")
                    else:
                        st.error("❌ Cannot connect a molecule to itself!")
        
        # Manage connections
        if st.session_state.value_chain_edges:
            with st.expander("🔧 Manage Connections"):
                for idx, edge in enumerate(st.session_state.value_chain_edges):
                    # Find node labels
                    from_node = next((node for node in st.session_state.value_chain_nodes 
                                    if node['id'] == edge['from']), None)
                    to_node = next((node for node in st.session_state.value_chain_nodes 
                                  if node['id'] == edge['to']), None)
                    
                    if from_node and to_node:
                        from_label = from_node['label']
                        to_label = to_node['label']
                        
                        col_edge, col_del = st.columns([3, 1])
                        with col_edge:
                            st.write(f"**{from_label}** → **{to_label}**")
                        with col_del:
                            if st.button("🗑️", key=f"del_edge_{idx}"):
                                st.session_state.value_chain_edges.pop(idx)
                                st.experimental_rerun()
        
        # Clear all
        st.markdown("---")
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.value_chain_nodes = []
            st.session_state.value_chain_edges = []
            st.session_state.node_counter = 0
            st.experimental_rerun()
    
    with col_viz:
        st.markdown("#### 🔬 Value Chain Visualization")
        
        if st.session_state.value_chain_nodes:
            # Create nodes and edges for agraph
            nodes = []
            edges = []
            
            for node in st.session_state.value_chain_nodes:
                nodes.append(Node(
                    id=node['id'],
                    label=node['label'],
                    size=node['size'],
                    color=node['color'],
                    font=node.get('font', {'size': 14, 'color': '#ffffff'}),
                    title=node.get('title', f"{node['label']} ({node['type']})"),
                    shape=node.get('shape', 'box'),
                    borderWidth=2,
                    borderWidthSelected=4,
                    chosen=True,
                    physics=True
                ))
            
            for edge in st.session_state.value_chain_edges:
                edges.append(Edge(
                    source=edge['from'],
                    target=edge['to'],
                    width=edge.get('width', 2),
                    color=edge.get('color', '#4ade80'),
                    dashes=edge.get('dashes', False),
                    arrows=edge.get('arrows', {'to': {'enabled': True}})
                ))
            
            # Configure the graph
            config = Config(
                width=800,
                height=600,
                directed=True,
                physics=True,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6",
                collapsible=False,
                node={'labelProperty': 'label'},
                link={'labelProperty': 'label', 'renderLabel': False},
                interaction={
                    'dragNodes': True,
                    'dragView': True,
                    'zoomView': True,
                    'hover': True,
                    'navigationButtons': True,
                    'keyboard': True
                },
                manipulation={
                    'enabled': False
                }
            )
            
            # Display the graph
            return_value = agraph(nodes=nodes, edges=edges, config=config)
            
            # Legend
            st.markdown("---")
            st.markdown("##### 🎨 Legend")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("🔵 **Raw Material**")
            with col2:
                st.markdown("🟠 **Intermediate**")
            with col3:
                st.markdown("🔴 **Target Product**")
            with col4:
                st.markdown("🟣 **By-Product**")
            
            # Show application category colors
            group_nodes = [node for node in st.session_state.value_chain_nodes if node.get('is_group', False)]
            if group_nodes:
                st.markdown("**Application Categories:**")
                
                # Create columns dynamically based on number of groups
                num_groups = len(group_nodes)
                cols_per_row = 3
                
                for i in range(0, num_groups, cols_per_row):
                    cols = st.columns(min(cols_per_row, num_groups - i))
                    for j, col in enumerate(cols):
                        if i + j < num_groups:
                            node = group_nodes[i + j]
                            category_name = node['label'].split('\n')[0]  # Get category name without count
                            with col:
                                st.markdown(f"<div style='background-color: {node['color']}; padding: 8px; border-radius: 5px; text-align: center; color: white; font-weight: bold; font-size: 0.85rem; margin: 2px;'>{category_name}</div>", unsafe_allow_html=True)
            
            # Statistics
            st.markdown("##### 📊 Statistics")
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            molecule_nodes = [n for n in st.session_state.value_chain_nodes if not n.get('is_group', False)]
            group_count = len(group_nodes)
            
            with col_stat1:
                st.metric("Molecules", len(molecule_nodes))
            with col_stat2:
                st.metric("Categories", group_count)
            with col_stat3:
                st.metric("Connections", len(st.session_state.value_chain_edges))
            with col_stat4:
                target_count = sum(1 for node in molecule_nodes if node.get('type') == "Target Product")
                st.metric("Target Products", target_count)
        else:
            st.info("👈 Start by adding molecules using the controls panel")
            
            # Sample value chain
            if st.button("📚 Load Sample Value Chain"):
                sample_nodes = [
                    {'id': 'node_0', 'label': 'Benzene', 'type': 'Raw Material', 'color': '#3b82f6', 'size': 25, 'font': {'size': 14, 'color': '#ffffff'}},
                    {'id': 'node_1', 'label': 'Nitrobenzene', 'type': 'Intermediate', 'color': '#f59e0b', 'size': 25, 'font': {'size': 14, 'color': '#ffffff'}},
                    {'id': 'node_2', 'label': 'Aniline', 'type': 'Target Product', 'color': '#ef4444', 'size': 30, 'font': {'size': 14, 'color': '#ffffff'}},
                ]
                
                sample_edges = [
                    {'from': 'node_0', 'to': 'node_1', 'width': 2, 'color': '#4ade80', 'dashes': False, 'arrows': {'to': {'enabled': True, 'scaleFactor': 1}}},
                    {'from': 'node_1', 'to': 'node_2', 'width': 2, 'color': '#4ade80', 'dashes': False, 'arrows': {'to': {'enabled': True, 'scaleFactor': 1}}},
                ]
                
                # Sample categories from your data
                sample_categories = {
                    'Pharmaceuticals': ['Isatin', 'Phenazopyridine', 'Salverine', 'Sufentanil'],
                    'Rubbers': ['N,N\'-Diphenylguanidine', 'N-Phenyl-1-naphthylamine'],
                    'Agrochemicals': ['Fenuron', 'Forchlorfenuron', 'Carbendazim']
                }
                
                sample_colors = {
                    'Pharmaceuticals': '#fbbf24',
                    'Rubbers': '#ec4899',
                    'Agrochemicals': '#10b981'
                }
                
                st.session_state.value_chain_nodes = sample_nodes
                st.session_state.value_chain_edges = sample_edges
                st.session_state.node_counter = 3
                
                # Create group nodes
                for cat, chemicals in sample_categories.items():
                    cat_id = f"group_{cat.lower()}"
                    group_label = f"{cat}\n({len(chemicals)} chemicals)"
                    
                    group_node = {
                        'id': cat_id,
                        'label': group_label,
                        'type': 'Application Group',
                        'color': sample_colors[cat],
                        'size': 35,
                        'font': {'size': 12, 'color': '#ffffff'},
                        'is_group': True,
                        'shape': 'box',
                        'title': f"{cat}:\n" + "\n".join(chemicals)
                    }
                    st.session_state.value_chain_nodes.append(group_node)
                    
                    # Connect to target product
                    new_edge = {
                        'from': 'node_2',
                        'to': cat_id,
                        'width': 3,
                        'color': sample_colors[cat],
                        'dashes': False,
                        'arrows': {'to': {'enabled': True, 'scaleFactor': 1.2}}
                    }
                    st.session_state.value_chain_edges.append(new_edge)
                
                st.experimental_rerun()

with tab4:
    st.markdown("""
    ### 📈 Analytics & Insights
    Analyze your cleaned datasets with comprehensive analytics and visualizations.
    """)
    
    
    # Check for saved datasets only for EXIM and Data Overview tabs
    datasets_available = bool(st.session_state.saved_datasets)
    


    if not st.session_state.saved_datasets:
        st.info("📊 No saved datasets available yet. Please process and save data in the **Data Processing** tab first.")
    else:
        st.success(f"✅ {len(st.session_state.saved_datasets)} dataset(s) available for analysis")
        
        # Create sub-tabs for different analytics views
        analytics_tab1, analytics_tab2 = st.tabs([
            "📊 EXIM Analysis", 
            "📈 Data Overview"
        ])
        
        with analytics_tab1:
            st.subheader("📊 EXIM Analysis Table")
            st.write("Comprehensive Import, Export, and Global trade analysis with financial year breakdowns")
            
            # Methodology info box
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(251, 146, 60, 0.15) 0%, rgba(249, 115, 22, 0.1) 100%); 
                        padding: 20px; border-radius: 12px; border-left: 5px solid #f97316; margin: 20px 0;'>
                <h4 style='color: #fb923c; margin: 0 0 10px 0; font-weight: 700;'>
                    📐 Methodology
                </h4>
                <ul style='color: #ffffff; margin: 0; font-weight: 600; line-height: 1.8;'>
                    <li><strong>Unit Filter:</strong> Only METRIC TON and KILOGRAMS rows are included</li>
                    <li><strong>Conversion:</strong> MT → kg (×1000) | Price/MT → Price/kg (÷1000)</li>
                    <li><strong>Formula:</strong> Price ($/kg) = Σ(qty_kg × price_$/kg) ÷ Σ(qty_kg)</li>
                    <li><strong>Financial Year:</strong> April to March cycle</li>
                    <li><strong>Display Format:</strong> Qty in MT (2 decimals) | Price in $/kg (1 decimal)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Helper function to determine financial year (April-March)
            def get_financial_year(date_val):
                """Convert date to financial year (April-March)"""
                try:
                    if pd.isna(date_val):
                        return None
                    
                    if isinstance(date_val, str):
                        date_obj = pd.to_datetime(date_val, dayfirst=True, errors='coerce')
                    else:
                        date_obj = pd.to_datetime(date_val)
                    
                    if pd.isna(date_obj):
                        return None
                    
                    year = date_obj.year
                    month = date_obj.month
                    
                    if month >= 4:  # April onwards
                        return f"FY {year}-{str(year+1)[2:]}"
                    else:  # Jan-March
                        return f"FY {year-1}-{str(year)[2:]}"
                except:
                    return None
            
            # Helper function to compute qty_kg and price_usd_per_kg for each row
            def compute_row_metrics(row, qty_col, unit_col, value_col):
                """
                Convert each row to qty_kg and price_usd_per_kg based on unit.
                Returns: (qty_kg, price_usd_per_kg) or (None, None) if invalid
                """
                try:
                    # Get values
                    qty = row[qty_col]
                    unit = row[unit_col]
                    unit_value_usd = row[value_col]
                    
                    # Validate
                    if pd.isna(qty) or pd.isna(unit) or pd.isna(unit_value_usd):
                        return None, None
                    
                    if qty <= 0 or unit_value_usd <= 0:
                        return None, None
                    
                    # Normalize unit string
                    unit_str = str(unit).strip().upper()
                    
                    # Process based on unit
                    if 'METRIC TON' in unit_str or unit_str == 'MTS' or unit_str == 'MT':
                        # Unit is METRIC TON
                        qty_kg = float(qty) * 1000  # 1 MT = 1000 kg
                        price_usd_per_kg = float(unit_value_usd) / 1000.0  # Convert $/MT to $/kg
                        return qty_kg, price_usd_per_kg
                    
                    elif 'KILOGRAM' in unit_str or unit_str == 'KGS' or unit_str == 'KG':
                        # Unit is KILOGRAMS
                        qty_kg = float(qty)
                        price_usd_per_kg = float(unit_value_usd)  # Already $/kg
                        return qty_kg, price_usd_per_kg
                    
                    else:
                        # Other units (GRAMS, NUMBER, etc.) - exclude
                        return None, None
                
                except:
                    return None, None
            
            # Process all saved datasets with CORRECT weighted average logic
            def process_exim_data():
                """
                Process all saved datasets and create EXIM analysis data.
                Uses ONLY METRIC TON and KILOGRAMS rows for weighted average price calculation.
                """
                exim_data = {
                    'Imports': [],
                    'Exports': [],
                    'Global': []
                }
                
                financial_years = [
                    "FY 2020-21", "FY 2021-22", "FY 2022-23", 
                    "FY 2023-24", "FY 2024-25", "FY 2025-26"
                ]
                
                # Track excluded rows for logging
                excluded_stats = {
                    'total': 0, 
                    'wrong_unit': 0, 
                    'missing_data': 0,
                    'by_dataset': {}
                }
                
                for dataset_name, dataset_info in st.session_state.saved_datasets.items():
                    data_type = dataset_info['type']
                    df = dataset_info['data'].copy()
                    
                    # Determine section
                    if data_type == 'Import':
                        section = 'Imports'
                    elif data_type == 'Export':
                        section = 'Exports'
                    else:
                        section = 'Global'
                    
                    # Check for required columns
                    if 'Standardized Name' not in df.columns:
                        st.warning(f"⚠️ Dataset '{dataset_name}' missing 'Standardized Name' column. Skipping.")
                        continue
                    
                    # Find required columns
                    date_col = None
                    for col in df.columns:
                        if 'date' in col.lower() or 'period' in col.lower():
                            date_col = col
                            break
                    
                    qty_col = None
                    for col in df.columns:
                        if 'quantity' in col.lower() or 'qty' in col.lower() or 'weight' in col.lower():
                            qty_col = col
                            break
                    
                    unit_col = None
                    for col in df.columns:
                        if 'unit' in col.lower() or 'uqc' in col.lower():
                            unit_col = col
                            break
                    
                    # Find Unit Value (USD) column - multiple possible names
                    value_col = None
                    for col in df.columns:
                        col_lower = col.lower()
                        if 'unit value' in col_lower and 'usd' in col_lower:
                            value_col = col
                            break
                        elif 'unit price' in col_lower or 'price' in col_lower:
                            value_col = col
                            break
                    
                    if not value_col:
                        # Fallback to any value/amount column
                        for col in df.columns:
                            col_lower = col.lower()
                            if 'value' in col_lower or 'amount' in col_lower or 'fob' in col_lower or 'cif' in col_lower:
                                value_col = col
                                break
                    
                    if not all([date_col, qty_col, unit_col, value_col]):
                        st.warning(f"⚠️ Dataset '{dataset_name}' missing required columns (Date, Quantity, Unit, Value). Skipping.")
                        st.info(f"Found: Date={date_col}, Qty={qty_col}, Unit={unit_col}, Value={value_col}")
                        continue
                    
                    # Add financial year column
                    df['FY'] = df[date_col].apply(get_financial_year)
                    
                    # Compute qty_kg and price_usd_per_kg for each row
                    metrics = df.apply(lambda row: compute_row_metrics(row, qty_col, unit_col, value_col), axis=1)
                    df['qty_kg'] = metrics.apply(lambda x: x[0] if x[0] is not None else None)
                    df['price_usd_per_kg'] = metrics.apply(lambda x: x[1] if x[1] is not None else None)
                    
                    # Count excluded rows
                    original_count = len(df)
                    
                    # Filter: Keep only rows with valid qty_kg and price_usd_per_kg
                    df_valid = df[df['qty_kg'].notna() & df['price_usd_per_kg'].notna()].copy()
                    
                    excluded_count = original_count - len(df_valid)
                    if excluded_count > 0:
                        excluded_stats['total'] += excluded_count
                        excluded_stats['by_dataset'][dataset_name] = {
                            'original': original_count,
                            'excluded': excluded_count,
                            'kept': len(df_valid),
                            'percentage_kept': (len(df_valid) / original_count * 100) if original_count > 0 else 0
                        }
                        st.info(f"ℹ️ Dataset '{dataset_name}': Excluded {excluded_count} rows (non MT/KG units or missing data) | Kept: {len(df_valid)} rows ({(len(df_valid)/original_count*100):.1f}%)")
                    
                    if len(df_valid) == 0:
                        st.warning(f"⚠️ Dataset '{dataset_name}': No valid rows after filtering. Skipping.")
                        continue
                    
                    # Get unique products
                    products = df_valid['Standardized Name'].unique()
                    
                    for product in products:
                        product_df = df_valid[df_valid['Standardized Name'] == product].copy()
                        
                        # Initialize row
                        row = {
                            'Product': f"{product} — [Dataset: {dataset_name}]",
                            'Product_Clean': product,
                            'Dataset': dataset_name,
                            'Relation to Product': st.session_state.product_relations.get(f"{product}_{dataset_name}", "Product")
                        }
                        
                        # Calculate metrics for each FY using WEIGHTED AVERAGE
                        for fy in financial_years:
                            fy_data = product_df[product_df['FY'] == fy].copy()
                            
                            if not fy_data.empty:
                                # Calculate weighted average price
                                # Formula: Σ(qty_kg × price_usd_per_kg) / Σ(qty_kg)
                                
                                total_qty_kg = fy_data['qty_kg'].sum()
                                
                                if total_qty_kg > 0:
                                    # Weighted average price calculation
                                    numerator = (fy_data['qty_kg'] * fy_data['price_usd_per_kg']).sum()
                                    denominator = total_qty_kg
                                    weighted_price_per_kg = numerator / denominator
                                    
                                    # Convert qty_kg to MT for display
                                    total_qty_mt = total_qty_kg / 1000.0
                                    
                                    # Store with proper rounding
                                    row[f'{fy}_Qty'] = round(total_qty_mt, 2)  # 2 decimal places for MT
                                    row[f'{fy}_Price'] = round(weighted_price_per_kg, 1)  # 1 decimal place for $/kg
                                    
                                    # Store raw values for tooltip/debugging
                                    row[f'{fy}_Numerator'] = numerator
                                    row[f'{fy}_Denominator'] = denominator
                                    row[f'{fy}_RowCount'] = len(fy_data)
                                else:
                                    row[f'{fy}_Qty'] = None
                                    row[f'{fy}_Price'] = None
                            else:
                                row[f'{fy}_Qty'] = None
                                row[f'{fy}_Price'] = None
                        
                        exim_data[section].append(row)
                
                # Display exclusion statistics with details
                if excluded_stats['total'] > 0:
                    st.markdown("---")
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 146, 60, 0.1) 100%); 
                                padding: 20px; border-radius: 12px; border-left: 5px solid #f59e0b; margin: 20px 0;'>
                        <h4 style='color: #fbbf24; margin: 0 0 10px 0; font-weight: 700;'>
                            ⚠️ Data Quality Report
                        </h4>
                        <p style='color: #ffffff; margin: 0 0 10px 0; font-weight: 600;'>
                            Some rows were excluded from analysis due to unsupported units or missing data.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_exc1, col_exc2 = st.columns(2)
                    with col_exc1:
                        st.metric("📊 Total Rows Excluded", f"{excluded_stats['total']:,}")
                    with col_exc2:
                        total_rows = sum(info['original'] for info in excluded_stats['by_dataset'].values())
                        kept_rows = sum(info['kept'] for info in excluded_stats['by_dataset'].values())
                        st.metric("✅ Total Rows Used", f"{kept_rows:,} ({(kept_rows/total_rows*100):.1f}%)")
                    
                    with st.expander("📋 View Detailed Exclusion Report by Dataset"):
                        exclusion_report = []
                        for ds_name, info in excluded_stats['by_dataset'].items():
                            exclusion_report.append({
                                'Dataset': ds_name,
                                'Original Rows': f"{info['original']:,}",
                                'Rows Used': f"{info['kept']:,}",
                                'Rows Excluded': f"{info['excluded']:,}",
                                'Success Rate': f"{info['percentage_kept']:.1f}%"
                            })
                        
                        if exclusion_report:
                            exc_df = pd.DataFrame(exclusion_report)
                            st.dataframe(exc_df, use_container_width=True)
                        
                        st.info("""
                        **Common reasons for exclusion:**
                        - Units other than METRIC TON or KILOGRAMS (e.g., GRAMS, NUMBER, PIECES)
                        - Missing Quantity or Unit Value (USD)
                        - Zero or negative values
                        - Invalid date formats
                        """)
                
                return exim_data
            
            # Process data with detailed logging
            st.markdown("---")
            st.markdown("### 🔄 Processing Status")
            
            with st.spinner("🔄 Processing EXIM data from all saved datasets..."):
                exim_data = process_exim_data()
            
            st.success("✅ Data processing complete!")
            
            # Add unit test / validation section
            st.markdown("---")
            st.markdown("### 🧪 Calculation Validation")
            
            with st.expander("📊 View Sample Calculation (Unit Test)"):
                st.markdown("""
                **Example Weighted Average Calculation:**
                
                Given data for "Aniline" in FY 2023-24 from 3 shipments:
                
                | Row | Quantity | Unit | Unit Value (USD) | qty_kg | price_usd_per_kg |
                |-----|----------|------|------------------|--------|------------------|
                | 1   | 500      | KILOGRAMS | $2.50/kg   | 500    | $2.50           |
                | 2   | 2        | METRIC TON | $2000/MT  | 2000   | $2.00           |
                | 3   | 1500     | KILOGRAMS | $3.00/kg   | 1500   | $3.00           |
                | 4*  | 50       | GRAMS     | $5.00/g    | ❌ EXCLUDED (wrong unit) | |
                
                *Row 4 is excluded because unit is GRAMS (not MT or KG)
                
                **Step-by-Step Calculation:**
                ```
                Step 1: Convert all to qty_kg and price_usd_per_kg
                  Row 1: qty_kg = 500, price = $2.50/kg
                  Row 2: qty_kg = 2×1000 = 2000, price = $2000/1000 = $2.00/kg
                  Row 3: qty_kg = 1500, price = $3.00/kg
                
                Step 2: Calculate weighted average
                  Numerator = Σ(qty_kg × price_usd_per_kg)
                            = (500 × 2.50) + (2000 × 2.00) + (1500 × 3.00)
                            = 1250 + 4000 + 4500
                            = 9750
                  
                  Denominator = Σ(qty_kg)
                              = 500 + 2000 + 1500
                              = 4000
                  
                  Weighted Avg Price = 9750 ÷ 4000 = 2.4375 $/kg
                
                Step 3: Round to 1 decimal
                  Price ($/kg) = 2.4 $/kg
                
                Step 4: Convert total quantity to MT
                  Total Qty (MT) = 4000 ÷ 1000 = 4.00 MT
                
                Final Display: Aniline | FY 2023-24 | 4.00 MT @ $2.4/kg
                ```
                
                **Verification:**
                - Total value = 9750 USD (numerator represents total USD spent on kg)
                - Total weight = 4000 kg = 4.00 MT
                - Average = $9750 / 4000 kg = $2.4375/kg ≈ $2.4/kg ✓
                
                **Key Points:**
                - ✅ Only METRIC TON and KILOGRAMS rows are used
                - ✅ MT rows: qty converted to kg (×1000), price converted to $/kg (÷1000)
                - ✅ KG rows: used directly
                - ✅ Price is weighted by quantity in kg
                - ✅ Final price rounded to 1 decimal place
                - ✅ Final quantity displayed in MT (2 decimal places)
                - ❌ Rows with other units (GRAMS, NUMBER, etc.) excluded
                """)
                
                # Add a visual diagram
                st.markdown("""
                **Visual Flow:**
                ```
                Raw Data → Filter Units → Convert to kg → Calculate Weighted Avg → Format Output
                   ↓           ↓              ↓                    ↓                 ↓
                Multiple    Keep only    All in kg &         Σ(qty×price)      Round & Display
                 rows       MT & KG      same unit           ─────────         MT (2 dec)
                                                              Σ(qty)          $/kg (1 dec)
                ```
                """)
            
            st.markdown("---")
            financial_years = [
                "FY 2020-21", "FY 2021-22", "FY 2022-23", 
                "FY 2023-24", "FY 2024-25", "FY 2025-26"
            ]
            
            relation_options = [
                "Product", "Downstream", "Raw Material (RM)", 
                "Completion Product", "N+1", "N+2", "N-1", "N-2"
            ]
            
            # Section colors
            section_colors = {
                'Imports': '#3b82f6',    # Blue
                'Exports': '#f59e0b',    # Amber
                'Global': '#10b981'      # Green
            }
            
            section_icons = {
                'Imports': '📥',
                'Exports': '📤',
                'Global': '🌍'
            }
            
            for section in ['Imports', 'Exports', 'Global']:
                # Section header with color
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, {section_colors[section]}22 0%, {section_colors[section]}11 100%); 
                            padding: 15px; border-radius: 10px; border-left: 5px solid {section_colors[section]}; margin: 20px 0;'>
                    <h3 style='color: {section_colors[section]}; margin: 0; font-weight: 700;'>
                        {section_icons[section]} {section}
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                if not exim_data[section]:
                    st.info(f"No {section.lower()} data available. Save datasets in Tab 1 to see analysis.")
                    continue
                
                # Create display dataframe
                display_data = []
                
                for idx, row in enumerate(exim_data[section]):
                    display_row = {
                        'Product': row['Product'],
                        'Relation': row['Relation to Product']
                    }
                    
                    # Add FY columns with better formatting
                    for fy in financial_years:
                        qty = row.get(f'{fy}_Qty')
                        price = row.get(f'{fy}_Price')
                        
                        # Format quantity
                        if qty is not None and qty > 0:
                            display_row[f'{fy}\nQty (MT)'] = f"{qty:,.2f}"
                        else:
                            display_row[f'{fy}\nQty (MT)'] = "—"
                        
                        # Format price with 1 decimal place
                        if price is not None and price > 0:
                            display_row[f'{fy}\nPrice ($/kg)'] = f"${price:.1f}"
                        else:
                            display_row[f'{fy}\nPrice ($/kg)'] = "—"
                    
                    display_data.append(display_row)
                
                # Create DataFrame
                if display_data:
                    df_display = pd.DataFrame(display_data)
                    
                    st.write(f"**Total Products: {len(display_data)}**")
                    
                    # Display styled table with tooltip information
                    st.dataframe(
                        df_display, 
                        use_container_width=True,
                        height=min(600, len(display_data) * 40 + 50)
                    )
                    
                    # Show calculation details in expander
                    with st.expander(f"🔍 View Calculation Details for {section}"):
                        st.write("**Weighted Average Price Calculation Details:**")
                        st.write("Formula: `Price ($/kg) = Σ(qty_kg × price_usd_per_kg) / Σ(qty_kg)`")
                        st.write("Only rows with units **METRIC TON** or **KILOGRAMS** are included.")
                        
                        # Show detailed breakdown for selected products
                        for idx, row_data in enumerate(exim_data[section][:5]):  # Show first 5 products
                            st.markdown(f"**{row_data['Product']}:**")
                            
                            detail_data = []
                            for fy in financial_years:
                                if row_data.get(f'{fy}_Qty'):
                                    numerator = row_data.get(f'{fy}_Numerator', 0)
                                    denominator = row_data.get(f'{fy}_Denominator', 0)
                                    row_count = row_data.get(f'{fy}_RowCount', 0)
                                    
                                    detail_data.append({
                                        'FY': fy,
                                        'Total Qty (kg)': f"{denominator:,.2f}",
                                        'Weighted Sum': f"{numerator:,.2f}",
                                        'Price ($/kg)': f"${row_data[f'{fy}_Price']:.1f}",
                                        'Rows Used': row_count
                                    })
                            
                            if detail_data:
                                detail_df = pd.DataFrame(detail_data)
                                st.dataframe(detail_df, use_container_width=True)
                            else:
                                st.write("No data available for this product")
                            
                            if idx < 4:  # Don't add separator after last item
                                st.markdown("---")
                    
                    # Edit Relations Section
                    with st.expander(f"✏️ Edit Product Relations for {section}"):
                        st.write("Update the relationship classification for each product:")
                        
                        # Create form for editing relations
                        for idx, row_data in enumerate(exim_data[section]):
                            product_key = f"{row_data['Product_Clean']}_{row_data['Dataset']}"
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{row_data['Product']}**")
                            with col2:
                                current_relation = st.session_state.product_relations.get(product_key, "Product")
                                new_relation = st.selectbox(
                                    "Relation",
                                    options=relation_options,
                                    index=relation_options.index(current_relation) if current_relation in relation_options else 0,
                                    key=f"relation_{section}_{idx}"
                                )
                                
                                # Update session state
                                st.session_state.product_relations[product_key] = new_relation
                        
                        if st.button(f"💾 Save Changes for {section}", key=f"save_relations_{section}"):
                            st.success(f"✅ Relations updated for {section}!")
                            st.experimental_rerun()
                    
                    # Summary statistics with enhanced visuals
                    st.markdown("---")
                    st.markdown("##### 📊 Summary Statistics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_products = len(display_data)
                        st.metric("Total Products", total_products)
                    with col2:
                        latest_fy = financial_years[-1]
                        # Calculate total quantity for products with valid data
                        total_qty = sum([
                            row.get(f'{latest_fy}_Qty', 0) 
                            for row in exim_data[section] 
                            if row.get(f'{latest_fy}_Qty') is not None
                        ])
                        st.metric(f"{latest_fy} Qty", f"{total_qty:,.2f} MT")
                    with col3:
                        # Calculate weighted average price for latest FY
                        valid_products = [
                            row for row in exim_data[section] 
                            if row.get(f'{latest_fy}_Price') is not None and row.get(f'{latest_fy}_Qty') is not None
                        ]
                        
                        if valid_products:
                            total_numerator = sum([
                                row.get(f'{latest_fy}_Numerator', 0) 
                                for row in valid_products
                            ])
                            total_denominator = sum([
                                row.get(f'{latest_fy}_Denominator', 0) 
                                for row in valid_products
                            ])
                            
                            if total_denominator > 0:
                                avg_price = total_numerator / total_denominator
                                st.metric(f"{latest_fy} Avg Price", f"${avg_price:.1f}/kg")
                            else:
                                st.metric(f"{latest_fy} Avg Price", "N/A")
                        else:
                            st.metric(f"{latest_fy} Avg Price", "N/A")
                    with col4:
                        # Total value in latest FY
                        if valid_products and total_denominator > 0:
                            total_value_usd = total_numerator  # This is already Σ(qty_kg × price_usd_per_kg)
                            st.metric(f"{latest_fy} Total Value", f"${total_value_usd/1000:,.1f}K")
                        else:
                            st.metric(f"{latest_fy} Total Value", "N/A")
                    
                    # Download section data with enhanced formatting
                    st.markdown("---")
                    st.markdown("##### 📥 Export Data")
                    
                    # Create export dataframe with numeric values
                    export_data = []
                    for row in exim_data[section]:
                        export_row = {
                            'Product': row['Product'],
                            'Relation to Product': row['Relation to Product']
                        }
                        for fy in financial_years:
                            qty = row.get(f'{fy}_Qty')
                            price = row.get(f'{fy}_Price')
                            
                            export_row[f'{fy} Qty (MT)'] = qty if qty is not None else ''
                            export_row[f'{fy} Price ($/kg)'] = price if price is not None else ''
                        export_data.append(export_row)
                    
                    df_export = pd.DataFrame(export_data)
                    
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_export.to_excel(writer, index=False, sheet_name=section)
                    output.seek(0)
                    
                    st.download_button(
                        label=f"📥 Download {section} Data",
                        data=output,
                        file_name=f"exim_{section.lower()}_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{section}"
                    )
                
                st.markdown("---")
            
            # Export all EXIM data with enhanced UI
            if any(exim_data.values()):
                st.markdown("---")
                st.markdown("""
                <div style='background: linear-gradient(90deg, #10b98122 0%, #3b82f611 100%); 
                            padding: 20px; border-radius: 12px; border: 2px solid #10b981; margin: 20px 0;'>
                    <h4 style='color: #10b981; margin: 0 0 10px 0; font-weight: 700;'>
                        📦 Export Complete EXIM Analysis
                    </h4>
                    <p style='color: #ffffff; margin: 0; font-weight: 600;'>
                        Download a comprehensive report with all Import, Export, and Global trade data in a single Excel file
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary of what will be exported
                col_summary1, col_summary2, col_summary3 = st.columns(3)
                with col_summary1:
                    st.metric("Imports Products", len(exim_data['Imports']))
                with col_summary2:
                    st.metric("Exports Products", len(exim_data['Exports']))
                with col_summary3:
                    st.metric("Global Products", len(exim_data['Global']))
                
                if st.button("📥 Download Complete EXIM Report", key="download_complete_exim", type="primary"):
                    with st.spinner("📦 Generating comprehensive EXIM report..."):
                        output_all = BytesIO()
                        with pd.ExcelWriter(output_all, engine='openpyxl') as writer:
                            for section in ['Imports', 'Exports', 'Global']:
                                if exim_data[section]:
                                    export_data = []
                                    for row in exim_data[section]:
                                        export_row = {
                                            'Product': row['Product'],
                                            'Relation to Product': row['Relation to Product']
                                        }
                                        for fy in financial_years:
                                            qty = row.get(f'{fy}_Qty')
                                            price = row.get(f'{fy}_Price')
                                            
                                            export_row[f'{fy} Qty (MT)'] = qty if qty is not None else ''
                                            export_row[f'{fy} Price ($/kg)'] = price if price is not None else ''
                                        export_data.append(export_row)
                                    
                                    df_section = pd.DataFrame(export_data)
                                    df_section.to_excel(writer, index=False, sheet_name=section)
                        
                        output_all.seek(0)
                        st.download_button(
                            label="📥 Click Here to Download Complete Report",
                            data=output_all,
                            file_name=f"complete_exim_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_complete_button",
                            type="primary"
                        )
                        st.success("✅ Report generated successfully!")
        with analytics_tab2:
            st.subheader("📊 Data Overview & Insights")
            st.write("Interactive visualizations with quarterly trends, geographic distribution, and supply chain mapping")
            
            # Dataset selection
            st.markdown("---")
            col_select1, col_select2, col_select3 = st.columns([2, 1, 1])
            
            with col_select1:
                selected_dataset = st.selectbox(
                    "📁 Select Dataset for Analysis:",
                    options=list(st.session_state.saved_datasets.keys()),
                    key="overview_dataset_select"
                )
            
            dataset_info = st.session_state.saved_datasets[selected_dataset]
            
            with col_select2:
                st.metric("Data Type", dataset_info['type'])
            with col_select3:
                st.metric("Total Rows", f"{dataset_info['rows']:,}")
            
            # Process dataset
            st.markdown("---")
            with st.spinner("🔄 Processing dataset for analytics..."):
                df_processed, error = process_dataset_for_analytics(dataset_info['data'])
            
            if error:
                st.error(f"❌ {error}")
                st.info("💡 Ensure your dataset has Date, Quantity, Unit, and Unit Value columns with MT/KG entries.")
            else:
                original_rows = len(dataset_info['data'])
                processed_rows = len(df_processed)
                excluded_rows = original_rows - processed_rows
                
                st.success(f"✅ Processed {processed_rows:,} rows ({excluded_rows:,} excluded - non MT/KG units)")
                
                # Add Financial Year column
                def get_fy_from_quarter(quarter):
                    """Extract FY from quarter string"""
                    if pd.isna(quarter):
                        return None
                    try:
                        return quarter.split()[0]
                    except:
                        return None
                
                df_processed['FY'] = df_processed['Quarter'].apply(get_fy_from_quarter)
                
                # Key metrics
                st.markdown("### 📊 Key Metrics")
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                total_volume = df_processed['Quantity_MT'].sum()
                avg_price = (df_processed['Quantity_MT'] * df_processed['Price_USD_per_kg']).sum() / total_volume
                unique_quarters = df_processed['Quarter'].nunique()
                
                with col_m1:
                    st.metric("Total Volume", f"{total_volume:,.2f} MT")
                with col_m2:
                    st.metric("Weighted Avg Price", f"${avg_price:.1f}/kg")
                with col_m3:
                    st.metric("Time Periods", f"{unique_quarters} Quarters")
                with col_m4:
                    if 'Standardized Name' in df_processed.columns:
                        st.metric("Unique Products", df_processed['Standardized Name'].nunique())
                    else:
                        st.metric("Data Points", f"{processed_rows:,}")
                
                # 1. Quarterly Volume & Price Analysis
                st.markdown("---")
                st.markdown("### 📈 Quarterly Volume & Price Analysis")
                
                # Group by quarter
                quarterly = df_processed.groupby('Quarter').agg({
                    'Quantity_MT': 'sum',
                    'Price_USD_per_kg': lambda x: (df_processed.loc[x.index, 'Quantity_MT'] * df_processed.loc[x.index, 'Price_USD_per_kg']).sum() / df_processed.loc[x.index, 'Quantity_MT'].sum()
                }).reset_index().sort_values('Quarter')
                
                # Create dual-axis chart
                fig_quarterly = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig_quarterly.add_trace(
                    go.Bar(
                        x=quarterly['Quarter'],
                        y=quarterly['Quantity_MT'],
                        name="Volume (MT)",
                        marker_color='#fb923c',
                        hovertemplate='<b>%{x}</b><br>Volume: %{y:.2f} MT<extra></extra>'
                    ),
                    secondary_y=False
                )
                
                fig_quarterly.add_trace(
                    go.Scatter(
                        x=quarterly['Quarter'],
                        y=quarterly['Price_USD_per_kg'],
                        name="Weighted Avg Price ($/kg)",
                        mode='lines+markers',
                        line=dict(color='#10b981', width=3),
                        marker=dict(size=10, color='#10b981'),
                        hovertemplate='<b>%{x}</b><br>Price: $%{y:.1f}/kg<extra></extra>'
                    ),
                    secondary_y=True
                )
                
                fig_quarterly.update_layout(
                    title="Quarterly Volume & Weighted Average Price",
                    hovermode='x unified',
                    height=500,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor='rgba(255,255,255,0.05)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', size=14)
                )
                
                fig_quarterly.update_xaxes(title_text="Quarter", tickangle=45, title_font=dict(size=14))
                fig_quarterly.update_yaxes(title_text="<b>Volume (MT)</b>", secondary_y=False, gridcolor='rgba(251, 146, 60, 0.2)', title_font=dict(size=14, color='#fb923c'))
                fig_quarterly.update_yaxes(title_text="<b>Price ($/kg)</b>", secondary_y=True, gridcolor='rgba(16, 185, 129, 0.2)', title_font=dict(size=14, color='#10b981'))
                
                st.plotly_chart(fig_quarterly, use_container_width=True)
                
                # 2. Geographic Distribution
                st.markdown("---")
                st.markdown("### 🌍 Geographic Distribution")
                
                country_col = df_processed.attrs.get('country_col')
                if country_col and country_col in df_processed.columns:
                    geo_data = df_processed.groupby(country_col).agg({
                        'Quantity_MT': 'sum',
                        'Price_USD_per_kg': lambda x: (df_processed.loc[x.index, 'Quantity_MT'] * df_processed.loc[x.index, 'Price_USD_per_kg']).sum() / df_processed.loc[x.index, 'Quantity_MT'].sum()
                    }).reset_index()
                    
                    geo_data.columns = ['Country', 'Volume_MT', 'Avg_Price']
                    
                    fig_geo = px.choropleth(
                        geo_data,
                        locations='Country',
                        locationmode='country names',
                        color='Volume_MT',
                        hover_name='Country',
                        hover_data={'Volume_MT': ':.2f', 'Avg_Price': ':.1f'},
                        color_continuous_scale=[[0, '#fff7ed'], [0.5, '#fb923c'], [1, '#ea580c']],
                        title="Volume Distribution by Country (MT)"
                    )
                    
                    fig_geo.update_layout(
                        height=500,
                        geo=dict(
                            showframe=False, 
                            showcoastlines=True, 
                            projection_type='natural earth',
                            bgcolor='rgba(0,0,0,0)',
                            lakecolor='rgba(10, 36, 99, 0.3)',
                            landcolor='rgba(255, 255, 255, 0.05)'
                        ),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#ffffff', size=14),
                        coloraxis_colorbar=dict(
                            title="Volume (MT)",
                            titlefont=dict(size=14),
                            tickfont=dict(size=12)
                        )
                    )
                    
                    st.plotly_chart(fig_geo, use_container_width=True)
                else:
                    st.info("No geographic data available in this dataset.")
                

                           
                                             
                



                # 3. Supply Chain Visualization
                st.markdown("---")
                st.markdown("### 🔗 Supply Chain Visualization")
                st.write("Interactive supply chain mapping showing flows between suppliers and buyers")
                
                # Financial year selector
                available_fys = sorted(df_processed['FY'].dropna().unique())
                
                if len(available_fys) > 0:
                    col_fy_select, col_fy_info = st.columns([1, 2])
                    
                    with col_fy_select:
                        selected_fy = st.selectbox(
                            "📅 Select Financial Year:",
                            options=available_fys,
                            key="fy_sankey_select"
                        )
                    
                    # Filter data for selected FY
                    fy_data = df_processed[df_processed['FY'] == selected_fy].copy()
                    
                    with col_fy_info:
                        st.write("")
                        st.write("")
                        st.info(f"📊 Showing data for **{selected_fy}** | {len(fy_data):,} transactions")
                    
                    # Determine data type and columns
                    data_type = dataset_info['type']
                    
                    # Find relevant columns based on data type
                    if data_type == 'Import':
                        source_label = 'Supplier'
                        target_label = 'Importer'
                        source_col_name = 'Supplier' if 'Supplier' in fy_data.columns else None
                        target_col_name = 'Importer' if 'Importer' in fy_data.columns else None
                        source_country_col = 'Country of Origin' if 'Country of Origin' in fy_data.columns else None
                        target_country_col = None
                        
                        # Fallback search if exact column names not found
                        if not source_col_name:
                            for col in fy_data.columns:
                                col_lower = col.lower()
                                if 'supplier' in col_lower and 'country' not in col_lower:
                                    source_col_name = col
                                    break
                        
                        if not target_col_name:
                            for col in fy_data.columns:
                                col_lower = col.lower()
                                if 'importer' in col_lower and 'country' not in col_lower:
                                    target_col_name = col
                                    break
                        
                    elif data_type == 'Export':
                        source_label = 'Exporter'
                        target_label = 'Foreign Buyer'
                        source_col_name = 'Exporter' if 'Exporter' in fy_data.columns else None
                        target_col_name = 'Foreign Buyer' if 'Foreign Buyer' in fy_data.columns else None
                        source_country_col = None
                        target_country_col = 'Country of Destination' if 'Country of Destination' in fy_data.columns else None
                        
                        # Fallback search if exact column names not found
                        if not source_col_name:
                            for col in fy_data.columns:
                                col_lower = col.lower()
                                if 'exporter' in col_lower and 'country' not in col_lower:
                                    source_col_name = col
                                    break
                        
                        if not target_col_name:
                            for col in fy_data.columns:
                                col_lower = col.lower()
                                if 'foreign' in col_lower and 'buyer' in col_lower and 'country' not in col_lower:
                                    target_col_name = col
                                    break
                        
                    else:  # Global
                        source_label = 'Supplier'
                        target_label = 'Buyer'
                        source_col_name = 'Supplier' if 'Supplier' in fy_data.columns else None
                        target_col_name = 'Buyer' if 'Buyer' in fy_data.columns else None
                        source_country_col = 'Supplier Country' if 'Supplier Country' in fy_data.columns else None
                        target_country_col = 'Buyer Country' if 'Buyer Country' in fy_data.columns else None
                        
                        # Fallback search if exact column names not found
                        if not source_col_name:
                            for col in fy_data.columns:
                                col_lower = col.lower()
                                if 'supplier' in col_lower and 'country' not in col_lower:
                                    source_col_name = col
                                    break
                        
                        if not target_col_name:
                            for col in fy_data.columns:
                                col_lower = col.lower()
                                if 'buyer' in col_lower and 'country' not in col_lower and 'foreign' not in col_lower:
                                    target_col_name = col
                                    break
                    
                    # Check if required columns exist
                    if source_col_name and target_col_name and source_col_name in fy_data.columns and target_col_name in fy_data.columns:
                        # Build Sankey data
                        nodes = []
                        node_dict = {}
                        links = []
                        
                        # Color palette
                        source_color = '#fb923c'  # Orange for suppliers/exporters
                        target_color = '#10b981'  # Green for buyers/importers
                        
                        # Get top entities for each side (limit to top 15 to avoid clutter)
                        top_sources = fy_data.groupby(source_col_name)['Quantity_MT'].sum().sort_values(ascending=False).head(15)
                        top_targets = fy_data.groupby(target_col_name)['Quantity_MT'].sum().sort_values(ascending=False).head(15)
                        
                        # Filter data to only top entities
                        filtered_data = fy_data[
                            (fy_data[source_col_name].isin(top_sources.index)) &
                            (fy_data[target_col_name].isin(top_targets.index))
                        ].copy()
                        
                        if len(filtered_data) > 0:
                            # Calculate aggregated data for each entity
                            agg_dict_source = {
                                'Quantity_MT': 'sum',
                                'Price_USD_per_kg': lambda x: (filtered_data.loc[x.index, 'Quantity_MT'] * x).sum() / filtered_data.loc[x.index, 'Quantity_MT'].sum()
                            }
                            if source_country_col and source_country_col in filtered_data.columns:
                                agg_dict_source[source_country_col] = 'first'
                            
                            source_data = filtered_data.groupby(source_col_name).agg(agg_dict_source).reset_index()
                            
                            agg_dict_target = {
                                'Quantity_MT': 'sum',
                                'Price_USD_per_kg': lambda x: (filtered_data.loc[x.index, 'Quantity_MT'] * x).sum() / filtered_data.loc[x.index, 'Quantity_MT'].sum()
                            }
                            if target_country_col and target_country_col in filtered_data.columns:
                                agg_dict_target[target_country_col] = 'first'
                            
                            target_data = filtered_data.groupby(target_col_name).agg(agg_dict_target).reset_index()
                            
                            # Build source nodes
                            for _, row in source_data.iterrows():
                                company = row[source_col_name]
                                volume = row['Quantity_MT']
                                price = row['Price_USD_per_kg']
                                country = row.get(source_country_col, 'N/A') if source_country_col and source_country_col in source_data.columns else 'N/A'
                                
                                node_key = f"SOURCE::{company}"
                                node_dict[node_key] = len(nodes)
                                
                                hover_text = f"<b>{company}</b><br>Country: {country}<br>Total Volume: {volume:.2f} MT<br>Avg Price: ${price:.2f}/kg"
                                nodes.append({
                                    'label': company,
                                    'color': source_color,
                                    'customdata': hover_text
                                })
                            
                            # Build target nodes
                            for _, row in target_data.iterrows():
                                company = row[target_col_name]
                                volume = row['Quantity_MT']
                                price = row['Price_USD_per_kg']
                                country = row.get(target_country_col, 'N/A') if target_country_col and target_country_col in target_data.columns else 'N/A'
                                
                                node_key = f"TARGET::{company}"
                                node_dict[node_key] = len(nodes)
                                
                                hover_text = f"<b>{company}</b><br>Country: {country}<br>Total Volume: {volume:.2f} MT<br>Avg Price: ${price:.2f}/kg"
                                nodes.append({
                                    'label': company,
                                    'color': target_color,
                                    'customdata': hover_text
                                })
                            
                            # Build links between sources and targets
                            flow_data = filtered_data.groupby([source_col_name, target_col_name])['Quantity_MT'].sum().reset_index()
                            
                            for _, row in flow_data.iterrows():
                                source_key = f"SOURCE::{row[source_col_name]}"
                                target_key = f"TARGET::{row[target_col_name]}"
                                
                                if source_key in node_dict and target_key in node_dict:
                                    links.append({
                                        'source': node_dict[source_key],
                                        'target': node_dict[target_key],
                                        'value': row['Quantity_MT'],
                                        'color': 'rgba(251, 146, 60, 0.25)'
                                    })
                            
                            # Create Sankey diagram
                            if len(links) > 0:
                                fig_sankey = go.Figure(data=[go.Sankey(
                                    arrangement='snap',
                                    node=dict(
                                        pad=20,
                                        thickness=20,
                                        line=dict(color='white', width=2),
                                        label=[node['label'] for node in nodes],
                                        color=[node['color'] for node in nodes],
                                        customdata=[node['customdata'] for node in nodes],
                                        hovertemplate='%{customdata}<extra></extra>'
                                    ),
                                    link=dict(
                                        source=[link['source'] for link in links],
                                        target=[link['target'] for link in links],
                                        value=[link['value'] for link in links],
                                        color=[link['color'] for link in links],
                                        hovertemplate='Flow: %{value:.2f} MT<extra></extra>'
                                    )
                                )])
                                
                                # Add column headers as annotations
                                fig_sankey.update_layout(
                                    title=f"Supply Chain Flow - {data_type} ({selected_fy})",
                                    font=dict(size=14, color='#ffffff', family='Poppins'),
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    height=700,
                                    annotations=[
                                        dict(
                                            x=0.05,
                                            y=1.05,
                                            xref='paper',
                                            yref='paper',
                                            text=f'<b>{source_label}</b>',
                                            showarrow=False,
                                            font=dict(size=18, color='#fb923c', family='Poppins')
                                        ),
                                        dict(
                                            x=0.95,
                                            y=1.05,
                                            xref='paper',
                                            yref='paper',
                                            text=f'<b>{target_label}</b>',
                                            showarrow=False,
                                            font=dict(size=18, color='#10b981', family='Poppins')
                                        )
                                    ]
                                )
                                
                                st.plotly_chart(fig_sankey, use_container_width=True)
                                
                                # Insights Summary Panel
                                st.markdown("---")
                                st.markdown("#### 📊 Supply Chain Insights")
                                
                                col_insight1, col_insight2, col_insight3, col_insight4 = st.columns(4)
                                
                                # Calculate insights
                                unique_sources = len(source_data)
                                unique_targets = len(target_data)
                                total_volume = filtered_data['Quantity_MT'].sum()
                                avg_price = (filtered_data['Quantity_MT'] * filtered_data['Price_USD_per_kg']).sum() / total_volume if total_volume > 0 else 0
                                
                                with col_insight1:
                                    st.markdown(f"""
                                    <div style='background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(249, 115, 22, 0.1)); 
                                                padding: 20px; border-radius: 12px; border: 2px solid #fb923c; text-align: center;'>
                                        <h3 style='color: #fb923c; margin: 0; font-size: 2rem;'>{unique_sources}</h3>
                                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>{source_label}s</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_insight2:
                                    st.markdown(f"""
                                    <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1)); 
                                                padding: 20px; border-radius: 12px; border: 2px solid #10b981; text-align: center;'>
                                        <h3 style='color: #10b981; margin: 0; font-size: 2rem;'>{unique_targets}</h3>
                                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>{target_label}s</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_insight3:
                                    st.markdown(f"""
                                    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(124, 58, 237, 0.1)); 
                                                padding: 20px; border-radius: 12px; border: 2px solid #8b5cf6; text-align: center;'>
                                        <h3 style='color: #8b5cf6; margin: 0; font-size: 2rem;'>{total_volume:.0f}</h3>
                                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>Total Volume (MT)</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_insight4:
                                    st.markdown(f"""
                                    <div style='background: linear-gradient(135deg, rgba(236, 72, 153, 0.2), rgba(219, 39, 119, 0.1)); 
                                                padding: 20px; border-radius: 12px; border: 2px solid #ec4899; text-align: center;'>
                                        <h3 style='color: #ec4899; margin: 0; font-size: 2rem;'>${avg_price:.2f}</h3>
                                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>Avg Price/kg</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Top Trading Pairs
                                st.markdown("---")
                                st.markdown("#### 🏆 Top 5 Trading Pairs")
                                
                                top_pairs = flow_data.sort_values('Quantity_MT', ascending=False).head(5)
                                
                                for idx, row in top_pairs.iterrows():
                                    col_pair, col_volume = st.columns([3, 1])
                                    
                                    with col_pair:
                                        st.markdown(f"""
                                        <div style='background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); 
                                                    padding: 15px; border-radius: 8px; border-left: 4px solid #fbbf24;'>
                                            <b style='color: #fb923c;'>{row[source_col_name]}</b> 
                                            <span style='color: #9ca3af;'>→</span> 
                                            <b style='color: #10b981;'>{row[target_col_name]}</b>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col_volume:
                                        st.markdown(f"""
                                        <div style='background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.1)); 
                                                    padding: 15px; border-radius: 8px; text-align: center;'>
                                            <b style='color: #fbbf24; font-size: 1.1rem;'>{row['Quantity_MT']:.2f} MT</b>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            else:
                                st.warning("⚠️ No valid flows found. Try selecting a different financial year.")
                        else:
                            st.warning("⚠️ Insufficient data after filtering to top entities.")
                    else:
                        st.warning("⚠️ Required columns for supply chain visualization not found in dataset.")
                        st.info(f"""
                        **Expected columns for {data_type} data:**
                        • {source_label}: {source_col_name if source_col_name else 'NOT FOUND'}
                        • {target_label}: {target_col_name if target_col_name else 'NOT FOUND'}
                        """)
                else:
                    st.info("No financial year data available. Ensure your dataset has valid date information.")
                
                # Download processed data
                st.markdown("---")
                st.markdown("### 📥 Export Processed Data")
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_processed.to_excel(writer, index=False, sheet_name='Processed Data')
                output.seek(0)
                
                st.download_button(
                    label="📥 Download Processed Analytics Data",
                    data=output,
                    file_name=f"analytics_{selected_dataset}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_analytics"
                )
        



with tab5:
    st.markdown("""
    ### 📊 Market Estimation For Last FY or Last Surveyed year
    Estimate total market demand for your target product based on downstream applications
    """)
    
    # Initialize session state for downstreams
    if 'downstreams' not in st.session_state:
        st.session_state.downstreams = []
    if 'downstream_counter' not in st.session_state:
        st.session_state.downstream_counter = 0
    
    # Helper function to parse numeric input (handle NA, blank, or valid numbers)
    def parse_numeric_input(value):
        """Convert input to float, treating NA/blank as 0"""
        if value is None or value == "" or str(value).strip().upper() == "NA":
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    # Section 1: Target Product Input
    st.markdown("---")
    st.markdown("#### 🎯 Target Product")
    
    target_product = st.text_input(
        "Enter Target Product Name",
        placeholder="e.g., Aniline, Benzene, etc.",
        key="target_product_input",
        help="The main product for which you want to estimate market demand"
    )
    
    if target_product:
        st.success(f"✅ Target Product: **{target_product}**")
        
        # Section 2: Downstream Applications
        st.markdown("---")
        st.markdown("#### 📦 Downstream Applications")
        st.write("Add downstream applications that consume your target product")
        
        # Add new downstream form
        with st.expander("➕ Add New Downstream Application", expanded=len(st.session_state.downstreams) == 0):
            col_name, col_category = st.columns([2, 1])
            
            with col_name:
                downstream_name = st.text_input(
                    "Downstream Product/Application Name",
                    placeholder="e.g., Paracetamol, Glyphosate, Rubber Antioxidant",
                    key="new_downstream_name"
                )
            
            with col_category:
                downstream_category = st.selectbox(
                    "Category",
                    options=["Pharma", "Agro", "Others"],
                    key="new_downstream_category"
                )
            
            # Manual entry inputs for all categories
            col_demand, col_norm = st.columns(2)
            
            with col_demand:
                demand_input = st.text_input(
                    "Demand (MT)",
                    placeholder="Enter demand or 'NA'",
                    key="demand_input",
                    help="Enter the demand for this downstream product in metric tons"
                )
            
            with col_norm:
                norm_input = st.text_input(
                    "Norm (MT per MT of Target Product)",
                    placeholder="e.g., 0.85 or 'NA'",
                    key="norm_input",
                    help="How many MT of target product needed per MT of downstream product"
                )
            
            # Add downstream button
            if st.button("➕ Add Downstream", key="add_downstream_btn"):
                if downstream_name:
                    # Parse inputs
                    demand = parse_numeric_input(demand_input)
                    norm = parse_numeric_input(norm_input)
                    
                    # Create downstream entry
                    new_downstream = {
                        'id': st.session_state.downstream_counter,
                        'name': downstream_name,
                        'category': downstream_category,
                        'demand_mt': demand,
                        'norm': norm,
                        'calculated_demand': demand * norm
                    }
                    
                    st.session_state.downstreams.append(new_downstream)
                    st.session_state.downstream_counter += 1
                    
                    st.success(f"✅ Added: {downstream_name} ({downstream_category})")
                    st.experimental_rerun()
                else:
                    st.error("⚠️ Please enter a downstream product name")
        
        # Display existing downstreams
        if st.session_state.downstreams:
            st.markdown("---")
            st.markdown("#### 📋 Added Downstreams")
            
            # Create display table
            display_data = []
            for ds in st.session_state.downstreams:
                display_data.append({
                    'Downstream Product': ds['name'],
                    'Category': ds['category'],
                    'Demand (MT)': f"{ds['demand_mt']:,.2f}" if ds['demand_mt'] > 0 else "NA",
                    'Norm (MT/MT)': f"{ds['norm']:.4f}" if ds['norm'] > 0 else "NA",
                    'Calculated Demand (MT)': f"{ds['calculated_demand']:,.2f}" if ds['calculated_demand'] > 0 else "NA"
                })
            
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True)
            
            # Management options
            col_manage1, col_manage2 = st.columns([3, 1])
            
            with col_manage1:
                selected_to_remove = st.selectbox(
                    "Select downstream to remove:",
                    options=["-- Select --"] + [ds['name'] for ds in st.session_state.downstreams],
                    key="remove_downstream_select"
                )
            
            with col_manage2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remove", key="remove_downstream_btn"):
                    if selected_to_remove != "-- Select --":
                        st.session_state.downstreams = [
                            ds for ds in st.session_state.downstreams 
                            if ds['name'] != selected_to_remove
                        ]
                        st.success(f"Removed: {selected_to_remove}")
                        st.experimental_rerun()
            
            # Calculate total market estimation
            st.markdown("---")
            st.markdown("#### 🎯 Market Estimation Calculation")
            
            if st.button("📊 Calculate Market Estimation", type="primary", use_container_width=True):
                st.markdown("---")
                st.markdown("### 📈 Results")
                
                # Category-wise breakdown
                pharma_demand = sum([ds['calculated_demand'] for ds in st.session_state.downstreams if ds['category'] == 'Pharma'])
                agro_demand = sum([ds['calculated_demand'] for ds in st.session_state.downstreams if ds['category'] == 'Agro'])
                others_demand = sum([ds['calculated_demand'] for ds in st.session_state.downstreams if ds['category'] == 'Others'])
                total_demand = pharma_demand + agro_demand + others_demand
                
                # Display breakdown by category
                st.markdown("##### 📊 Demand Breakdown by Category")
                
                col_cat1, col_cat2, col_cat3, col_cat4 = st.columns(4)
                
                with col_cat1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.1)); 
                                padding: 20px; border-radius: 12px; border: 2px solid #fbbf24; text-align: center;'>
                        <h3 style='color: #fbbf24; margin: 0; font-size: 1.8rem;'>{pharma_demand:,.2f}</h3>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>Pharma (MT)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_cat2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.1)); 
                                padding: 20px; border-radius: 12px; border: 2px solid #22c55e; text-align: center;'>
                        <h3 style='color: #22c55e; margin: 0; font-size: 1.8rem;'>{agro_demand:,.2f}</h3>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>Agro (MT)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_cat3:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(124, 58, 237, 0.1)); 
                                padding: 20px; border-radius: 12px; border: 2px solid #8b5cf6; text-align: center;'>
                        <h3 style='color: #8b5cf6; margin: 0; font-size: 1.8rem;'>{others_demand:,.2f}</h3>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 600;'>Others (MT)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_cat4:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(220, 38, 38, 0.15)); 
                                padding: 20px; border-radius: 12px; border: 3px solid #ef4444; text-align: center; 
                                box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);'>
                        <h3 style='color: #ef4444; margin: 0; font-size: 2rem; font-weight: 800;'>{total_demand:,.2f}</h3>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-weight: 700; text-transform: uppercase;'>TOTAL DEMAND (MT)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed breakdown per downstream
                st.markdown("---")
                st.markdown("##### 📋 Detailed Breakdown by Downstream")
                
                breakdown_data = []
                for ds in st.session_state.downstreams:
                    breakdown_data.append({
                        'Downstream Product': ds['name'],
                        'Category': ds['category'],
                        'Demand (MT)': ds['demand_mt'],
                        'Norm (MT/MT)': ds['norm'],
                        'Calculated Demand (MT)': ds['calculated_demand'],
                        'Contribution %': (ds['calculated_demand'] / total_demand * 100) if total_demand > 0 else 0
                    })
                
                df_breakdown = pd.DataFrame(breakdown_data)
                
                # Format the dataframe
                df_breakdown['Demand (MT)'] = df_breakdown['Demand (MT)'].apply(lambda x: f"{x:,.2f}" if x > 0 else "NA")
                df_breakdown['Norm (MT/MT)'] = df_breakdown['Norm (MT/MT)'].apply(lambda x: f"{x:.4f}" if x > 0 else "NA")
                df_breakdown['Calculated Demand (MT)'] = df_breakdown['Calculated Demand (MT)'].apply(lambda x: f"{x:,.2f}")
                df_breakdown['Contribution %'] = df_breakdown['Contribution %'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(df_breakdown, use_container_width=True)
                
                # Visual representation - Pie chart
                st.markdown("---")
                st.markdown("##### 🥧 Demand Distribution")
                
                if total_demand > 0:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=[ds['name'] for ds in st.session_state.downstreams],
                        values=[ds['calculated_demand'] for ds in st.session_state.downstreams],
                        hole=0.4,
                        marker=dict(
                            colors=['#fbbf24', '#22c55e', '#8b5cf6', '#ef4444', '#3b82f6', '#ec4899', '#14b8a6', '#f97316'],
                            line=dict(color='#ffffff', width=2)
                        ),
                        textposition='auto',
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Demand: %{value:,.2f} MT<br>Share: %{percent}<extra></extra>'
                    )])
                    
                    fig_pie.update_layout(
                        title=f"Market Distribution for {target_product}",
                        font=dict(size=14, color='#ffffff', family='Poppins'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=500,
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            bgcolor='rgba(255,255,255,0.05)',
                            bordercolor='rgba(251, 146, 60, 0.3)',
                            borderwidth=2
                        )
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Summary report
                st.markdown("---")
                st.markdown("##### 📄 Summary Report")
                
                summary_text = f"""
**Market Estimation Summary for {target_product}**

**Total Estimated Demand:** {total_demand:,.2f} MT

**Breakdown by Category:**
- Pharmaceuticals: {pharma_demand:,.2f} MT ({(pharma_demand/total_demand*100) if total_demand > 0 else 0:.1f}%)
- Agrochemicals: {agro_demand:,.2f} MT ({(agro_demand/total_demand*100) if total_demand > 0 else 0:.1f}%)
- Others: {others_demand:,.2f} MT ({(others_demand/total_demand*100) if total_demand > 0 else 0:.1f}%)

**Number of Downstream Applications:** {len(st.session_state.downstreams)}

**Top 3 Contributors:**
"""
                # Sort by calculated demand
                sorted_downstreams = sorted(st.session_state.downstreams, key=lambda x: x['calculated_demand'], reverse=True)
                for i, ds in enumerate(sorted_downstreams[:3], 1):
                    contribution_pct = (ds['calculated_demand'] / total_demand * 100) if total_demand > 0 else 0
                    summary_text += f"\n{i}. {ds['name']} ({ds['category']}): {ds['calculated_demand']:,.2f} MT ({contribution_pct:.1f}%)"
                
                st.markdown(summary_text)
                
                # Download options
                st.markdown("---")
                st.markdown("##### 📥 Export Results")
                
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    # Excel export
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Summary sheet
                        summary_df = pd.DataFrame({
                            'Target Product': [target_product],
                            'Total Demand (MT)': [total_demand],
                            'Pharma Demand (MT)': [pharma_demand],
                            'Agro Demand (MT)': [agro_demand],
                            'Others Demand (MT)': [others_demand],
                            'Number of Downstreams': [len(st.session_state.downstreams)]
                        })
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                        
                        # Detailed breakdown sheet
                        detail_df = pd.DataFrame(breakdown_data)
                        detail_df.to_excel(writer, sheet_name='Detailed Breakdown', index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=output,
                        file_name=f"market_estimation_{target_product.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col_dl2:
                    # Text report export
                    st.download_button(
                        label="📄 Download Text Summary",
                        data=summary_text,
                        file_name=f"market_summary_{target_product.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
        
        else:
            st.info("👆 Add downstream applications to begin market estimation")
    
    else:
        st.info("👆 Enter a target product name to begin")
    
    # Help section
    st.markdown("---")
    with st.expander("ℹ️ How to Use Market Estimation", expanded=False):
        st.markdown("""
        **Step-by-Step Guide:**
        
        1. **Enter Target Product:** Input the name of the product for which you want to estimate market demand
        
        2. **Add Downstream Applications:** For each downstream application that uses your target product:
           - Enter the downstream product/application name
           - Select category (Pharma/Agro/Others)
           - Enter demand in metric tons (MT)
           - Enter norm (consumption ratio): How many MT of target product are needed per MT of downstream product
        
        3. **Review Added Downstreams:** Check the table of added applications and remove any if needed
        
        4. **Calculate:** Click the "Calculate Market Estimation" button to see:
           - Total estimated demand for your target product
           - Category-wise breakdown (Pharma/Agro/Others)
           - Detailed contribution from each downstream
           - Visual distribution charts
           - Downloadable reports
        
        **Tips:**
        - Enter "NA" or leave blank for any missing information (treated as 0)
        - Norm values are typically between 0 and 2 (e.g., 0.85 means 0.85 MT of target needed per 1 MT of downstream)
        - You can add multiple downstreams in the same or different categories
        - The calculated demand = Downstream Demand × Norm
        
        **Example:**
        - Target Product: Aniline
        - Downstream: Paracetamol (Pharma)
          - Demand: 12,500 MT
          - Norm: 0.85 MT/MT
          - Calculated: 10,625 MT of Aniline needed
        """)

with tab6:
             st.subheader("🔬 Environmental Clearance Analysis")
             st.write("Search for environmental clearances related to chemical products using AI-powered research")
    
             # Create tabs within analytics_tab3
             ec_search_tab, advanced_analytics_tab = st.tabs(["🔍 EC Search", "📊 Advanced Analytics"])
    
             with ec_search_tab:
              st.markdown("""
              <div style='background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); 
               padding: 25px; border-radius: 12px; border: 2px solid rgba(34, 197, 94, 0.3); margin-bottom: 20px;'>
               <h4 style='color: #22c55e; margin-bottom: 15px;'>🌍 Environmental Clearance Document Search</h4>
               <p style='color: #ffffff; font-size: 0.95rem; line-height: 1.6; margin: 0;'>
              Search across PARIVESH, MoEFCC, and other Indian environmental databases for EC documents 
               mentioning specific chemical products or CAS numbers.
              </p>
             </div>
              """, unsafe_allow_html=True)
        
             # Input section
             col_input1, col_input2 = st.columns(2)
        
             with col_input1:
              product_name = st.text_input(
                "🧪 Product Name",
                placeholder="e.g., Tiafenacil, Aniline, etc.",
                help="Enter the chemical product name you want to search for"
             )
        
             with col_input2:
               cas_number = st.text_input(
                "🔢 CAS Number (Optional)",
                placeholder="e.g., 1228284-64-7",
                help="Enter CAS number for more precise results"
             )
        
             # Search button
             search_button = st.button("🔎 Search Environmental Clearances", type="primary", use_container_width=True)
        
             if search_button:
              if not product_name and not cas_number:
                st.error("⚠️ Please enter either a product name or CAS number to search.")
             else:
                with st.spinner("🔍 Searching environmental clearance databases... This may take 30-60 seconds."):
                    try:
                        # Perplexity API configuration
                        PERPLEXITY_API_KEY = "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"
                        
                        # Build search query
                        search_terms = []
                        if product_name:
                            search_terms.append(f'product name: "{product_name}"')
                        if cas_number:
                            search_terms.append(f'CAS number: "{cas_number}"')
                        
                        search_query = " OR ".join(search_terms)
                        
                        # Create the prompt for Perplexity
                        prompt = f"""You are an expert data extraction assistant specializing in environmental compliance research. Task: Find all publicly available environmental clearance (EC) documents on the internet that mention the given chemical product or CAS number. Apart from searching the whole internet for this also focus on government portals such as PARIVESH (https://parivesh.nic.in), MoEFCC's environmental clearance site (https://environmentclearance.nic.in), and other verified Indian state or national EC databases.

              Input parameters:
             - Product name: "{product_name if product_name else 'Not specified'}"
             - CAS number: "{cas_number if cas_number else 'Not specified'}"

             Instructions:
             1. Search the entire internet (including state and central EC repositories) for environmental clearances mentioning the above product name or CAS number.
             2. Extract results into a structured table with the following columns:
             - Company Name
             - Capacity (in MT or TPA)
             - Date of EC approval
             - Location (state/district)
             - Context (brief description or mention of the product within the EC)
             - EC Link (direct URL to EC PDF or project page)
             3. Ensure links are active and verifiable (prefer PARIVESH and MoEFCC sources).
             4. Output the results in Markdown table format.
             5. If no results are found, clearly state that and suggest alternative search terms or related chemicals.
             6. Keep the tone factual, structured, and research-oriented.

             Please provide a comprehensive search of all available EC databases."""

                        # Make API request to Perplexity
                        headers = {
                            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        payload = {
                            "model": "sonar",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a precise environmental compliance research assistant. Provide structured, factual data from verified government sources only."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.2,
                            "max_tokens": 4000,
                            "return_citations": True,
                            "search_domain_filter": ["parivesh.nic.in", "environmentclearance.nic.in"]
                        }
                        
                        response = requests.post(
                            "https://api.perplexity.ai/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Extract the response content
                            if 'choices' in result and len(result['choices']) > 0:
                                ec_results = result['choices'][0]['message']['content']
                                
                                # Display results
                                st.success("✅ Search completed successfully!")
                                
                                # Show search parameters
                                st.markdown("---")
                                st.markdown("### 📋 Search Parameters")
                                params_col1, params_col2 = st.columns(2)
                                with params_col1:
                                    st.info(f"**Product:** {product_name if product_name else 'N/A'}")
                                with params_col2:
                                    st.info(f"**CAS Number:** {cas_number if cas_number else 'N/A'}")
                                
                                # Display results
                                st.markdown("---")
                                st.markdown("### 📊 Environmental Clearance Results")
                                st.markdown(ec_results)
                                
                                # Show citations if available
                                if 'citations' in result and result['citations']:
                                    st.markdown("---")
                                    st.markdown("### 🔗 Sources")
                                    for idx, citation in enumerate(result['citations'], 1):
                                        st.markdown(f"{idx}. [{citation}]({citation})")
                                
                                # Download option
                                st.markdown("---")
                                st.download_button(
                                    label="📥 Download Results as Text",
                                    data=ec_results,
                                    file_name=f"EC_Search_{product_name.replace(' ', '_') if product_name else cas_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                                
                            else:
                                st.error("❌ No results returned from the API.")
                        
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                            st.error(f"Response: {response.text}")
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. The search is taking longer than expected. Please try again.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"🔴 Network Error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        
                    st.info("💡 **Pro Tip:** Keep saving your datasets in Tab 1 to build a comprehensive historical database for advanced analytics!")