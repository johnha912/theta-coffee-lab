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
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    
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
    
    # Check for low inventory
    low_inventory_count = len(inventory_df[inventory_df['Quantity'] <= st.session_state.alert_threshold])
    
    with col3:
        st.metric("Low Inventory Items", f"{low_inventory_count}")
    
    # Load products data
    products_df = pd.read_csv("data/products.csv")
    
    with col4:
        st.metric("Menu Items", f"{len(products_df)}")
        
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")

# Custom Navigation using page_link
st.subheader("Navigation")
st.write("Click on any of the links below to navigate to different sections of the application:")

# Create a container for navigation links with a nice layout
nav_container = st.container()
col1, col2, col3 = nav_container.columns(3)

with col1:
    st.page_link("app.py", label="🏠 Home", icon=None)
    st.page_link("pages/1_dashboard.py", label="📊 Dashboard", icon=None)
    
with col2:
    st.page_link("pages/2_order.py", label="🧾 Order", icon=None)
    st.page_link("pages/3_inventory.py", label="🗄️ Inventory", icon=None)
    
with col3:
    st.page_link("pages/4_product.py", label="☕️ Product", icon=None)
    st.page_link("pages/5_financial.py", label="💵 Financial", icon=None)
    st.page_link("pages/6_settings.py", label="⚙️ Settings", icon=None)

# Footer
st.markdown("---")
st.caption("© 2025 Theta Coffee Lab Management System")
