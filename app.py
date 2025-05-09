import streamlit as st
import pandas as pd
import os
import utils
from data_init import initialize_data_files

# Set page configuration
st.set_page_config(
    page_title="Theta Coffee Lab Management System",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
utils.initialize_session_state()

# Set additional application-specific session state variables
if 'default_time_filter' not in st.session_state:
    st.session_state.default_time_filter = "Today"
if 'username' not in st.session_state:
    st.session_state.username = "Admin"
if 'alert_threshold' not in st.session_state:
    st.session_state.alert_threshold = 5.0  # Ngưỡng cảnh báo tồn kho thấp mặc định

# Initialize data files if they don't exist
initialize_data_files()

# Main page - redirects to dashboard
st.title("Theta Coffee Lab Management System")

# Introduction message
st.write("""
Welcome to the Theta Coffee Lab Management System! This application helps you manage your cafe operations 
including sales tracking, inventory management, product recipes, and financial reporting.
""")

# Quick stats in the main page
st.header("Quick Overview")

col1, col2, col3, col4 = st.columns(4)

try:
    # Load sales data
    sales_df = pd.read_csv("data/sales.csv")
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
    
    # Filter for today's data
    today = pd.Timestamp.now().date()
    today_sales = sales_df[sales_df['Date'].dt.date == today]
    
    # Calculate KPIs
    total_revenue = today_sales['Total'].sum()
    order_count = len(today_sales['Order_ID'].unique())
    
    with col1:
        st.metric("Today's Revenue", utils.format_currency(total_revenue))
    
    with col2:
        st.metric("Today's Orders", f"{order_count}")
    
    # Load inventory data
    inventory_df = pd.read_csv("data/inventory.csv")
    
    # Check for low inventory using intelligent thresholds
    # Define thresholds by unit type
    thresholds = {
        'ml': 300.0,  # For liquid ingredients (more than 3 coffee drinks)
        'g': 100.0,   # For dry ingredients
        'pcs': st.session_state.alert_threshold  # Use general threshold for pieces
    }
    
    # Count low inventory items using smart thresholds
    low_inventory_count = 0
    for idx, row in inventory_df.iterrows():
        unit_type = row['Unit'].lower()
        # Convert units to base units
        if unit_type == 'l':
            unit_type = 'ml'
            threshold = thresholds['ml'] * 1000  # Convert to ml
        elif unit_type == 'kg':
            unit_type = 'g'
            threshold = thresholds['g'] * 1000  # Convert to g
        else:
            # Handle standard units
            threshold = thresholds.get(unit_type, st.session_state.alert_threshold)
        
        # Check if below threshold
        if row['Quantity'] <= threshold:
            low_inventory_count += 1
    
    with col3:
        st.metric("Low Inventory Items", f"{low_inventory_count}")
    
    # Load products data
    products_df = pd.read_csv("data/products.csv")
    
    with col4:
        st.metric("Menu Items", f"{len(products_df)}")
        
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")

# Navigation guidance
st.subheader("Navigation")
st.write("""
Use the sidebar to navigate to different sections of the application:
1. **Dashboard** - View KPIs and performance metrics
2. **Order** - Enter new orders and track sales
3. **Inventory** - Manage your inventory and supplies
4. **Product** - Design product recipes and menu items
5. **Financial Report** - Access detailed financial analytics
6. **Settings** - Configure application preferences
""")

# Footer
st.markdown("---")
st.caption("© 2025 Theta Coffee Lab Management System")
