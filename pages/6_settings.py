import streamlit as st
import base64
import json
import os
from datetime import datetime
from utils import initialize_session_state, ensure_data_dir
from ui_utils import display_header

# Initialize session state
initialize_session_state()

# Page config
st.set_page_config(
    page_title="Settings - Theta Coffee Lab",
    page_icon="⚙️",
    layout="wide"
)

# Display common header
display_header()

# Main title
st.title("System Settings")

# Toggle theme function
def toggle_theme():
    """Toggle between light and dark theme"""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'

# Save settings function
def save_settings():
    """Save settings to a file"""
    settings = {
        'theme': st.session_state.theme,
        'language': st.session_state.language,
        'alert_threshold': st.session_state.alert_threshold,
        'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Ensure data directory exists
    ensure_data_dir()
    
    # Save to JSON file
    with open('data/settings.json', 'w') as f:
        json.dump(settings, f)
    
    return True

# Load settings function
def load_settings():
    """Load settings from file"""
    if os.path.exists('data/settings.json'):
        try:
            with open('data/settings.json', 'r') as f:
                settings = json.load(f)
            
            # Update session state
            if 'theme' in settings:
                st.session_state.theme = settings['theme']
            
            if 'language' in settings:
                st.session_state.language = settings['language']
            
            if 'alert_threshold' in settings:
                st.session_state.alert_threshold = settings['alert_threshold']
            
            return True
        except Exception as e:
            st.error(f"Error loading settings: {e}")
    
    return False

# Load settings on page load
load_settings()

# Create tabs for different settings categories
tabs = st.tabs(["General", "Appearance", "About"])

# General settings tab
with tabs[0]:
    st.subheader("General Settings")
    
    # Inventory alert threshold
    st.number_input(
        "Inventory Alert Threshold",
        min_value=1,
        max_value=1000,
        value=st.session_state.alert_threshold,
        step=1,
        help="When inventory items go below this quantity, they will be highlighted in the dashboard.",
        key="alert_threshold_input",
        on_change=lambda: setattr(st.session_state, 'alert_threshold', st.session_state.alert_threshold_input)
    )
    
    # Language setting
    st.selectbox(
        "Language",
        ["English", "Vietnamese"],
        index=0 if st.session_state.language == 'en' else 1,
        key="language_select",
        on_change=lambda: setattr(st.session_state, 'language', 'en' if st.session_state.language_select == 'English' else 'vi')
    )
    
    # Save button
    if st.button("Save Settings", use_container_width=True):
        if save_settings():
            st.success("Settings saved successfully!")

# Appearance settings tab
with tabs[1]:
    st.subheader("Appearance Settings")
    
    # Theme selection
    st.radio(
        "Theme",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == 'light' else 1,
        horizontal=True,
        key="theme_select",
        on_change=lambda: setattr(st.session_state, 'theme', 'light' if st.session_state.theme_select == 'Light' else 'dark')
    )
    
    # Preview of selected theme
    theme_preview = """
    <div style="padding: 20px; border-radius: 10px; margin-top: 20px; 
                background-color: {bg}; color: {text};">
        <h3 style="color: {text};">Theme Preview</h3>
        <p>This is how your theme will look like.</p>
        <div style="background-color: {card}; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: {text};">Card Example</h4>
            <p style="color: {text};">Content inside a card.</p>
            <button style="background-color: {button}; color: white; border: none; padding: 8px 16px; 
                         border-radius: 4px; cursor: pointer;">
                Button Example
            </button>
        </div>
    </div>
    """
    
    if st.session_state.theme == 'light':
        theme_html = theme_preview.format(
            bg="#F5F5F5",
            text="#5D4037",
            card="#FFFFFF",
            button="#795548"
        )
    else:
        theme_html = theme_preview.format(
            bg="#212121",
            text="#E0E0E0",
            card="#333333",
            button="#795548"
        )
    
    st.markdown(theme_html, unsafe_allow_html=True)
    
    # Apply theme button
    if st.button("Apply Theme", use_container_width=True):
        if save_settings():
            st.success("Theme applied successfully! Please refresh the page to see the changes.")

# About tab
with tabs[2]:
    st.subheader("About Theta Coffee Lab Management System")
    
    st.markdown("""
    ### Version 1.0.0
    
    A comprehensive cafe management system built for Theta Coffee Lab, providing integrated solutions for:
    
    - Sales tracking and analytics
    - Inventory management
    - Product and recipe design
    - Financial reporting and analysis
    - Order management
    
    #### Technologies Used
    - Streamlit
    - Pandas
    - Plotly
    
    #### Created By
    Replit Developer
    
    #### Copyright © 2025 Theta Coffee Lab
    All rights reserved.
    """)
    
    # System info
    st.subheader("System Information")
    st.text(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if os.path.exists('data/settings.json'):
        try:
            with open('data/settings.json', 'r') as f:
                settings = json.load(f)
                if 'last_update' in settings:
                    st.text(f"Settings Last Updated: {settings['last_update']}")
        except:
            pass
    
    # Data files info
    st.subheader("Data Files")
    data_files = [
        "sales.csv",
        "inventory.csv",
        "products.csv",
        "product_recipe.csv",
        "expenses.csv",
        "settings.json"
    ]
    
    for file in data_files:
        file_path = os.path.join("data", file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            st.text(f"{file}: {size} bytes, Last modified: {modified}")
        else:
            st.text(f"{file}: Not found")
    
    # Initialize data button
    with st.expander("Initialize System Data"):
        st.warning("Caution: This will create empty data files if they don't exist. It will not overwrite existing data.")
        if st.button("Initialize Data Files", use_container_width=True):
            from data_init import initialize_data_files
            initialize_data_files()
            st.success("Data files initialized successfully.")
        
        st.warning("Caution: This will generate sample data for testing. It will only add data if the files are empty.")
        if st.button("Generate Sample Data", use_container_width=True):
            from data_init import generate_sample_data
            generate_sample_data()
            st.success("Sample data generated successfully.")