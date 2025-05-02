import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import datetime
import uuid
import utils
import os

# Initialize session state
utils.initialize_session_state()

# Set page config
st.set_page_config(page_title="Order Management", page_icon="🛒", layout="wide")

# Set default template to ggplot2 (consistent with other pages)
pio.templates.default = 'ggplot2'

# Custom ggplot2 template with gray background and white grid
custom_ggplot2_template = pio.templates['ggplot2']
custom_ggplot2_template.layout.update(
    paper_bgcolor='#F0F0F0',  # Paper background color
    plot_bgcolor='#F0F0F0',   # Plot background color
    xaxis=dict(
        showgrid=True,
        gridcolor='white',
        gridwidth=1.5
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='white',
        gridwidth=1.5
    )
)
pio.templates['custom_ggplot2'] = custom_ggplot2_template

# Add page title
st.title("Order Management")
st.subheader("Create and manage orders")

# Define the main functions
def add_item_to_order():
    """Add an item to the current order"""
    if not product_name or quantity <= 0:
        st.error("Please select a product and enter a valid quantity")
        return
    
    # Get product price
    product_price = float(products_df[products_df['Name'] == product_name]['Price'].values[0])
    total_price = product_price * quantity
    
    # Add to order items
    st.session_state.order_items.append({
        'Product': product_name,
        'Quantity': quantity,
        'Unit_Price': product_price,
        'Total': total_price
    })
    st.success(f"Added {quantity} {product_name}(s) to order")

def clear_order():
    """Clear the current order"""
    st.session_state.order_items = []
    st.success("Order cleared")
    st.rerun()

def remove_item_from_order(index):
    """Remove an item from the current order"""
    if 0 <= index < len(st.session_state.order_items):
        removed_item = st.session_state.order_items.pop(index)
        st.success(f"Removed {removed_item['Product']} from order")
    else:
        st.error("Invalid item index")

def edit_item_in_order(index, product_name, quantity, product_price):
    """Edit an item in the current order"""
    if 0 <= index < len(st.session_state.order_items):
        # Calculate new total
        total_price = product_price * quantity
        
        # Update the item
        st.session_state.order_items[index] = {
            'Product': product_name,
            'Quantity': quantity,
            'Unit_Price': product_price,
            'Total': total_price
        }
        
        st.success(f"Updated {product_name} in order")
    else:
        st.error("Invalid item index")

def delete_saved_order(order_id):
    """Delete a saved order from sales.csv and restore inventory"""
    try:
        # Load sales data
        sales_df = pd.read_csv("data/sales.csv")
        
        # Convert order_id to string for accurate comparison
        order_id_str = str(order_id).strip()
        
        # Check if order exists
        order_items = sales_df[sales_df['Order_ID'].astype(str) == order_id_str]
        if not order_items.empty:
            # First, restore inventory based on the deleted items
            try:
                inventory_df = pd.read_csv("data/inventory.csv")
                recipe_df = pd.read_csv("data/product_recipe.csv")
                
                # For each deleted item, restore inventory
                for _, item in order_items.iterrows():
                    product = item['Product']
                    quantity_sold = item['Quantity']
                    
                    # Get recipe for this product
                    product_recipe = recipe_df[recipe_df['Product'] == product]
                    
                    # Restore inventory for each ingredient
                    for _, recipe_row in product_recipe.iterrows():
                        ingredient = recipe_row['Ingredient']
                        quantity_to_restore = recipe_row['Quantity'] * quantity_sold
                        
                        # Update inventory - add the quantity back
                        inventory_index = inventory_df[inventory_df['Name'] == ingredient].index
                        if not inventory_index.empty:
                            current_quantity = inventory_df.loc[inventory_index[0], 'Quantity']
                            new_quantity = current_quantity + quantity_to_restore
                            inventory_df.loc[inventory_index[0], 'Quantity'] = new_quantity
                            st.info(f"Restored {quantity_to_restore} {ingredient} to inventory")
                
                # Save updated inventory
                inventory_df.to_csv("data/inventory.csv", index=False)
                
            except Exception as e:
                st.error(f"Error restoring inventory: {str(e)}")
            
            # Now remove the order from sales data
            sales_df = sales_df[sales_df['Order_ID'].astype(str) != order_id_str]
            
            # Save updated sales data
            sales_df.to_csv("data/sales.csv", index=False)
            
            st.success(f"Order {order_id} deleted successfully and inventory restored")
            return True
        else:
            st.error(f"Order {order_id} not found")
            return False
    except Exception as e:
        st.error(f"Error deleting order: {str(e)}")
        return False

def save_order():
    """Save the current order to sales.csv and update inventory"""
    if not st.session_state.order_items:
        st.error("Order is empty. Please add items before saving.")
        return
    
    try:
        # Get order ID (either from manual input or generate a new one)
        order_id = st.session_state.manual_order_id if st.session_state.manual_order_id else str(uuid.uuid4())[:8]
        
        # Get hour and minute directly from session state to avoid parsing issues
        hour = st.session_state.order_hour
        minute = st.session_state.order_minute
        
        # Prepare order data for sales.csv
        order_data = []
        for item in st.session_state.order_items:
            # Create datetime with date and time components
            order_datetime = datetime.datetime.combine(
                order_date,
                datetime.time(hour=hour, minute=minute)
            )
            
            # Calculate promo distribution for each item proportionally
            total_order_value = sum(item['Total'] for item in st.session_state.order_items)
            item_promo = (item['Total'] / total_order_value * st.session_state.promo_amount) if total_order_value > 0 else 0
            item_net_total = item['Total'] - item_promo
            
            order_data.append({
                'Date': order_datetime.strftime('%Y-%m-%d %H:%M'),
                'Order_ID': order_id,
                'Product': item['Product'],
                'Quantity': item['Quantity'],
                'Unit_Price': item['Unit_Price'],
                'Total': item['Total'],
                'Promo': item_promo,
                'Net_Total': item_net_total,
                'Location': st.session_state.order_location if len(order_data) == 0 else ''  # Only add location to first item
            })
        
        # Load existing sales data
        try:
            sales_df = pd.read_csv("data/sales.csv")
        except FileNotFoundError:
            sales_df = pd.DataFrame(columns=['Date', 'Order_ID', 'Product', 'Quantity', 'Unit_Price', 'Total', 'Promo', 'Net_Total'])
        
        # Check and add missing columns if needed
        if 'Promo' not in sales_df.columns:
            sales_df['Promo'] = 0.0
        if 'Net_Total' not in sales_df.columns:
            sales_df['Net_Total'] = sales_df['Total']
        if 'Location' not in sales_df.columns:
            sales_df['Location'] = ''
            
        # Append new order to sales
        new_sales = pd.DataFrame(order_data)
        sales_df = pd.concat([sales_df, new_sales], ignore_index=True)
        
        # Save updated sales data
        sales_df.to_csv("data/sales.csv", index=False)
        
        # Update inventory based on recipe
        try:
            inventory_df = pd.read_csv("data/inventory.csv")
            recipe_df = pd.read_csv("data/product_recipe.csv")
            
            # For each item in order, reduce inventory
            for item in st.session_state.order_items:
                product = item['Product']
                quantity_sold = item['Quantity']
                
                # Get recipe for this product
                product_recipe = recipe_df[recipe_df['Product'] == product]
                
                # Reduce inventory for each ingredient
                for _, recipe_row in product_recipe.iterrows():
                    ingredient = recipe_row['Ingredient']
                    quantity_needed = recipe_row['Quantity'] * quantity_sold
                    
                    # Update inventory
                    inventory_index = inventory_df[inventory_df['Name'] == ingredient].index
                    if not inventory_index.empty:
                        current_quantity = inventory_df.loc[inventory_index[0], 'Quantity']
                        new_quantity = current_quantity - quantity_needed
                        
                        # Check if enough inventory
                        if new_quantity < 0:
                            st.warning(f"Warning: Not enough {ingredient} in inventory. Quantity will be set to 0.")
                            new_quantity = 0
                            
                        inventory_df.loc[inventory_index[0], 'Quantity'] = new_quantity
                    else:
                        st.warning(f"Warning: Ingredient {ingredient} not found in inventory")
            
            # Save updated inventory
            inventory_df.to_csv("data/inventory.csv", index=False)
            
        except Exception as e:
            st.error(f"Error updating inventory: {str(e)}")
            return
        
        # Clear order after saving
        st.session_state.order_items = []
        st.session_state.manual_order_id = ''  # Reset manual order ID
        st.session_state.promo_amount = 0.0    # Reset promo amount
        st.success(f"Order {order_id} saved successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error saving order: {str(e)}")

def update_order_promo(order_id, new_promo_amount):
    """Update promotion amount for an existing order"""
    try:
        # Load sales data
        sales_df = pd.read_csv("data/sales.csv")
        
        # Convert order_id to string for accurate comparison
        order_id_str = str(order_id).strip()
        
        # Find the order
        order_items = sales_df[sales_df['Order_ID'].astype(str) == order_id_str]
        
        if not order_items.empty:
            # Calculate total for this order
            order_total = order_items['Total'].sum()
            
            # Create a copy of the dataframe
            sales_df_copy = sales_df.copy()
            
            # Update each item in the order
            for idx, item in order_items.iterrows():
                # Distribute promo amount proportionally
                item_promo = (item['Total'] / order_total * new_promo_amount) if order_total > 0 else 0
                item_net_total = item['Total'] - item_promo
                
                # Update values
                sales_df_copy.loc[idx, 'Promo'] = item_promo
                sales_df_copy.loc[idx, 'Net_Total'] = item_net_total
            
            # Save updated data
            sales_df_copy.to_csv("data/sales.csv", index=False)
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error updating promotion: {str(e)}")
        return False

def update_order_time(order_id, new_hour, new_minute):
    """Update time for an existing order"""
    try:
        # Load sales data
        sales_df = pd.read_csv("data/sales.csv")
        
        # Convert order_id to string for accurate comparison
        order_id_str = str(order_id).strip()
        
        # Find the order
        order_items = sales_df[sales_df['Order_ID'].astype(str) == order_id_str]
        
        if not order_items.empty:
            # Create a copy of the dataframe
            sales_df_copy = sales_df.copy()
            
            # Update each item in the order
            for idx, item in order_items.iterrows():
                # Parse the current date
                current_date = pd.to_datetime(item['Date'])
                
                # Create new datetime with updated hour and minute
                new_date = current_date.replace(hour=new_hour, minute=new_minute)
                
                # Update Date field with new formatted value
                sales_df_copy.loc[idx, 'Date'] = new_date.strftime('%Y-%m-%d %H:%M')
            
            # Save updated data
            sales_df_copy.to_csv("data/sales.csv", index=False)
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error updating order time: {str(e)}")
        return False

def update_order_id(order_id, new_order_id):
    """Update Order_ID for an existing order"""
    try:
        # Load sales data
        sales_df = pd.read_csv("data/sales.csv")
        
        # Convert order_id to string for accurate comparison
        order_id_str = str(order_id).strip()
        new_order_id_str = str(new_order_id).strip()
        
        # Check if the new Order_ID already exists (to avoid duplicates)
        if new_order_id_str != order_id_str and (sales_df['Order_ID'].astype(str) == new_order_id_str).any():
            st.error(f"Order ID {new_order_id} already exists. Please use a different ID.")
            return False
        
        # Find the order
        order_items = sales_df[sales_df['Order_ID'].astype(str) == order_id_str]
        
        if not order_items.empty:
            # Create a copy of the dataframe
            sales_df_copy = sales_df.copy()
            
            # Update each item in the order
            for idx, _ in order_items.iterrows():
                # Update the Order_ID
                sales_df_copy.loc[idx, 'Order_ID'] = new_order_id_str
            
            # Save updated data
            sales_df_copy.to_csv("data/sales.csv", index=False)
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error updating order ID: {str(e)}")
        return False

# Initialize session state variables if they don't exist
if 'order_items' not in st.session_state:
    st.session_state.order_items = []

if 'promo_amount' not in st.session_state:
    st.session_state.promo_amount = 0.0

if 'manual_order_id' not in st.session_state:
    st.session_state.manual_order_id = ''

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
    
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = -1
    
if 'loaded_order_id' not in st.session_state:
    st.session_state.loaded_order_id = ''
    
if 'loaded_order_total' not in st.session_state:
    st.session_state.loaded_order_total = 0.0
    
if 'loaded_order_promo' not in st.session_state:
    st.session_state.loaded_order_promo = 0.0
    
if 'loaded_time_order_id' not in st.session_state:
    st.session_state.loaded_time_order_id = ''
    
if 'loaded_time_hour' not in st.session_state:
    st.session_state.loaded_time_hour = 0
    
if 'loaded_time_minute' not in st.session_state:
    st.session_state.loaded_time_minute = 0
    
if 'loaded_orderid_order' not in st.session_state:
    st.session_state.loaded_orderid_order = ''

if 'order_location' not in st.session_state:
    st.session_state.order_location = ''

if 'loaded_location_order_id' not in st.session_state:
    st.session_state.loaded_location_order_id = ''

if 'loaded_location' not in st.session_state:
    st.session_state.loaded_location = ''

# Main code
try:
    # Load product data
    products_df = pd.read_csv("data/products.csv")
    
    # Create New Order section
    st.header("Create New Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Order date selection
        order_date = st.date_input("Order Date", datetime.datetime.now())
        
        # Order time selection - using separate number inputs for hour and minute to avoid jumps
        if 'order_hour' not in st.session_state:
            st.session_state.order_hour = datetime.datetime.now().hour
        if 'order_minute' not in st.session_state:
            st.session_state.order_minute = datetime.datetime.now().minute
        
        # Use columns for hour and minute inputs
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            hour_input = st.number_input("Hour (0-23)", 
                                        min_value=0, 
                                        max_value=23, 
                                        value=st.session_state.order_hour,
                                        key="order_hour_input")
        with time_col2:
            minute_input = st.number_input("Minute (0-59)", 
                                          min_value=0, 
                                          max_value=59, 
                                          value=st.session_state.order_minute,
                                          key="order_minute_input")
        
        # Update session state
        st.session_state.order_hour = hour_input
        st.session_state.order_minute = minute_input
        
        # Construct time string for use in save_order
        time_input = f"{hour_input:02d}:{minute_input:02d}"
        
        # Show current time selection
        st.info(f"Selected time: {time_input}")
        
        # Product selection
        product_name = st.selectbox("Select Product", options=products_df['Name'].tolist())
        
        # Get product details when selected
        if product_name:
            selected_product = products_df[products_df['Name'] == product_name].iloc[0]
            st.info(f"Price: {utils.format_currency(selected_product['Price'])}")
    
    with col2:
        # Quantity input
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
        # Calculate total price
        if product_name:
            product_price = float(products_df[products_df['Name'] == product_name]['Price'].values[0])
            total_price = product_price * quantity
            st.info(f"Total: {utils.format_currency(total_price)}")
        
        # Add to order button
        st.button("Add to Order", on_click=add_item_to_order, key="add_to_order_btn")
    
    # Manual Order ID input
    st.header("Order Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        manual_order_id = st.text_input("Enter Order ID (optional)", value=st.session_state.manual_order_id,
                                      help="If left empty, a random ID will be generated automatically")
        # Save to session state
        st.session_state.manual_order_id = manual_order_id
    
    with col2:
        location = st.text_input("Delivery Location", value=st.session_state.order_location,
                              help="Enter customer address or location for this order (for map display)")
        # Save to session state
        st.session_state.order_location = location
    
    # Display current order
    st.header("Current Order")
    
    if st.session_state.order_items:
        # Show current items in order
        order_df = pd.DataFrame(st.session_state.order_items)
        
        # Add index column for reference
        order_df = order_df.reset_index().rename(columns={'index': 'Item #'})
        
        # Format currency columns
        order_df['Unit_Price'] = order_df['Unit_Price'].apply(lambda x: utils.format_currency(x, include_currency=True))
        order_df['Total'] = order_df['Total'].apply(lambda x: utils.format_currency(x, include_currency=True))
        
        st.dataframe(order_df)
        
        # Calculate order total
        order_total = sum(item['Total'] for item in st.session_state.order_items)
        
        # Add promo input field
        st.subheader("Order Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Order Total", f"{utils.format_currency(order_total)}")
            promo_amount = st.number_input("Promotion Amount (VND)", 
                                          min_value=0.0, 
                                          max_value=order_total,
                                          value=st.session_state.promo_amount,
                                          step=1000.0)
            st.session_state.promo_amount = promo_amount
        
        with col2:
            net_total = order_total - promo_amount
            st.metric("Net Total", f"{utils.format_currency(net_total)}", 
                     delta=f"-{utils.format_currency(promo_amount)}" if promo_amount > 0 else None)
            st.info("Net Total = Order Total - Promotion Amount")
        
        # Edit and Remove Items
        with st.expander("Edit or Remove Items"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_index = st.number_input("Item #", min_value=0, 
                                           max_value=len(st.session_state.order_items)-1, 
                                           value=0,
                                           help="Select the item number to edit or remove")
                
                if st.button("Remove Item", key="remove_item_btn"):
                    remove_item_from_order(item_index)
                    st.rerun()
            
            with col2:
                # Edit Item UI
                if st.button("Edit Item", key="edit_item_btn"):
                    st.session_state.edit_mode = True
                    st.session_state.edit_index = item_index
                    st.rerun()
        
        # Show edit form if in edit mode
        if st.session_state.edit_mode and 0 <= st.session_state.edit_index < len(st.session_state.order_items):
            with st.form("edit_item_form"):
                st.subheader(f"Edit Item #{st.session_state.edit_index}")
                
                # Get current values
                current_item = st.session_state.order_items[st.session_state.edit_index]
                
                # Edit fields
                edit_product = st.selectbox("Product", 
                                          options=products_df['Name'].tolist(),
                                          index=products_df['Name'].tolist().index(current_item['Product']) 
                                               if current_item['Product'] in products_df['Name'].tolist() else 0)
                
                edit_quantity = st.number_input("Quantity", 
                                             min_value=1, 
                                             value=current_item['Quantity'])
                
                # Get product price
                edit_price = float(products_df[products_df['Name'] == edit_product]['Price'].values[0])
                edit_total = edit_price * edit_quantity
                
                st.info(f"New Total: {utils.format_currency(edit_total)}")
                
                # Submit button
                if st.form_submit_button("Update Item"):
                    edit_item_in_order(st.session_state.edit_index, edit_product, edit_quantity, edit_price)
                    st.session_state.edit_mode = False
                    st.session_state.edit_index = -1
                    st.rerun()
                
                if st.form_submit_button("Cancel"):
                    st.session_state.edit_mode = False
                    st.session_state.edit_index = -1
                    st.rerun()
        
        # Order action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Order", key="clear_order_btn"):
                clear_order()
        with col2:
            if st.button("Save Order", key="save_order_btn"):
                save_order()
    else:
        st.info("No items in current order")
    
    # Recent orders
    st.header("Recent Orders")
    
    # Time filter for recent orders
    order_time_options = ["Last 7 Days", "Last 30 Days", "All Time"]
    order_time_filter = st.selectbox("Time Period", options=order_time_options, index=0)
    
    # Recent orders section
    try:
        # Load sales data
        sales_df = pd.read_csv("data/sales.csv")
        
        # Check if we have any sales data
        if sales_df.empty:
            st.info("No sales data available yet")
        else:
            # Convert Date column to datetime
            sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
            
            # Get orders based on selected time filter
            if order_time_filter == "Last 7 Days":
                recent_date = datetime.datetime.now() - datetime.timedelta(days=7)
            elif order_time_filter == "Last 30 Days":
                recent_date = datetime.datetime.now() - datetime.timedelta(days=30)
            else:  # All Time
                recent_date = datetime.datetime(2020, 1, 1)
            
            recent_sales = sales_df[sales_df['Date'] >= recent_date]
            
            # If no data in the selected time period
            if recent_sales.empty:
                st.info(f"No orders in the selected time period: {order_time_filter}")
            else:
                # Check and add missing columns if needed
                if 'Promo' not in recent_sales.columns:
                    recent_sales['Promo'] = 0.0
                if 'Net_Total' not in recent_sales.columns:
                    recent_sales['Net_Total'] = recent_sales['Total']
                
                # Create standard time columns for sorting
                recent_sales['Hour'] = recent_sales['Date'].dt.hour
                recent_sales['Minute'] = recent_sales['Date'].dt.minute
                
                # Group by order
                recent_orders = recent_sales.groupby(['Date', 'Order_ID']).agg({
                    'Total': 'sum',
                    'Promo': 'sum',
                    'Net_Total': 'sum',
                    'Hour': 'first',
                    'Minute': 'first'
                }).reset_index()
                
                # Sort by date and time (newest first)
                recent_orders = recent_orders.sort_values(['Date', 'Hour', 'Minute'], ascending=[False, False, False])
                
                # Format for display
                display_df = recent_orders.copy()
                display_df['Time'] = display_df.apply(lambda x: f"{int(x['Hour']):02d}:{int(x['Minute']):02d}", axis=1)
                display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%y')
                
                # Format currency columns - hide VND in Total and Net_Total
                display_df['Total_Display'] = display_df['Total'].apply(lambda x: utils.format_currency(x, include_currency=False))
                display_df['Promo_Display'] = display_df['Promo'].apply(utils.format_currency)
                display_df['Net_Total_Display'] = display_df['Net_Total'].apply(lambda x: utils.format_currency(x, include_currency=False))
                
                # Show all recent orders based on time filter
                
                # Select columns for display
                display_cols = ['Date', 'Time', 'Order_ID', 'Total_Display', 'Promo_Display', 'Net_Total_Display']
                renamed_cols = {'Total_Display': 'Total', 'Promo_Display': 'Promo', 'Net_Total_Display': 'Net Total'}
                
                # Create display DataFrame with selected columns and renamed headers
                table_df = display_df[display_cols].rename(columns=renamed_cols)
                
                # Display table
                st.dataframe(table_df, hide_index=True)
                
                # Edit or Delete Saved Orders
                with st.expander("Edit or Delete Saved Order"):
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Delete Order", "Edit Promotion", "Edit Time", "Edit Order ID", "Edit Location"])
                    
                    with tab1:
                        # Delete order
                        delete_order_id = st.text_input("Enter Order ID to delete")
                        
                        if st.button("Delete Order", key="delete_order_btn"):
                            if delete_order_id:
                                if delete_saved_order(delete_order_id):
                                    st.rerun()
                    
                    with tab2:
                        # Edit promo amount for an existing order
                        edit_promo_id = st.text_input("Order ID", key="edit_promo_id", help="Enter Order ID to adjust promotion amount")
                        
                        # Add a button to load the order information
                        if st.button("Load Order", key="load_order_btn"):
                            if edit_promo_id:
                                # Convert to string for accurate comparison
                                edit_promo_id_str = str(edit_promo_id).strip()
                                
                                # Check if order exists
                                order_info = sales_df[sales_df['Order_ID'].astype(str) == edit_promo_id_str]
                                
                                if not order_info.empty:
                                    # Calculate total for the order
                                    order_total = order_info['Total'].sum()
                                    current_promo = order_info['Promo'].sum() if 'Promo' in order_info.columns else 0
                                    
                                    # Store in session state
                                    st.session_state.loaded_order_id = edit_promo_id
                                    st.session_state.loaded_order_total = order_total
                                    st.session_state.loaded_order_promo = current_promo
                                    st.success(f"Loaded Order {edit_promo_id}")
                                    st.rerun()
                                else:
                                    st.error(f"Order {edit_promo_id} not found")
                        
                        # Display and edit order if it's loaded
                        if st.session_state.loaded_order_id:
                            order_total = st.session_state.loaded_order_total
                            current_promo = st.session_state.loaded_order_promo
                            
                            st.metric("Order Total", f"{utils.format_currency(order_total)}")
                            
                            new_promo = st.number_input(
                                "New Promotion Amount",
                                min_value=0.0,
                                max_value=float(order_total),
                                value=float(current_promo),
                                step=1000.0,
                                key="new_promo_amount"
                            )
                            
                            if st.button("Update Promotion", key="update_promo_btn"):
                                if update_order_promo(st.session_state.loaded_order_id, new_promo):
                                    st.success(f"Updated promotion for Order {st.session_state.loaded_order_id}")
                                    # Reset state
                                    st.session_state.loaded_order_id = ''
                                    st.session_state.loaded_order_total = 0.0
                                    st.session_state.loaded_order_promo = 0.0
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update promotion for Order {st.session_state.loaded_order_id}")
                    
                    with tab3:
                        # No need to initialize session variables here since we did it at the top of the file
                        
                        # Edit time for an existing order
                        edit_time_id = st.text_input("Order ID", key="edit_time_id", help="Enter Order ID to adjust time")
                        
                        # Add a button to load the order information
                        if st.button("Load Order", key="load_time_order_btn"):
                            if edit_time_id:
                                # Convert to string for accurate comparison
                                edit_time_id_str = str(edit_time_id).strip()
                                
                                # Check if order exists
                                order_info = sales_df[sales_df['Order_ID'].astype(str) == edit_time_id_str]
                                
                                if not order_info.empty:
                                    # Get first date from order (all items in same order have same date)
                                    first_date = order_info['Date'].iloc[0]
                                    
                                    # Extract hour and minute
                                    current_hour = first_date.hour
                                    current_minute = first_date.minute
                                    
                                    # Store in session state
                                    st.session_state.loaded_time_order_id = edit_time_id
                                    st.session_state.loaded_time_hour = current_hour
                                    st.session_state.loaded_time_minute = current_minute
                                    
                                    st.success(f"Loaded Order {edit_time_id}")
                                    st.rerun()
                                else:
                                    st.error(f"Order {edit_time_id} not found")
                        
                        # Display and edit time if order is loaded
                        if st.session_state.loaded_time_order_id:
                            # Get current time values from session state
                            current_hour = st.session_state.loaded_time_hour
                            current_minute = st.session_state.loaded_time_minute
                            
                            # Format current time for display
                            current_time = f"{current_hour:02d}:{current_minute:02d}"
                            st.info(f"Current Time: {current_time}")
                            
                            # Use number_input for hour and minute for more precise control
                            col1, col2 = st.columns(2)
                            with col1:
                                new_hour = st.number_input("Hour (0-23)", 
                                                        min_value=0, 
                                                        max_value=23, 
                                                        value=current_hour,
                                                        key="edit_hour")
                            with col2:
                                new_minute = st.number_input("Minute (0-59)", 
                                                          min_value=0, 
                                                          max_value=59, 
                                                          value=current_minute,
                                                          key="edit_minute")
                            
                            # Update button
                            if st.button("Update Time", key="update_time_btn"):
                                if update_order_time(st.session_state.loaded_time_order_id, new_hour, new_minute):
                                    st.success(f"Updated time for Order {st.session_state.loaded_time_order_id} to {new_hour:02d}:{new_minute:02d}")
                                    # Reset state
                                    st.session_state.loaded_time_order_id = ''
                                    st.session_state.loaded_time_hour = 0
                                    st.session_state.loaded_time_minute = 0
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update time for Order {st.session_state.loaded_time_order_id}")
                    
                    with tab4:
                        # No need to initialize session variables here since we did it at the top of the file
                        
                        # Edit Order ID for an existing order
                        edit_orderid_id = st.text_input("Current Order ID", key="edit_orderid_id", help="Enter existing Order ID to change")
                        
                        # Add a button to load the order information
                        if st.button("Load Order", key="load_orderid_btn"):
                            if edit_orderid_id:
                                # Convert to string for accurate comparison
                                edit_orderid_str = str(edit_orderid_id).strip()
                                
                                # Check if order exists
                                order_info = sales_df[sales_df['Order_ID'].astype(str) == edit_orderid_str]
                                
                                if not order_info.empty:
                                    # Store in session state
                                    st.session_state.loaded_orderid_order = edit_orderid_id
                                    
                                    # Display success and order details
                                    order_details = f"Order contains {len(order_info)} items, total: {utils.format_currency(order_info['Total'].sum())}"
                                    st.success(f"Loaded Order {edit_orderid_id}. {order_details}")
                                    st.rerun()
                                else:
                                    st.error(f"Order {edit_orderid_id} not found")
                        
                        # Display and edit Order ID if order is loaded
                        if st.session_state.loaded_orderid_order:
                            # Get current Order ID value from session state
                            current_orderid = st.session_state.loaded_orderid_order
                            
                            st.info(f"Current Order ID: {current_orderid}")
                            
                            # Input field for new Order ID
                            new_orderid = st.text_input(
                                "New Order ID",
                                value="",
                                help="Enter the new Order ID for this order",
                                key="new_orderid_input"
                            )
                            
                            # Update button
                            if st.button("Update Order ID", key="update_orderid_btn"):
                                if new_orderid and new_orderid.strip():
                                    if update_order_id(current_orderid, new_orderid):
                                        st.success(f"Updated Order ID from {current_orderid} to {new_orderid}")
                                        # Reset state
                                        st.session_state.loaded_orderid_order = ''
                                        st.rerun()
                                    # Error message is already shown in the update_order_id function
                                else:
                                    st.error("New Order ID cannot be empty")
    except FileNotFoundError:
        st.info("No sales data found. Please create and save orders first.")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please check that your data files exist and are properly formatted.")
except FileNotFoundError:
    st.error("Product data not found. Please make sure data/products.csv exists.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check that your data files exist and are properly formatted.")