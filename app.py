import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils import initialize_session_state
from ui_utils import display_header, display_summary_metrics, display_styled_table
from data_init import initialize_data_files, generate_sample_data

# Initialize session state
initialize_session_state()

# Initialize data files if they don't exist
initialize_data_files()

# Page config
st.set_page_config(
    page_title="Theta Coffee Lab Management System",
    page_icon="☕",
    layout="wide"
)

# CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Display common header
display_header()

# Main title
st.title("Theta Coffee Lab Management System")

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Check if data files exist
data_files_exist = os.path.exists('data/sales.csv') and os.path.exists('data/inventory.csv') and os.path.exists('data/products.csv')

if not data_files_exist:
    st.warning("Some data files are missing. Please initialize data files.")
    if st.button("Initialize Data Files", use_container_width=True):
        initialize_data_files()
        st.success("Data files initialized successfully!")
        st.rerun()
    
    st.info("You can also generate sample data for testing purposes.")
    if st.button("Generate Sample Data", use_container_width=True):
        generate_sample_data()
        st.success("Sample data generated successfully!")
        st.rerun()
else:
    # Load data from CSV files
    sales_df = pd.read_csv('data/sales.csv') if os.path.exists('data/sales.csv') else pd.DataFrame()
    inventory_df = pd.read_csv('data/inventory.csv') if os.path.exists('data/inventory.csv') else pd.DataFrame()
    products_df = pd.read_csv('data/products.csv') if os.path.exists('data/products.csv') else pd.DataFrame()
    expenses_df = pd.read_csv('data/expenses.csv') if os.path.exists('data/expenses.csv') else pd.DataFrame()
    
    # Dashboard overview
    st.header("System Overview")
    
    # Metrics row
    metrics = {
        "Products": {
            "value": len(products_df) if not products_df.empty else 0,
            "help": "Total number of products in the system"
        },
        "Inventory Items": {
            "value": len(inventory_df['Name'].unique()) if not inventory_df.empty else 0,
            "help": "Number of unique inventory items"
        },
        "Orders Processed": {
            "value": len(sales_df['Order_ID'].unique()) if not sales_df.empty else 0,
            "help": "Total number of orders processed"
        },
        "Total Revenue": {
            "value": sales_df['Total'].sum() if not sales_df.empty else 0,
            "help": "Total revenue from all sales",
            "unit": "VND"
        }
    }
    display_summary_metrics(metrics)
    
    # Welcome message and system information
    st.markdown("""
    ## Welcome to Theta Coffee Lab Management System
    
    This system provides comprehensive tools for managing your cafe operations including:
    
    - Dashboard analytics for business monitoring
    - Order management for sales processing
    - Inventory tracking for stock management
    - Product and recipe design for menu development
    - Financial reporting for business insights
    - System settings for customization
    
    Navigate through the system using the sidebar menu.
    """)
    
    # Low stock alert
    if not inventory_df.empty:
        threshold = st.session_state.alert_threshold
        low_stock = inventory_df[inventory_df['Quantity'] <= threshold]
        
        if not low_stock.empty:
            st.warning(f"⚠️ {len(low_stock)} inventory items are below the alert threshold ({threshold})!")
            
            with st.expander("View Low Stock Items"):
                # Display latest entry for each item below threshold
                unique_items = []
                for item in low_stock['Name'].unique():
                    item_df = low_stock[low_stock['Name'] == item].sort_values('Date')
                    unique_items.append(item_df.iloc[-1])
                
                unique_low_stock = pd.DataFrame(unique_items)
                display_styled_table(unique_low_stock[['Name', 'Unit', 'Quantity']])
    
    # Quick links
    st.header("Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Manage Orders 🧾
        Process customer orders, track sales, and manage transactions.
        """)
        st.page_link("pages/2_order.py", label="Go to Order Management", icon="🧾")
    
    with col2:
        st.markdown("""
        ### Manage Inventory 📦
        Track stock levels, update inventory, and manage supplies.
        """)
        st.page_link("pages/3_inventory.py", label="Go to Inventory Management", icon="📦")
    
    with col3:
        st.markdown("""
        ### Financial Analysis 💰
        View financial reports, profit analysis, and expense tracking.
        """)
        st.page_link("pages/5_financial.py", label="Go to Financial Analysis", icon="💰")
    
    # System status
    st.header("System Status")
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown("**Current Time:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        st.markdown("**System Theme:** " + st.session_state.theme.capitalize())
        st.markdown("**Language:** " + ("English" if st.session_state.language == 'en' else "Vietnamese"))
    
    with status_col2:
        # Check data file creation dates
        if os.path.exists('data/sales.csv'):
            sales_modified = datetime.fromtimestamp(os.path.getmtime('data/sales.csv')).strftime("%Y-%m-%d %H:%M:%S")
            st.markdown("**Last Sales Update:** " + sales_modified)
        
        if os.path.exists('data/inventory.csv'):
            inventory_modified = datetime.fromtimestamp(os.path.getmtime('data/inventory.csv')).strftime("%Y-%m-%d %H:%M:%S")
            st.markdown("**Last Inventory Update:** " + inventory_modified)
        
        if os.path.exists('data/settings.json'):
            settings_modified = datetime.fromtimestamp(os.path.getmtime('data/settings.json')).strftime("%Y-%m-%d %H:%M:%S")
            st.markdown("**Last Settings Update:** " + settings_modified)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Theta Coffee Lab Management System v1.0.0</p>
    <p>© 2025 Theta Coffee Lab. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)