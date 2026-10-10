import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import utils
import store

# Initialize session_state
utils.initialize_session_state()

header, period = st.columns([3, 2], vertical_alignment="bottom")
with header:
    st.title("Dashboard")
    st.caption("Overview of Cafe Performance")

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
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
else:
    start_date, end_date = utils.get_date_range(time_filter)

try:
    # Load data
    sales_df = store.load("sales")
    inventory_df = store.load("inventory")
    products_df = store.load("products")
    product_recipe_df = store.load("product_recipe")

    # Prepare sales data
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
    filtered_sales = sales_df[(sales_df['Date'].dt.date >= start_date) &
                              (sales_df['Date'].dt.date <= end_date)].copy()

    # Add Net_Total and Promo columns if they don't exist
    if 'Net_Total' not in filtered_sales.columns:
        filtered_sales['Net_Total'] = filtered_sales['Total']
    if 'Promo' not in filtered_sales.columns:
        filtered_sales['Promo'] = 0.0

    if filtered_sales.empty:
        st.info(f"No sales in **{time_filter}**. Pick a longer period, such as All Time.", icon=":material/event_busy:")
        st.stop()

    kpi = utils.sales_summary(filtered_sales, products_df)

    # Top selling product
    product_sales = filtered_sales.groupby('Product')['Quantity'].sum().reset_index()
    top_product = product_sales.loc[product_sales['Quantity'].idxmax()]

    # Calculate ingredients used
    filtered_sales_recipe = filtered_sales.rename(columns={'Quantity': 'Order_Quantity'})  # Rename to avoid collision
    product_recipe_df_renamed = product_recipe_df.rename(columns={'Quantity': 'Recipe_Quantity'})  # Rename recipe quantity
    merged_df = pd.merge(filtered_sales_recipe, product_recipe_df_renamed, left_on='Product', right_on='Product')
    # Calculate total ingredient use (order quantity * recipe quantity)
    merged_df['Total_Ingredient_Used'] = merged_df['Order_Quantity'] * merged_df['Recipe_Quantity']
    ingredients_used = merged_df.groupby('Ingredient')['Total_Ingredient_Used'].sum().reset_index()
    ingredients_used.columns = ['Ingredient', 'Quantity_Used']
    top_ingredients = ingredients_used.sort_values('Quantity_Used', ascending=False).head(5)

    # Daily series for the charts and the KPI sparklines
    filtered_sales['Gross_Profit'] = utils.row_gross_profit(filtered_sales, products_df)
    filtered_sales['Is_Top'] = filtered_sales['Product'] == top_product['Product']
    daily = filtered_sales.groupby(filtered_sales['Date'].dt.date).agg(
        Revenue=('Net_Total', 'sum'),
        Gross_Profit=('Gross_Profit', 'sum'),
        Orders=('Order_ID', 'nunique'),
        Cups=('Quantity', 'sum'),
    ).rename_axis('Date').reset_index()
    daily['Margin'] = (daily['Gross_Profit'] / daily['Revenue'] * 100).where(daily['Revenue'] > 0, 0)
    daily['Order_Value'] = daily['Revenue'] / daily['Orders']
    top_daily = filtered_sales[filtered_sales['Is_Top']].groupby(filtered_sales['Date'].dt.date)['Quantity'].sum()

    # Key performance indicators: two full-width rows of equal tiles, each with a daily sparkline
    tile = dict(border=True, height="stretch")
    row = st.columns(4)
    row[0].metric("Total Revenue", utils.format_currency(kpi['revenue']), icon=":material/payments:",
                  chart_data=daily['Revenue'], chart_type="area", **tile)
    row[1].metric("Gross Profit", utils.format_currency(kpi['gross_profit']), icon=":material/trending_up:",
                  chart_data=daily['Gross_Profit'], chart_type="area", **tile)
    row[2].metric("Total Orders", f"{kpi['orders']:,}", icon=":material/receipt_long:",
                  chart_data=daily['Orders'], chart_type="bar", **tile)
    row[3].metric("Gross Profit Margin", f"{kpi['margin']:.2f}%", icon=":material/percent:",
                  chart_data=daily['Margin'], chart_type="line", **tile)
    row = st.columns(3)
    row[0].metric("Best Selling Product", top_product['Product'], f"{int(top_product['Quantity'])} units",
                  delta_color="off", delta_arrow="off", icon=":material/workspace_premium:",
                  chart_data=top_daily, chart_type="bar", **tile)
    row[1].metric("Total Coffee Cups Sold", f"{kpi['cups']:,}", icon=":material/coffee:",
                  chart_data=daily['Cups'], chart_type="bar", **tile)
    row[2].metric("Average Order Value", utils.format_currency(kpi['revenue'] / kpi['orders']),
                  icon=":material/shopping_bag:", chart_data=daily['Order_Value'], chart_type="line", **tile)

    fig1 = px.area(
        daily,
        x='Date',
        y='Revenue',
        title='Daily Revenue',
        labels={'Date': 'Date', 'Revenue': 'Revenue (VND)'},
        height=380
    )
    fig1.update_xaxes(tickformat='%d/%m/%y')
    utils.chart(fig1)

    # Two rankings side by side, same height and form
    col1, col2 = st.columns(2)
    with col1:
        utils.chart(utils.hbar(product_sales.nlargest(8, 'Quantity'), 'Quantity', 'Product',
                               'Top 8 Products by Cups Sold', labels={'Quantity': 'Cups'}, height=380))
    with col2:
        utils.chart(utils.hbar(top_ingredients, 'Quantity_Used', 'Ingredient', 'Top 5 Ingredients Used',
                               labels={'Quantity_Used': 'Quantity Used'}, height=380))

    with st.container(border=True):
        # Intelligent inventory alerts
        st.markdown("**Inventory Alerts**")

        low_stock = utils.low_stock(inventory_df, st.session_state.alert_threshold)
        if not low_stock.empty:
            st.warning(f"{len(low_stock)} items below recommended threshold!", icon=":material/warning:")
            st.dataframe(low_stock[['Name', 'Quantity', 'Unit']], hide_index=True)
        else:
            st.success("All inventory items are at healthy levels.", icon=":material/check_circle:")

except Exception as e:
    st.error(f"Error loading dashboard data: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
