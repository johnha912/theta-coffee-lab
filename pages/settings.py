import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("Settings")
st.subheader("Configure application preferences")

# Save settings function
def save_settings():
    st.session_state.currency = currency
    st.session_state.alert_threshold = alert_threshold
    st.session_state.default_time_filter = default_time_filter
    st.session_state.username = username
    st.success("Settings saved successfully!")

# Settings form
st.header("Application Settings")

col1, col2 = st.columns(2)

with col1:
    # Inventory alert threshold
    alert_threshold = st.number_input(
        "Inventory Alert Threshold",
        min_value=1.0,  # Ensure all numeric values are float
        value=float(st.session_state.alert_threshold),
        step=1.0,
        help="Set the minimum inventory level that will trigger alerts"
    )
    
    # Currency selection
    currency_options = ["VND", "USD"]
    currency = st.selectbox(
        "Currency",
        options=currency_options,
        index=currency_options.index(st.session_state.currency),
        help="Select the currency to display throughout the application"
    )

with col2:
    # Default time filter
    time_filter_options = ["Today", "Last 7 Days", "Last 30 Days"]
    default_time_filter = st.selectbox(
        "Default Time Filter",
        options=time_filter_options,
        index=time_filter_options.index(st.session_state.default_time_filter),
        help="Set the default time filter for reports and dashboard"
    )
    
    # Username
    username = st.text_input(
        "Username",
        value=st.session_state.username,
        help="Enter your name or username for the application"
    )

# Save settings button
st.button("Save Settings", on_click=save_settings)

# Data management
st.header("Data Management")

# Export data
with st.expander("Export Data"):
    st.write("Export your data to CSV files")
    
    if st.button("Export All Data"):
        # ZIP file creation would go here in a full implementation
        st.info("Data export functionality will be added in a future update")

# Import data
with st.expander("Import Data"):
    st.write("Import data from CSV files")
    
    st.file_uploader("Upload Sales Data (CSV)", type="csv", key="sales_upload")
    st.file_uploader("Upload Inventory Data (CSV)", type="csv", key="inventory_upload")
    st.file_uploader("Upload Products Data (CSV)", type="csv", key="products_upload")
    
    if st.button("Import Selected Files"):
        st.info("Data import functionality will be added in a future update")

# Reset application
with st.expander("Reset Application"):
    st.write("⚠️ Warning: This will reset all data and settings to default values")
    
    if st.button("Reset Application", key="reset_button"):
        # This would reset all data files and settings
        st.warning("Reset functionality will be added in a future update")

# About section
st.header("About")

st.markdown("""
### Cafe Management System
Version 1.0

This application helps you manage your cafe operations including:
- Sales tracking and order management
- Inventory management
- Product recipe design
- Financial reporting and analysis

For support or feedback, please contact the developer.
""")

# System information
st.subheader("System Information")

# Check data files
data_files = [
    "data/sales.csv",
    "data/inventory.csv",
    "data/products.csv",
    "data/product_recipe.csv",
    "data/operational_costs.csv",
    "data/inventory_transactions.csv"
]

file_status = []
for file in data_files:
    file_status.append({
        "File": file,
        "Status": "Available" if os.path.exists(file) else "Not Found"
    })

status_df = pd.DataFrame(file_status)
st.dataframe(status_df)
