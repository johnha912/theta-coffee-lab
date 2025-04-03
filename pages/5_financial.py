import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from utils import initialize_session_state, format_currency, get_date_range, ensure_data_dir
from ui_utils import display_header, display_styled_table

# Initialize session state
initialize_session_state()

# Page config
st.set_page_config(
    page_title="Financial Analysis - Theta Coffee Lab",
    page_icon="💰",
    layout="wide"
)

# Display common header
display_header()

# Main title
st.title("Financial Analysis")

# Time filter
time_filter = st.selectbox(
    "Time range",
    ["Today", "Last 7 days", "Last 30 days", "This month", "All time"],
    index=1  # Default to "Last 7 days"
)

# Load data functions
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

def load_products_data():
    """Load products data"""
    if not os.path.exists("data/products.csv"):
        return pd.DataFrame()
    
    products_df = pd.read_csv("data/products.csv")
    return products_df

def load_expenses_data():
    """Load and filter expenses data"""
    ensure_data_dir()
    if not os.path.exists("data/expenses.csv"):
        # Create empty expenses file
        pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note']).to_csv("data/expenses.csv", index=False)
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

# Add expense function
def add_expense():
    """Add a new expense"""
    # Get form data
    date = st.session_state.expense_date
    category = st.session_state.expense_category
    amount = st.session_state.expense_amount
    note = st.session_state.expense_note
    
    # Create new expense entry
    new_expense = pd.DataFrame({
        'Date': [date],
        'Category': [category],
        'Amount': [amount],
        'Note': [note]
    })
    
    # Load existing expenses
    expenses_df = load_expenses_data()
    if isinstance(expenses_df, pd.DataFrame) and 'Date' in expenses_df.columns:
        # Convert date column to string if it's datetime
        if expenses_df['Date'].dtype == 'datetime64[ns]':
            expenses_df['Date'] = expenses_df['Date'].dt.strftime('%Y-%m-%d')
    else:
        # Create a new DataFrame if expenses_df is empty or missing required columns
        expenses_df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note'])
    
    # Append new expense
    expenses_df = pd.concat([expenses_df, new_expense], ignore_index=True)
    
    # Save to file
    expenses_df.to_csv("data/expenses.csv", index=False)
    
    return True

# Delete expense function
def delete_expense(expense_id):
    """Delete an expense"""
    expenses_df = load_expenses_data()
    if not expenses_df.empty and expense_id < len(expenses_df):
        expenses_df = expenses_df.drop(expense_id).reset_index(drop=True)
        
        # Convert date column to string if it's datetime
        if expenses_df['Date'].dtype == 'datetime64[ns]':
            expenses_df['Date'] = expenses_df['Date'].dt.strftime('%Y-%m-%d')
        
        expenses_df.to_csv("data/expenses.csv", index=False)
        return True
    return False

# Edit expense function
def edit_expense(expense_id, new_date, new_category, new_amount, new_note):
    """Edit an expense"""
    expenses_df = load_expenses_data()
    if not expenses_df.empty and expense_id < len(expenses_df):
        expenses_df.at[expense_id, 'Date'] = new_date
        expenses_df.at[expense_id, 'Category'] = new_category
        expenses_df.at[expense_id, 'Amount'] = new_amount
        expenses_df.at[expense_id, 'Note'] = new_note
        
        # Convert date column to string if it's datetime
        if expenses_df['Date'].dtype == 'datetime64[ns]':
            expenses_df['Date'] = expenses_df['Date'].dt.strftime('%Y-%m-%d')
        
        expenses_df.to_csv("data/expenses.csv", index=False)
        return True
    return False

# Load data
sales_df = load_sales_data()
products_df = load_products_data()
expenses_df = load_expenses_data()

# Add Profit calculation to sales data
if not sales_df.empty and not products_df.empty:
    # Merge sales with product COGS
    sales_with_cogs = sales_df.merge(products_df[['Product', 'COGS']], on='Product', how='left')
    
    # Handle NaN COGS (products without COGS data)
    sales_with_cogs['COGS'] = sales_with_cogs['COGS'].fillna(0)
    
    # Calculate profit
    sales_with_cogs['Profit'] = sales_with_cogs['Total'] - (sales_with_cogs['Quantity'] * sales_with_cogs['COGS'])
else:
    # Create empty DataFrame if either sales or products is empty
    sales_with_cogs = pd.DataFrame(columns=['Date', 'Product', 'Total', 'Profit'])

# Calculate financial metrics
total_revenue = sales_df['Total'].sum() if not sales_df.empty else 0
total_profit = sales_with_cogs['Profit'].sum() if not sales_with_cogs.empty else 0
total_expenses = expenses_df['Amount'].sum() if not expenses_df.empty else 0
net_profit = total_profit - total_expenses

# Calculate profit margin
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

# Create layout
col1, col2 = st.columns(2)

# Left column - Financial metrics
with col1:
    st.subheader("Financial Overview")
    
    # Create metrics 
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric("Total Revenue", format_currency(total_revenue))
        st.metric("Total Profit", format_currency(total_profit))
    
    with metrics_col2:
        st.metric("Total Expenses", format_currency(total_expenses))
        st.metric("Net Profit", format_currency(net_profit))
    
    st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    # Expense management
    st.subheader("Manage Expenses")
    
    with st.form("add_expense_form", clear_on_submit=True):
        st.date_input("Date", value=datetime.now(), key="expense_date")
        st.selectbox("Category", 
                   ["Rent", "Utilities", "Salary", "Inventory", "Marketing", "Maintenance", "Other"],
                   key="expense_category")
        st.number_input("Amount (VND)", min_value=0, step=10000, key="expense_amount")
        st.text_input("Note", key="expense_note")
        
        submit_col, _ = st.columns(2)
        with submit_col:
            submit_button = st.form_submit_button("Add Expense", use_container_width=True)
    
    # Process form submission
    if submit_button:
        if st.session_state.expense_amount > 0:
            # Format date to string
            if isinstance(st.session_state.expense_date, datetime):
                st.session_state.expense_date = st.session_state.expense_date.strftime("%Y-%m-%d")
            
            if add_expense():
                st.success("Expense added successfully!")
                st.rerun()
        else:
            st.error("Please enter a valid amount.")

# Right column - Financial analysis
with col2:
    st.subheader("Profit & Loss Analysis")
    
    if not sales_with_cogs.empty:
        # Group by date
        daily_financials = sales_with_cogs.groupby('Date').agg(
            Revenue=('Total', 'sum'),
            Profit=('Profit', 'sum')
        ).reset_index()
        
        # Add expenses per day
        expense_per_day = expenses_df.groupby('Date').agg(
            Expenses=('Amount', 'sum')
        ).reset_index() if not expenses_df.empty else pd.DataFrame(columns=['Date', 'Expenses'])
        
        # Merge with daily financials
        if not expense_per_day.empty:
            daily_financials = daily_financials.merge(expense_per_day, on='Date', how='left')
            daily_financials['Expenses'] = daily_financials['Expenses'].fillna(0)
            daily_financials['Net_Profit'] = daily_financials['Profit'] - daily_financials['Expenses']
        else:
            daily_financials['Expenses'] = 0
            daily_financials['Net_Profit'] = daily_financials['Profit']
        
        # Format date for display in chart
        daily_financials['FormattedDate'] = pd.to_datetime(daily_financials['Date']).dt.strftime('%d/%m/%y')
        
        # Create a line chart for revenue, profit, and net profit
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_financials['Date'],
            y=daily_financials['Revenue'],
            name='Revenue',
            line=dict(color='#4CAF50', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_financials['Date'],
            y=daily_financials['Profit'],
            name='Gross Profit',
            line=dict(color='#2196F3', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_financials['Date'],
            y=daily_financials['Net_Profit'],
            name='Net Profit',
            line=dict(color='#FF9800', width=2)
        ))
        
        fig.update_layout(
            title='Daily Financial Performance',
            xaxis_title='Date',
            yaxis_title='Amount (VND)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template='ggplot2',
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            xaxis=dict(tickformat='%d/%m/%y'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Product profitability analysis
        if 'Product' in sales_with_cogs.columns and 'Profit' in sales_with_cogs.columns:
            # Group by product
            product_profit = sales_with_cogs.groupby('Product').agg(
                Revenue=('Total', 'sum'),
                Profit=('Profit', 'sum'),
                Units=('Quantity', 'sum')
            ).reset_index()
            
            # Calculate profit margin percentage
            product_profit['Profit_Margin'] = (product_profit['Profit'] / product_profit['Revenue'] * 100).round(1)
            
            # Sort by profit
            product_profit = product_profit.sort_values('Profit', ascending=False)
            
            # Top 5 most profitable products
            top_products = product_profit.head(5)
            
            # Create a bar chart
            if not top_products.empty:
                fig_products = px.bar(
                    top_products,
                    x='Product',
                    y='Profit',
                    text='Profit_Margin',
                    title='Top 5 Most Profitable Products',
                    color='Profit_Margin',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    template='ggplot2'
                )
                
                fig_products.update_traces(
                    texttemplate='%{text:.1f}%', 
                    textposition='outside'
                )
                
                fig_products.update_layout(
                    xaxis_title='Product',
                    yaxis_title='Profit (VND)',
                    coloraxis_colorbar=dict(title='Profit Margin (%)'),
                    plot_bgcolor='rgba(240, 240, 240, 0.8)',
                    paper_bgcolor='rgba(255, 255, 255, 0.8)',
                    height=400
                )
                
                st.plotly_chart(fig_products, use_container_width=True)
            else:
                st.info("No product profitability data available for the selected time period.")
        else:
            st.info("Product profitability data not available. Check if COGS is set for products.")
    else:
        st.info("No financial data available for the selected time period.")

# Expense breakdown
st.subheader("Expense Breakdown")

# First show a breakdown of expenses by category
if not expenses_df.empty:
    expense_by_category = expenses_df.groupby('Category').agg(
        Amount=('Amount', 'sum')
    ).reset_index()
    
    # Create a pie chart
    fig_expense = px.pie(
        expense_by_category,
        values='Amount',
        names='Category',
        title='Expenses by Category',
        template='ggplot2'
    )
    
    fig_expense.update_traces(
        textinfo='percent+label',
        hole=0.4
    )
    
    fig_expense.update_layout(
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.8)',
    )
    
    st.plotly_chart(fig_expense, use_container_width=True)
    
    # Show the expense table with edit/delete functionality
    st.subheader("Expense Details")
    
    # Create a formatted table for display
    display_df = expenses_df.copy()
    if 'Date' in display_df.columns and display_df['Date'].dtype == 'datetime64[ns]':
        display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
    
    # For each expense, provide edit/delete controls
    for i, row in expenses_df.reset_index().iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 2])
        
        with col1:
            if isinstance(row['Date'], str):
                try:
                    date_obj = datetime.strptime(row['Date'], '%Y-%m-%d')
                except ValueError:
                    date_obj = datetime.now()
            else:
                date_obj = row['Date']
            
            new_date = st.date_input(f"Date {i}", value=date_obj, key=f"edit_date_{i}")
        
        with col2:
            categories = ["Rent", "Utilities", "Salary", "Inventory", "Marketing", "Maintenance", "Other"]
            cat_index = categories.index(row['Category']) if row['Category'] in categories else 0
            new_category = st.selectbox(f"Category {i}", categories, index=cat_index, key=f"edit_cat_{i}")
        
        with col3:
            new_amount = st.number_input(f"Amount {i}", min_value=0, value=int(row['Amount']), step=10000, key=f"edit_amt_{i}")
        
        with col4:
            new_note = st.text_input(f"Note {i}", value=row['Note'], key=f"edit_note_{i}")
        
        with col5:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some space
            
            if st.button("Save", key=f"save_exp_{i}", use_container_width=True):
                if edit_expense(i, new_date.strftime("%Y-%m-%d"), new_category, new_amount, new_note):
                    st.success("Expense updated successfully!")
                    st.rerun()
            
            if st.button("Delete", key=f"del_exp_{i}", use_container_width=True):
                if delete_expense(i):
                    st.success("Expense deleted successfully!")
                    st.rerun()
else:
    st.info("No expense data available. Add expenses using the form.")