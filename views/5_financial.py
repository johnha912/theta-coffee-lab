import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import utils
import store

# Initialize session_state
utils.initialize_session_state()

header, period = st.columns([3, 2], vertical_alignment="bottom")
with header:
    st.title("Financial Report")
    st.caption("Financial KPIs and Analysis")

# Time filter
time_options = ["Today", "Last 7 Days", "Last 30 Days", "All Time", "Custom"]
# Ensure default_time_filter exists and is valid
if 'default_time_filter' not in st.session_state or st.session_state.default_time_filter not in time_options:
    st.session_state.default_time_filter = "Today"
with period, st.container(horizontal_alignment="right"):
    time_filter = st.segmented_control("Time Period", options=time_options, default=st.session_state.default_time_filter, required=True)

# Date range for custom filter
if time_filter == "Custom":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.datetime.now())
else:
    start_date, end_date = utils.get_date_range(time_filter)

try:
    # Load data
    sales_df = store.load("sales")
    products_df = store.load("products")
    product_recipe_df = store.load("product_recipe")
    
    # Load operational costs if available
    try:
        operational_costs_df = store.load("operational_costs")
        operational_costs_df['Date'] = pd.to_datetime(operational_costs_df['Date'])
    except FileNotFoundError:
        operational_costs_df = pd.DataFrame(columns=['Date', 'Type', 'Amount'])
        
    # Prepare sales data
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
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
        # Add Net_Total and Promo columns if they don't exist
        if 'Net_Total' not in filtered_sales.columns:
            filtered_sales['Net_Total'] = filtered_sales['Total']
        if 'Promo' not in filtered_sales.columns:
            filtered_sales['Promo'] = 0.0
        
        # Calculate revenue using Total (gross revenue before discounts)
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
        store.save("operational_costs", test_cost_to_save)
        
        st.success("Added test operational cost of 5,000,000 VND for demonstration")
    
    # Calculate operational costs in the period
    filtered_costs = operational_costs_df[(operational_costs_df['Date'].dt.date >= start_date) & 
                                       (operational_costs_df['Date'].dt.date <= end_date)]
    
    # Make sure Amount column is numeric
    operational_costs_df['Amount'] = pd.to_numeric(operational_costs_df['Amount'], errors='coerce').fillna(0)
    filtered_costs['Amount'] = pd.to_numeric(filtered_costs['Amount'], errors='coerce').fillna(0)
    
    # Calculate sum of filtered costs
    operational_costs = filtered_costs['Amount'].sum()
    
    st.caption(f"{len(filtered_costs)} operational costs in this period ({utils.format_currency(operational_costs)}); "
               f"{utils.format_currency(operational_costs_df['Amount'].sum())} recorded in total.")

    # Calculate financial metrics based on the formulas provided
    
    # 1. Revenue & Profit
    # Gross Revenue = Total sales revenue (before discounts, returns, taxes)
    gross_revenue = filtered_sales['Total'].sum()
    
    # Net Revenue = Gross Revenue - Discounts - Returns - VAT
    # In our case, we don't have returns or VAT, so Net Revenue = Gross Revenue - Promotions
    net_revenue = filtered_sales['Net_Total'].sum()
    
    # Gross Profit = Net Revenue - Cost of Goods Sold (COGS)
    gross_profit_correct = net_revenue - total_cogs
    
    # Operating Profit = Gross Profit - Selling Expenses - Administrative Expenses
    # In our system, we combine all operational costs together
    operating_profit = gross_profit_correct - operational_costs
    
    # Net Profit (After-tax profit) = Operating Profit - Financial Expenses - Corporate Income Tax
    # Since we don't track taxes or financial expenses separately, Net Profit = Operating Profit
    net_profit = operating_profit
    
    # Calculate revenue reduction due to promotions
    promo_percentage = ((gross_revenue - net_revenue) / gross_revenue * 100) if gross_revenue > 0 else 0
    # Gross Profit Margin = Gross Profit / Net Revenue
    gross_profit_margin = (gross_profit_correct / net_revenue * 100) if net_revenue > 0 else 0
    # Net Profit Margin = Net Profit / Net Revenue
    net_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0

    # Display KPIs: revenue, profit, and bottom-line rows
    kpi_rows = [
        [("Gross Revenue", utils.format_currency(gross_revenue), ":material/payments:"),
         ("Net Revenue", utils.format_currency(net_revenue), ":material/account_balance_wallet:"),
         ("Promotion Impact", f"{promo_percentage:.2f}%", ":material/sell:")],
        [("Total COGS", utils.format_currency(total_cogs), ":material/inventory:"),
         ("Gross Profit", utils.format_currency(gross_profit_correct), ":material/trending_up:"),
         ("Gross Profit Margin", f"{gross_profit_margin:.2f}%", ":material/percent:")],
        [("Operational Costs", utils.format_currency(operational_costs), ":material/storefront:"),
         ("Net Profit", utils.format_currency(net_profit), ":material/savings:"),
         ("Net Profit Margin", f"{net_margin:.2f}%", ":material/percent:")],
    ]
    for row in kpi_rows:
        for col, (label, value, icon) in zip(st.columns(3), row):
            col.metric(label, value, icon=icon, border=True)

    # Financial Charts
    st.header("Financial Performance Visualization")

    # Waterfall: how gross revenue turns into net profit for the period
    if gross_revenue > 0:
        mode = st.context.theme.type or "light"
        palette = st.get_option(f"theme.{mode}.chartCategoricalColors")
        steps = [("Gross Revenue", gross_revenue, "absolute"),
                 ("Promotions", -(gross_revenue - net_revenue), "relative"),
                 ("COGS", -total_cogs, "relative"),
                 ("Operational Costs", -operational_costs, "relative"),
                 ("Net Profit", net_profit, "total")]
        fig_flow = go.Figure(go.Waterfall(
            x=[name for name, _, _ in steps],
            y=[value for _, value, _ in steps],
            measure=[measure for _, _, measure in steps],
            text=[f"{value / 1e6:+,.2f}M" if measure == "relative" else f"{value / 1e6:,.2f}M"
                  for _, value, measure in steps],
            textposition="outside",
            customdata=[abs(value) for _, value, _ in steps],
            hovertemplate="<b>%{x}</b><br>%{customdata:,.0f} VND<extra></extra>",
            totals=dict(marker=dict(color=palette[0])),
            decreasing=dict(marker=dict(color=palette[1])),
            increasing=dict(marker=dict(color=palette[2])),
            connector=dict(line=dict(width=1, color="rgba(128,128,128,0.4)")),
        ))
        fig_flow.update_layout(title="From Gross Revenue to Net Profit", yaxis_title="Amount (VND)",
                               showlegend=False, height=420)
        utils.chart(fig_flow)
    
    # Daily revenue and costs chart
    if not filtered_sales.empty:
        # Check if Net_Total column exists
        if 'Net_Total' in filtered_sales.columns:
            daily_finance = filtered_sales.groupby(filtered_sales['Date'].dt.date).agg({
                'Total': 'sum',
                'Net_Total': 'sum',
                'Promo': 'sum'
            }).reset_index()
        else:
            # Fallback to only Total for backward compatibility
            daily_finance = filtered_sales.groupby(filtered_sales['Date'].dt.date).agg({
                'Total': 'sum'
            }).reset_index()
            # Add placeholder columns
            daily_finance['Net_Total'] = daily_finance['Total']
            daily_finance['Promo'] = 0
        
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
        
        # Calculate daily financial metrics properly
        daily_finance['Net_Revenue'] = daily_finance['Net_Total']
        
        # Gross Profit = Net Revenue - COGS (using the correct formula from accounting principles)
        daily_finance['Gross_Profit'] = daily_finance['Net_Revenue'] - daily_finance['COGS']
        
        # Also calculate daily operating profit (would need operational costs data by day but we don't have that)
        # So we'll just make an estimate by distributing operational costs equally across the days
        if len(daily_finance) > 0 and operational_costs > 0:
            daily_op_cost = operational_costs / len(daily_finance)
            daily_finance['Operating_Profit'] = daily_finance['Gross_Profit'] - daily_op_cost
        else:
            daily_finance['Operating_Profit'] = daily_finance['Gross_Profit']
        
        # Format date to DD/MM/YY
        daily_finance['Date_Formatted'] = daily_finance['Date'].apply(lambda x: x.strftime('%d/%m/%y'))
        
        # Line chart for revenue, COGS, gross profit
        fig1 = go.Figure()
        
        # Show both Total (Gross Revenue) and Net_Total after promotions
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Total'],
            mode='lines+markers',
            name='Gross Revenue'
        ))
        
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Net_Total'],
            mode='lines+markers',
            name='Net Revenue'
        ))
        
        # Show Promotions as a bar chart below
        fig1.add_trace(go.Bar(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Promo'],
            name='Promotions'
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
            name='Gross Profit'
        ))
        
        fig1.update_layout(
            title='Daily Financial Performance',
            xaxis_title='Date',
            yaxis_title='Amount (VND)',
            hovermode='x unified'
        )
        
        utils.chart(fig1)
    else:
        st.info("No sales data available for the selected period to display charts")
    
    # Product analysis: two headline tiles, then two same-height rankings
    if not filtered_sales.empty:
        units = filtered_sales.groupby('Product')['Quantity'].sum()
        tiles = st.columns(2)
        tiles[0].metric("Best Selling Product", units.idxmax(), f"{int(units.max())} units",
                        delta_color="off", delta_arrow="off", icon=":material/local_cafe:", border=True)
        tiles[1].metric("Most Profitable Product", most_profitable['Product'], utils.format_currency(most_profitable['Profit']),
                        delta_color="off", delta_arrow="off", icon=":material/workspace_premium:", border=True)

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
                
                fig2 = utils.hbar(product_sales, 'Quantity', 'Product', 'Top 5 Best Selling Products',
                                  labels={'Quantity': 'Units Sold'}, height=360)
                utils.chart(fig2)
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
                fig3 = utils.hbar(top_products, 'Profit', 'Product', 'Top 5 Most Profitable Products',
                                  labels={'Profit': 'Profit (VND)'}, height=360)
                utils.chart(fig3)
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
                    costs_df = store.load("operational_costs")
                except FileNotFoundError:
                    costs_df = pd.DataFrame(columns=['Date', 'Type', 'Amount'])
                
                # Add new cost
                new_cost = {
                    'Date': cost_date.strftime('%Y-%m-%d'),
                    'Type': cost_type,
                    'Amount': cost_amount
                }
                
                costs_df = pd.concat([costs_df, pd.DataFrame([new_cost])], ignore_index=True)
                store.save("operational_costs", costs_df)
                
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
                            costs_df = store.load("operational_costs")
                            
                            # Get the actual index from original dataframe
                            if not filtered_costs.empty and cost_id < len(display_costs):
                                actual_index = display_costs.loc[cost_id, 'ID']
                                
                                # Remove the selected cost
                                costs_df = costs_df.drop(actual_index).reset_index(drop=True)
                                
                                # Save updated costs
                                store.save("operational_costs", costs_df)
                                
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
                                    costs_df = store.load("operational_costs")
                                    
                                    # Get the actual index from original dataframe
                                    actual_index = selected_cost['ID']
                                    
                                    # Update values
                                    costs_df.loc[actual_index, 'Date'] = edit_date.strftime('%Y-%m-%d')
                                    costs_df.loc[actual_index, 'Type'] = edit_type
                                    costs_df.loc[actual_index, 'Amount'] = edit_amount
                                    
                                    # Save updated costs
                                    store.save("operational_costs", costs_df)
                                    
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
            
            fig4 = utils.hbar(cost_breakdown, 'Amount', 'Type', 'Operational Costs Breakdown',
                              labels={'Amount': 'Cost (VND)'})
            utils.chart(fig4)
        else:
            st.info("No operational costs recorded for the selected period")
    else:
        st.info("No operational costs data available")
    
    # Comprehensive business costs breakdown
    st.header("Business Costs Breakdown by Category")
    st.caption("Each tile's area is its share of total spend. Click a group to zoom in; click the top bar to zoom out.")
    
    # Prepare data for comprehensive costs pie chart
    # 1. Get costs by inventory item (raw materials)
    try:
        # Load inventory data
        inventory_df = store.load("inventory")
        
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
    
    # Treemap: cost type -> item, sized by spend (35+ items fit where a bar list would scroll)
    if not all_costs.empty and all_costs['Amount'].sum() > 0:
        # Soft tints of the theme's first two series colors keep large tiles calm and text readable
        mode = st.context.theme.type or "light"
        palette = st.get_option(f"theme.{mode}.chartCategoricalColors")
        tint = lambda c: f"rgba({int(c[1:3], 16)}, {int(c[3:5], 16)}, {int(c[5:7], 16)}, 0.4)"
        fig_all_costs = px.treemap(
            all_costs,
            path=[px.Constant("All costs"), 'Type', 'Category'],
            values='Amount',
            color='Type',
            color_discrete_map={"(?)": "rgba(0,0,0,0)", "Variable Cost": tint(palette[0]), "Operational": tint(palette[1])},
            title='Inventory Items & Operational Costs',
            height=560
        )
        fig_all_costs.update_traces(
            marker=dict(cornerradius=4, line=dict(width=2)),
            textfont=dict(color=st.get_option(f"theme.{mode}.textColor")),
            tiling=dict(pad=4),
            texttemplate="<b>%{label}</b><br>%{value:,.0f} VND<br>%{percentRoot:.1%}",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} VND<br>%{percentRoot:.1%} of all costs<extra></extra>",
        )
        utils.chart(fig_all_costs)
        with st.expander("Show as table"):
            st.dataframe(
                all_costs.sort_values('Amount', ascending=False).assign(
                    Share=lambda d: d['Amount'] / d['Amount'].sum()),
                hide_index=True,
                column_config={"Amount": st.column_config.NumberColumn("Cost (VND)", format="%,.0f"),
                               "Share": st.column_config.NumberColumn(format="percent")},
            )
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
