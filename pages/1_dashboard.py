import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
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

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Navigation menu
def display_navigation():
    menu_container = st.container()
    with menu_container:
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        with col2:
            nav_cols = st.columns(7)
            with nav_cols[0]:
                st.page_link("app.py", label="🏠", help="Home")
            with nav_cols[1]:
                st.page_link("pages/1_dashboard.py", label="📊", help="Dashboard")
            with nav_cols[2]:
                st.page_link("pages/2_order.py", label="🧾", help="Order")
            with nav_cols[3]:
                st.page_link("pages/3_inventory.py", label="🗄️", help="Inventory")
            with nav_cols[4]:
                st.page_link("pages/4_product.py", label="☕️", help="Product")
            with nav_cols[5]:
                st.page_link("pages/5_financial.py", label="💵", help="Financial")
            with nav_cols[6]:
                st.page_link("pages/6_settings.py", label="⚙️", help="Settings")
        # Removed user display from navigation menu as per user request

display_navigation()
st.divider()

st.title("Dashboard")
st.subheader("Overview of Cafe Performance")

# Time filter
time_options = ["Today", "Last 7 Days", "Last 30 Days", "Custom"]
time_filter = st.selectbox("Time Period", options=time_options, index=time_options.index(st.session_state.default_time_filter))

# Date range for custom filter
if time_filter == "Custom":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
else:
    # Set date range based on selection
    end_date = datetime.now().date()
    if time_filter == "Today":
        start_date = end_date
    elif time_filter == "Last 7 Days":
        start_date = end_date - timedelta(days=6)
    elif time_filter == "Last 30 Days":
        start_date = end_date - timedelta(days=29)

try:
    # Load data
    sales_df = pd.read_csv("data/sales.csv")
    inventory_df = pd.read_csv("data/inventory.csv")
    products_df = pd.read_csv("data/products.csv")
    product_recipe_df = pd.read_csv("data/product_recipe.csv")
    
    # Prepare sales data
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    filtered_sales = sales_df[(sales_df['Date'].dt.date >= start_date) & 
                             (sales_df['Date'].dt.date <= end_date)]
    
    # Calculate KPIs
    total_revenue = filtered_sales['Total'].sum()
    total_orders = len(filtered_sales['Order_ID'].unique())
    
    # Top selling product
    product_sales = filtered_sales.groupby('Product')['Quantity'].sum().reset_index()
    top_product = product_sales.loc[product_sales['Quantity'].idxmax()] if not product_sales.empty else pd.Series({'Product': 'N/A', 'Quantity': 0})
    
    # Total coffee cups sold
    total_cups = filtered_sales['Quantity'].sum()
    
    # Calculate ingredients used
    filtered_sales_recipe = filtered_sales.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
    product_recipe_df_renamed = product_recipe_df.rename(columns={'Quantity': 'Recipe_Quantity'})  # Rename recipe quantity
    merged_df = pd.merge(filtered_sales_recipe, product_recipe_df_renamed, left_on='Product', right_on='Product')
    # Calculate total ingredient use (order quantity * recipe quantity)
    merged_df['Total_Ingredient_Used'] = merged_df['Order_Quantity'] * merged_df['Recipe_Quantity'] 
    ingredients_used = merged_df.groupby('Ingredient')['Total_Ingredient_Used'].sum().reset_index()
    ingredients_used.columns = ['Ingredient', 'Quantity_Used']
    top_ingredients = ingredients_used.sort_values('Quantity_Used', ascending=False).head(5)
    
    # Calculate gross profit
    filtered_sales_copy = filtered_sales.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
    product_costs = pd.merge(filtered_sales_copy, products_df, left_on='Product', right_on='Name')
    gross_profit = total_revenue - (product_costs['COGS'] * product_costs['Order_Quantity']).sum()
    
    # Display KPIs
    st.header("Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", utils.format_currency(total_revenue))
        st.metric("Total Orders", f"{total_orders}")
    
    with col2:
        st.metric("Best Selling Product", f"{top_product['Product']} ({int(top_product['Quantity'])} units)")
        st.metric("Total Coffee Cups Sold", f"{total_cups}")
    
    with col3:
        st.metric("Gross Profit", utils.format_currency(gross_profit))
        gp_percentage = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Gross Profit Margin", f"{gp_percentage:.2f}%")
    
    # Charts
    st.header("Performance Charts")
    
    # Daily revenue chart
    daily_revenue = filtered_sales.groupby(filtered_sales['Date'].dt.date)['Total'].sum().reset_index()
    
    # Format date to DD/MM/YY
    daily_revenue['Date_Formatted'] = daily_revenue['Date'].apply(lambda x: x.strftime('%d/%m/%y'))
    
    fig1 = px.line(
        daily_revenue, 
        x='Date_Formatted', 
        y='Total',
        title='Daily Revenue',
        labels={'Date_Formatted': 'Date', 'Total': 'Revenue (VND)'}
    )
    fig1.update_layout(xaxis_title='Date', yaxis_title='Revenue (VND)')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Top 5 ingredients used chart
    fig2 = px.bar(
        top_ingredients,
        x='Ingredient',
        y='Quantity_Used',
        title='Top 5 Ingredients Used',
        labels={'Ingredient': 'Ingredient', 'Quantity_Used': 'Quantity Used'}
    )
    fig2.update_layout(xaxis_title='Ingredient', yaxis_title='Quantity Used')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Additional insights
    col1, col2 = st.columns(2)
    
    with col1:
        # Product sales breakdown
        st.subheader("Product Sales Breakdown")
        product_breakdown = filtered_sales.groupby('Product')['Quantity'].sum().reset_index()
        product_breakdown = product_breakdown.sort_values('Quantity', ascending=False)
        
        fig3 = px.pie(
            product_breakdown, 
            values='Quantity', 
            names='Product',
            title='Product Sales Distribution'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Low inventory alert
        st.subheader("Inventory Alerts")
        low_inventory = inventory_df[inventory_df['Quantity'] <= st.session_state.alert_threshold]
        
        if not low_inventory.empty:
            st.warning(f"{len(low_inventory)} items below threshold!")
            st.dataframe(low_inventory[['Name', 'Quantity', 'Unit']])
        else:
            st.success("All inventory items are above threshold levels")

except Exception as e:
    st.error(f"Error loading dashboard data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
