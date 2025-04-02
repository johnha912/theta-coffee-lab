import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import utils

st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

st.title("Inventory Management")
st.subheader("Track and manage inventory items")

def add_inventory():
    """Add new inventory items"""
    try:
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
            # Add new material
            new_id = len(inventory_df) + 1
            new_row = {
                'ID': new_id,
                'Name': material_name,
                'Quantity': add_quantity,
                'Unit': unit,
                'Avg_Cost': unit_cost,
                'Date': inventory_date.strftime('%Y-%m-%d')
            }
            inventory_df = pd.concat([inventory_df, pd.DataFrame([new_row])], ignore_index=True)
            message = f"Added new material: {material_name}"
        
        # Save updated inventory
        inventory_df.to_csv("data/inventory.csv", index=False)
        st.success(message)
        
        # Record transaction in inventory_transactions.csv
        try:
            trans_df = pd.read_csv("data/inventory_transactions.csv")
        except FileNotFoundError:
            trans_df = pd.DataFrame(columns=['Date', 'Material', 'Quantity', 'Unit', 'Unit_Cost', 'Total_Cost', 'Type'])
        
        new_trans = {
            'Date': inventory_date.strftime('%Y-%m-%d'),
            'Material': material_name,
            'Quantity': add_quantity,
            'Unit': unit,
            'Unit_Cost': unit_cost,
            'Total_Cost': add_quantity * unit_cost,
            'Type': 'Addition'
        }
        
        trans_df = pd.concat([trans_df, pd.DataFrame([new_trans])], ignore_index=True)
        trans_df.to_csv("data/inventory_transactions.csv", index=False)
        
    except Exception as e:
        st.error(f"Error adding inventory: {str(e)}")

try:
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
        # Material selection
        existing_materials = inventory_df['Name'].unique().tolist() if not inventory_df.empty else []
        material_name = st.selectbox(
            "Material Name", 
            options=existing_materials + ["Coffee Beans", "Fresh Milk", "Sugar", "Plastic Cup", "Paper Cup", "Syrup", "Other"],
            index=0 if existing_materials else 7
        )
        
        if material_name == "Other":
            material_name = st.text_input("Specify Material Name")
        
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
        add_quantity = st.number_input("Quantity", min_value=0.0, value=100.0, step=10.0)
        
        # Cost input
        unit_cost = st.number_input("Cost per Unit (VND)", min_value=0.0, value=1000.0, step=1000.0)
        
        # Date selection
        inventory_date = st.date_input("Date", datetime.datetime.now())
    
    # Calculate total cost
    total_cost = add_quantity * unit_cost
    st.info(f"Total Cost: {utils.format_currency(total_cost)}")
    
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
        
        # Add alert indicator
        display_df['Status'] = display_df.apply(
            lambda row: "⚠️ Low" if row['Quantity'] <= st.session_state.alert_threshold else "✅ Good", 
            axis=1
        )
        
        # Rearrange and display
        columns_to_show = ['ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Total Value', 'Status', 'Date']
        st.dataframe(display_df[columns_to_show])
        
        # Calculate total inventory value
        total_inventory_value = (inventory_df['Quantity'] * inventory_df['Avg_Cost']).sum()
        st.subheader(f"Total Inventory Value: {utils.format_currency(total_inventory_value)}")
        
        # Inventory visualization
        st.header("Inventory Visualization")
        
        # Bar chart for inventory quantities
        fig = px.bar(
            inventory_df,
            x='Name',
            y='Quantity',
            color='Name',
            labels={'Name': 'Material', 'Quantity': 'Quantity Available'},
            title="Current Inventory Levels"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Low inventory alerts
        low_inventory = inventory_df[inventory_df['Quantity'] <= st.session_state.alert_threshold]
        
        if not low_inventory.empty:
            st.header("Low Inventory Alerts")
            st.warning(f"{len(low_inventory)} items below threshold!")
            
            for _, row in low_inventory.iterrows():
                st.info(f"{row['Name']}: {row['Quantity']} {row['Unit']} remaining (threshold: {st.session_state.alert_threshold})")
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
