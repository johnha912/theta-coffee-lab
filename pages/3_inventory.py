import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import datetime
import utils

# Initialize session_state
utils.initialize_session_state()

# Set default template to ggplot2
pio.templates.default = 'ggplot2'

# Create custom ggplot2 template with gray background and grid
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
pio.templates.default = 'custom_ggplot2'

st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

st.title("Inventory Management")
st.subheader("Track and manage inventory items")

def add_inventory():
    """Add new inventory items"""
    try:
        # Validate input
        if not material_name or material_name.isspace():
            st.error("Please enter a valid material name")
            return
            
        if add_quantity <= 0:
            st.error("Quantity must be greater than zero")
            return
        
        # Load current inventory
        try:
            inventory_df = pd.read_csv("data/inventory.csv")
        except FileNotFoundError:
            inventory_df = pd.DataFrame(columns=['ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Date'])
        
        # Find the item if it exists
        if material_name in inventory_df['Name'].values:
            # Update existing material
            idx = inventory_df[inventory_df['Name'] == material_name].index[0]
            current_qty = inventory_df.loc[idx, 'Quantity']
            current_avg_cost = inventory_df.loc[idx, 'Avg_Cost']
            
            # Calculate new average cost
            new_total_value = (current_qty * current_avg_cost) + (add_quantity * unit_cost)
            new_total_qty = current_qty + add_quantity
            new_avg_cost = new_total_value / new_total_qty if new_total_qty > 0 else unit_cost
            
            # Update the inventory
            inventory_df.loc[idx, 'Quantity'] = new_total_qty
            inventory_df.loc[idx, 'Avg_Cost'] = new_avg_cost
            inventory_df.loc[idx, 'Date'] = inventory_date.strftime('%Y-%m-%d')
            
            message = f"Updated {material_name} inventory: added {add_quantity} {unit}"
        else:
            # Add new material - using loc to avoid concat warnings
            new_id = len(inventory_df) + 1
            
            # Create a new row index
            new_idx = len(inventory_df)
            
            # Use DataFrame.loc to add the new row
            inventory_df.loc[new_idx] = [
                new_id,
                material_name,
                add_quantity,
                unit,
                unit_cost,
                inventory_date.strftime('%Y-%m-%d')
            ]
            
            message = f"Added new material: {material_name}"
        
        # Save updated inventory
        inventory_df.to_csv("data/inventory.csv", index=False)
        st.success(message)
        
        # Record transaction in inventory_transactions.csv
        try:
            trans_df = pd.read_csv("data/inventory_transactions.csv")
        except FileNotFoundError:
            trans_df = pd.DataFrame(columns=['Date', 'Material', 'Quantity', 'Unit', 'Unit_Cost', 'Total_Cost', 'Type'])
        
        # Add transaction - using loc instead of concat
        new_idx = len(trans_df)
        trans_df.loc[new_idx] = [
            inventory_date.strftime('%Y-%m-%d'),
            material_name,
            add_quantity,
            unit,
            unit_cost,
            add_quantity * unit_cost,
            'Addition'
        ]
        
        trans_df.to_csv("data/inventory_transactions.csv", index=False)
        
        # After successful add, refresh the form/page
        st.rerun()
        
    except Exception as e:
        st.error(f"Error adding inventory: {str(e)}")
        
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    try:
        # Load current inventory
        try:
            inventory_df = pd.read_csv("data/inventory.csv")
        except FileNotFoundError:
            st.error("No inventory data found")
            return
            
        if inventory_df.empty:
            st.error("Inventory is empty")
            return
            
        # Find the item
        if item_id not in inventory_df['ID'].values:
            st.error(f"Item ID {item_id} not found in inventory")
            return
            
        # Get item details for confirmation message
        item_row = inventory_df[inventory_df['ID'] == item_id].iloc[0]
        item_name = item_row['Name']
        
        # Delete the item
        inventory_df = inventory_df[inventory_df['ID'] != item_id].reset_index(drop=True)
        
        # Reindex IDs to maintain sequence
        inventory_df['ID'] = range(1, len(inventory_df) + 1)
        
        # Save updated inventory
        inventory_df.to_csv("data/inventory.csv", index=False)
        
        # Record transaction in inventory_transactions.csv
        try:
            trans_df = pd.read_csv("data/inventory_transactions.csv")
        except FileNotFoundError:
            trans_df = pd.DataFrame(columns=['Date', 'Material', 'Quantity', 'Unit', 'Unit_Cost', 'Total_Cost', 'Type'])
        
        # Add deletion transaction - using loc instead of concat
        new_idx = len(trans_df)
        trans_df.loc[new_idx] = [
            datetime.datetime.now().strftime('%Y-%m-%d'),
            item_name,
            0,  # Quantity is 0 for deletion
            "",  # Empty unit for deletion
            0,   # Unit cost is 0 for deletion
            0,   # Total cost is 0 for deletion
            'Deletion'
        ]
        
        trans_df.to_csv("data/inventory_transactions.csv", index=False)
        
        st.success(f"Deleted inventory item: {item_name}")
        
        # After successful delete, refresh the form/page
        st.rerun()
        
    except Exception as e:
        st.error(f"Error deleting inventory item: {str(e)}")
        
def edit_inventory_item(item_id, new_name, new_unit, new_quantity, new_cost, new_date):
    """Edit an inventory item"""
    try:
        # Load current inventory
        try:
            inventory_df = pd.read_csv("data/inventory.csv")
        except FileNotFoundError:
            st.error("No inventory data found")
            return
            
        if inventory_df.empty:
            st.error("Inventory is empty")
            return
            
        # Find the item
        if item_id not in inventory_df['ID'].values:
            st.error(f"Item ID {item_id} not found in inventory")
            return
        
        # Get original item details for recording changes
        item_idx = inventory_df[inventory_df['ID'] == item_id].index[0]
        old_item = inventory_df.loc[item_idx].copy()
        
        # Update the item
        inventory_df.loc[item_idx, 'Name'] = new_name
        inventory_df.loc[item_idx, 'Unit'] = new_unit
        inventory_df.loc[item_idx, 'Quantity'] = new_quantity
        inventory_df.loc[item_idx, 'Avg_Cost'] = new_cost
        inventory_df.loc[item_idx, 'Date'] = new_date.strftime('%Y-%m-%d')
        
        # Save updated inventory
        inventory_df.to_csv("data/inventory.csv", index=False)
        
        # Record transaction in inventory_transactions.csv
        try:
            trans_df = pd.read_csv("data/inventory_transactions.csv")
        except FileNotFoundError:
            trans_df = pd.DataFrame(columns=['Date', 'Material', 'Quantity', 'Unit', 'Unit_Cost', 'Total_Cost', 'Type'])
        
        # Add edit transaction
        new_idx = len(trans_df)
        trans_df.loc[new_idx] = [
            datetime.datetime.now().strftime('%Y-%m-%d'),
            new_name,
            new_quantity,
            new_unit,
            new_cost,
            new_quantity * new_cost,
            'Edit'
        ]
        
        trans_df.to_csv("data/inventory_transactions.csv", index=False)
        
        st.success(f"Updated inventory item: {new_name}")
        
        # After successful edit, refresh the form/page
        st.rerun()
        
    except Exception as e:
        st.error(f"Error editing inventory item: {str(e)}")

try:
    # Ensure data directory exists
    utils.ensure_data_dir()
    
    # Initialize session state variables
    utils.initialize_session_state()
        
    # Load inventory data
    try:
        inventory_df = pd.read_csv("data/inventory.csv")
    except FileNotFoundError:
        inventory_df = pd.DataFrame(columns=['ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Date'])
        inventory_df.to_csv("data/inventory.csv", index=False)
    
    # Form for adding inventory
    st.header("Add Inventory Items")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Option to switch between select and manual input
        input_method = st.radio(
            "Material Input Method",
            ["Select from list", "Enter manually"],
            horizontal=True
        )
        
        if input_method == "Enter manually":
            # Direct text input for material name
            material_name = st.text_input("Material Name", value="")
            if not material_name.strip():
                st.warning("Please enter a material name")
                material_name = ""  # Prevent empty names by using empty string which won't match any existing material
        else:
            # Select from existing options
            existing_materials = inventory_df['Name'].unique().tolist() if not inventory_df.empty else []
            default_materials = ["Coffee Beans", "Fresh Milk", "Sugar", "Plastic Cup", "Paper Cup", "Syrup"]
            
            # Combine and remove duplicates while preserving order
            all_materials = []
            for item in existing_materials + default_materials:
                if item not in all_materials:
                    all_materials.append(item)
            
            if not all_materials:
                all_materials = ["Coffee Beans"]  # Default if no materials exist
                
            material_name = st.selectbox(
                "Material Name", 
                options=all_materials,
                index=0
            )
        
        # Unit selection
        unit_options = ["g", "ml", "pcs", "kg", "l"]
        if not inventory_df.empty and material_name in inventory_df['Name'].values:
            default_unit = inventory_df[inventory_df['Name'] == material_name]['Unit'].values[0]
            unit_index = unit_options.index(default_unit) if default_unit in unit_options else 0
        else:
            unit_index = 0
        
        unit = st.selectbox("Unit", options=unit_options, index=unit_index)
    
    with col2:
        # Quantity input
        add_quantity = st.number_input("Purchase Quantity", min_value=0.0, value=500.0, step=50.0)
        
        # Cost input - now for total purchase
        total_purchase_cost = st.number_input("Purchase Cost (VND)", min_value=0.0, value=100000.0, step=10000.0)
        
        # Calculate unit cost from total purchase
        unit_cost = total_purchase_cost / add_quantity if add_quantity > 0 else 0
        
        # Date selection
        inventory_date = st.date_input("Date", datetime.datetime.now())
    
    # Display calculated unit cost and total
    st.info(f"Unit Cost: {utils.format_currency(unit_cost)} per {unit}")
    st.info(f"Total Purchase Cost: {utils.format_currency(total_purchase_cost)}")
    
    # Add inventory button
    if st.button("Add to Inventory"):
        add_inventory()
    
    # Display current inventory
    st.header("Current Inventory")
    
    if not inventory_df.empty:
        # Format inventory table for display
        display_df = inventory_df.copy()
        display_df['Total Value'] = display_df['Quantity'] * display_df['Avg_Cost']
        
        # Format columns
        display_df['Avg_Cost'] = display_df['Avg_Cost'].apply(utils.format_currency)
        display_df['Total Value'] = display_df['Total Value'].apply(utils.format_currency)
        
        # Rearrange and display
        columns_to_show = ['ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Total Value', 'Date']
        st.dataframe(display_df[columns_to_show])
        
        # Add management options
        st.subheader("Manage Inventory Items")
        
        # Create columns for management actions
        manage_col1, manage_col2 = st.columns([1, 3])
        
        with manage_col1:
            # Selection dropdown for item to manage
            selected_item_id = st.selectbox(
                "Select Item ID", 
                options=inventory_df['ID'].tolist(),
                format_func=lambda x: f"ID: {x} - {inventory_df[inventory_df['ID']==x]['Name'].values[0]}"
            )
        
        with manage_col2:
            # Display information about selected item
            selected_item = inventory_df[inventory_df['ID'] == selected_item_id].iloc[0]
            st.write(f"Selected: **{selected_item['Name']}** ({selected_item['Quantity']} {selected_item['Unit']})")
            
            # Initialize session state for editing
            if 'edit_mode' not in st.session_state:
                st.session_state.edit_mode = False
            
            # Action buttons - wrapped in columns for layout
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                # Edit button
                edit_button = st.button("✏️ Edit Item", key="edit_btn")
                if edit_button:
                    st.session_state.edit_mode = True
                    
            with action_col2:
                # Delete button
                delete_button = st.button("🗑️ Delete Item", key="delete_btn")
                if delete_button:
                    # Show confirmation dialog using session state
                    st.session_state.delete_confirmation = True
            
            # Show delete confirmation outside of the columns
            if st.session_state.get('delete_confirmation', False):
                st.warning(f"Are you sure you want to delete {selected_item['Name']}?")
                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("✓ Yes, Delete", key="confirm_delete"):
                        delete_inventory_item(selected_item_id)
                with confirm_col2:
                    if st.button("✗ Cancel", key="cancel_delete"):
                        st.session_state.delete_confirmation = False
                        st.rerun()
            
            # Show edit form if in edit mode
            if st.session_state.edit_mode:
                st.write("---")
                st.subheader(f"Edit Item: {selected_item['Name']}")
                
                edit_col1, edit_col2 = st.columns(2)
                
                with edit_col1:
                    # Edit name
                    edit_name = st.text_input("Material Name", value=selected_item['Name'], key="edit_name")
                    
                    # Edit unit
                    unit_options = ["g", "ml", "pcs", "kg", "l"]
                    current_unit_index = unit_options.index(selected_item['Unit']) if selected_item['Unit'] in unit_options else 0
                    edit_unit = st.selectbox("Unit", options=unit_options, index=current_unit_index, key="edit_unit")
                
                with edit_col2:
                    # Edit quantity
                    edit_quantity = st.number_input("Quantity", min_value=0.0, value=selected_item['Quantity'], step=10.0, key="edit_quantity")
                    
                    # Edit cost
                    edit_cost = st.number_input("Cost per Unit (VND)", min_value=0.0, value=selected_item['Avg_Cost'], step=1000.0, key="edit_cost")
                    
                    # Edit date
                    try:
                        original_date = datetime.datetime.strptime(selected_item['Date'], '%Y-%m-%d').date()
                    except:
                        original_date = datetime.datetime.now().date()
                        
                    edit_date = st.date_input("Last Updated", value=original_date, key="edit_date")
                
                # Total value calculation
                edit_total_value = edit_quantity * edit_cost
                st.info(f"Total Value: {utils.format_currency(edit_total_value)}")
                
                # Save and Cancel buttons
                save_col1, save_col2 = st.columns(2)
                
                with save_col1:
                    if st.button("💾 Save Changes", key="save_edit"):
                        edit_inventory_item(
                            selected_item_id,
                            edit_name,
                            edit_unit,
                            edit_quantity,
                            edit_cost,
                            edit_date
                        )
                        
                with save_col2:
                    if st.button("❌ Cancel", key="cancel_edit"):
                        st.session_state.edit_mode = False
                        st.rerun()
        
        # Calculate total inventory value
        total_inventory_value = (inventory_df['Quantity'] * inventory_df['Avg_Cost']).sum()
        st.subheader(f"Total Inventory Value: {utils.format_currency(total_inventory_value)}")
        
        # Inventory visualization
        st.header("Inventory Visualization")
        
        # Group inventory by unit type
        if not inventory_df.empty:
            # Extract base unit types (remove numbers)
            inventory_df['Unit_Group'] = inventory_df['Unit'].str.lower().replace({'kg': 'g', 'l': 'ml'})
            
            # Get unique unit groups
            unit_groups = sorted(inventory_df['Unit_Group'].unique())
            
            # Create tabs for each unit group
            tabs = st.tabs([unit.upper() for unit in unit_groups])
            
            # Display inventory by unit group
            for i, unit in enumerate(unit_groups):
                with tabs[i]:
                    unit_data = inventory_df[inventory_df['Unit_Group'] == unit].copy()
                    
                    if not unit_data.empty:
                        # Sort the data from smallest to largest quantity
                        unit_data = unit_data.sort_values('Quantity')
                        
                        # Bar chart for this unit group
                        fig = px.bar(
                            unit_data,
                            x='Name',
                            y='Quantity',
                            color='Name',
                            labels={'Name': 'Material', 'Quantity': f'Quantity ({unit})'},
                            title=f"Inventory Levels - {unit.upper()} Units"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No inventory items with unit type: {unit}")
        
        # Intelligent low inventory alerts with category-based thresholds
        st.header("Inventory Alerts")
        
        # Define thresholds by unit type
        thresholds = {
            'ml': 300.0,  # For liquid ingredients (more than 3 coffee drinks)
            'g': 100.0,   # For dry ingredients
            'pcs': st.session_state.alert_threshold  # Use general threshold for pieces
        }
        
        # Track low inventory items
        low_inventory_items = []
        
        # Check each inventory item against its appropriate threshold
        for idx, row in inventory_df.iterrows():
            unit_type = row['Unit'].lower()
            # Convert units to base units
            if unit_type == 'l':
                unit_type = 'ml'
                threshold = thresholds['ml'] * 1000  # Convert to ml
            elif unit_type == 'kg':
                unit_type = 'g'
                threshold = thresholds['g'] * 1000  # Convert to g
            else:
                # Handle standard units
                threshold = thresholds.get(unit_type, st.session_state.alert_threshold)
            
            # Check if below threshold
            if row['Quantity'] <= threshold:
                low_inventory_items.append({
                    'Name': row['Name'],
                    'Quantity': row['Quantity'],
                    'Unit': row['Unit'],
                    'Threshold': threshold
                })
        
        # Display low inventory alerts
        if low_inventory_items:
            st.warning(f"{len(low_inventory_items)} items below recommended threshold!")
            
            for item in low_inventory_items:
                st.info(f"{item['Name']}: {item['Quantity']} {item['Unit']} remaining (threshold: {item['Threshold']} {item['Unit']})")
        else:
            st.success("All inventory items are at healthy levels.")
    else:
        st.info("No inventory data available. Please add items.")
    
    # Inventory transactions
    st.header("Recent Inventory Transactions")
    
    try:
        trans_df = pd.read_csv("data/inventory_transactions.csv")
        trans_df['Date'] = pd.to_datetime(trans_df['Date'])
        
        # Sort by date (most recent first)
        trans_df = trans_df.sort_values('Date', ascending=False)
        
        # Format for display
        display_trans = trans_df.copy()
        display_trans['Date'] = display_trans['Date'].dt.strftime('%Y-%m-%d')
        display_trans['Unit_Cost'] = display_trans['Unit_Cost'].apply(utils.format_currency)
        display_trans['Total_Cost'] = display_trans['Total_Cost'].apply(utils.format_currency)
        
        st.dataframe(display_trans.head(10))
    except FileNotFoundError:
        st.info("No transaction history available yet")

except Exception as e:
    st.error(f"Error loading inventory data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
