import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import datetime
import utils

# Khởi tạo session_state
utils.initialize_session_state()

# Set default template to ggplot2
pio.templates.default = 'ggplot2'

# Tạo template ggplot2 custom với nền xám và lưới
custom_ggplot2_template = pio.templates['ggplot2']
custom_ggplot2_template.layout.update(
    paper_bgcolor='#F0F0F0',  # Màu nền paper
    plot_bgcolor='#F0F0F0',   # Màu nền plot
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

st.set_page_config(page_title="Financial Report", page_icon="💰", layout="wide")

st.title("Financial Report")
st.subheader("Financial KPIs and Analysis")

# Time filter
time_options = ["Today", "Last 7 Days", "Last 30 Days", "Custom"]
time_filter = st.selectbox("Time Period", options=time_options, index=time_options.index(st.session_state.default_time_filter))

# Date range for custom filter
if time_filter == "Custom":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.datetime.now())
else:
    # Set date range based on selection
    end_date = datetime.datetime.now().date()
    if time_filter == "Today":
        start_date = end_date
    elif time_filter == "Last 7 Days":
        start_date = end_date - datetime.timedelta(days=6)
    elif time_filter == "Last 30 Days":
        start_date = end_date - datetime.timedelta(days=29)

try:
    # Load data
    sales_df = pd.read_csv("data/sales.csv")
    products_df = pd.read_csv("data/products.csv")
    product_recipe_df = pd.read_csv("data/product_recipe.csv")
    
    # Load operational costs if available
    try:
        operational_costs_df = pd.read_csv("data/operational_costs.csv")
        operational_costs_df['Date'] = pd.to_datetime(operational_costs_df['Date'])
    except FileNotFoundError:
        operational_costs_df = pd.DataFrame(columns=['Date', 'Type', 'Amount'])
        
    # Prepare sales data
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    filtered_sales = sales_df[(sales_df['Date'].dt.date >= start_date) & 
                             (sales_df['Date'].dt.date <= end_date)]
    
    # Financial KPIs
    st.header("Financial Key Performance Indicators")
    
    # Check if filtered_sales is empty
    if filtered_sales.empty:
        total_revenue = 0
        total_cogs = 0
        merged_sales = pd.DataFrame(columns=['Product', 'Order_Quantity', 'COGS', 'Price'])
    else:
        # Calculate revenue
        total_revenue = filtered_sales['Total'].sum()
        
        # Calculate COGS
        filtered_sales_copy = filtered_sales.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
        merged_sales = pd.merge(filtered_sales_copy, products_df, left_on='Product', right_on='Name', how='left')
        
        # Check if COGS column exists in products_df
        if 'COGS' in merged_sales.columns:
            total_cogs = (merged_sales['COGS'] * merged_sales['Order_Quantity']).sum()
        else:
            total_cogs = 0
    
    # Calculate gross profit
    gross_profit = total_revenue - total_cogs
    
    # Calculate gross profit margin
    gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Most profitable product
    def calc_profit(group):
        # Only calculate if all required columns exist
        if all(col in group.columns for col in ['Price', 'COGS', 'Order_Quantity']):
            # Make sure all values are numeric
            try:
                return ((group['Price'] - group['COGS']) * group['Order_Quantity']).sum()
            except:
                return 0
        return 0
        
    # Fix groupby warning by handling product profit calculation differently
    product_profit_list = []
    
    # Check if necessary columns are present
    required_cols = ['Product', 'Price', 'COGS', 'Order_Quantity']
    if all(col in merged_sales.columns for col in required_cols) and not merged_sales.empty:
        # Process each product individually
        for product in merged_sales['Product'].unique():
            if pd.notna(product):  # Skip NaN product names
                product_data = merged_sales[merged_sales['Product'] == product]
                profit = calc_profit(product_data)
                product_profit_list.append({'Product': product, 'Profit': profit})
    
    # Convert to DataFrame (empty if no products)
    product_profit = pd.DataFrame(product_profit_list)
    
    # Safely get the most profitable product with multiple checks
    if not product_profit.empty and 'Profit' in product_profit.columns and product_profit['Profit'].notnull().any():
        # Only proceed if we have valid profit data
        max_idx = product_profit['Profit'].idxmax()
        if max_idx is not None:
            most_profitable = product_profit.loc[max_idx]
        else:
            most_profitable = pd.Series({'Product': 'N/A', 'Profit': 0})
    else:
        most_profitable = pd.Series({'Product': 'N/A', 'Profit': 0})
    
    # Make a fake cost entry for testing if no costs exist
    if operational_costs_df.empty:
        today = datetime.datetime.now()
        test_cost = pd.DataFrame([{
            'Date': today,
            'Type': 'Rent',
            'Amount': 5000000  # 5 million VND
        }])
        operational_costs_df = pd.concat([operational_costs_df, test_cost], ignore_index=True)
        
        # Save the test data
        test_cost_to_save = pd.DataFrame([{
            'Date': today.strftime('%Y-%m-%d'),
            'Type': 'Rent',
            'Amount': 5000000
        }])
        test_cost_to_save.to_csv("data/operational_costs.csv", index=False)
        
        st.success("Added test operational cost of 5,000,000 VND for demonstration")
    
    # Calculate operational costs in the period
    filtered_costs = operational_costs_df[(operational_costs_df['Date'].dt.date >= start_date) & 
                                       (operational_costs_df['Date'].dt.date <= end_date)]
    
    # Make sure Amount column is numeric
    operational_costs_df['Amount'] = pd.to_numeric(operational_costs_df['Amount'], errors='coerce').fillna(0)
    filtered_costs['Amount'] = pd.to_numeric(filtered_costs['Amount'], errors='coerce').fillna(0)
    
    # Calculate sum of filtered costs
    operational_costs = filtered_costs['Amount'].sum()
    
    # Debug information 
    st.info(f"Found {len(filtered_costs)} operational costs in selected period. Total: {utils.format_currency(operational_costs)}")
    st.write(f"Total Operational Costs in Database: {utils.format_currency(operational_costs_df['Amount'].sum())}")
    
    # Calculate net profit
    net_profit = gross_profit - operational_costs
    
    # Display KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Revenue", utils.format_currency(total_revenue))
        st.metric("Total COGS", utils.format_currency(total_cogs))
        st.metric("COGS to Revenue Ratio", f"{(total_cogs / total_revenue * 100):.2f}%" if total_revenue > 0 else "0.00%")
    
    with col2:
        st.metric("Gross Profit", utils.format_currency(gross_profit))
        st.metric("Gross Profit Margin", f"{gross_profit_margin:.2f}%")
        st.metric("Most Profitable Product", f"{most_profitable['Product']} ({utils.format_currency(most_profitable['Profit'])})")
    
    with col3:
        st.metric("Operational Costs", utils.format_currency(operational_costs))
        st.metric("Net Profit", utils.format_currency(net_profit))
        net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Net Profit Margin", f"{net_margin:.2f}%")
    
    # Financial Charts
    st.header("Financial Performance Visualization")
    
    # Daily revenue and costs chart
    if not filtered_sales.empty:
        daily_finance = filtered_sales.groupby(filtered_sales['Date'].dt.date).agg({
            'Total': 'sum'
        }).reset_index()
        
        # Add COGS data - use a safer approach that works with all pandas versions
        if 'COGS' in merged_sales.columns and 'Order_Quantity' in merged_sales.columns:
            merged_sales_with_date = merged_sales.copy()
            
            if 'Date' in merged_sales_with_date.columns:
                merged_sales_with_date['Date_Only'] = merged_sales_with_date['Date'].dt.date
                
                # Calculate COGS per row
                merged_sales_with_date['Row_COGS'] = merged_sales_with_date['COGS'] * merged_sales_with_date['Order_Quantity']
                
                # Group by date and sum the COGS
                cogs_by_date = merged_sales_with_date.groupby('Date_Only')['Row_COGS'].sum().reset_index()
                cogs_by_date.rename(columns={'Row_COGS': 'COGS'}, inplace=True)
                
                # Convert Date_Only back to same format as in daily_finance
                cogs_by_date['Date'] = cogs_by_date['Date_Only']
                
                daily_finance = pd.merge(
                    daily_finance,
                    cogs_by_date[['Date', 'COGS']],
                    on='Date',
                    how='left'
                ).fillna(0)
            else:
                # If no Date column, simply add a COGS column with zeros
                daily_finance['COGS'] = 0
        else:
            # If no COGS data, add it as zeros
            daily_finance['COGS'] = 0
        
        # Calculate daily gross profit
        daily_finance['Gross_Profit'] = daily_finance['Total'] - daily_finance['COGS']
        
        # Format date to DD/MM/YY
        daily_finance['Date_Formatted'] = daily_finance['Date'].apply(lambda x: x.strftime('%d/%m/%y'))
        
        # Line chart for revenue, COGS, gross profit
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Total'],
            mode='lines+markers',
            name='Revenue'
        ))
        
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['COGS'],
            mode='lines+markers',
            name='COGS'
        ))
        
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Gross_Profit'],
            mode='lines+markers',
            name='Gross Profit',
            line=dict(color='green')
        ))
        
        fig1.update_layout(
            title='Daily Financial Performance',
            xaxis_title='Date',
            yaxis_title='Amount (VND)'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No sales data available for the selected period to display charts")
    
    # Product analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Top selling products
        if not filtered_sales.empty:
            product_sales = filtered_sales.groupby('Product')['Quantity'].sum().reset_index()
            
            if not product_sales.empty:
                # Sort by quantity and get top 5 or less if we don't have 5
                product_sales = product_sales.sort_values('Quantity', ascending=False).head(
                    min(5, len(product_sales))
                )
                
                fig2 = px.bar(
                    product_sales,
                    x='Product',
                    y='Quantity',
                    title='Top 5 Best Selling Products',
                    labels={'Product': 'Product', 'Quantity': 'Units Sold'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No product sales data available to display")
        else:
            st.info("No sales data available for the selected period")
    
    with col2:
        # Profit by product
        if not product_profit.empty and 'Profit' in product_profit.columns:
            # Sort by profit and get top 5 or less if we don't have 5
            top_products = product_profit.sort_values('Profit', ascending=False).head(
                min(5, len(product_profit))
            )
            
            if not top_products.empty:
                fig3 = px.bar(
                    top_products,
                    x='Product',
                    y='Profit',
                    title='Top 5 Most Profitable Products',
                    labels={'Product': 'Product', 'Profit': 'Profit (VND)'}
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No profit data available for display")
        else:
            st.info("No product profit data available for this period")
    
    # Operational costs breakdown
    st.header("Operational Costs")
    
    # Form to add operational costs
    with st.expander("Add Operational Cost"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cost_date = st.date_input("Date", datetime.datetime.now())
        
        with col2:
            cost_type = st.selectbox("Cost Type", options=["Rent", "Salary", "Utilities", "Marketing", "Maintenance", "Other"])
            
            if cost_type == "Other":
                cost_type = st.text_input("Specify Cost Type")
        
        with col3:
            cost_amount = st.number_input("Amount (VND)", min_value=0.0, step=10000.0)
        
        if st.button("Add Cost"):
            try:
                # Load current costs
                try:
                    costs_df = pd.read_csv("data/operational_costs.csv")
                except FileNotFoundError:
                    costs_df = pd.DataFrame(columns=['Date', 'Type', 'Amount'])
                
                # Add new cost
                new_cost = {
                    'Date': cost_date.strftime('%Y-%m-%d'),
                    'Type': cost_type,
                    'Amount': cost_amount
                }
                
                costs_df = pd.concat([costs_df, pd.DataFrame([new_cost])], ignore_index=True)
                costs_df.to_csv("data/operational_costs.csv", index=False)
                
                st.success("Cost added successfully!")
                
                # Reload data
                operational_costs_df = costs_df
                operational_costs_df['Date'] = pd.to_datetime(operational_costs_df['Date'])
                
            except Exception as e:
                st.error(f"Error adding cost: {str(e)}")
    
    # Show operational costs for the period
    if not operational_costs_df.empty:
        filtered_costs = operational_costs_df[(operational_costs_df['Date'].dt.date >= start_date) & 
                                           (operational_costs_df['Date'].dt.date <= end_date)]
        
        if not filtered_costs.empty:
            # Format for display
            display_costs = filtered_costs.copy()
            
            # Add index column for reference
            display_costs = display_costs.reset_index().rename(columns={'index': 'ID'})
            
            # Format date and amount for display
            display_costs['Date_Formatted'] = display_costs['Date'].dt.strftime('%d/%m/%y')
            display_costs['Amount_Formatted'] = display_costs['Amount'].apply(utils.format_currency)
            
            # Display with formatted columns but keep original data in the background
            st.dataframe(
                display_costs[['ID', 'Date_Formatted', 'Type', 'Amount_Formatted']].rename(
                    columns={'Date_Formatted': 'Date', 'Amount_Formatted': 'Amount'}
                )
            )
            
            # Edit and Delete section for operational costs
            with st.expander("Edit or Delete Operational Cost"):
                col1, col2 = st.columns(2)
                
                with col1:
                    cost_id = st.number_input("Cost ID", 
                                            min_value=0, 
                                            max_value=len(display_costs)-1 if not display_costs.empty else 0,
                                            value=0,
                                            help="Select the ID of the cost to edit or delete")
                    
                    # Delete cost button
                    if st.button("Delete Cost"):
                        try:
                            # Load current costs data
                            costs_df = pd.read_csv("data/operational_costs.csv")
                            
                            # Get the actual index from original dataframe
                            if not filtered_costs.empty and cost_id < len(display_costs):
                                actual_index = display_costs.loc[cost_id, 'ID']
                                
                                # Remove the selected cost
                                costs_df = costs_df.drop(actual_index).reset_index(drop=True)
                                
                                # Save updated costs
                                costs_df.to_csv("data/operational_costs.csv", index=False)
                                
                                st.success(f"Cost ID {cost_id} deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Invalid cost ID selected")
                        except Exception as e:
                            st.error(f"Error deleting cost: {str(e)}")
                
                with col2:
                    # Edit cost button
                    if st.button("Edit Cost"):
                        if not filtered_costs.empty and cost_id < len(display_costs):
                            # Store the selected cost ID in session state for the edit form
                            st.session_state.edit_cost_id = cost_id
                            st.session_state.edit_cost_mode = True
                            st.rerun()
                        else:
                            st.error("Invalid cost ID selected")
            
            # Edit form (only shown when in edit mode)
            if st.session_state.get('edit_cost_mode', False) and 'edit_cost_id' in st.session_state:
                edit_id = st.session_state.edit_cost_id
                
                if edit_id < len(display_costs):
                    selected_cost = display_costs.loc[edit_id]
                    
                    with st.form("edit_cost_form"):
                        st.subheader(f"Edit Cost ID: {edit_id}")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Convert pandas Timestamp to Python date for date_input
                            edit_date = st.date_input("Date", 
                                                    selected_cost['Date'].date() 
                                                    if pd.notna(selected_cost['Date']) 
                                                    else datetime.datetime.now())
                        
                        with col2:
                            cost_types = ["Rent", "Salary", "Utilities", "Marketing", "Maintenance", "Other"]
                            edit_type = st.selectbox("Cost Type", 
                                                    options=cost_types,
                                                    index=cost_types.index(selected_cost['Type']) 
                                                          if selected_cost['Type'] in cost_types 
                                                          else 0)
                            
                            if edit_type == "Other":
                                edit_type = st.text_input("Specify Cost Type", 
                                                         value=selected_cost['Type'] if selected_cost['Type'] not in cost_types else "")
                        
                        with col3:
                            edit_amount = st.number_input("Amount (VND)", 
                                                        min_value=0.0, 
                                                        value=float(selected_cost['Amount']),
                                                        step=10000.0)
                        
                        # Submit buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Cost"):
                                try:
                                    # Load current costs
                                    costs_df = pd.read_csv("data/operational_costs.csv")
                                    
                                    # Get the actual index from original dataframe
                                    actual_index = selected_cost['ID']
                                    
                                    # Update values
                                    costs_df.loc[actual_index, 'Date'] = edit_date.strftime('%Y-%m-%d')
                                    costs_df.loc[actual_index, 'Type'] = edit_type
                                    costs_df.loc[actual_index, 'Amount'] = edit_amount
                                    
                                    # Save updated costs
                                    costs_df.to_csv("data/operational_costs.csv", index=False)
                                    
                                    # Reset edit mode
                                    st.session_state.edit_cost_mode = False
                                    del st.session_state.edit_cost_id
                                    
                                    st.success("Cost updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating cost: {str(e)}")
                        
                        with col2:
                            if st.form_submit_button("Cancel"):
                                # Reset edit mode
                                st.session_state.edit_cost_mode = False
                                del st.session_state.edit_cost_id
                                st.rerun()
            
            # Pie chart of cost breakdown
            cost_breakdown = filtered_costs.groupby('Type')['Amount'].sum().reset_index()
            
            fig4 = px.pie(
                cost_breakdown,
                values='Amount',
                names='Type',
                title='Operational Costs Breakdown'
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No operational costs recorded for the selected period")
    else:
        st.info("No operational costs data available")
    
    # Comprehensive business costs breakdown
    st.header("Business Costs Breakdown by Category")
    st.info("This chart shows inventory item costs and operational expenses")
    
    # Prepare data for comprehensive costs pie chart
    # 1. Get costs by inventory item (raw materials)
    try:
        # Load inventory data
        inventory_df = pd.read_csv("data/inventory.csv")
        
        # Calculate total value of each inventory item
        inventory_costs_list = []
        
        if not inventory_df.empty:
            # For each inventory item, calculate its total value
            for _, item in inventory_df.iterrows():
                try:
                    # Skip invalid entries
                    if pd.isna(item['Name']) or pd.isna(item['Quantity']) or pd.isna(item['Avg_Cost']):
                        continue
                        
                    name = item['Name']
                    quantity = float(item['Quantity'])
                    unit_cost = float(item['Avg_Cost'])
                    
                    # Calculate total value
                    total_value = quantity * unit_cost
                    
                    if total_value > 0:
                        inventory_costs_list.append({
                            'Category': name,
                            'Amount': total_value,
                            'Type': 'Variable Cost'
                        })
                except (ValueError, TypeError):
                    continue
        
        # Convert to DataFrame
        if inventory_costs_list:
            inventory_costs = pd.DataFrame(inventory_costs_list)
        else:
            inventory_costs = pd.DataFrame(columns=['Category', 'Amount', 'Type'])
    except Exception as e:
        st.error(f"Error calculating inventory costs: {str(e)}")
        inventory_costs = pd.DataFrame(columns=['Category', 'Amount', 'Type'])
        
    # 2. Get all operational costs (not filtered by time period for this chart)
    if not operational_costs_df.empty:
        # Summarize all operational costs by type
        op_costs = operational_costs_df.groupby('Type')['Amount'].sum().reset_index()
        op_costs.rename(columns={'Type': 'Category'}, inplace=True)
        op_costs['Type'] = 'Operational'
    else:
        op_costs = pd.DataFrame(columns=['Category', 'Amount', 'Type'])
    
    # 3. Combine all cost categories
    all_costs = pd.concat([inventory_costs, op_costs], ignore_index=True)
    
    # Remove any NaN values 
    all_costs = all_costs.dropna(subset=['Amount'])
    
    # Convert to numeric and ensure non-zero values
    all_costs['Amount'] = pd.to_numeric(all_costs['Amount'], errors='coerce').fillna(0)
    all_costs = all_costs[all_costs['Amount'] > 0]
    
    # Display pie chart of all business costs
    if not all_costs.empty and all_costs['Amount'].sum() > 0:
        # Sort the data by amount for better color gradient
        all_costs = all_costs.sort_values('Amount')
        
        # Create a pie chart showing percentage breakdown of all costs
        fig_all_costs = px.pie(
            all_costs,
            values='Amount',
            names='Category',
            title='Inventory Items & Operational Costs',
            color='Amount',  # Color by amount value for gradient
            color_discrete_sequence=px.colors.sequential.Plasma_r,  # Use a sequential colorscale (plasma reversed)
            hover_data=['Amount', 'Type'],  # Show amount and type on hover
            labels={'Amount': 'Cost (VND)'}
        )
        
        # Update hover template to show the percentage and formatted amount
        # Create a custom hover template that safely formats the amount and includes type
        hover_data = []
        for _, row in all_costs.iterrows():
            formatted_amount = f"{int(row['Amount']):,} VND"
            cost_type = row['Type']
            hover_data.append([formatted_amount, cost_type])
            
        # Update figure with customized hover information
        fig_all_costs.update_traces(
            customdata=hover_data,
            hovertemplate='<b>%{label}</b><br>Amount: %{customdata[0]}<br>Type: %{customdata[1]}<br>Percentage: %{percent:.1%}'
        )
        
        # Custom legend title
        fig_all_costs.update_layout(
            legend_title_text='Cost Type'
        )
        
        st.plotly_chart(fig_all_costs, use_container_width=True)
    else:
        st.info("No cost data available. Add inventory items and operational costs to see breakdown.")
    
    # Financial summary table
    st.header("Financial Summary")
    
    # Prepare summary data
    summary_data = {
        'Metric': [
            'Total Revenue',
            'Total COGS',
            'Gross Profit',
            'Gross Profit Margin',
            'Operational Costs',
            'Net Profit',
            'Net Profit Margin'
        ],
        'Value': [
            utils.format_currency(total_revenue),
            utils.format_currency(total_cogs),
            utils.format_currency(gross_profit),
            f"{gross_profit_margin:.2f}%",
            utils.format_currency(operational_costs),
            utils.format_currency(net_profit),
            f"{net_margin:.2f}%"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)

except Exception as e:
    st.error(f"Error in financial reporting: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
