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

# Create feature table with icons using HTML
features_html = """
<table style="width:100%; border-collapse: collapse;">
    <tr style="background-color: #f2f2f2;">
        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Feature</th>
        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #ddd;">Description</th>
    </tr>
    <tr>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;"><b>📊 Sales Tracking</b></td>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;">Record and monitor all sales transactions with detailed order information</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
        <td style="padding: 12px; border-bottom: 1px solid #ddd;"><b>📦 Inventory Management</b></td>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;">Track stock levels, receive alerts for low inventory, and manage purchases</td>
    </tr>
    <tr>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;"><b>🍵 Recipe & Menu Development</b></td>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;">Create and modify product recipes with precise ingredient measurements and accurate cost calculations</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
        <td style="padding: 12px; border-bottom: 1px solid #ddd;"><b>💰 Financial Analytics</b></td>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;">Access detailed financial reports including revenue, costs, and profitability metrics</td>
    </tr>
    <tr>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;"><b>🗺️ Customer Location Analysis</b></td>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;">Visualize customer order locations on an interactive map using Google Plus Codes</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
        <td style="padding: 12px; border-bottom: 1px solid #ddd;"><b>🌓 Light/Dark Mode Support</b></td>
        <td style="padding: 12px; border-bottom: 1px solid #ddd;">Choose between light and dark mode interface based on your preference</td>
    </tr>
</table>
"""

st.markdown(features_html, unsafe_allow_html=True)

# Navigation guidance with interactive buttons
st.subheader("Navigation")
st.write("Use the sidebar or these buttons to navigate to different sections of the application:")

# Create three columns for the navigation buttons
col1, col2, col3 = st.columns(3)

# First row of buttons
with col1:
    st.markdown("""
    <a href="dashboard" target="_self" style="text-decoration: none;">
        <div style="background-color: #4CAF50; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            📊 Dashboard<br><small>View KPIs and metrics</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <a href="order" target="_self" style="text-decoration: none;">
        <div style="background-color: #2196F3; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            🛒 Order<br><small>Manage sales transactions</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <a href="inventory" target="_self" style="text-decoration: none;">
        <div style="background-color: #FF9800; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            📦 Inventory<br><small>Track stock levels</small>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Second row of buttons
with col1:
    st.markdown("""
    <a href="product" target="_self" style="text-decoration: none;">
        <div style="background-color: #9C27B0; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            🍵 Product<br><small>Create recipes</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <a href="financial" target="_self" style="text-decoration: none;">
        <div style="background-color: #E91E63; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            💰 Financial<br><small>Analyze finances</small>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <a href="map" target="_self" style="text-decoration: none;">
        <div style="background-color: #607D8B; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            🗺️ Map<br><small>View customer locations</small>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Third row with only settings button
col1, col2, col3 = st.columns(3)
with col2:
    st.markdown("""
    <a href="settings" target="_self" style="text-decoration: none;">
        <div style="background-color: #795548; color: white; padding: 12px 16px; border-radius: 5px; cursor: pointer; text-align: center; margin-bottom: 10px;">
            ⚙️ Settings<br><small>Configure preferences</small>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("© 2025 Theta Coffee Lab Management System")
