import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils import initialize_session_state, format_currency, ensure_data_dir
from ui_utils import display_header, display_styled_table, create_tabs_with_icons

# Initialize session state
initialize_session_state()

# Page config
st.set_page_config(
    page_title="Inventory Management - Theta Coffee Lab",
    page_icon="📦",
    layout="wide"
)

# Display common header
display_header()

# Main title
st.title("Inventory Management")

# Load inventory data
def load_inventory_data():
    """Load inventory data"""
    ensure_data_dir()
    if not os.path.exists("data/inventory.csv"):
        # Create empty inventory file
        pd.DataFrame(columns=['Name', 'Unit', 'Quantity', 'Cost', 'Date']).to_csv("data/inventory.csv", index=False)
        return pd.DataFrame(columns=['Name', 'Unit', 'Quantity', 'Cost', 'Date'])
    
    inventory_df = pd.read_csv("data/inventory.csv")
    return inventory_df

# Add new inventory
def add_inventory():
    """Add new inventory items"""
    # Get form data
    item_name = st.session_state.item_name
    unit = st.session_state.unit
    quantity = st.session_state.quantity
    cost = st.session_state.cost
    date = st.session_state.date
    
    # Add to inventory
    new_item = pd.DataFrame({
        'Name': [item_name],
        'Unit': [unit],
        'Quantity': [quantity],
        'Cost': [cost],
        'Date': [date]
    })
    
    # Load existing data
    inventory_df = load_inventory_data()
    
    # Append new data
    inventory_df = pd.concat([inventory_df, new_item], ignore_index=True)
    
    # Save to file
    inventory_df.to_csv("data/inventory.csv", index=False)
    
    # Reset form
    st.session_state.item_name = ""
    st.session_state.quantity = 0
    st.session_state.cost = 0

# Delete an inventory item
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    inventory_df = load_inventory_data()
    if not inventory_df.empty and item_id < len(inventory_df):
        inventory_df = inventory_df.drop(item_id).reset_index(drop=True)
        inventory_df.to_csv("data/inventory.csv", index=False)
        return True
    return False

# Edit an inventory item
def edit_inventory_item(item_id, new_name, new_unit, new_quantity, new_cost, new_date):
    """Edit an inventory item"""
    inventory_df = load_inventory_data()
    if not inventory_df.empty and item_id < len(inventory_df):
        inventory_df.at[item_id, 'Name'] = new_name
        inventory_df.at[item_id, 'Unit'] = new_unit
        inventory_df.at[item_id, 'Quantity'] = new_quantity
        inventory_df.at[item_id, 'Cost'] = new_cost
        inventory_df.at[item_id, 'Date'] = new_date
        inventory_df.to_csv("data/inventory.csv", index=False)
        return True
    return False

# Load inventory data
inventory_df = load_inventory_data()

# Create layout with two columns
col1, col2 = st.columns([2, 3])

# Left column - Add inventory form
with col1:
    st.subheader("Add Inventory")
    
    with st.form("add_inventory_form", clear_on_submit=True):
        st.text_input("Item Name", key="item_name")
        
        unit_col, quantity_col = st.columns(2)
        with unit_col:
            st.selectbox("Unit", ["g", "kg", "ml", "l", "pcs"], key="unit")
        with quantity_col:
            st.number_input("Quantity", min_value=0.0, step=0.1, key="quantity")
        
        st.number_input("Cost (VND)", min_value=0, step=1000, key="cost")
        st.date_input("Date", value=datetime.now(), key="date")
        
        submit_col, _ = st.columns(2)
        with submit_col:
            submit_button = st.form_submit_button("Add to Inventory", use_container_width=True)
    
    # Process form submission
    if submit_button:
        if st.session_state.item_name and st.session_state.quantity > 0 and st.session_state.cost > 0:
            # Convert date to string
            st.session_state.date = st.session_state.date.strftime("%Y-%m-%d")
            add_inventory()
            st.success("Inventory added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all fields.")

# Right column - Inventory overview
with col2:
    st.subheader("Current Inventory")
    
    if not inventory_df.empty:
        # Group items by unit for better visualization
        inventory_by_unit = {}
        units = inventory_df['Unit'].unique()
        
        # Group similar units
        unit_groups = {
            'Weight': ['g', 'kg'],
            'Volume': ['ml', 'l'],
            'Count': ['pcs']
        }
        
        # Create tabs for unit types
        tabs = create_tabs_with_icons({
            "Weight (g/kg)": "weight",
            "Volume (ml/l)": "volume",
            "Count (pcs)": "count"
        })
        
        # Weight units tab
        with tabs["weight"]:
            weight_units = inventory_df[inventory_df['Unit'].isin(['g', 'kg'])]
            if not weight_units.empty:
                # Group by item name and get the latest entry
                latest_items = {}
                for item in weight_units['Name'].unique():
                    item_df = weight_units[weight_units['Name'] == item].sort_values('Date')
                    latest_items[item] = item_df.iloc[-1].name
                
                # Display all entries with edit/delete options
                for i, row in weight_units.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1.5, 1.5, 1])
                    
                    # Highlight latest entry
                    is_latest = i in latest_items.values()
                    style = "color: #5D4037; font-weight: bold;" if is_latest else ""
                    
                    with col1:
                        item_name = st.text_input(f"Item {i}", value=row['Name'], key=f"item_{i}")
                    
                    with col2:
                        unit = st.selectbox(f"Unit {i}", ["g", "kg"], index=0 if row['Unit'] == 'g' else 1, key=f"unit_{i}")
                    
                    with col3:
                        quantity = st.number_input(f"Qty {i}", min_value=0.0, value=float(row['Quantity']), step=0.1, key=f"qty_{i}")
                    
                    with col4:
                        cost = st.number_input(f"Cost {i}", min_value=0, value=int(row['Cost']), step=1000, key=f"cost_{i}")
                    
                    with col5:
                        date = st.date_input(f"Date {i}", 
                                           value=datetime.strptime(row['Date'], "%Y-%m-%d") if isinstance(row['Date'], str) else datetime.now(),
                                           key=f"date_{i}")
                    
                    with col6:
                        st.markdown("<br>", unsafe_allow_html=True)  # Add some space
                        
                        if st.button("Save", key=f"save_{i}", use_container_width=True):
                            if edit_inventory_item(i, item_name, unit, quantity, cost, date.strftime("%Y-%m-%d")):
                                st.success("Item updated successfully!")
                                st.rerun()
                        
                        if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                            if delete_inventory_item(i):
                                st.success("Item deleted successfully!")
                                st.rerun()
            else:
                st.info("No weight items in inventory.")
        
        # Volume units tab
        with tabs["volume"]:
            volume_units = inventory_df[inventory_df['Unit'].isin(['ml', 'l'])]
            if not volume_units.empty:
                # Group by item name and get the latest entry
                latest_items = {}
                for item in volume_units['Name'].unique():
                    item_df = volume_units[volume_units['Name'] == item].sort_values('Date')
                    latest_items[item] = item_df.iloc[-1].name
                
                # Display all entries with edit/delete options
                for i, row in volume_units.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1.5, 1.5, 1])
                    
                    # Highlight latest entry
                    is_latest = i in latest_items.values()
                    style = "color: #5D4037; font-weight: bold;" if is_latest else ""
                    
                    with col1:
                        item_name = st.text_input(f"Item {i}", value=row['Name'], key=f"item_{i}")
                    
                    with col2:
                        unit = st.selectbox(f"Unit {i}", ["ml", "l"], index=0 if row['Unit'] == 'ml' else 1, key=f"unit_{i}")
                    
                    with col3:
                        quantity = st.number_input(f"Qty {i}", min_value=0.0, value=float(row['Quantity']), step=0.1, key=f"qty_{i}")
                    
                    with col4:
                        cost = st.number_input(f"Cost {i}", min_value=0, value=int(row['Cost']), step=1000, key=f"cost_{i}")
                    
                    with col5:
                        date = st.date_input(f"Date {i}", 
                                           value=datetime.strptime(row['Date'], "%Y-%m-%d") if isinstance(row['Date'], str) else datetime.now(),
                                           key=f"date_{i}")
                    
                    with col6:
                        st.markdown("<br>", unsafe_allow_html=True)  # Add some space
                        
                        if st.button("Save", key=f"save_{i}", use_container_width=True):
                            if edit_inventory_item(i, item_name, unit, quantity, cost, date.strftime("%Y-%m-%d")):
                                st.success("Item updated successfully!")
                                st.rerun()
                        
                        if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                            if delete_inventory_item(i):
                                st.success("Item deleted successfully!")
                                st.rerun()
            else:
                st.info("No volume items in inventory.")
        
        # Count units tab
        with tabs["count"]:
            count_units = inventory_df[inventory_df['Unit'].isin(['pcs'])]
            if not count_units.empty:
                # Group by item name and get the latest entry
                latest_items = {}
                for item in count_units['Name'].unique():
                    item_df = count_units[count_units['Name'] == item].sort_values('Date')
                    latest_items[item] = item_df.iloc[-1].name
                
                # Display all entries with edit/delete options
                for i, row in count_units.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1.5, 1.5, 1])
                    
                    # Highlight latest entry
                    is_latest = i in latest_items.values()
                    style = "color: #5D4037; font-weight: bold;" if is_latest else ""
                    
                    with col1:
                        item_name = st.text_input(f"Item {i}", value=row['Name'], key=f"item_{i}")
                    
                    with col2:
                        unit = st.selectbox(f"Unit {i}", ["pcs"], index=0, key=f"unit_{i}")
                    
                    with col3:
                        quantity = st.number_input(f"Qty {i}", min_value=0, value=int(row['Quantity']), step=1, key=f"qty_{i}")
                    
                    with col4:
                        cost = st.number_input(f"Cost {i}", min_value=0, value=int(row['Cost']), step=1000, key=f"cost_{i}")
                    
                    with col5:
                        date = st.date_input(f"Date {i}", 
                                           value=datetime.strptime(row['Date'], "%Y-%m-%d") if isinstance(row['Date'], str) else datetime.now(),
                                           key=f"date_{i}")
                    
                    with col6:
                        st.markdown("<br>", unsafe_allow_html=True)  # Add some space
                        
                        if st.button("Save", key=f"save_{i}", use_container_width=True):
                            if edit_inventory_item(i, item_name, unit, quantity, cost, date.strftime("%Y-%m-%d")):
                                st.success("Item updated successfully!")
                                st.rerun()
                        
                        if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                            if delete_inventory_item(i):
                                st.success("Item deleted successfully!")
                                st.rerun()
            else:
                st.info("No count items in inventory.")
        
    else:
        st.info("No inventory items found. Add inventory items using the form.")

# Inventory summary at the bottom
st.subheader("Inventory Summary")

if not inventory_df.empty:
    # Group by Name and take the latest entry for each
    unique_items = []
    for item in inventory_df['Name'].unique():
        item_df = inventory_df[inventory_df['Name'] == item].sort_values('Date')
        unique_items.append(item_df.iloc[-1])
    
    latest_inventory = pd.DataFrame(unique_items)
    
    # Calculate total inventory value
    latest_inventory['Value'] = latest_inventory['Quantity'] * latest_inventory['Cost'] / latest_inventory['Quantity']
    total_value = latest_inventory['Value'].sum()
    
    # Show summary
    st.markdown(f"**Total Inventory Value:** {format_currency(total_value)}")
    
    # Display inventory value by category
    if len(latest_inventory) > 0:
        fig = px.pie(
            latest_inventory, 
            values='Value', 
            names='Name',
            title='Inventory Value Distribution',
            template='ggplot2'
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No inventory data available for summary.")