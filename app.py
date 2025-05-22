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

# Main page
st.title("Theta Coffee Lab Management System")

# Introduction message
st.write("""
Welcome to the Theta Coffee Lab Management System! This application helps you manage your cafe operations including sales tracking, inventory management, 
product recipes, and financial reporting.
""")

# Add a more detailed description
st.markdown("""
### System Features

Theta Coffee Lab Management System offers a comprehensive suite of tools to manage your café business efficiently:

- **Real-time Sales Tracking**: Record and monitor all sales transactions with detailed order information
- **Inventory Management**: Track stock levels, receive alerts for low inventory, and manage purchases
- **Recipe & Menu Development**: Create and modify product recipes with precise ingredient measurements and accurate cost calculations
- **Financial Analytics**: Access detailed financial reports including revenue, costs, and profitability metrics
- **Customer Location Analysis**: Visualize customer order locations on an interactive map using Google Plus Codes
- **Light/Dark Mode Support**: Choose between light and dark mode interface based on your preference
""")

# Add an image
st.image("generated-icon.png", width=150)

# Navigation guidance
st.subheader("Navigation")
st.write("""
Use the sidebar to navigate to different sections of the application:
1. **Dashboard** - View KPIs and performance metrics
2. **Order** - Enter new orders and track sales
3. **Inventory** - Manage your inventory and supplies
4. **Product** - Design product recipes and menu items
5. **Financial Report** - Access detailed financial analytics
6. **Map** - Visualize order locations and customer distribution
7. **Settings** - Configure application preferences
""")

# Footer
st.markdown("---")
st.caption("© 2025 Theta Coffee Lab Management System")
