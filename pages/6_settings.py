import streamlit as st
import pandas as pd
import os
import utils

# Khởi tạo session_state
utils.initialize_session_state()

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Navigation menu
def display_navigation():
    menu_container = st.container()
    with menu_container:
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        with col2:
            nav_cols = st.columns(7)
            with nav_cols[0]:
                st.page_link("app.py", label="🏠", help="Home")
            with nav_cols[1]:
                st.page_link("pages/1_dashboard.py", label="📊", help="Dashboard")
            with nav_cols[2]:
                st.page_link("pages/2_order.py", label="🧾", help="Order")
            with nav_cols[3]:
                st.page_link("pages/3_inventory.py", label="🗄️", help="Inventory")
            with nav_cols[4]:
                st.page_link("pages/4_product.py", label="☕️", help="Product")
            with nav_cols[5]:
                st.page_link("pages/5_financial.py", label="💵", help="Financial")
            with nav_cols[6]:
                st.page_link("pages/6_settings.py", label="⚙️", help="Settings")
        with col3:
            st.write(f"👤 User: {st.session_state.username}")

display_navigation()
st.divider()

st.title("Settings")
st.subheader("Configure application preferences")

# Function to toggle theme
def toggle_theme():
    # Toggle the theme between light and dark
    current_theme = st.session_state.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    
    # Update the theme in session state
    st.session_state.theme = new_theme
    
    # Update config.toml file with new theme
    theme_config = {
        'light': {
            'primaryColor': "#FF4B4B",
            'backgroundColor': "#FFFFFF",
            'secondaryBackgroundColor': "#F0F2F6",
            'textColor': "#262730"
        },
        'dark': {
            'primaryColor': "#FF4B4B",
            'backgroundColor': "#0E1117",
            'secondaryBackgroundColor': "#262730",
            'textColor': "#FAFAFA"
        }
    }
    
    # Get the current theme configuration
    selected_theme = theme_config[new_theme]
    
    # Update config.toml
    with open('.streamlit/config.toml', 'r') as file:
        config_content = file.read()
    
    # Replace theme section
    import re
    theme_section = f"""[theme]
primaryColor = "{selected_theme['primaryColor']}"
backgroundColor = "{selected_theme['backgroundColor']}"
secondaryBackgroundColor = "{selected_theme['secondaryBackgroundColor']}"
textColor = "{selected_theme['textColor']}"
font = "sans serif"
"""
    
    # Check if theme section exists and replace it
    if '[theme]' in config_content:
        pattern = r'\[theme\].*?(?=\[|\Z)'
        config_content = re.sub(pattern, theme_section, config_content, flags=re.DOTALL)
    else:
        # Add theme section if it doesn't exist
        config_content += "\n" + theme_section
    
    # Write updated config back to file
    with open('.streamlit/config.toml', 'w') as file:
        file.write(config_content)
    
    st.success(f"Theme changed to {new_theme.capitalize()} Mode! Restarting app...")
    st.rerun()  # Rerun to apply theme changes

# Save settings function
def save_settings():
    st.session_state.currency = currency
    st.session_state.alert_threshold = alert_threshold
    st.session_state.default_time_filter = default_time_filter
    st.session_state.username = username
    st.session_state.theme = theme_mode
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
    
    # Theme Mode selection
    theme_options = ["light", "dark"]
    current_theme = st.session_state.get('theme', 'light')
    theme_mode = st.selectbox(
        "Theme Mode",
        options=theme_options,
        index=theme_options.index(current_theme),
        help="Choose between Light and Dark mode for the application"
    )

# Save settings button
col1, col2 = st.columns(2)
with col1:
    st.button("Save Settings", on_click=save_settings)
with col2:
    st.button("Toggle Theme Now", on_click=toggle_theme, help="Immediately switch between light and dark mode")

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
### Theta Coffee Lab Management System
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
