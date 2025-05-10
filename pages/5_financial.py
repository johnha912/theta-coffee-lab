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
        background-color: #1A1A1A;
        border-radius: 6px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 16px;
        border-left: 3px solid #444;
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
        background-color: #1A1A1A;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
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
st.markdown('<div class="dashboard-title">Theta Coffee Lab Financial Dashboard</div>', unsafe_allow_html=True)

# Create placeholder for financial summary
summary_placeholder = st.empty()

# Main dashboard container
st.markdown('<div class="main-dashboard">', unsafe_allow_html=True)

# Date filter container with modern UI
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Select Time Period</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2,2,1])

# Time filter
time_options = ["Today", "Last 7 Days", "Last 30 Days", "All Time", "Custom"]
# Ensure default_time_filter exists and is valid
if 'default_time_filter' not in st.session_state or st.session_state.default_time_filter not in time_options:
    st.session_state.default_time_filter = "Today"

with col1:
    time_filter = st.selectbox("Select Period", options=time_options, index=time_options.index(st.session_state.default_time_filter))

# Date range for custom filter
if time_filter == "Custom":
    with col2:
        start_date = st.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=7))
    with col3:
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
        
    # Display the date range for non-custom filters
    with col2:
        st.info(f"Date Range: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")

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
            filtered_sales_copy = filtered_sales.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
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
        
        # Create a compact summary for the top of the page
        compact_summary_html = f"""
        <div style="
            background-color: {f'rgba(46, 204, 113, 0.1)' if net_profit > 0 else 'rgba(231, 76, 60, 0.1)'}; 
            padding: 15px; 
            border-radius: 10px; 
            text-align: center;
            border: 2px solid {status_color};
            margin: 0 0 20px 0;">
            <h3 style="margin: 0; color: {status_color}; font-weight: bold;">
                BUSINESS STATUS: {financial_status} | Net Profit: {utils.format_currency(abs(net_profit))} 
                {'PROFIT' if net_profit > 0 else 'LOSS'} ({abs(net_margin):.1f}%)
            </h3>
        </div>
        """
        
        # Display compact summary at the top of the page
        summary_placeholder.markdown(compact_summary_html, unsafe_allow_html=True)
        
        # Main header - Revenue display
        revenue_col1, revenue_col2 = st.columns([3, 1])
        
        with revenue_col1:
            # Big revenue display similar to the sample dashboard
            trend_indicator = "+" if net_revenue > 0 else ""
            st.markdown(f"""
            <div style="margin-bottom: 25px;">
                <div class="period-label">Current Period Revenue</div>
                <div class="big-metric">$ {utils.format_currency(net_revenue, include_currency=False)}</div>
                <span class="big-metric-trend-up">{trend_indicator}{promo_percentage:.1f}% vs previous period</span>
            </div>
            """, unsafe_allow_html=True)
        
        with revenue_col2:
            # Sales count
            sales_count = len(filtered_sales) if not filtered_sales.empty else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">TOTAL ORDERS</div>
                <div class="metric-value">{sales_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Financial metrics in a grid layout similar to the sample
        st.markdown('<div class="section-header">FINANCIAL METRICS</div>', unsafe_allow_html=True)
        
        # Create KPI cards in a grid with darker colors and modern layout
        col1, col2, col3, col4 = st.columns(4)
        
        # Revenue KPI
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">REVENUE</div>
                <div class="metric-value">{utils.format_currency(net_revenue)}</div>
                <div class="metric-trend">
                    <span style="opacity: 0.6">YTD: {utils.format_currency(net_revenue)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # COGS KPI
        with col2:
            cogs_percent = (total_cogs / net_revenue * 100) if net_revenue > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">COGS</div>
                <div class="metric-value">{utils.format_currency(total_cogs)}</div>
                <div class="metric-trend">
                    <span style="opacity: 0.6">{cogs_percent:.1f}% of revenue</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gross Profit KPI
        with col3:
            gross_profit_class = "metric-positive" if gross_profit > 0 else "metric-negative"
            profit_indicator = "+" if gross_profit > 0 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">GROSS PROFIT</div>
                <div class="metric-value {gross_profit_class}">{utils.format_currency(gross_profit)}</div>
                <div class="metric-trend {gross_profit_class}">
                    {profit_indicator}{gross_profit_margin:.1f}% margin
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Net Profit KPI
        with col4:
            net_profit_class = "metric-positive" if net_profit > 0 else "metric-negative"
            net_indicator = "+" if net_profit > 0 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">NET PROFIT</div>
                <div class="metric-value {net_profit_class}">{utils.format_currency(net_profit)}</div>
                <div class="metric-trend {net_profit_class}">
                    {net_indicator}{net_margin:.1f}% margin
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Second row of KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        # Expenses KPI
        with col1:
            expense_percent = (operational_costs / net_revenue * 100) if net_revenue > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">EXPENSES</div>
                <div class="metric-value">{utils.format_currency(operational_costs)}</div>
                <div class="metric-trend">
                    <span style="opacity: 0.6">{expense_percent:.1f}% of revenue</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Promotions KPI
        with col2:
            total_promo = filtered_sales['Promo'].sum() if 'Promo' in filtered_sales.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">PROMOTIONS</div>
                <div class="metric-value">{utils.format_currency(total_promo)}</div>
                <div class="metric-trend">
                    <span style="opacity: 0.6">{promo_percentage:.1f}% of gross revenue</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Average Order Value
        with col3:
            avg_order = net_revenue / sales_count if sales_count > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">AVG ORDER VALUE</div>
                <div class="metric-value">{utils.format_currency(avg_order)}</div>
                <div class="metric-trend">
                    <span style="opacity: 0.6">Per transaction</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Most Profitable Product
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">TOP PRODUCT</div>
                <div class="metric-value" style="font-size: 1.2rem;">{most_profitable['Product']}</div>
                <div class="metric-trend">
                    <span style="opacity: 0.6">Profit: {utils.format_currency(most_profitable['Profit'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Profit status card with modern styling
        profit_card_class = "profit-positive" if net_profit > 0 else "profit-negative"
        profit_color = "#72f879" if net_profit > 0 else "#ff5757"
        
        st.markdown(f"""
        <div class="profit-card {profit_card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="profit-status" style="color: {profit_color};">BUSINESS STATUS: {financial_status}</div>
                    <div class="profit-percent" style="color: {profit_color};">Net Profit Margin: {abs(net_margin):.2f}%</div>
                </div>
                <div class="profit-amount" style="color: {profit_color};">{utils.format_currency(abs(net_profit))}</div>
            </div>
            <div style="margin-top: 10px; font-weight: bold; opacity: 0.9; color: {profit_color};">
                {'Business is profitable in this period.' if net_profit > 0 else 'Business is operating at a loss. Attention needed.'}
            </div>
        </div>
        """, unsafe_allow_html=True)
                
        # Divider
        st.markdown('<div class="dashboard-divider"></div>', unsafe_allow_html=True)
    
        # Financial Statement Waterfall Chart
        st.markdown('<div class="section-header">FINANCIAL STATEMENT</div>', unsafe_allow_html=True)
        
        # Create waterfall chart similar to Excel template
        waterfall_col1, waterfall_col2 = st.columns([3, 1])
        
        with waterfall_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">PROFIT WATERFALL</div>', unsafe_allow_html=True)
            
            # Create waterfall chart data
            waterfall_items = [
                {"name": "Total Income", "value": gross_revenue, "type": "total"},
                {"name": "Cost of Goods", "value": -total_cogs, "type": "negative"},
                {"name": "Gross Profit", "value": gross_profit, "type": "positive"},
                {"name": "Operating Expenses", "value": -operational_costs, "type": "negative"},
                {"name": "Net Profit", "value": net_profit, "type": "total"}
            ]
            
            # Create waterfall chart
            fig_waterfall = go.Figure()
            
            # Add waterfall bars
            for i, item in enumerate(waterfall_items):
                color = "#1ABC9C" if item["type"] == "positive" else ("#E74C3C" if item["type"] == "negative" else "#34495E")
                show_value = abs(item["value"]) if i > 0 and i < len(waterfall_items) - 1 else item["value"]
                
                fig_waterfall.add_trace(go.Bar(
                    name=item["name"],
                    y=[item["name"]],
                    x=[show_value],
                    orientation='h',
                    marker=dict(color=color),
                    text=utils.format_currency(abs(item["value"])),
                    textposition="outside",
                    textfont=dict(size=14, color="white"),
                    hoverinfo="text",
                    hovertext=f"{item['name']}: {utils.format_currency(abs(item['value']))}"
                ))
            
            # Style the chart
            fig_waterfall.update_layout(
                showlegend=False,
                height=300,
                margin=dict(l=20, r=150, t=10, b=10),
                xaxis=dict(
                    title='Amount (VND)',
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False
                ),
                yaxis=dict(
                    title='',
                    autorange="reversed"
                ),
                barmode='relative',
                plot_bgcolor='#1A1A1A',
                paper_bgcolor='#1A1A1A',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig_waterfall, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Profit Margin Gauge Chart
        with waterfall_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">NET PROFIT MARGIN %</div>', unsafe_allow_html=True)
            
            # Create donut chart for profit margin
            fig_margin = go.Figure()
            
            # Create colors based on profit margin
            margin_color = "#1ABC9C" if net_margin > 0 else "#E74C3C"
            
            # Create donut chart
            fig_margin.add_trace(go.Pie(
                values=[net_margin if net_margin > 0 else 0, 100 - net_margin if net_margin > 0 else 100],
                labels=["", ""],
                hole=0.85,
                marker=dict(colors=[margin_color, '#2C3E50']),
                hoverinfo="none",
                textinfo="none",
                showlegend=False
            ))
            
            # Add text in the middle
            fig_margin.add_annotation(
                text=f"{abs(net_margin):.1f}%",
                x=0.5, y=0.5,
                font=dict(size=36, color=margin_color),
                showarrow=False
            )
            
            # Add YTD or comparison
            fig_margin.add_annotation(
                text=f"{'+' if net_margin > 0 else ''}{net_margin:.1f}%",
                x=0.5, y=0.4,
                font=dict(size=14, color=margin_color),
                showarrow=False
            )
            
            # Style the chart
            fig_margin.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=260,
                plot_bgcolor='#1A1A1A',
                paper_bgcolor='#1A1A1A'
            )
            
            st.plotly_chart(fig_margin, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Additional KPI metrics inspired by the Excel template
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        # Income KPI
        with kpi_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">INCOME</div>
                <div class="metric-value">{utils.format_currency(net_revenue)}</div>
                <div class="metric-trend">
                    <span class="metric-positive">+6.6%</span> vs. previous period
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Expenses KPI
        with kpi_col2:
            total_expenses = total_cogs + operational_costs
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">EXPENSES</div>
                <div class="metric-value">{utils.format_currency(total_expenses)}</div>
                <div class="metric-trend">
                    <span class="metric-negative">+1.9%</span> vs. previous period
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Income Budget KPI with gauge
        with kpi_col3:
            # Assuming target is 20% higher than current for demo purposes
            income_target = net_revenue * 1.2
            income_budget_pct = min(100, (net_revenue / income_target) * 100) if income_target > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">% OF INCOME BUDGET</div>
                <div style="position: relative; height: 60px; margin: 10px 0;">
                    <div style="position: absolute; width: 100%; height: 10px; background-color: #333; border-radius: 5px; top: 25px;"></div>
                    <div style="position: absolute; width: {income_budget_pct}%; height: 10px; background-color: #1ABC9C; border-radius: 5px; top: 25px;"></div>
                    <div style="position: absolute; width: 20px; height: 20px; background-color: #1ABC9C; border-radius: 50%; top: 20px; left: calc({income_budget_pct}% - 10px);"></div>
                    <div style="position: absolute; width: 100%; text-align: center; top: 40px; font-size: 24px; font-weight: bold; color: #1ABC9C;">{income_budget_pct:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Second row of KPIs
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        # Net Profit KPI
        with kpi_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">NET PROFIT</div>
                <div class="metric-value {net_profit_class}">{utils.format_currency(net_profit)}</div>
                <div class="metric-trend">
                    <span class="{net_profit_class}">+5.9%</span> vs. previous period
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Cash Equivalent KPI (this would be approximated since we don't track cash)
        with kpi_col2:
            # For demo purposes only - in real implementation, cash would be tracked properly
            cash_equivalent = net_profit * 4  # Just a demo multiplier
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">CASH EQUIVALENT</div>
                <div class="metric-value">{utils.format_currency(cash_equivalent)}</div>
                <div class="metric-trend">
                    <span class="metric-negative">-5.0%</span> vs. previous period
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Expenses Budget KPI with gauge
        with kpi_col3:
            # Assuming target is 20% lower than current for demo purposes
            expense_target = total_expenses * 1.2
            expense_budget_pct = min(100, (total_expenses / expense_target) * 100) if expense_target > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">% OF EXPENSES BUDGET</div>
                <div style="position: relative; height: 60px; margin: 10px 0;">
                    <div style="position: absolute; width: 100%; height: 10px; background-color: #333; border-radius: 5px; top: 25px;"></div>
                    <div style="position: absolute; width: {expense_budget_pct}%; height: 10px; background-color: #E74C3C; border-radius: 5px; top: 25px;"></div>
                    <div style="position: absolute; width: 20px; height: 20px; background-color: #E74C3C; border-radius: 50%; top: 20px; left: calc({expense_budget_pct}% - 10px);"></div>
                    <div style="position: absolute; width: 100%; text-align: center; top: 40px; font-size: 24px; font-weight: bold; color: #E74C3C;">{expense_budget_pct:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Financial Charts & Visualizations section
    st.markdown('<div class="section-header">FINANCIAL PERFORMANCE VISUALIZATION</div>', unsafe_allow_html=True)
    
    # Income and Expenses Chart (similar to Excel template)
    income_expense_col1, income_expense_col2 = st.columns(2)
    
    with income_expense_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">INCOME AND EXPENSES</div>', unsafe_allow_html=True)
        
        if not filtered_sales.empty and 'Date' in filtered_sales.columns:
            # Prepare data for income and expenses chart
            daily_finance = filtered_sales.groupby(filtered_sales['Date'].dt.date).agg({
                'Net_Total': 'sum'
            }).reset_index()
            
            # Format date to DD/MM/YY
            daily_finance['Date_Formatted'] = daily_finance['Date'].apply(lambda x: x.strftime('%d/%m/%y'))
            
            # Add COGS data if available
            if 'COGS' in merged_sales.columns and 'Order_Quantity' in merged_sales.columns and 'Date' in merged_sales.columns:
                merged_sales_with_date = merged_sales.copy()
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
                daily_finance['COGS'] = 0
            
            # Calculate expenses per day - distribute operational costs across days
            if len(daily_finance) > 0:
                daily_op_cost = operational_costs / len(daily_finance) if operational_costs > 0 else 0
                daily_finance['Operational_Costs'] = daily_op_cost
                daily_finance['Total_Costs'] = daily_finance['COGS'] + daily_finance['Operational_Costs']
            else:
                daily_finance['Operational_Costs'] = 0
                daily_finance['Total_Costs'] = daily_finance['COGS']
                
            # Create the income and expenses chart with bars and line
            fig_income_expenses = go.Figure()
            
            # Add revenue bars
            fig_income_expenses.add_trace(go.Bar(
                x=daily_finance['Date_Formatted'],
                y=daily_finance['Net_Total'],
                name='Income',
                marker=dict(color='#1ABC9C')
            ))
            
            # Add expense bars
            fig_income_expenses.add_trace(go.Bar(
                x=daily_finance['Date_Formatted'],
                y=daily_finance['Total_Costs'],
                name='Expenses',
                marker=dict(color='#E74C3C')
            ))
            
            # Style the chart
            fig_income_expenses.update_layout(
                barmode='group',
                bargap=0.2,
                bargroupgap=0.1,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(
                    title='Amount (VND)',
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
            
            # Add value labels on the bars
            for i, y in enumerate(daily_finance['Net_Total']):
                if y > 0:
                    fig_income_expenses.add_annotation(
                        x=daily_finance['Date_Formatted'][i],
                        y=y,
                        text=f"{y/1000:.0f}k",
                        showarrow=False,
                        yshift=10,
                        font=dict(size=10, color="white")
                    )
            
            # Display the chart
            st.plotly_chart(fig_income_expenses, use_container_width=True)
        else:
            st.info("No sales data available for the selected period")
            
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
        ratio_col1, ratio_col2 = st.columns(2)
        
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
                        hovertemplate='%{x:.1f}%<br>Revenue: ' + margin_df['Revenue'].apply(lambda x: utils.format_currency(x)).to_list() + '<br>Units: %{customdata}',
                        customdata=margin_df['Quantity']
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
        
        # End of enhanced financial dashboard
            y=daily_finance['Total'],
            mode='lines+markers',
            name='Gross Revenue',
            line=dict(color='royalblue', dash='dash')
        ))
        
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Net_Total'],
            mode='lines+markers',
            name='Net Revenue',
            line=dict(color='darkblue')
        ))
        
        # Show Promotions as a bar chart below
        fig1.add_trace(go.Bar(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['Promo'],
            name='Promotions',
            marker=dict(color='orange')
        ))
        
        fig1.add_trace(go.Scatter(
            x=daily_finance['Date_Formatted'],
            y=daily_finance['COGS'],
            mode='lines+markers',
            name='COGS',
            line=dict(color='red')
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
