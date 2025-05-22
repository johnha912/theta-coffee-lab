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

# Add a more detailed description in a table format
st.subheader("System Features")
st.write("Theta Coffee Lab Management System offers a comprehensive suite of tools to manage your café business efficiently:")

# Create feature table that adapts to light/dark theme
features_html = """
<style>
    .features-table {
        width: 100%;
        border-collapse: collapse;
    }
    .features-table th, .features-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid var(--text-color, #ddd);
    }
    .features-table tr:nth-child(even) {
        background-color: var(--background-color, transparent);
    }
    /* Dark mode will be handled by Streamlit's theme */
</style>

<table class="features-table">
    <tr>
        <th>Feature</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><b>📊 Sales Tracking</b></td>
        <td>Record and monitor all sales transactions with detailed order information</td>
    </tr>
    <tr>
        <td><b>📦 Inventory Management</b></td>
        <td>Track stock levels, receive alerts for low inventory, and manage purchases</td>
    </tr>
    <tr>
        <td><b>🍵 Recipe & Menu Development</b></td>
        <td>Create and modify product recipes with precise ingredient measurements and accurate cost calculations</td>
    </tr>
    <tr>
        <td><b>💰 Financial Analytics</b></td>
        <td>Access detailed financial reports including revenue, costs, and profitability metrics</td>
    </tr>
    <tr>
        <td><b>🗺️ Customer Location Analysis</b></td>
        <td>Visualize customer order locations on an interactive map using Google Plus Codes</td>
    </tr>
    <tr>
        <td><b>⚙️ Application Settings</b></td>
        <td>Configure application preferences including light/dark mode display options</td>
    </tr>
</table>
"""

st.markdown(features_html, unsafe_allow_html=True)

# Navigation guidance with interactive buttons
st.subheader("Navigation")
st.write("Use the sidebar or these buttons to navigate to different sections of the application:")

# CSS for nav buttons that respect light/dark theme
st.markdown("""
<style>
    .nav-button {
        background-color: #424242; 
        color: white; 
        padding: 12px 16px; 
        border-radius: 5px; 
        cursor: pointer; 
        text-align: center; 
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .nav-button:hover {
        background-color: #212121;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Create three columns for the navigation buttons
col1, col2, col3 = st.columns(3)

# First row of buttons
with col1:
    st.markdown("""
    <a href="dashboard" target="_self" style="text-decoration: none;">
        <div class="nav-button">
            📊 Dashboard<br><small>View KPIs and metrics</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <a href="order" target="_self" style="text-decoration: none;">
        <div class="nav-button">
            🛒 Order<br><small>Manage sales transactions</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <a href="inventory" target="_self" style="text-decoration: none;">
        <div class="nav-button">
            📦 Inventory<br><small>Track stock levels</small>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Second row of buttons
with col1:
    st.markdown("""
    <a href="product" target="_self" style="text-decoration: none;">
        <div class="nav-button">
            🍵 Product<br><small>Create recipes</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <a href="financial" target="_self" style="text-decoration: none;">
        <div class="nav-button">
            💰 Financial<br><small>Analyze finances</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <a href="map" target="_self" style="text-decoration: none;">
        <div class="nav-button">
            🗺️ Map<br><small>View customer locations</small>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Removed settings button as requested

# Footer
st.markdown("---")
st.caption("© 2025 Theta Coffee Lab Management System")
