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
        
    # Initialize promotion amount
    if 'promo_amount' not in st.session_state:
        st.session_state.promo_amount = 0.0
        
    # Initialize editable orders
    if 'editable_orders' not in st.session_state:
        st.session_state.editable_orders = None
        
    # Initialize edit cost mode variables
    if 'edit_cost_mode' not in st.session_state:
        st.session_state.edit_cost_mode = False
        
    if 'edit_cost_id' not in st.session_state:
        st.session_state.edit_cost_id = None
        
    # Initialize edit mode variables
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
        
    if 'edit_index' not in st.session_state:
        st.session_state.edit_index = -1
        
    # Initialize edit order variables
    if 'edit_order_loaded' not in st.session_state:
        st.session_state.edit_order_loaded = False
        
    if 'edit_order_total' not in st.session_state:
        st.session_state.edit_order_total = 0
        
    if 'edit_order_promo' not in st.session_state:
        st.session_state.edit_order_promo = 0
        
    # Initialize delete confirmation
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = False
        
    # Initialize theme
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Initialize default time filter
    if 'default_time_filter' not in st.session_state:
        st.session_state.default_time_filter = "Today"
        
    # Make sure the default_time_filter is one of the valid options
    valid_time_filters = ["Today", "Last 7 Days", "Last 30 Days", "All Time", "Custom"]
    if st.session_state.default_time_filter not in valid_time_filters:
        st.session_state.default_time_filter = "Today"
        
    # Initialize username
    if 'username' not in st.session_state:
        st.session_state.username = "Cafe Manager"

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
    elif time_filter == "All Time":
        start_date = datetime(2020, 1, 1).date()
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
    
    # If no recipe found for this product
    if product_recipe.empty:
        return 0
    
    total_cost = 0
    for _, row in product_recipe.iterrows():
        try:
            ingredient = row['Ingredient']
            # Convert quantity to float to ensure numeric calculation
            quantity = float(row['Quantity'])
            
            # Skip if ingredient is missing or quantity is invalid
            if pd.isna(ingredient) or pd.isna(quantity) or quantity <= 0:
                continue
                
            # Get cost from inventory
            inventory_item = inventory_df[inventory_df['Name'] == ingredient]
            if not inventory_item.empty:
                # Ensure unit_cost is a valid number
                unit_cost = inventory_item.iloc[0]['Avg_Cost']
                if not pd.isna(unit_cost) and unit_cost > 0:
                    total_cost += quantity * unit_cost
        except (ValueError, TypeError) as e:
            # Skip this ingredient if any calculation error
            continue
    
    # Ensure we don't return NaN or negative values
    return max(0, total_cost)

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
