import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import datetime
import utils
import numpy as np

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
        text-align: center;
        font-size: 2.5rem;
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
        background-color: #1A1A1A;
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

# Dashboard Title
st.markdown('# Financial Dashboard')

# Main dashboard container with dark theme
st.markdown('<div class="main-dashboard">', unsafe_allow_html=True)

# Date filter container with modern UI and consistent dark color
st.markdown('<div class="chart-container" style="background-color: #2C2C2C;">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Select Time Period</div>', unsafe_allow_html=True)

# Create single column for filter
col1 = st.container()

# Time filter
time_options = ["Today", "Last 7 Days", "Last 30 Days", "All Time", "Custom"]
# Ensure default_time_filter exists and is valid
if 'default_time_filter' not in st.session_state or st.session_state.default_time_filter not in time_options:
    st.session_state.default_time_filter = "Today"

with col1:
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
    
    # Display the date range in a separate container below the dropdown with full width
    st.markdown(
        f"""<div style="background-color: #2C2C2C; padding: 12px; border-radius: 4px; margin-top: 10px; text-align: center;">
            <span style="color: #fff;">Date Range: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}</span>
        </div>""", 
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

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
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
    filtered_sales = sales_df[(sales_df['Date'].dt.date >= start_date) & 
                             (sales_df['Date'].dt.date <= end_date)]
    
    # Financial analysis container
    with st.container():
        # Calculate financial metrics
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
            filtered_sales_copy = filtered_sales.copy()
            filtered_sales_copy = filtered_sales_copy.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
            merged_sales = pd.merge(filtered_sales_copy, products_df, left_on='Product', right_on='Name', how='left')
            
            # Check if COGS column exists in products_df
            if 'COGS' in merged_sales.columns:
                total_cogs = (merged_sales['COGS'] * merged_sales['Order_Quantity']).sum()
            else:
                total_cogs = 0
        
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
        
        # Calculate operational costs in the period
        filtered_costs = operational_costs_df[(operational_costs_df['Date'].dt.date >= start_date) & 
                                         (operational_costs_df['Date'].dt.date <= end_date)]
        
        # Make sure Amount column is numeric
        operational_costs_df['Amount'] = pd.to_numeric(operational_costs_df['Amount'], errors='coerce').fillna(0)
        filtered_costs['Amount'] = pd.to_numeric(filtered_costs['Amount'], errors='coerce').fillna(0)
        
        # Calculate sum of filtered costs
        operational_costs = filtered_costs['Amount'].sum()
        
        # Calculate financial metrics based on the formulas provided
        # Gross Revenue = Tổng doanh thu bán hàng (chưa trừ chiết khấu, hoàn trả, thuế)
        gross_revenue = filtered_sales['Total'].sum() if not filtered_sales.empty else 0
        
        # Net Revenue = Gross Revenue – Chiết khấu – Hàng bán bị trả lại – Thuế GTGT
        # In our case, we don't have returns or VAT, so Net Revenue = Gross Revenue - Promotions
        net_revenue = filtered_sales['Net_Total'].sum() if not filtered_sales.empty else 0
        
        # Gross Profit = Net Revenue – Giá vốn hàng bán (COGS)
        gross_profit = net_revenue - total_cogs
        
        # Operating Profit = Gross Profit – Chi phí bán hàng – Chi phí quản lý doanh nghiệp
        # In our system, we combine all operational costs together
        operating_profit = gross_profit - operational_costs
        
        # Net Profit (Lợi nhuận sau thuế) = Operating Profit – Chi phí tài chính – Thuế thu nhập doanh nghiệp
        # Since we don't track taxes or financial expenses separately, Net Profit = Operating Profit
        net_profit = operating_profit
        
        # Calculate margins
        gross_profit_margin = (gross_profit / net_revenue * 100) if net_revenue > 0 else 0
        net_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0
        
        # Calculate revenue reduction due to promotions
        promo_total = gross_revenue - net_revenue
        promo_percentage = (promo_total / gross_revenue * 100) if gross_revenue > 0 else 0
        
        # Most profitable product calculation
        product_profit_list = []
        
        # Check if necessary columns are present for profit calculation
        required_cols = ['Product', 'Price', 'COGS', 'Order_Quantity']
        if all(col in merged_sales.columns for col in required_cols) and not merged_sales.empty:
            # Process each product individually
            for product in merged_sales['Product'].unique():
                if pd.notna(product):  # Skip NaN product names
                    product_data = merged_sales[merged_sales['Product'] == product]
                    try:
                        profit = ((product_data['Price'] - product_data['COGS']) * product_data['Order_Quantity']).sum()
                        product_profit_list.append({'Product': product, 'Profit': profit})
                    except:
                        continue
        
        # Convert to DataFrame (empty if no products)
        product_profit = pd.DataFrame(product_profit_list)
        
        # Safely get the most profitable product
        if not product_profit.empty and 'Profit' in product_profit.columns and product_profit['Profit'].notnull().any():
            max_idx = product_profit['Profit'].idxmax()
            if max_idx is not None:
                most_profitable = product_profit.loc[max_idx]
            else:
                most_profitable = pd.Series({'Product': 'N/A', 'Profit': 0})
        else:
            most_profitable = pd.Series({'Product': 'N/A', 'Profit': 0})
        
        # Determine financial status
        financial_status = "PROFITABLE" if net_profit > 0 else "LOSS MAKING"
        status_color = "#2ECC71" if net_profit > 0 else "#E74C3C"  # Green or Red
        
        # Removed summary display at the top of the page
        
        # Main header - Revenue display
        with st.container():
            # Use width ratio closer to visual in screenshot
            revenue_col1, revenue_col2 = st.columns([2, 1])
            
            with revenue_col1:
                # Big revenue display with consistent height
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
                sales_count = len(filtered_sales) if not filtered_sales.empty else 0
                st.markdown(f"""
                <div style="margin-bottom: 25px; padding: 18px; background-color: #2C2C2C; border-radius: 6px; height: 130px;">
                    <div class="period-label">TOTAL ORDERS</div>
                    <div class="big-metric" style="font-size: 2rem; margin-top: 10px;">{sales_count}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Financial metrics in a grid layout similar to the sample
        st.markdown('<div class="section-header">FINANCIAL METRICS</div>', unsafe_allow_html=True)
        
        # Create container for KPI cards with equal spacing
        with st.container():
            # Create KPI cards in a grid with darker colors and modern layout
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns([1, 1, 1, 1])
        
        with kpi_col1:
            kpi_class = "metric-positive" if gross_profit > 0 else "metric-negative"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">GROSS PROFIT</div>
                <div class="metric-value {kpi_class}">{utils.format_currency(gross_profit)}</div>
                <div class="metric-trend">{gross_profit_margin:.1f}% margin</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi_col2:
            kpi_class = "metric-positive" if net_profit > 0 else "metric-negative"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">NET PROFIT</div>
                <div class="metric-value {kpi_class}">{utils.format_currency(net_profit)}</div>
                <div class="metric-trend">{net_margin:.1f}% margin</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">COST OF GOODS</div>
                <div class="metric-value">{utils.format_currency(total_cogs)}</div>
                <div class="metric-trend">{(total_cogs/net_revenue*100):.1f}% of revenue</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">OPERATIONAL COSTS</div>
                <div class="metric-value">{utils.format_currency(operational_costs)}</div>
                <div class="metric-trend">{(operational_costs/net_revenue*100):.1f}% of revenue</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add profit status card with improved styling
        with st.container():
            st.markdown(f"""
            <div class="{'profit-card profit-positive' if net_profit > 0 else 'profit-card profit-negative'}" style="margin: 10px 0 30px 0;">
                <div class="profit-status">YOUR BUSINESS IS {financial_status}</div>
                <div class="profit-amount">{utils.format_currency(abs(net_profit))} {'PROFIT' if net_profit > 0 else 'LOSS'}</div>
                <div class="profit-percent">Net Profit Margin: {abs(net_margin):.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create a divider between sections
        st.markdown('<div class="dashboard-divider"></div>', unsafe_allow_html=True)
        
        # Revenue and cost breakdown
        st.markdown('<div class="section-header">REVENUE & COST BREAKDOWN</div>', unsafe_allow_html=True)
        
        # Create a container for the charts to ensure even spacing and use it directly
        chart_col1, chart_col2 = st.columns([1, 1])
        
        # Revenue breakdown chart
        with chart_col1:
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
                    color_continuous_scale='Blues',
                    labels={'Net_Total': 'Revenue (VND)', 'Product': ''},
                    text_auto='.2s'
                )
                
                # Format hover text with commas and VND
                fig.update_traces(
                    hovertemplate='%{x:,.0f} VND<br>%{y}'
                )
                
                # Style the chart
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    coloraxis_showscale=False,
                    yaxis=dict(
                        title='',
                        autorange="reversed"  # Reverse to put highest at top
                    ),
                    xaxis=dict(
                        title='Revenue (VND)',
                        tickformat=',d',
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Cost breakdown chart (Operational costs by type)
        with chart_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">BUSINESS COSTS BREAKDOWN</div>', unsafe_allow_html=True)
            
            # Check if there's cost data
            if not filtered_costs.empty:
                # Group costs by type
                cost_breakdown = pd.concat([
                    # Operational costs
                    filtered_costs.groupby('Type')['Amount'].sum().reset_index(),
                    # Add an entry for COGS as "Variable Cost"
                    pd.DataFrame({'Type': ['Variable Cost (COGS)'], 'Amount': [total_cogs]})
                ])
                
                # Sort from smallest to largest
                cost_breakdown = cost_breakdown.sort_values('Amount')
                
                # Create the horizontal bar chart
                fig = px.bar(
                    cost_breakdown, 
                    y='Type',
                    x='Amount',
                    orientation='h',
                    color='Amount',
                    color_continuous_scale='Reds',
                    labels={'Amount': 'Cost (VND)', 'Type': ''},
                    text_auto='.2s'
                )
                
                # Format hover text with commas and VND
                fig.update_traces(
                    hovertemplate='%{x:,.0f} VND<br>%{y}'
                )
                
                # Style the chart
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    coloraxis_showscale=False,
                    yaxis=dict(
                        title='',
                        autorange="reversed"  # Reverse to put highest at top
                    ),
                    xaxis=dict(
                        title='Cost (VND)',
                        tickformat=',d',
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cost data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Create a divider between sections
        st.markdown('<div class="dashboard-divider"></div>', unsafe_allow_html=True)
        
        # Product profitability section
        st.markdown('<div class="section-header">PROFITABILITY ANALYSIS</div>', unsafe_allow_html=True)
        
        # Create grid for profitability analysis with equal width
        profit_col1, profit_col2 = st.columns([1, 1])
        
        # Most/least profitable products
        with profit_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PRODUCT PROFITABILITY</div>', unsafe_allow_html=True)
            
            if not product_profit.empty:
                # Sort from smallest to largest
                product_profit_sorted = product_profit.sort_values('Profit')
                
                # Create bar chart
                fig = px.bar(
                    product_profit_sorted, 
                    y='Product',
                    x='Profit',
                    orientation='h',
                    color='Profit',
                    color_continuous_scale='RdYlGn',
                    labels={'Profit': 'Profit (VND)', 'Product': ''},
                    text_auto='.2s'
                )
                
                # Format hover text
                fig.update_traces(
                    hovertemplate='%{x:,.0f} VND<br>%{y}'
                )
                
                # Style the chart
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    coloraxis_showscale=False,
                    yaxis=dict(
                        title='',
                        autorange="reversed"
                    ),
                    xaxis=dict(
                        title='Profit (VND)',
                        tickformat=',d',
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No product profit data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Profit Waterfall chart (similar to Excel template)
        with profit_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PROFIT WATERFALL</div>', unsafe_allow_html=True)
            
            # Create waterfall chart data
            waterfall_data = pd.DataFrame([
                {'Step': 'Gross Revenue', 'Amount': gross_revenue, 'Type': 'Total'},
                {'Step': 'Promotions', 'Amount': -promo_total, 'Type': 'Negative'},
                {'Step': 'Net Revenue', 'Amount': net_revenue, 'Type': 'Subtotal'},
                {'Step': 'COGS', 'Amount': -total_cogs, 'Type': 'Negative'},
                {'Step': 'Gross Profit', 'Amount': gross_profit, 'Type': 'Subtotal'},
                {'Step': 'Operational Costs', 'Amount': -operational_costs, 'Type': 'Negative'},
                {'Step': 'Net Profit', 'Amount': net_profit, 'Type': 'Total'}
            ])
            
            # Create custom colors for waterfall chart
            waterfall_colors = {
                'Total': '#3498DB',  # Blue 
                'Negative': '#E74C3C',  # Red
                'Subtotal': '#2ECC71',  # Green
                'Connector': 'rgba(255, 255, 255, 0.5)'  # Light gray
            }
            
            # Create waterfall chart
            fig = go.Figure()
            
            # Add connector lines
            for i in range(len(waterfall_data) - 1):
                # Skip drawing connector after subtotals
                if waterfall_data.iloc[i]['Type'] != 'Subtotal':
                    # Calculate measures and positions
                    current_measure = 'relative' if waterfall_data.iloc[i]['Type'] != 'Total' else 'total'
                    next_measure = 'relative' if waterfall_data.iloc[i+1]['Type'] != 'Total' and waterfall_data.iloc[i+1]['Type'] != 'Subtotal' else 'total'
                    
                    # Current y position
                    if i == 0:
                        y_curr = waterfall_data.iloc[i]['Amount']
                    elif waterfall_data.iloc[i-1]['Type'] == 'Subtotal':
                        y_curr = waterfall_data.iloc[i-1]['Amount']
                    else:
                        y_curr = sum(waterfall_data.iloc[:i+1]['Amount'])
                        
                    # Next y position
                    if waterfall_data.iloc[i+1]['Type'] == 'Total' or waterfall_data.iloc[i+1]['Type'] == 'Subtotal':
                        y_next = waterfall_data.iloc[i+1]['Amount']
                    else:
                        y_next = y_curr + waterfall_data.iloc[i+1]['Amount']
                    
                    fig.add_trace(go.Scatter(
                        x=[waterfall_data.iloc[i]['Step'], waterfall_data.iloc[i+1]['Step']],
                        y=[y_curr, y_curr],
                        mode='lines',
                        line=dict(color=waterfall_colors['Connector'], width=1, dash='dot'),
                        showlegend=False,
                        hoverinfo='none'
                    ))
            
            # Add main waterfall bars
            fig.add_trace(go.Waterfall(
                name="Profit Waterfall",
                orientation="v",
                measure=["total" if x == 'Total' or x == 'Subtotal' else "relative" for x in waterfall_data['Type']],
                x=waterfall_data['Step'],
                y=waterfall_data['Amount'],
                text=[f"{utils.format_currency(abs(x), include_currency=False)}" for x in waterfall_data['Amount']],
                textposition="outside",
                connector={"line": {"color": "rgba(0, 0, 0, 0)"}},  # Hide default connectors
                decreasing={"marker": {"color": waterfall_colors['Negative']}},
                increasing={"marker": {"color": waterfall_colors['Total']}},
                totals={"marker": {"color": waterfall_colors['Subtotal']}}
            ))
            
            # Style the chart
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                yaxis=dict(
                    title='Amount (VND)',
                    tickformat=',d',
                    gridcolor='rgba(255, 255, 255, 0.1)'
                ),
                xaxis=dict(
                    title='',
                    categoryorder='array',
                    categoryarray=waterfall_data['Step'],
                    gridcolor='rgba(255, 255, 255, 0.1)'
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Third row for financial charts
        income_expense_col1, income_expense_col2 = st.columns([1, 1])
        
        # Profit split donut chart (similar to Excel template)
        with income_expense_col1:
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
                
                # Add components
                if cogs_pct > 0:
                    labels.append(f"COGS ({cogs_pct:.1f}%)")
                    values.append(cogs_pct)
                    colors.append('#3498DB')  # Blue
                    
                if op_costs_pct > 0:
                    labels.append(f"Operational Costs ({op_costs_pct:.1f}%)")
                    values.append(op_costs_pct)
                    colors.append('#9B59B6')  # Purple
                    
                if profit_pct > 0:
                    labels.append(f"Net Profit ({profit_pct:.1f}%)")
                    values.append(profit_pct)
                    colors.append('#2ECC71')  # Green
                    
                if loss_pct > 0:
                    labels.append(f"Net Loss ({loss_pct:.1f}%)")
                    values.append(loss_pct)
                    colors.append('#E74C3C')  # Red
                
                # Create the donut chart
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.6,
                    marker=dict(colors=colors)
                )])
                
                # Style the chart
                fig.update_layout(
                    height=400,
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.1,
                        xanchor="center",
                        x=0.5
                    ),
                    annotations=[dict(
                        text=f"{utils.format_currency(gross_revenue, include_currency=False)}<br>Total Revenue",
                        showarrow=False,
                        font=dict(size=14)
                    )]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No revenue data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Accounts Receivable / Payable (similar to template)
        with income_expense_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">DAILY REVENUE BREAKDOWN</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty and 'Date' in filtered_sales.columns:
                # Calculate daily revenue by product
                product_daily = filtered_sales.groupby(['Date', 'Product'])['Net_Total'].sum().reset_index()
                
                # Format date
                product_daily['Date_Formatted'] = product_daily['Date'].dt.strftime('%d/%m/%y')
                
                # Get unique dates and products
                dates = product_daily['Date_Formatted'].unique()
                products = product_daily['Product'].unique()
                
                # Create a colorful stacked bar chart
                fig_product_revenue = go.Figure()
                
                # Get a colorful palette
                colors = px.colors.qualitative.Bold
                
                # Add bars for each product
                for i, product in enumerate(products):
                    product_data = product_daily[product_daily['Product'] == product]
                    
                    fig_product_revenue.add_trace(go.Bar(
                        x=product_data['Date_Formatted'],
                        y=product_data['Net_Total'],
                        name=product,
                        marker=dict(color=colors[i % len(colors)]),
                        hovertemplate='%{y:,.0f} VND<br>%{x}'
                    ))
                
                # Style the chart
                fig_product_revenue.update_layout(
                    barmode='stack',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(
                        title='Revenue (VND)',
                        tickformat=',d',
                        gridcolor='rgba(255, 255, 255, 0.1)'
                    ),
                    xaxis=dict(
                        tickangle=-45,
                        gridcolor='rgba(255, 255, 255, 0.1)'
                    ),
                    plot_bgcolor='#1A1A1A',
                    paper_bgcolor='#1A1A1A',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig_product_revenue, use_container_width=True)
            else:
                st.info("No sales data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Financial Ratios Row
        ratio_col1, ratio_col2 = st.columns([1, 1])
        
        # Quick Ratio (similar to Excel template)
        with ratio_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PROFIT MARGIN ANALYSIS</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty:
                # Calculate profit margins for all products
                product_margins = []
                
                for product in merged_sales['Product'].unique():
                    if pd.notna(product):
                        product_data = merged_sales[merged_sales['Product'] == product]
                        
                        if 'Price' in product_data.columns and 'COGS' in product_data.columns:
                            try:
                                # Get product price and COGS
                                product_price = product_data['Price'].iloc[0] if not product_data.empty else 0
                                product_cogs = product_data['COGS'].iloc[0] if not product_data.empty else 0
                                product_quantity = product_data['Order_Quantity'].sum() if not product_data.empty else 0
                                
                                # Calculate margin
                                if product_price > 0:
                                    margin_pct = ((product_price - product_cogs) / product_price) * 100
                                    product_margins.append({
                                        'Product': product,
                                        'Margin': margin_pct,
                                        'Revenue': product_price * product_quantity,
                                        'Quantity': product_quantity
                                    })
                            except:
                                continue
                
                # Create DataFrame and sort by margin
                if product_margins:
                    margin_df = pd.DataFrame(product_margins)
                    margin_df = margin_df.sort_values('Margin', ascending=False)
                    
                    # Create horizontal bar chart for margins
                    fig_margins = go.Figure()
                    
                    # Add bars
                    fig_margins.add_trace(go.Bar(
                        y=margin_df['Product'],
                        x=margin_df['Margin'],
                        orientation='h',
                        marker=dict(
                            color=margin_df['Margin'],
                            colorscale='Viridis',
                            colorbar=dict(title='Margin %')
                        ),
                        hovertemplate='%{x:.1f}%<br>Revenue: %{customdata[0]}<br>Units: %{customdata[1]}',
                        customdata=np.stack((
                            [utils.format_currency(x) for x in margin_df['Revenue']],
                            margin_df['Quantity']
                        ), axis=-1)
                    ))
                    
                    # Add text labels
                    fig_margins.update_traces(
                        texttemplate='%{x:.1f}%',
                        textposition='outside'
                    )
                    
                    # Style the chart
                    fig_margins.update_layout(
                        margin=dict(l=10, r=120, t=10, b=10),
                        xaxis=dict(
                            title='Profit Margin %',
                            gridcolor='rgba(255, 255, 255, 0.1)'
                        ),
                        yaxis=dict(
                            title='',
                            gridcolor='rgba(255, 255, 255, 0.1)'
                        ),
                        plot_bgcolor='#1A1A1A',
                        paper_bgcolor='#1A1A1A',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig_margins, use_container_width=True)
                else:
                    st.info("No margin data available")
            else:
                st.info("No sales data available for the selected period")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Current Ratio (similar to Excel template)
        with ratio_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">SALES TREND ANALYSIS</div>', unsafe_allow_html=True)
            
            if not filtered_sales.empty and 'Date' in filtered_sales.columns:
                # Calculate sales trends by day
                daily_sales = filtered_sales.groupby(filtered_sales['Date'].dt.date)['Net_Total'].sum().reset_index()
                daily_sales['Date_Formatted'] = daily_sales['Date'].apply(lambda x: x.strftime('%d/%m/%y'))
                
                # Calculate 3-day moving average if enough data
                if len(daily_sales) >= 3:
                    daily_sales['MA3'] = daily_sales['Net_Total'].rolling(window=3).mean()
                
                # Create sales trend chart
                fig_sales_trend = go.Figure()
                
                # Add daily sales scatter
                fig_sales_trend.add_trace(go.Scatter(
                    x=daily_sales['Date_Formatted'],
                    y=daily_sales['Net_Total'],
                    mode='lines+markers',
                    name='Daily Revenue',
                    line=dict(color='#3498DB'),
                    hovertemplate='%{y:,.0f} VND<br>%{x}'
                ))
                
                # Add moving average if available
                if len(daily_sales) >= 3:
                    fig_sales_trend.add_trace(go.Scatter(
                        x=daily_sales['Date_Formatted'],
                        y=daily_sales['MA3'],
                        mode='lines',
                        name='3-Day Moving Avg',
                        line=dict(color='#E74C3C', width=3, dash='dot'),
                        hovertemplate='%{y:,.0f} VND<br>%{x}'
                    ))
                
                # Style the chart
                fig_sales_trend.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(
                        title='Revenue (VND)',
                        tickformat=',d',
                        gridcolor='rgba(255, 255, 255, 0.1)'
                    ),
                    xaxis=dict(
                        tickangle=-45,
                        gridcolor='rgba(255, 255, 255, 0.1)'
                    ),
                    plot_bgcolor='#1A1A1A',
                    paper_bgcolor='#1A1A1A',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig_sales_trend, use_container_width=True)
            else:
                st.info("No sales data available for trend analysis")
                
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
                            'Date': cost_date.strftime('%Y-%m-%d'),
                            'Type': cost_type,
                            'Amount': cost_amount
                        }])
                        
                        # Check if file exists
                        try:
                            existing_costs = pd.read_csv("data/operational_costs.csv")
                            updated_costs = pd.concat([existing_costs, new_cost], ignore_index=True)
                        except FileNotFoundError:
                            updated_costs = new_cost
                            
                        # Save updated costs
                        updated_costs.to_csv("data/operational_costs.csv", index=False)
                        st.success(f"Added {cost_type} cost of {utils.format_currency(cost_amount)}")
                        st.rerun()
        
        # Show operational costs table
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.markdown('<div class="table-header">OPERATIONAL COSTS</div>', unsafe_allow_html=True)
        
        # Format operational costs for display
        display_costs = operational_costs_df.copy()
        display_costs['Date'] = pd.to_datetime(display_costs['Date']).dt.strftime('%d/%m/%Y')
        display_costs['Amount_Formatted'] = display_costs['Amount'].apply(lambda x: utils.format_currency(x))
        
        # Add Delete button column
        display_costs = display_costs.reset_index()
        
        # Allow editing costs
        edited_costs = st.data_editor(
            display_costs[['Date', 'Type', 'Amount_Formatted', 'index']],
            column_config={
                "index": st.column_config.Column(
                    "Action",
                    width="small",
                    disabled=True,
                ),
                "Date": st.column_config.Column(
                    "Date",
                    width="medium",
                ),
                "Type": st.column_config.Column(
                    "Cost Type",
                    width="medium",
                ),
                "Amount_Formatted": st.column_config.Column(
                    "Amount",
                    width="medium",
                )
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Delete selected cost
        delete_cost_col1, delete_cost_col2 = st.columns([3, 1])
        
        with delete_cost_col1:
            cost_to_delete = st.selectbox(
                "Select a cost to delete",
                options=display_costs['index'],
                format_func=lambda x: f"{display_costs.loc[display_costs['index'] == x, 'Date'].values[0]} - {display_costs.loc[display_costs['index'] == x, 'Type'].values[0]} - {display_costs.loc[display_costs['index'] == x, 'Amount_Formatted'].values[0]}"
            )
        
        with delete_cost_col2:
            if st.button("Delete Cost"):
                # Get the original index
                original_index = cost_to_delete
                
                # Remove from DataFrame
                updated_costs = operational_costs_df.drop(original_index).reset_index(drop=True)
                
                # Save updated costs
                updated_costs.to_csv("data/operational_costs.csv", index=False)
                
                st.success("Cost deleted successfully")
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Close main dashboard div
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("If this is your first time running the app, make sure all required data files exist in the 'data' directory (sales.csv, products.csv, product_recipe.csv, operational_costs.csv).")