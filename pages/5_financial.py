import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import datetime
import utils
import numpy as np
import os

# Khởi tạo session_state
utils.initialize_session_state()

# Set dark theme for modern financial dashboard appearance
pio.templates.default = 'plotly_dark'

# Create a custom dark theme
custom_dark_template = pio.templates['plotly_dark']
custom_dark_template.layout.update(
    paper_bgcolor='#1E1E1E',  # Dark background
    plot_bgcolor='#1E1E1E',   # Dark plot area
    font=dict(color='#FFFFFF'),
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)',
        gridwidth=0.5
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)',
        gridwidth=0.5
    )
)
pio.templates['custom_dark'] = custom_dark_template
pio.templates.default = 'custom_dark'

# Custom CSS for the financial dashboard based on the dark theme inspiration
custom_css = """
<style>
    .dashboard-title {
        text-align: left;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: white;
    }
    
    .metric-card {
        background-color: #2C2C2C;
        border-radius: 6px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 16px;
        border-left: 3px solid #444;
        height: 100%;
    }
    
    .metric-title {
        font-size: 0.8rem;
        font-weight: 400;
        margin-bottom: 5px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .metric-positive {
        color: #72f879;
    }
    
    .metric-negative {
        color: #ff5757;
    }
    
    .metric-trend {
        font-size: 0.8rem;
        display: flex;
        align-items: center;
    }
    
    .profit-card {
        padding: 18px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .profit-positive {
        background-color: rgba(114, 248, 121, 0.05);
        border-left: 3px solid #72f879;
    }
    
    .profit-negative {
        background-color: rgba(255, 87, 87, 0.05);
        border-left: 3px solid #ff5757;
    }
    
    .profit-status {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .profit-amount {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .profit-percent {
        font-size: 1rem;
        margin-bottom: 10px;
        opacity: 0.8;
    }
    
    .chart-container {
        background-color: #2C2C2C;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        height: 100%;
    }
    
    .chart-title {
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 15px;
        color: #CCC;
        text-align: left;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .dashboard-divider {
        margin: 24px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .main-dashboard {
        padding: 20px;
        background-color: #121212;
        border-radius: 6px;
    }
    
    .period-label {
        color: #888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .period-value {
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    
    .section-header {
        font-size: 1rem;
        color: #CCC;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-left: 3px solid #666;
        padding-left: 10px;
        margin: 30px 0 15px 0;
    }
    
    /* Custom styling for Streamlit components */
    div[data-testid="stSelectbox"] > div > div {
        background-color: #333;
        border: none;
        color: white;
    }
    
    div[data-testid="stDateInput"] > div > div {
        background-color: #333;
        border: none;
        color: white;
    }
    
    .big-metric {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
    }
    
    .big-metric-trend-up {
        color: #72f879;
        font-size: 0.9rem;
        margin-left: 10px;
    }
    
    .big-metric-trend-down {
        color: #ff5757;
        font-size: 0.9rem;
        margin-left: 10px;
    }
    
    .table-container {
        background-color: #2C2C2C;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 20px;
    }
    
    .table-header {
        color: #888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding-bottom: 10px;
        border-bottom: 1px solid #333;
    }
</style>
"""

st.set_page_config(page_title="Financial Dashboard", page_icon="📊", layout="wide")

# Apply custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Main dashboard container
with st.container():
    # Dashboard Title
    st.markdown('<div class="main-dashboard">', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Financial Dashboard</div>', unsafe_allow_html=True)
    
    # Date filter section
    with st.container():
        st.markdown('<div class="section-header">SELECT TIME PERIOD</div>', unsafe_allow_html=True)
        
        # Time filter
        time_options = ["Today", "Last 7 Days", "Last 30 Days", "All Time", "Custom"]
        # Ensure default_time_filter exists and is valid
        if 'default_time_filter' not in st.session_state or st.session_state.default_time_filter not in time_options:
            st.session_state.default_time_filter = "Today"
        
        # Use full width for the select box
        time_filter = st.selectbox("Select Period", options=time_options, index=time_options.index(st.session_state.default_time_filter))
        
        # Date range for custom filter
        if time_filter == "Custom":
            date_cols = st.columns([1, 1])
            with date_cols[0]:
                start_date = st.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=7))
            with date_cols[1]:
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
            elif time_filter == "All Time":
                # Set to a very old date for "All Time"
                start_date = datetime.datetime(2020, 1, 1).date()
            
            # Display the date range below the dropdown with full width
            st.markdown(
                f"""<div style="background-color: #2C2C2C; padding: 12px; border-radius: 4px; margin-top: 10px; text-align: center;">
                    <span style="color: #fff;">Date Range: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}</span>
                </div>""", 
                unsafe_allow_html=True
            )

    try:
        # Create error message for debugging
        error_msg = ""
        
        # Check if data files exist
        files_to_check = {
            "data/sales.csv": "sales.csv",
            "data/products.csv": "products.csv",
            "data/product_recipe.csv": "product_recipe.csv"
        }
        
        missing_files = []
        for file_path, file_name in files_to_check.items():
            if not os.path.exists(file_path):
                missing_files.append(file_name)
        
        if missing_files:
            error_msg = f"Missing required data files: {', '.join(missing_files)}"
            st.error(error_msg)
            st.info("If this is your first time running the app, make sure all required data files exist in the 'data' directory.")
            st.stop()
        
        # Load data with error handling
        try:
            sales_df = pd.read_csv("data/sales.csv")
            error_msg += "Sales data loaded. "
        except Exception as e:
            st.error(f"Error loading sales.csv: {str(e)}")
            st.stop()
            
        try:
            products_df = pd.read_csv("data/products.csv")
            error_msg += "Products data loaded. "
        except Exception as e:
            st.error(f"Error loading products.csv: {str(e)}")
            st.stop()
            
        try:
            product_recipe_df = pd.read_csv("data/product_recipe.csv")
            error_msg += "Recipe data loaded. "
        except Exception as e:
            st.error(f"Error loading product_recipe.csv: {str(e)}")
            st.stop()
        
        # Load operational costs if available
        try:
            operational_costs_df = pd.read_csv("data/operational_costs.csv")
            operational_costs_df['Date'] = pd.to_datetime(operational_costs_df['Date'])
            error_msg += "Operational costs loaded. "
        except Exception:
            # If operational costs file doesn't exist or has errors, create empty DataFrame
            operational_costs_df = pd.DataFrame(columns=['Date', 'Type', 'Amount'])
            error_msg += "Created empty operational costs. "
            
        # Validate and fix column names in products_df
        required_cols = ['Product', 'COGS']
        for col in required_cols:
            if col not in products_df.columns:
                # Check if there's a 'Name' column that should be 'Product'
                if col == 'Product' and 'Name' in products_df.columns:
                    products_df['Product'] = products_df['Name']
                    error_msg += "Renamed 'Name' to 'Product' in products data. "
                else:
                    products_df[col] = 0
                    error_msg += f"Added missing column '{col}' to products data. "
            
        # Prepare sales data
        try:
            sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
            filtered_sales = sales_df[(sales_df['Date'].dt.date >= start_date) & 
                                    (sales_df['Date'].dt.date <= end_date)]
            error_msg += "Sales data filtered by date. "
        except Exception as e:
            st.error(f"Error processing dates in sales data: {str(e)}")
            filtered_sales = pd.DataFrame(columns=sales_df.columns)
            error_msg += "Created empty filtered sales data due to date error. "
        
        # Financial summary section
        summary_container = st.container()
        with summary_container:
            # Calculate financial metrics
            # Check if filtered_sales is empty
            if filtered_sales.empty:
                net_revenue = 0
                gross_revenue = 0
                total_orders = 0
                promo_total = 0
                promo_percentage = 0
                net_profit = 0
                total_cogs = 0
                operational_costs = 0
            else:
                # Prepare data for calculations, adding missing columns if needed
                if 'Promo' not in filtered_sales.columns:
                    filtered_sales['Promo'] = 0
                if 'Net_Total' not in filtered_sales.columns:
                    filtered_sales['Net_Total'] = filtered_sales['Total']
                
                # Calculate metrics
                gross_revenue = filtered_sales['Total'].sum()
                promo_total = filtered_sales['Promo'].fillna(0).sum()
                net_revenue = filtered_sales['Net_Total'].fillna(0).sum()
                total_orders = len(filtered_sales)
                promo_percentage = (promo_total / gross_revenue * 100) if gross_revenue > 0 else 0
                
                # Filter operational costs for the selected period
                filtered_costs = operational_costs_df[(operational_costs_df['Date'].dt.date >= start_date) & 
                                                    (operational_costs_df['Date'].dt.date <= end_date)]
                
                # Calculate operational costs
                operational_costs = filtered_costs['Amount'].sum() if not filtered_costs.empty else 0
                
                # Calculate COGS (Cost of Goods Sold)
                # Merge sales with products to get COGS information
                merged_sales = pd.merge(filtered_sales, 
                                        products_df[['Product', 'COGS']], 
                                        on='Product', 
                                        how='left')
                
                # Calculate total COGS
                merged_sales['Total_COGS'] = merged_sales['Quantity'] * merged_sales['COGS']
                total_cogs = merged_sales['Total_COGS'].sum()
                
                # Calculate net profit
                net_profit = net_revenue - total_cogs - operational_costs
            
            # Current period revenue and order count
            revenue_col1, revenue_col2 = st.columns([3, 1])
            
            with revenue_col1:
                # Big revenue display 
                trend_indicator = "+" if net_revenue > 0 else ""
                st.markdown(f"""
                <div style="margin-bottom: 25px; padding: 18px; background-color: #2C2C2C; border-radius: 6px; height: 130px;">
                    <div class="period-label">CURRENT PERIOD REVENUE</div>
                    <div class="big-metric">{utils.format_currency(net_revenue, include_currency=False)}</div>
                    <span class="big-metric-trend-up">{trend_indicator}{promo_percentage:.1f}% vs previous period</span>
                </div>
                """, unsafe_allow_html=True)
            
            with revenue_col2:
                # Sales count with matching height
                st.markdown(f"""
                <div style="margin-bottom: 25px; padding: 18px; background-color: #2C2C2C; border-radius: 6px; height: 130px;">
                    <div class="period-label">TOTAL ORDERS</div>
                    <div class="big-metric">{total_orders}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Profit Status Card
            if net_profit > 0:
                st.markdown(f"""
                <div class="profit-card profit-positive">
                    <div class="profit-status">YOUR BUSINESS IS PROFITABLE</div>
                    <div class="profit-amount">{utils.format_currency(net_profit)}</div>
                    <div class="profit-percent">PROFIT</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="profit-card profit-negative">
                    <div class="profit-status">YOUR BUSINESS IS OPERATING AT A LOSS</div>
                    <div class="profit-amount">{utils.format_currency(net_profit)}</div>
                    <div class="profit-percent">LOSS</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Financial metrics KPIs
            st.markdown('<div class="section-header">FINANCIAL METRICS</div>', unsafe_allow_html=True)
            
            # Create KPI cards in a grid with equal sizing
            kpi_cols = st.columns(4)
            
            # Gross Profit KPI
            gross_profit = net_revenue - total_cogs
            gross_margin = (gross_profit / net_revenue * 100) if net_revenue > 0 else 0
            
            with kpi_cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">GROSS PROFIT</div>
                    <div class="metric-value metric-positive">{utils.format_currency(gross_profit)}</div>
                    <div class="metric-trend">{gross_margin:.1f}% margin</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Net Profit KPI
            net_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0
            profit_class = "metric-positive" if net_profit >= 0 else "metric-negative"
            
            with kpi_cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">NET PROFIT</div>
                    <div class="metric-value {profit_class}">{utils.format_currency(net_profit)}</div>
                    <div class="metric-trend">{net_margin:.1f}% margin</div>
                </div>
                """, unsafe_allow_html=True)
            
            # COGS KPI
            cogs_percentage = (total_cogs / net_revenue * 100) if net_revenue > 0 else 0
            
            with kpi_cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">COST OF GOODS</div>
                    <div class="metric-value">{utils.format_currency(total_cogs)}</div>
                    <div class="metric-trend">{cogs_percentage:.1f}% of revenue</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Operational Costs KPI
            op_costs_percentage = (operational_costs / net_revenue * 100) if net_revenue > 0 else 0
            
            with kpi_cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">OPERATIONAL COSTS</div>
                    <div class="metric-value">{utils.format_currency(operational_costs)}</div>
                    <div class="metric-trend">{op_costs_percentage:.1f}% of revenue</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Create a divider between sections
        st.markdown('<div class="dashboard-divider"></div>', unsafe_allow_html=True)
        
        # Revenue and cost breakdown
        st.markdown('<div class="section-header">REVENUE & COST BREAKDOWN</div>', unsafe_allow_html=True)
        
        # Create revenue and cost breakdown charts
        rev_cost_cols = st.columns([1, 1])
        
        # Revenue breakdown chart
        with rev_cost_cols[0]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">REVENUE BY PRODUCT</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty:
                # Group by product and calculate revenue
                product_revenue = filtered_sales.groupby('Product')['Net_Total'].sum().reset_index()
                
                # Sort from smallest to largest
                product_revenue = product_revenue.sort_values('Net_Total')
                
                # Create a color gradient from light to dark
                colors = px.colors.sequential.Blues[-len(product_revenue):]
                
                # Create the horizontal bar chart
                fig = px.bar(
                    product_revenue, 
                    y='Product',
                    x='Net_Total',
                    orientation='h',
                    color='Net_Total',
                    color_continuous_scale=colors,
                    labels={'Net_Total': 'Revenue (VND)', 'Product': ''},
                    text_auto='.2s'
                )
                
                # Update the layout for better appearance
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    coloraxis_showscale=False,
                    height=400,
                    font=dict(size=12),
                )
                
                # Format the text to display formatted numbers
                fig.update_traces(
                    texttemplate='%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Revenue: %{x:,.0f} VND<extra></extra>'
                )
                
                fig.update_xaxes(
                    title_text='',
                    tickformat=',d',
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available for the selected period")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Cost breakdown chart (Operational costs by type)
        with rev_cost_cols[1]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">BUSINESS COSTS BREAKDOWN</div>', unsafe_allow_html=True)
            
            # Check if there's cost data
            if not filtered_costs.empty:
                # Group costs by type
                cost_breakdown = pd.concat([
                    pd.DataFrame([{'Type': 'Variable Cost', 'Amount': total_cogs}]),
                    filtered_costs[['Type', 'Amount']]
                ])
                
                # Sort from smallest to largest
                cost_breakdown = cost_breakdown.sort_values('Amount')
                
                # Create a color gradient from light to dark
                colors = px.colors.sequential.Reds[-len(cost_breakdown):]
                
                # Create the bar chart
                fig = px.bar(
                    cost_breakdown, 
                    y='Type',
                    x='Amount',
                    orientation='h',
                    color='Amount',
                    color_continuous_scale=colors,
                    labels={'Amount': 'Cost (VND)', 'Type': ''},
                    text_auto='.2s'
                )
                
                # Update the layout for better appearance
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    coloraxis_showscale=False,
                    height=400,
                    font=dict(size=12),
                )
                
                # Format the text
                fig.update_traces(
                    texttemplate='%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Cost: %{x:,.0f} VND<extra></extra>'
                )
                
                fig.update_xaxes(
                    title_text='',
                    tickformat=',d',
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cost data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Create a divider between sections
        st.markdown('<div class="dashboard-divider"></div>', unsafe_allow_html=True)
        
        # Product profitability section
        st.markdown('<div class="section-header">PROFITABILITY ANALYSIS</div>', unsafe_allow_html=True)
        
        # Create profitability analysis charts
        profitability_cols = st.columns([1, 1])
        
        # Product Profit chart
        with profitability_cols[0]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PRODUCT PROFITABILITY</div>', unsafe_allow_html=True)
            
            # Calculate profit by product
            if not filtered_sales.empty and 'COGS' in merged_sales.columns:
                # Calculate profit for each sale
                merged_sales['Product_Profit'] = merged_sales['Net_Total'] - merged_sales['Total_COGS']
                
                # Group by product
                product_profit = merged_sales.groupby('Product')[['Net_Total', 'Total_COGS', 'Product_Profit']].sum().reset_index()
                
                if not product_profit.empty:
                    # Sort from smallest to largest
                    product_profit_sorted = product_profit.sort_values('Product_Profit')
                    
                    # Create the colors list with red for negative and green for positive
                    colors = []
                    for profit in product_profit_sorted['Product_Profit']:
                        if profit < 0:
                            colors.append('#ff5757')  # Red for loss
                        else:
                            colors.append('#72f879')  # Green for profit
                    
                    # Create the horizontal bar chart for product profit
                    fig = px.bar(
                        product_profit_sorted, 
                        y='Product',
                        x='Product_Profit',
                        orientation='h',
                        color='Product_Profit',
                        color_continuous_scale=[[0, 'rgba(255, 87, 87, 0.7)'], [0.5, 'rgba(255, 87, 87, 0.7)'], [0.5, 'rgba(114, 248, 121, 0.7)'], [1, 'rgba(114, 248, 121, 0.7)']],
                        labels={'Product_Profit': 'Profit (VND)', 'Product': ''},
                        text_auto='.2s'
                    )
                    
                    # Update the layout for better appearance
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=30, b=20),
                        coloraxis_showscale=False,
                        height=400,
                        font=dict(size=12),
                    )
                    
                    # Format the text
                    fig.update_traces(
                        texttemplate='%{text:,.0f}',
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Profit: %{x:,.0f} VND<extra></extra>'
                    )
                    
                    fig.update_xaxes(
                        title_text='',
                        tickformat=',d',
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No profit data available for the selected period")
            else:
                st.info("No sales or COGS data available for the selected period")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Profit Waterfall chart
        with profitability_cols[1]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PROFIT WATERFALL</div>', unsafe_allow_html=True)
            
            # Create waterfall chart data
            waterfall_data = pd.DataFrame([
                {'Step': 'Gross Revenue', 'Amount': gross_revenue, 'Type': 'Total'},
                {'Step': 'Promotions', 'Amount': -promo_total, 'Type': 'Negative'},
                {'Step': 'Net Revenue', 'Amount': net_revenue, 'Type': 'Total'},
                {'Step': 'COGS', 'Amount': -total_cogs, 'Type': 'Negative'},
                {'Step': 'Gross Profit', 'Amount': gross_profit, 'Type': 'Total'},
                {'Step': 'Operational Costs', 'Amount': -operational_costs, 'Type': 'Negative'},
                {'Step': 'Net Profit', 'Amount': net_profit, 'Type': 'Total'}
            ])
            
            # Create the waterfall chart
            fig = go.Figure(go.Waterfall(
                name="Financial Waterfall",
                orientation="v",
                measure=waterfall_data['Type'],
                x=waterfall_data['Step'],
                y=waterfall_data['Amount'],
                textposition="outside",
                text=waterfall_data['Amount'].apply(lambda x: f"{x:,.0f}"),
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": "#ff5757"}},
                increasing={"marker": {"color": "#72f879"}},
                totals={"marker": {"color": "#4a9af5"}}
            ))
            
            # Update the layout for better appearance
            fig.update_layout(
                title=None,
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20),
                height=400,
                font=dict(size=12),
                yaxis=dict(
                    title="Amount (VND)",
                    tickformat=",d",
                    showgrid=True,
                    gridcolor="rgba(255, 255, 255, 0.1)",
                    zeroline=True,
                    zerolinecolor="rgba(255, 255, 255, 0.2)",
                    zerolinewidth=1
                ),
                xaxis=dict(
                    title="",
                    tickangle=0
                ),
                plot_bgcolor="#1E1E1E",
                paper_bgcolor="#1E1E1E"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Third row for financial charts
        financial_cols3 = st.columns([1, 1])
        
        # Profit split donut chart
        with financial_cols3[0]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PROFIT DISTRIBUTION</div>', unsafe_allow_html=True)
            
            # Create data for donut chart
            total_value = gross_revenue
            if total_value > 0:
                # Calculate percentages for each component
                cogs_pct = total_cogs / total_value * 100
                op_costs_pct = operational_costs / total_value * 100
                profit_pct = net_profit / total_value * 100 if net_profit > 0 else 0
                loss_pct = -net_profit / total_value * 100 if net_profit < 0 else 0
                
                # Labels and values for the donut chart
                labels = []
                values = []
                colors = []
                
                # Add COGS
                labels.append(f"COGS ({cogs_pct:.1f}%)")
                values.append(cogs_pct)
                colors.append('#4a9af5')  # Blue for COGS
                
                # Add Operational Costs
                if operational_costs > 0:
                    labels.append(f"Operational Costs ({op_costs_pct:.1f}%)")
                    values.append(op_costs_pct)
                    colors.append('#f5a742')  # Orange for operational costs
                
                # Add Net Profit/Loss
                if net_profit >= 0:
                    labels.append(f"Net Profit ({profit_pct:.1f}%)")
                    values.append(profit_pct)
                    colors.append('#72f879')  # Green for profit
                else:
                    labels.append(f"Net Loss ({loss_pct:.1f}%)")
                    values.append(loss_pct)
                    colors.append('#ff5757')  # Red for loss
                
                # Create the donut chart
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.65,
                    marker_colors=colors,
                    textinfo='percent',
                    textfont=dict(size=12, color='white'),
                    hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>"
                )])
                
                # Add the center text with total revenue
                fig.add_annotation(
                    text=f"{total_value:,.0f}<br>Total Revenue",
                    font=dict(size=14, color='white', family="Arial"),
                    showarrow=False,
                    x=0.5,
                    y=0.5
                )
                
                # Update the layout for better appearance
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=11)
                    ),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No revenue data available for the selected period")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Daily Revenue Breakdown
        with financial_cols3[1]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">DAILY REVENUE BREAKDOWN</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty and 'Date' in filtered_sales.columns:
                # Calculate daily revenue by product
                product_daily = filtered_sales.groupby(['Date', 'Product'])['Net_Total'].sum().reset_index()
                
                # Format the date for display
                product_daily['Date_Formatted'] = product_daily['Date'].dt.strftime('%d/%m/%y')
                
                # Create stacked bar chart
                fig = px.bar(
                    product_daily,
                    x='Date_Formatted',
                    y='Net_Total',
                    color='Product',
                    labels={'Net_Total': 'Revenue (VND)', 'Date_Formatted': 'Date'},
                    category_orders={"Date_Formatted": sorted(product_daily['Date_Formatted'].unique())},
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                # Update the layout for better appearance
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=50),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=11)
                    ),
                    barmode='stack',
                    height=400,
                    font=dict(size=12),
                )
                
                # Format the y-axis
                fig.update_yaxes(
                    title_text='',
                    tickformat=',d',
                )
                
                # Format the x-axis
                fig.update_xaxes(
                    title_text='',
                    tickangle=45,
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daily sales data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Fourth row for financial analysis
        financial_cols4 = st.columns([1, 1])
        
        # Profit Margins Analysis
        with financial_cols4[0]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PROFIT MARGIN ANALYSIS</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty:
                # Calculate profit margins for all products
                product_margins = []
                
                for product in merged_sales['Product'].unique():
                    if pd.notna(product):
                        product_data = merged_sales[merged_sales['Product'] == product]
                        
                        if 'Price' in product_data.columns and 'COGS' in product_data.columns:
                            avg_price = product_data['Price'].mean()
                            avg_cogs = product_data['COGS'].mean()
                            margin = (avg_price - avg_cogs) / avg_price * 100 if avg_price > 0 else 0
                            
                            product_margins.append({
                                'Product': product,
                                'Margin': margin
                            })
                
                if product_margins:
                    # Convert to DataFrame
                    margin_df = pd.DataFrame(product_margins)
                    
                    # Sort from lowest to highest margin
                    margin_df = margin_df.sort_values('Margin')
                    
                    # Create a color scale for margins
                    colorscale = [
                        [0, 'rgb(255, 75, 75)'],        # Red for lowest margins (<50%)
                        [0.5, 'rgb(255, 230, 0)'],      # Yellow for mid margins (50-70%)
                        [0.7, 'rgb(185, 255, 137)'],    # Light green for good margins (70-80%)
                        [1, 'rgb(75, 255, 75)']         # Bright green for highest margins (>80%)
                    ]
                    
                    # Create the horizontal bar chart for margins
                    fig = px.bar(
                        margin_df, 
                        y='Product',
                        x='Margin',
                        orientation='h',
                        color='Margin',
                        color_continuous_scale=colorscale,
                        labels={'Margin': 'Profit Margin (%)', 'Product': ''},
                        range_color=[0, 100],
                        text='Margin'
                    )
                    
                    # Update the layout for better appearance
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=30, b=20),
                        height=400,
                        font=dict(size=12),
                        coloraxis=dict(
                            colorbar=dict(
                                title="Margin %",
                                tickvals=[0, 25, 50, 75, 100],
                                ticktext=["0%", "25%", "50%", "75%", "100%"],
                                len=0.8
                            )
                        )
                    )
                    
                    # Format the text
                    fig.update_traces(
                        texttemplate='%{x:.1f}%',
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Margin: %{x:.1f}%<extra></extra>'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No margin data available for the selected period")
            else:
                st.info("No sales data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sales Trend Analysis
        with financial_cols4[1]:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">SALES TREND ANALYSIS</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty and 'Date' in filtered_sales.columns:
                # Calculate sales trends by day
                daily_sales = filtered_sales.groupby(filtered_sales['Date'].dt.date)['Net_Total'].sum().reset_index()
                daily_sales['Date_Formatted'] = daily_sales['Date'].apply(lambda x: x.strftime('%d/%m/%y'))
                
                # Create line chart for sales trends
                fig = px.line(
                    daily_sales,
                    x='Date_Formatted',
                    y='Net_Total',
                    markers=True,
                    labels={'Net_Total': 'Revenue (VND)', 'Date_Formatted': 'Date'},
                    category_orders={"Date_Formatted": sorted(daily_sales['Date_Formatted'].unique())}
                )
                
                # Update the layout for better appearance
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=50),
                    height=400,
                    font=dict(size=12),
                )
                
                # Format the y-axis
                fig.update_yaxes(
                    title_text='',
                    tickformat=',d',
                )
                
                # Format the x-axis
                fig.update_xaxes(
                    title_text='',
                    tickangle=45,
                )
                
                # Format the line and markers
                fig.update_traces(
                    line=dict(width=3, color='#4a9af5'),
                    marker=dict(size=8, color='#4a9af5'),
                    hovertemplate='<b>%{x}</b><br>Revenue: %{y:,.0f} VND<extra></extra>'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daily sales data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Create a divider between sections
        st.markdown('<div class="dashboard-divider"></div>', unsafe_allow_html=True)
        
        # Operational Costs Section
        st.markdown('<div class="section-header">OPERATIONAL COSTS MANAGEMENT</div>', unsafe_allow_html=True)
        
        # Display and edit operational costs
        op_costs_col1, op_costs_col2 = st.columns([2, 1])
        
        with op_costs_col1:
            # Form for adding new operational costs
            with st.expander("Add Operational Cost", expanded=False):
                with st.form("add_cost_form"):
                    cost_date = st.date_input("Date", datetime.datetime.now())
                    cost_type = st.text_input("Cost Type", placeholder="e.g., Rent, Utilities, Labor")
                    cost_amount = st.number_input("Amount (VND)", min_value=0, step=10000)
                    
                    submit_cost = st.form_submit_button("Add Cost")
                    
                    if submit_cost and cost_type and cost_amount > 0:
                        # Add to operational costs DataFrame
                        new_cost = pd.DataFrame([{
                            'Date': cost_date,
                            'Type': cost_type,
                            'Amount': cost_amount
                        }])
                        
                        # Append to existing costs or create new DataFrame
                        try:
                            operational_costs_df = pd.concat([operational_costs_df, new_cost], ignore_index=True)
                        except:
                            operational_costs_df = new_cost
                        
                        # Save to CSV
                        operational_costs_df.to_csv("data/operational_costs.csv", index=False)
                        st.success(f"Added {cost_type} cost of {utils.format_currency(cost_amount)}")
                        st.rerun()
        
        # Display operational costs table
        st.markdown('<div class="table-header">OPERATIONAL COSTS</div>', unsafe_allow_html=True)
        
        # Format operational costs for display
        display_costs = operational_costs_df.copy()
        display_costs['Date'] = pd.to_datetime(display_costs['Date']).dt.strftime('%d/%m/%Y')
        display_costs['Amount_Formatted'] = display_costs['Amount'].apply(lambda x: utils.format_currency(x))
        
        # Sort by date (newest first)
        display_costs = display_costs.sort_values('Date', ascending=False)
        
        # Convert to strings for display
        costs_for_display = display_costs[['Date', 'Type', 'Amount_Formatted']].rename(
            columns={'Date': 'Date', 'Type': 'Cost Type', 'Amount_Formatted': 'Amount'}
        )
        
        # Display table with option to edit
        st.dataframe(costs_for_display, use_container_width=True)
        
        # Delete operational cost
        all_costs = operational_costs_df.copy()
        all_costs['Date'] = pd.to_datetime(all_costs['Date']).dt.strftime('%d/%m/%Y')
        all_costs['Display'] = all_costs['Date'] + " - " + all_costs['Type'] + " - " + all_costs['Amount'].astype(str) + " VND"
        
        with op_costs_col2:
            # Select cost to delete
            selected_cost = st.selectbox(
                "Select a cost to delete",
                options=all_costs['Display'].tolist(),
                index=0 if not all_costs.empty else None
            )
            
            # Delete button
            if st.button("Delete Cost"):
                if selected_cost:
                    # Find the selected cost
                    selected_index = all_costs[all_costs['Display'] == selected_cost].index[0]
                    
                    # Remove from DataFrame
                    operational_costs_df = operational_costs_df.drop(selected_index)
                    
                    # Save updated costs
                    operational_costs_df.to_csv("data/operational_costs.csv", index=False)
                    
                    st.success("Cost deleted successfully")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("If this is your first time running the app, make sure all required data files exist in the 'data' directory (sales.csv, products.csv, product_recipe.csv, operational_costs.csv).")