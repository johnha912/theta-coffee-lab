import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json
import numpy as np

# Initialize session state variables
def initialize_session_state():
    """Initialize session state variables"""
    if 'current_order' not in st.session_state:
        st.session_state.current_order = pd.DataFrame(columns=['Product', 'Quantity', 'Price', 'Total'])
    
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    if 'alert_threshold' not in st.session_state:
        st.session_state.alert_threshold = 10
    
    if 'order_id' not in st.session_state:
        st.session_state.order_id = generate_order_id()

# Format currency
def format_currency(value):
    """Format a number as currency with comma separators"""
    if pd.isna(value) or value is None:
        return "0 VND"
    return f"{int(value):,} VND"

# Get date range based on filter
def get_date_range(time_filter):
    """Get start and end dates based on time filter"""
    today = datetime.now()
    if time_filter == 'Today':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif time_filter == 'Last 7 days':
        start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif time_filter == 'Last 30 days':
        start_date = (today - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif time_filter == 'This month':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    else:  # All time
        start_date = datetime(2000, 1, 1)
        end_date = today
    
    return start_date, end_date

# Make sure data directory exists
def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs('data', exist_ok=True)

# Generate order ID
def generate_order_id():
    """Generate a unique order ID"""
    # Ensure sales.csv exists
    ensure_data_dir()
    if not os.path.exists('data/sales.csv'):
        return 1
    
    # Load existing sales
    sales = pd.read_csv('data/sales.csv')
    if 'OrderID' in sales.columns and not sales.empty:
        return sales['OrderID'].max() + 1
    return 1

# Calculate product COGS
def calculate_product_cogs(product_name, recipe_df, inventory_df):
    """Calculate COGS for a product based on recipe and inventory costs"""
    if recipe_df.empty or inventory_df.empty:
        return 0
    
    # Get recipe for this product
    product_recipe = recipe_df[recipe_df['Product'] == product_name]
    if product_recipe.empty:
        return 0
    
    total_cost = 0
    
    for _, row in product_recipe.iterrows():
        ingredient_name = row['Ingredient']
        ingredient_amount = row['Amount']
        
        # Find the ingredient in inventory
        ingredient_data = inventory_df[inventory_df['Item'] == ingredient_name]
        if not ingredient_data.empty:
            # Calculate cost per unit based on latest inventory entry
            latest_entry = ingredient_data.iloc[-1]
            unit_cost = latest_entry['Cost'] / latest_entry['Quantity']
            ingredient_cost = unit_cost * ingredient_amount
            total_cost += ingredient_cost
    
    return total_cost

# Update inventory from sale
def update_inventory_from_sale(product, quantity, recipe_df, inventory_df):
    """Update inventory based on a sale"""
    if recipe_df.empty or inventory_df.empty:
        return inventory_df
    
    # Get recipe for this product
    product_recipe = recipe_df[recipe_df['Product'] == product]
    if product_recipe.empty:
        return inventory_df
    
    updated_inventory = inventory_df.copy()
    
    for _, row in product_recipe.iterrows():
        ingredient_name = row['Ingredient']
        ingredient_amount = row['Amount'] * quantity
        
        # Find the ingredient in inventory
        ingredient_idx = updated_inventory[updated_inventory['Item'] == ingredient_name].index
        if len(ingredient_idx) > 0:
            # Update quantity - reduce by the amount used
            updated_inventory.at[ingredient_idx[-1], 'Quantity'] -= ingredient_amount
    
    return updated_inventory