import streamlit as st
import pandas as pd
import datetime
import uuid
import utils

st.set_page_config(page_title="Order Management", page_icon="🛒", layout="wide")

st.title("Order Management")
st.subheader("Create and manage orders")

# Initialize session state for order items if not exists
if 'order_items' not in st.session_state:
    st.session_state.order_items = []

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

def save_order():
    """Save the current order to sales.csv and update inventory"""
    if not st.session_state.order_items:
        st.error("Order is empty. Please add items before saving.")
        return
    
    try:
        # Get order ID (either from manual input or generate a new one)
        order_id = st.session_state.get('manual_order_id', '')
        if not order_id:
            order_id = str(uuid.uuid4())[:8]
        
        # Prepare order data for sales.csv
        order_data = []
        for item in st.session_state.order_items:
            # Create datetime with date and time components
            order_datetime = datetime.datetime.combine(
                order_date,
                datetime.time(hour=hour, minute=minute)
            )
            
            order_data.append({
                'Date': order_datetime.strftime('%Y-%m-%d %H:%M'),
                'Order_ID': order_id,
                'Product': item['Product'],
                'Quantity': item['Quantity'],
                'Unit_Price': item['Unit_Price'],
                'Total': item['Total']
            })
        
        # Load existing sales data
        try:
            sales_df = pd.read_csv("data/sales.csv")
        except FileNotFoundError:
            sales_df = pd.DataFrame(columns=['Date', 'Order_ID', 'Product', 'Quantity', 'Unit_Price', 'Total'])
        
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
        st.success(f"Order {order_id} saved successfully!")
        
    except Exception as e:
        st.error(f"Error saving order: {str(e)}")

try:
    # Load product data
    products_df = pd.read_csv("data/products.csv")
    
    # Order form
    st.header("Create New Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Order date selection
        order_date = st.date_input("Order Date", datetime.datetime.now())
        
        # Order time selection
        current_time = datetime.datetime.now().time()
        hour = st.selectbox("Hour", options=list(range(0, 24)), index=current_time.hour)
        minute = st.selectbox("Minute", options=list(range(0, 60)), index=current_time.minute)
        
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
        st.button("Add to Order", on_click=add_item_to_order)
    
    # Manual Order ID input
    st.header("Order ID")
    manual_order_id = st.text_input("Enter Order ID (optional)", value=st.session_state.get('manual_order_id', ''),
                                    help="If left empty, a random ID will be generated automatically")
    
    # Save to session state
    st.session_state.manual_order_id = manual_order_id
    
    # Display current order
    st.header("Current Order")
    
    if st.session_state.order_items:
        # Initialize session state for edit mode if not exists
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False
            st.session_state.edit_index = -1
        
        # Show current items in order
        order_df = pd.DataFrame(st.session_state.order_items)
        
        # Add index column for reference
        order_df = order_df.reset_index().rename(columns={'index': 'Item #'})
        
        # Format currency columns
        order_df['Unit_Price'] = order_df['Unit_Price'].apply(utils.format_currency)
        order_df['Total'] = order_df['Total'].apply(utils.format_currency)
        
        st.dataframe(order_df)
        
        # Calculate order total
        order_total = sum(item['Total'] for item in st.session_state.order_items)
        st.subheader(f"Order Total: {utils.format_currency(order_total)}")
        
        # Edit and Remove Items
        with st.expander("Edit or Remove Items"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_index = st.number_input("Item #", min_value=0, 
                                           max_value=len(st.session_state.order_items)-1, 
                                           value=0,
                                           help="Select the item number to edit or remove")
                
                if st.button("Remove Item"):
                    remove_item_from_order(item_index)
                    st.rerun()
            
            with col2:
                # Edit Item UI
                if st.button("Edit Item"):
                    # Enable edit mode and set the selected item
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
                
                # Show calculated total
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
            st.button("Clear Order", on_click=clear_order)
        with col2:
            st.button("Save Order", on_click=save_order)
    else:
        st.info("No items in current order")
    
    # Recent orders
    st.header("Recent Orders")
    
    try:
        sales_df = pd.read_csv("data/sales.csv")
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        
        # Get orders from the last 7 days
        recent_date = datetime.datetime.now() - datetime.timedelta(days=7)
        recent_sales = sales_df[sales_df['Date'] >= recent_date]
        
        # Group by order
        recent_orders = recent_sales.groupby(['Date', 'Order_ID'])['Total'].sum().reset_index()
        recent_orders = recent_orders.sort_values('Date', ascending=False)
        
        # Format for display
        recent_orders['Date'] = recent_orders['Date'].dt.strftime('%d/%m/%y')
        recent_orders['Total'] = recent_orders['Total'].apply(utils.format_currency)
        
        st.dataframe(recent_orders.head(10))
        
    except FileNotFoundError:
        st.info("No sales data available yet")
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
