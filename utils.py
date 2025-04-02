import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import os

def initialize_session_state():
    """Initialize session state variables"""
    if 'currency' not in st.session_state:
        st.session_state.currency = "VND"
    
    if 'alert_threshold' not in st.session_state:
        st.session_state.alert_threshold = 10.0
    else:
        # Ensure alert_threshold is float
        st.session_state.alert_threshold = float(st.session_state.alert_threshold)
    
    # Initialize order items
    if 'order_items' not in st.session_state:
        st.session_state.order_items = []
    
    # Initialize manual order ID
    if 'manual_order_id' not in st.session_state:
        st.session_state.manual_order_id = ''
        
    # Initialize edit mode variables
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
        
    if 'edit_index' not in st.session_state:
        st.session_state.edit_index = -1

def format_currency(value):
    """Format a number as currency with comma separators"""
    if pd.isna(value):
        return "0 VND"
    
    # Format with commas
    formatted = f"{value:,.0f} VND"
    return formatted

def get_date_range(time_filter):
    """Get start and end dates based on time filter"""
    end_date = datetime.now().date()
    
    if time_filter == "Today":
        start_date = end_date
    elif time_filter == "Last 7 Days":
        start_date = end_date - timedelta(days=6)
    elif time_filter == "Last 30 Days":
        start_date = end_date - timedelta(days=29)
    else:  # Custom - handled separately in the app
        start_date = end_date - timedelta(days=7)  # Default fallback
    
    return start_date, end_date

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists("data"):
        os.makedirs("data")

def calculate_product_cogs(product_name, recipe_df, inventory_df):
    """Calculate COGS for a product based on recipe and inventory costs"""
    if recipe_df.empty or inventory_df.empty:
        return 0
    
    # Get recipe items for this product
    product_recipe = recipe_df[recipe_df['Product'] == product_name]
    
    total_cost = 0
    for _, row in product_recipe.iterrows():
        ingredient = row['Ingredient']
        quantity = row['Quantity']
        
        # Get cost from inventory
        inventory_item = inventory_df[inventory_df['Name'] == ingredient]
        if not inventory_item.empty:
            unit_cost = inventory_item.iloc[0]['Avg_Cost']
            total_cost += quantity * unit_cost
    
    return total_cost

def update_inventory_from_sale(product, quantity, recipe_df, inventory_df):
    """Update inventory based on a sale"""
    if recipe_df.empty or inventory_df.empty:
        return inventory_df
    
    # Get recipe for this product
    product_recipe = recipe_df[recipe_df['Product'] == product]
    
    # Make a copy of inventory to update
    updated_inventory = inventory_df.copy()
    
    # For each ingredient in the recipe, reduce inventory
    for _, recipe_row in product_recipe.iterrows():
        ingredient = recipe_row['Ingredient']
        quantity_needed = recipe_row['Quantity'] * quantity
        
        # Find ingredient in inventory
        idx = updated_inventory[updated_inventory['Name'] == ingredient].index
        if len(idx) > 0:
            # Reduce quantity
            current_qty = updated_inventory.loc[idx[0], 'Quantity']
            new_qty = max(0, current_qty - quantity_needed)  # Don't go below zero
            updated_inventory.loc[idx[0], 'Quantity'] = new_qty
    
    return updated_inventory
