import streamlit as st
import pandas as pd
import datetime
import uuid
import utils

# Khởi tạo session_state
utils.initialize_session_state()

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

def delete_saved_order(order_id):
    """Delete a saved order from sales.csv and restore inventory"""
    try:
        # Load sales data
        sales_df = pd.read_csv("data/sales.csv")
        
        # Convert order_id to string for accurate comparison
        order_id_str = str(order_id).strip()
        
        # Check if order exists - convert to string for comparison
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
            
            # Now remove the order from sales data - using string comparison
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
        order_id = st.session_state.get('manual_order_id', '')
        if not order_id:
            order_id = str(uuid.uuid4())[:8]
        
        # Parse time input (format: HH:MM)
        try:
            time_parts = time_input.split(':')
            if len(time_parts) != 2:
                st.error("Time must be in format HH:MM (e.g., 14:30)")
                return
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                st.error("Invalid time. Hours must be 0-23, minutes must be 0-59")
                return
                
        except ValueError:
            st.error("Time must be in format HH:MM with valid numbers (e.g., 14:30)")
            return
        
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
                'Net_Total': item_net_total
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
        
        # Order time selection - Text input format HH:MM
        current_time = datetime.datetime.now().time()
        default_time = f"{current_time.hour:02d}:{current_time.minute:02d}"
        time_input = st.text_input("Time (HH:MM)", value=default_time, 
                                  help="Enter time in 24-hour format (e.g., 14:30 for 2:30 PM)")
        
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
    
    # Time filter for recent orders
    order_time_options = ["Last 7 Days", "Last 30 Days", "All Time"]
    order_time_filter = st.selectbox("Time Period", options=order_time_options, index=0, key="order_time_filter")
    
    try:
        sales_df = pd.read_csv("data/sales.csv")
        sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
        
        # Get orders based on selected time filter
        if order_time_filter == "Last 7 Days":
            recent_date = datetime.datetime.now() - datetime.timedelta(days=7)
        elif order_time_filter == "Last 30 Days":
            recent_date = datetime.datetime.now() - datetime.timedelta(days=30)
        else:  # All Time
            recent_date = datetime.datetime(2020, 1, 1)
            
        recent_sales = sales_df[sales_df['Date'] >= recent_date]
        
        # Check and add missing columns if needed
        if 'Promo' not in recent_sales.columns:
            recent_sales['Promo'] = 0.0
        if 'Net_Total' not in recent_sales.columns:
            recent_sales['Net_Total'] = recent_sales['Total']
            
        # Tạo cột thời gian chuẩn để sắp xếp
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
        
        # Sắp xếp theo ngày và giờ giảm dần (mới nhất lên đầu)
        recent_orders = recent_orders.sort_values(['Date', 'Hour', 'Minute'], ascending=[False, False, False])
        
        # Tạo DataFrame hiển thị với tất cả là string để dễ xử lý
        display_df = recent_orders.copy()
        
        # Format for display - Tạo cột Time từ Hour và Minute
        display_df['Time'] = display_df.apply(lambda x: f"{int(x['Hour']):02d}:{int(x['Minute']):02d}", axis=1)
        display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%y')
        
        # Lưu lại giá trị số trước khi format để tính toán
        display_df['Total_Value'] = display_df['Total']
        display_df['Promo_Value'] = display_df['Promo']
        
        # Format các giá trị tiền tệ - ẩn đi chữ VND ở Total và Net Total theo yêu cầu
        display_df['Total'] = display_df['Total'].apply(lambda x: utils.format_currency(x, include_currency=False))
        display_df['Promo'] = display_df['Promo'].apply(utils.format_currency)
        display_df['Net_Total'] = display_df['Net_Total'].apply(lambda x: utils.format_currency(x, include_currency=False))
        
        # Sắp xếp lại các cột để hiển thị 
        display_df = display_df[['Date', 'Time', 'Order_ID', 'Total', 'Promo', 'Net_Total', 'Total_Value', 'Promo_Value']]
        
        # Hiển thị bảng có thể chỉnh sửa
        st.subheader("Recent Orders (Last 10)")
        st.info("Click on the Promo cell to edit promotion value directly")
        
        # Tạo df chỉ có các cột cần thiết và chuyển đổi tất cả về định dạng đúng
        editor_data = []
        for _, row in display_df.head(10).iterrows():
            try:
                # Format promotion value with commas for thousands
                promo_value = f"{int(row['Promo_Value']):,}" if row['Promo_Value'].is_integer() else f"{float(row['Promo_Value']):,.0f}"
            except:
                # If conversion fails, use 0 formatted with comma
                promo_value = "0"
                
            editor_data.append({
                "Date": row['Date'],
                "Time": row['Time'],
                "Order_ID": row['Order_ID'],
                "Total": row['Total'],
                "Promo": promo_value,  # Formatted with comma separators
                "Net_Total": row['Net_Total']
            })
        
        # Tạo dataframe có thể chỉnh sửa với dữ liệu đã được xử lý
        edited_df = st.data_editor(
            editor_data,
            column_config={
                "Date": st.column_config.TextColumn("Date", disabled=True),
                "Time": st.column_config.TextColumn(
                    "Time",
                    help="Time in HH:MM format. Click to edit."
                ),
                "Order_ID": st.column_config.TextColumn("Order ID", disabled=True),
                "Total": st.column_config.TextColumn("Total", disabled=True),
                "Promo": st.column_config.TextColumn(
                    "Promo",
                    help="Promotion value. Click on cell to edit."
                ),
                "Net_Total": st.column_config.TextColumn("Net Total", disabled=True),
            },
            hide_index=True,
            key="editable_orders",
            on_change=None  # Không sử dụng callback mà lấy giá trị từ session_state sau khi chỉnh sửa
        )
        
        # Kiểm tra xem có dữ liệu chỉnh sửa hay không và xử lý an toàn
        editable_orders = st.session_state.get("editable_orders")
        if editable_orders is not None and isinstance(editable_orders, dict):
            changed = False
            sales_df_copy = sales_df.copy()
            
            # Debug: Sau khi hoàn thành, ẩn thông tin debug này
            # st.write("Đã chỉnh sửa các dòng:", st.session_state["editable_orders"])
            
            # Xử lý dữ liệu trong phần edited_rows (các hàng đã chỉnh sửa)
            if 'edited_rows' in editable_orders:
                for index, edited_data in editable_orders['edited_rows'].items():
                    try:
                        # Lấy chỉ số hàng
                        row_index = int(index)
                        
                        # Lấy dữ liệu gốc từ hàng này
                        if row_index < len(editor_data):
                            original_row = editor_data[row_index]
                            order_id = original_row["Order_ID"]
                            
                            # Lấy giá trị cũ từ dữ liệu gốc - chuyển sang string để so sánh chính xác
                            old_order_data = display_df[display_df['Order_ID'].astype(str) == str(order_id)]
                            if not old_order_data.empty:
                                # Xử lý chỉnh sửa Time
                                if 'Time' in edited_data:
                                    try:
                                        # Kiểm tra định dạng thời gian hợp lệ (HH:MM)
                                        new_time = edited_data['Time'].strip()
                                        time_parts = new_time.split(':')
                                        
                                        if len(time_parts) == 2:
                                            hour = int(time_parts[0])
                                            minute = int(time_parts[1])
                                            
                                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                                old_time = original_row["Time"]
                                                
                                                # Nếu thời gian thay đổi
                                                if new_time != old_time:
                                                    changed = True
                                                    st.success(f"Changed time for order {order_id} from {old_time} to {new_time}")
                                                    
                                                    # Tìm tất cả các mục của đơn hàng này
                                                    order_items = sales_df[sales_df['Order_ID'].astype(str) == str(order_id)]
                                                    
                                                    # Cập nhật giờ và phút cho tất cả các mục trong đơn hàng
                                                    for idx, _ in order_items.iterrows():
                                                        # Lấy đối tượng datetime hiện tại
                                                        current_date = pd.to_datetime(sales_df_copy.loc[idx, 'Date'])
                                                        
                                                        # Tạo datetime mới với giờ và phút đã cập nhật
                                                        new_date = current_date.replace(hour=hour, minute=minute)
                                                        
                                                        # Cập nhật lại trường Date với giá trị mới
                                                        sales_df_copy.loc[idx, 'Date'] = new_date
                                            else:
                                                st.error(f"Invalid time format: {new_time}. Hours must be 0-23, minutes must be 0-59.")
                                        else:
                                            st.error(f"Invalid time format: {new_time}. Please use HH:MM format.")
                                    except ValueError:
                                        st.error(f"Invalid time format: {edited_data['Time']}. Please use HH:MM format.")
                                
                                # Xử lý chỉnh sửa Promo
                                if 'Promo' in edited_data:
                                    try:
                                        # Remove commas from the input string before converting to float
                                        cleaned_promo = edited_data['Promo'].replace(',', '') if isinstance(edited_data['Promo'], str) else edited_data['Promo']
                                        new_promo = float(cleaned_promo)
                                    except (ValueError, TypeError, AttributeError):
                                        new_promo = 0
                                        
                                    old_promo = float(old_order_data.iloc[0]['Promo_Value'])
                                    
                                    # Nếu giá trị thay đổi
                                    if new_promo != old_promo:
                                        changed = True
                                        st.success(f"Changed promotion for order {order_id} from {utils.format_currency(old_promo)} to {utils.format_currency(new_promo)}")
                                        
                                        # Tìm tất cả các mục của đơn hàng này - chuyển sang string để so sánh chính xác
                                        order_items = sales_df[sales_df['Order_ID'].astype(str) == str(order_id)]
                                        total_order_value = order_items['Total'].sum()
                                        
                                        # Cập nhật từng mục trong đơn hàng
                                        for idx, item in order_items.iterrows():
                                            item_promo = (item['Total'] / total_order_value * new_promo) if total_order_value > 0 else 0
                                            item_net_total = item['Total'] - item_promo
                                            
                                            # Cập nhật giá trị trong DataFrame
                                            sales_df_copy.loc[idx, 'Promo'] = item_promo
                                            sales_df_copy.loc[idx, 'Net_Total'] = item_net_total
                    except Exception as e:
                        st.error(f"Error processing edited row: {str(e)}")
            
            # Nếu có sự thay đổi, lưu lại DataFrame
            if changed:
                sales_df_copy.to_csv("data/sales.csv", index=False)
                st.success("Order has been updated successfully")
                st.rerun()
        
        # Edit or Delete order section
        with st.expander("Edit or Delete Saved Order"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Delete order
                delete_order_id = st.text_input("Enter Order ID to delete", key="delete_order_id")
                
                if st.button("Delete Order"):
                    if delete_order_id:
                        delete_saved_order(delete_order_id)
                        st.rerun()
                    else:
                        st.error("Please enter an Order ID to delete")
            
            with col2:
                # Edit promotion
                edit_promo_id = st.text_input("Order ID", key="edit_promo_id", 
                                             help="Enter Order ID to adjust promotion amount")
                
                # Add a button to load the order information
                if st.button("Load Order"):
                    if edit_promo_id:
                        # Chuyển đổi sang string để đảm bảo so sánh chính xác
                        edit_promo_id_str = str(edit_promo_id).strip()
                        
                        # Check if order exists - convert to string for comparison
                        order_info = sales_df[sales_df['Order_ID'].astype(str) == edit_promo_id_str]
                        
                        if not order_info.empty:
                            # Calculate total for the order
                            order_total = order_info['Total'].sum()
                            current_promo = order_info['Promo'].sum() if 'Promo' in order_info.columns else 0
                            
                            # Store in session state
                            st.session_state.edit_order_total = order_total
                            st.session_state.edit_order_promo = current_promo
                            st.session_state.edit_order_loaded = True
                            st.rerun()
                        else:
                            # Debug để kiểm tra các Order_ID trong sales_df
                            st.error(f"Order {edit_promo_id} not found")
                            with st.expander("Debug Info"):
                                st.write("Order IDs in database:")
                                st.write(sales_df['Order_ID'].astype(str).tolist())
                    else:
                        st.error("Please enter an Order ID")
                
                # Show promotion adjustment section if an order is loaded
                if st.session_state.get('edit_order_loaded', False):
                    order_total = st.session_state.edit_order_total
                    current_promo = st.session_state.edit_order_promo
                    
                    st.write(f"Order Total: {utils.format_currency(order_total)}")
                    st.write(f"Current Promo: {utils.format_currency(current_promo)}")
                    
                    # Ensure all numeric arguments have the same type (float)
                    new_promo = st.number_input("New Promotion Amount", 
                                              min_value=0.0,
                                              max_value=float(order_total),
                                              value=float(current_promo),
                                              step=1000.0)
                    
                    if st.button("Update Promotion"):
                        try:
                            # Get the order - convert to string for comparison
                            order_info = sales_df[sales_df['Order_ID'].astype(str) == str(edit_promo_id).strip()]
                            
                            if not order_info.empty:
                                # Calculate promo distribution based on item totals
                                total_order_value = order_info['Total'].sum()
                                
                                # Create a copy of the DataFrame to avoid SettingWithCopyWarning
                                sales_df_copy = sales_df.copy()
                                
                                # Update each item in the order
                                for idx, row in order_info.iterrows():
                                    item_promo = (row['Total'] / total_order_value * new_promo) if total_order_value > 0 else 0
                                    item_net_total = row['Total'] - item_promo
                                    
                                    # Update values
                                    sales_df_copy.loc[idx, 'Promo'] = item_promo
                                    sales_df_copy.loc[idx, 'Net_Total'] = item_net_total
                                
                                # Save changes
                                sales_df_copy.to_csv("data/sales.csv", index=False)
                                
                                st.success(f"Updated promotion for Order {edit_promo_id}")
                                
                                # Reset session state
                                st.session_state.edit_order_loaded = False
                                st.session_state.edit_order_total = 0
                                st.session_state.edit_order_promo = 0
                                
                                st.rerun()
                            else:
                                st.error(f"Order {edit_promo_id} not found")
                        except Exception as e:
                            st.error(f"Error updating promotion: {str(e)}")
        
    except FileNotFoundError:
        st.info("No sales data available yet")
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
