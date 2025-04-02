import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import utils

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
    
    # Calculate revenue
    total_revenue = filtered_sales['Total'].sum()
    
    # Calculate COGS
    filtered_sales_copy = filtered_sales.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
    merged_sales = pd.merge(filtered_sales_copy, products_df, left_on='Product', right_on='Name')
    total_cogs = (merged_sales['COGS'] * merged_sales['Order_Quantity']).sum()
    
    # Calculate gross profit
    gross_profit = total_revenue - total_cogs
    
    # Calculate gross profit margin
    gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Most profitable product
    product_profit = merged_sales.groupby('Product').apply(
        lambda x: (x['Price'] - x['COGS']) * x['Order_Quantity']
    ).reset_index(name='Profit')
    
    most_profitable = product_profit.loc[product_profit['Profit'].idxmax()] if not product_profit.empty else pd.Series({'Product': 'N/A', 'Profit': 0})
    
    # Calculate operational costs in the period
    if not operational_costs_df.empty:
        filtered_costs = operational_costs_df[(operational_costs_df['Date'].dt.date >= start_date) & 
                                           (operational_costs_df['Date'].dt.date <= end_date)]
        operational_costs = filtered_costs['Amount'].sum()
    else:
        operational_costs = 0
    
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
    daily_finance = filtered_sales.groupby(filtered_sales['Date'].dt.date).agg({
        'Total': 'sum'
    }).reset_index()
    
    # Add COGS data
    daily_finance = pd.merge(
        daily_finance,
        merged_sales.groupby(merged_sales['Date'].dt.date).apply(
            lambda x: (x['COGS'] * x['Order_Quantity']).sum()
        ).reset_index(name='COGS'),
        on='Date',
        how='left'
    ).fillna(0)
    
    # Calculate daily gross profit
    daily_finance['Gross_Profit'] = daily_finance['Total'] - daily_finance['COGS']
    
    # Line chart for revenue, COGS, gross profit
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=daily_finance['Date'],
        y=daily_finance['Total'],
        mode='lines+markers',
        name='Revenue'
    ))
    
    fig1.add_trace(go.Scatter(
        x=daily_finance['Date'],
        y=daily_finance['COGS'],
        mode='lines+markers',
        name='COGS'
    ))
    
    fig1.add_trace(go.Scatter(
        x=daily_finance['Date'],
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
    
    # Product analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Top selling products
        product_sales = filtered_sales.groupby('Product')['Quantity'].sum().reset_index()
        product_sales = product_sales.sort_values('Quantity', ascending=False).head(5)
        
        fig2 = px.bar(
            product_sales,
            x='Product',
            y='Quantity',
            title='Top 5 Best Selling Products',
            labels={'Product': 'Product', 'Quantity': 'Units Sold'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Profit by product
        fig3 = px.bar(
            product_profit.sort_values('Profit', ascending=False).head(5),
            x='Product',
            y='Profit',
            title='Top 5 Most Profitable Products',
            labels={'Product': 'Product', 'Profit': 'Profit (VND)'}
        )
        st.plotly_chart(fig3, use_container_width=True)
    
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
            display_costs['Date'] = display_costs['Date'].dt.strftime('%Y-%m-%d')
            display_costs['Amount'] = display_costs['Amount'].apply(utils.format_currency)
            
            st.dataframe(display_costs)
            
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
