import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import re
from utils import initialize_session_state, format_currency, ensure_data_dir, generate_order_id, update_inventory_from_sale
from ui_utils import display_header, display_styled_table

# Initialize session state
initialize_session_state()

# Page config
st.set_page_config(
    page_title="Order Management - Theta Coffee Lab",
    page_icon="🧾",
    layout="wide"
)

# Display common header
display_header()

# Main title
st.title("Order Management")

# Load data functions
def load_products_data():
    """Load products data"""
    if not os.path.exists("data/products.csv"):
        return pd.DataFrame()
    
    products_df = pd.read_csv("data/products.csv")
    return products_df

def load_recipe_data():
    """Load recipe data"""
    if not os.path.exists("data/product_recipe.csv"):
        return pd.DataFrame()
    
    recipe_df = pd.read_csv("data/product_recipe.csv")
    return recipe_df

def load_inventory_data():
    """Load inventory data"""
    if not os.path.exists("data/inventory.csv"):
        return pd.DataFrame()
    
    inventory_df = pd.read_csv("data/inventory.csv")
    return inventory_df

def load_sales_data():
    """Load sales data"""
    if not os.path.exists("data/sales.csv"):
        return pd.DataFrame()
    
    sales_df = pd.read_csv("data/sales.csv")
    return sales_df

# Load data
products_df = load_products_data()
recipe_df = load_recipe_data()
inventory_df = load_inventory_data()
sales_df = load_sales_data()

# Add an item to the current order
def add_item_to_order():
    """Add an item to the current order"""
    # Get selected product info
    product_name = st.session_state.product_select
    product_info = products_df[products_df['Product'] == product_name]
    
    if not product_info.empty:
        product_price = product_info.iloc[0]['Price']
        
        # Get quantity
        quantity = st.session_state.product_quantity
        
        # Calculate total
        total = product_price * quantity
        
        # Add to order
        new_item = pd.DataFrame({
            'Product': [product_name],
            'Quantity': [quantity],
            'Price': [product_price],
            'Total': [total]
        })
        
        st.session_state.current_order = pd.concat([st.session_state.current_order, new_item], ignore_index=True)
        
        # Reset form
        st.session_state.product_quantity = 1

# Clear the current order
def clear_order():
    """Clear the current order"""
    st.session_state.current_order = pd.DataFrame(columns=['Product', 'Quantity', 'Price', 'Total'])

# Remove an item from the order
def remove_item_from_order(index):
    """Remove an item from the current order"""
    st.session_state.current_order = st.session_state.current_order.drop(index).reset_index(drop=True)

# Edit item in order
def edit_item_in_order(index, product_name, quantity, product_price):
    """Edit an item in the current order"""
    if index < len(st.session_state.current_order):
        st.session_state.current_order.at[index, 'Product'] = product_name
        st.session_state.current_order.at[index, 'Quantity'] = quantity
        st.session_state.current_order.at[index, 'Price'] = product_price
        st.session_state.current_order.at[index, 'Total'] = quantity * product_price

# Delete a saved order
def delete_saved_order(order_id):
    """Delete a saved order from sales.csv"""
    sales = load_sales_data()
    if not sales.empty:
        # Remove all rows with the matching OrderID
        sales = sales[sales['OrderID'] != order_id]
        # Save back to file
        sales.to_csv('data/sales.csv', index=False)
        st.success(f"Order #{order_id} has been deleted.")
        return True
    return False

# Save the current order
def save_order():
    """Save the current order to sales.csv and update inventory"""
    if st.session_state.current_order.empty:
        st.error("Cannot save empty order.")
        return False
    
    # Get current date and time
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # Use order ID from session state or generate new one
    order_id = st.session_state.order_id
    
    # Create sales entries
    sales_entries = []
    for _, row in st.session_state.current_order.iterrows():
        sales_entries.append({
            'OrderID': order_id,
            'Date': date_str,
            'Time': time_str,
            'Product': row['Product'],
            'Quantity': row['Quantity'],
            'Price': row['Price'],
            'Total': row['Total']
        })
    
    # Create or append to sales.csv
    ensure_data_dir()
    
    if not os.path.exists('data/sales.csv'):
        sales_df = pd.DataFrame(columns=['OrderID', 'Date', 'Time', 'Product', 'Quantity', 'Price', 'Total'])
    else:
        sales_df = pd.read_csv('data/sales.csv')
    
    # Append new entries
    sales_df = pd.concat([sales_df, pd.DataFrame(sales_entries)], ignore_index=True)
    
    # Save to file
    sales_df.to_csv('data/sales.csv', index=False)
    
    # Update inventory based on recipe
    new_inventory = inventory_df.copy()
    for _, row in st.session_state.current_order.iterrows():
        product = row['Product']
        quantity = row['Quantity']
        new_inventory = update_inventory_from_sale(product, quantity, recipe_df, new_inventory)
    
    # Save updated inventory
    new_inventory.to_csv('data/inventory.csv', index=False)
    
    # Clear the current order and generate new order ID
    clear_order()
    st.session_state.order_id = generate_order_id()
    
    return True

# Create layout with two columns
col1, col2 = st.columns([3, 2])

# Left column - Order creation
with col1:
    st.subheader("Create New Order")
    
    # Order ID input
    order_id_col, date_col = st.columns(2)
    with order_id_col:
        new_order_id = st.number_input("Order ID", 
                                      min_value=1, 
                                      value=st.session_state.order_id, 
                                      step=1)
        if new_order_id != st.session_state.order_id:
            st.session_state.order_id = new_order_id
            
    with date_col:
        st.text_input("Date/Time", value=datetime.now().strftime("%Y-%m-%d %H:%M"), disabled=True)
    
    # Product selection
    if not products_df.empty:
        product_col, quantity_col, add_col = st.columns([3, 1, 1])
        
        with product_col:
            st.selectbox("Select Product", 
                        products_df['Product'].tolist(),
                        key="product_select")
        
        with quantity_col:
            st.number_input("Quantity", 
                           min_value=1, 
                           value=1, 
                           step=1,
                           key="product_quantity")
        
        with add_col:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some space
            if st.button("Add to Order", use_container_width=True):
                add_item_to_order()
    else:
        st.warning("No products available. Please add products first.")
    
    # Show current order
    st.subheader("Current Order")
    
    if not st.session_state.current_order.empty:
        # Display the order with edit/delete options
        for i, row in st.session_state.current_order.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 1, 1])
            
            with col1:
                product_list = products_df['Product'].tolist()
                product_index = product_list.index(row['Product']) if row['Product'] in product_list else 0
                new_product = st.selectbox(f"Product #{i+1}", 
                                          product_list,
                                          index=product_index,
                                          key=f"edit_product_{i}")
            
            with col2:
                new_quantity = st.number_input(f"Qty #{i+1}", 
                                             min_value=1, 
                                             value=int(row['Quantity']),
                                             key=f"edit_qty_{i}")
            
            with col3:
                product_price = products_df.loc[products_df['Product'] == new_product, 'Price'].values[0]
                new_total = new_quantity * product_price
                st.text_input(f"Price #{i+1}", 
                             value=format_currency(product_price),
                             disabled=True,
                             key=f"price_{i}")
            
            with col4:
                st.text_input(f"Total #{i+1}", 
                             value=format_currency(new_total),
                             disabled=True,
                             key=f"total_{i}")
            
            with col5:
                st.markdown("<br>", unsafe_allow_html=True)  # Add some space
                if st.button("Update", key=f"update_{i}", use_container_width=True):
                    edit_item_in_order(i, new_product, new_quantity, product_price)
                
                if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                    remove_item_from_order(i)
                    st.rerun()
        
        # Total
        st.markdown("---")
        order_total = st.session_state.current_order['Total'].sum()
        st.markdown(f"### Total: {format_currency(order_total)}")
        
        # Action buttons
        save_col, clear_col = st.columns(2)
        with save_col:
            if st.button("Save Order", use_container_width=True):
                if save_order():
                    st.success("Order saved successfully!")
                    st.rerun()
        
        with clear_col:
            if st.button("Clear Order", use_container_width=True):
                clear_order()
                st.rerun()
    else:
        st.info("No items in the current order.")

# Right column - Recent orders
with col2:
    st.subheader("Recent Orders")
    
    if not sales_df.empty:
        # Group by OrderID and calculate totals
        order_totals = sales_df.groupby('OrderID').agg(
            Date=('Date', 'first'),
            Time=('Time', 'first'),
            Items=('Product', 'count'),
            Total=('Total', 'sum')
        ).reset_index().sort_values('OrderID', ascending=False).head(10)
        
        # Display as a table
        for i, row in order_totals.iterrows():
            with st.expander(f"Order #{int(row['OrderID'])} - {row['Date']} {row['Time']} - {format_currency(row['Total'])}"):
                # Get order details
                order_details = sales_df[sales_df['OrderID'] == row['OrderID']]
                
                # Display order details
                display_styled_table(order_details[['Product', 'Quantity', 'Price', 'Total']])
                
                # Delete button
                if st.button("Delete Order", key=f"delete_order_{int(row['OrderID'])}", use_container_width=True):
                    if delete_saved_order(int(row['OrderID'])):
                        st.rerun()
    else:
        st.info("No recent orders found.")