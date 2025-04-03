import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from utils import initialize_session_state, format_currency, get_date_range
from ui_utils import display_header, display_card, display_summary_metrics, display_styled_table

# Initialize session state
initialize_session_state()

# Page config
st.set_page_config(
    page_title="Dashboard - Theta Coffee Lab",
    page_icon="☕",
    layout="wide"
)

# Display common header
display_header()

# Main title
st.title("Dashboard")

# Time filter
time_filter = st.selectbox(
    "Time range",
    ["Today", "Last 7 days", "Last 30 days", "This month", "All time"],
    index=1  # Default to "Last 7 days"
)

def load_sales_data():
    """Load and filter sales data"""
    if not os.path.exists("data/sales.csv"):
        return pd.DataFrame()
    
    sales_df = pd.read_csv("data/sales.csv")
    if sales_df.empty:
        return pd.DataFrame()
    
    # Convert Date to datetime
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    
    # Filter by date range
    start_date, end_date = get_date_range(time_filter)
    filtered_df = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]
    
    return filtered_df

def load_expenses_data():
    """Load and filter expenses data"""
    if not os.path.exists("data/expenses.csv"):
        return pd.DataFrame()
    
    expenses_df = pd.read_csv("data/expenses.csv")
    if expenses_df.empty:
        return pd.DataFrame()
    
    # Convert Date to datetime
    expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
    
    # Filter by date range
    start_date, end_date = get_date_range(time_filter)
    filtered_df = expenses_df[(expenses_df['Date'] >= start_date) & (expenses_df['Date'] <= end_date)]
    
    return filtered_df

def load_inventory_data():
    """Load inventory data"""
    if not os.path.exists("data/inventory.csv"):
        return pd.DataFrame()
    
    inventory_df = pd.read_csv("data/inventory.csv")
    return inventory_df

def load_product_data():
    """Load product data"""
    if not os.path.exists("data/products.csv"):
        return pd.DataFrame()
    
    products_df = pd.read_csv("data/products.csv")
    return products_df

# Load data
sales_df = load_sales_data()
expenses_df = load_expenses_data()
inventory_df = load_inventory_data()
products_df = load_product_data()

# Calculate metrics
if not sales_df.empty:
    total_sales = sales_df['Total'].sum()
    total_orders = sales_df['OrderID'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Top selling products
    product_sales = sales_df.groupby('Product').agg(
        Sales=('Total', 'sum'),
        Quantity=('Quantity', 'sum')
    ).reset_index().sort_values('Sales', ascending=False)
    
    # Calculate profit if COGS is available
    if not products_df.empty and 'COGS' in products_df.columns:
        sales_with_products = sales_df.merge(products_df[['Product', 'COGS']], on='Product', how='left')
        sales_with_products['Profit'] = sales_with_products['Total'] - (sales_with_products['Quantity'] * sales_with_products['COGS'])
        total_profit = sales_with_products['Profit'].sum()
    else:
        total_profit = 0
else:
    total_sales = 0
    total_orders = 0
    avg_order_value = 0
    total_profit = 0
    product_sales = pd.DataFrame(columns=['Product', 'Sales', 'Quantity'])

# Expenses
total_expenses = expenses_df['Amount'].sum() if not expenses_df.empty else 0
net_income = total_profit - total_expenses

# Display metrics
with st.container():
    metrics = {
        "Total Revenue": {
            "value": total_sales,
            "help": "Total revenue from all sales in the selected period",
            "unit": "VND"
        },
        "Total Orders": {
            "value": total_orders,
            "help": "Number of unique orders in the selected period"
        },
        "Average Order Value": {
            "value": avg_order_value,
            "help": "Average value per order",
            "unit": "VND"
        },
        "Net Income": {
            "value": net_income,
            "help": "Profit after expenses",
            "unit": "VND"
        }
    }
    display_summary_metrics(metrics)

# Sales trend chart
st.subheader("Sales Trend")

if not sales_df.empty:
    # Group by date
    daily_sales = sales_df.groupby('Date').agg(
        Revenue=('Total', 'sum'),
        Orders=('OrderID', 'nunique')
    ).reset_index()
    
    # Format date to DD/MM/YY
    daily_sales['FormattedDate'] = daily_sales['Date'].dt.strftime('%d/%m/%y')
    
    # Plot using Plotly
    fig_sales = px.line(
        daily_sales, 
        x='Date', 
        y='Revenue',
        labels={'Date': 'Date', 'Revenue': 'Revenue (VND)'},
        title='Daily Revenue',
        template='ggplot2'
    )
    fig_sales.update_traces(mode='lines+markers')
    fig_sales.update_layout(
        xaxis_title='Date',
        yaxis_title='Revenue (VND)',
        xaxis=dict(tickformat='%d/%m/%y'),
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.8)',
        height=400
    )
    st.plotly_chart(fig_sales, use_container_width=True)
else:
    st.info("No sales data available for the selected time period.")

# Columns for charts
col1, col2 = st.columns(2)

# Top selling products
with col1:
    st.subheader("Top Selling Products")
    if not product_sales.empty:
        # Create a bar chart for top 5 products
        top_products = product_sales.head(5)
        fig_products = px.bar(
            top_products,
            y='Product',
            x='Sales',
            title='Top 5 Products by Sales',
            orientation='h',
            text='Sales',
            labels={'Sales': 'Sales (VND)', 'Product': 'Product'},
            template='ggplot2'
        )
        fig_products.update_traces(
            texttemplate='%{text:,.0f} VND', 
            textposition='outside'
        )
        fig_products.update_layout(
            xaxis_title='Sales (VND)',
            yaxis_title='Product',
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            height=400
        )
        st.plotly_chart(fig_products, use_container_width=True)
    else:
        st.info("No product sales data available for the selected time period.")

# Category distribution
with col2:
    st.subheader("Category Distribution")
    if not sales_df.empty and not products_df.empty:
        # Merge sales with product categories
        sales_with_category = sales_df.merge(products_df[['Product', 'Category']], on='Product', how='left')
        
        # Group by category
        category_sales = sales_with_category.groupby('Category').agg(
            Sales=('Total', 'sum')
        ).reset_index().sort_values('Sales', ascending=False)
        
        # Create a pie chart
        fig_categories = px.pie(
            category_sales,
            values='Sales',
            names='Category',
            title='Sales by Category',
            template='ggplot2'
        )
        fig_categories.update_traces(
            textinfo='percent+label',
            hole=0.4
        )
        fig_categories.update_layout(
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            height=400
        )
        st.plotly_chart(fig_categories, use_container_width=True)
    else:
        st.info("No category data available for the selected time period.")

# Recent orders section
st.subheader("Recent Orders")
if not sales_df.empty:
    recent_orders = sales_df.sort_values('Date', ascending=False).head(10)
    
    # Format the table
    display_df = recent_orders[['OrderID', 'Date', 'Time', 'Product', 'Quantity', 'Total']].copy()
    
    # Format date
    display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%y')
    
    # Add currency formatting
    display_df['Total'] = display_df['Total'].apply(lambda x: f"{x:,.0f}")
    
    # Display the table
    display_styled_table(display_df)
else:
    st.info("No recent orders available for the selected time period.")

# Low inventory alert
st.subheader("Inventory Alerts")
if not inventory_df.empty:
    # Calculate threshold
    threshold = st.session_state.alert_threshold if 'alert_threshold' in st.session_state else 10
    
    # Find low stock items
    low_stock = inventory_df[inventory_df['Quantity'] <= threshold].sort_values('Quantity')
    
    if not low_stock.empty:
        display_styled_table(low_stock[['Item', 'Unit', 'Quantity']])
    else:
        st.success("All inventory items are above the alert threshold.")
else:
    st.info("No inventory data available.")