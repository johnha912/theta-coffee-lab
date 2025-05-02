import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import datetime
from geopy.geocoders import Nominatim
import utils

# Initialize session state
utils.initialize_session_state()

# Set page config
st.set_page_config(page_title="User Map", page_icon="🗺️", layout="wide")

# Set default template to ggplot2 (consistent with other pages)
pio.templates.default = 'ggplot2'

# Custom ggplot2 template with gray background and white grid
custom_ggplot2_template = pio.templates['ggplot2']
custom_ggplot2_template.layout.update(
    paper_bgcolor='#F0F0F0',  # Paper background color
    plot_bgcolor='#F0F0F0',   # Plot background color
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

# Add page title
st.title("Customer Map")
st.subheader("Visualize order locations on a map")

# Initialize geocoder
@st.cache_resource
def get_geocoder():
    """Get a geocoder instance"""
    return Nominatim(user_agent="theta_coffee_lab_app")

geocoder = get_geocoder()

# Function to geocode addresses - cached to reduce API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def geocode_address(address):
    """Convert address to coordinates using geocoder"""
    if not address:
        return None, None
    
    try:
        location = geocoder.geocode(address)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        st.error(f"Error geocoding address: {str(e)}")
        return None, None

# Function to create map of order locations
def create_order_map(sales_df, time_filter="All Time"):
    """Create map visualization of order locations"""
    
    try:
        # Apply time filter
        start_date, _ = utils.get_date_range(time_filter)
        filtered_df = sales_df[sales_df['Date'] >= start_date]
        
        # Group by Order_ID and get unique locations
        if 'Location' in filtered_df.columns:
            # First, get the first item for each order (which has the location)
            order_groups = filtered_df.groupby('Order_ID')
            orders_with_location = []
            
            for order_id, group in order_groups:
                # Get first row in group (first item in order)
                first_item = group.iloc[0]
                location = first_item.get('Location', '')
                
                if location:  # Only include orders with locations
                    # Geocode the location
                    lat, lon = geocode_address(location)
                    
                    if lat is not None and lon is not None:
                        total = group['Total'].sum()
                        promo = group['Promo'].sum() if 'Promo' in group.columns else 0
                        net_total = group['Net_Total'].sum() if 'Net_Total' in group.columns else total
                        
                        orders_with_location.append({
                            'Order_ID': order_id,
                            'Location': location,
                            'Date': first_item['Date'],
                            'Total': total,
                            'Latitude': lat,
                            'Longitude': lon
                        })
            
            if orders_with_location:
                # Create dataframe with geocoded locations
                map_df = pd.DataFrame(orders_with_location)
                
                # Format for display
                map_df['Size'] = np.log1p(map_df['Total']) * 3  # Log scale for better visualization
                map_df['Total_Display'] = map_df['Total'].apply(utils.format_currency)
                map_df['Date_Display'] = pd.to_datetime(map_df['Date']).dt.strftime('%d/%m/%y %H:%M')
                
                # Prepare hover text
                map_df['Hover_Text'] = map_df.apply(
                    lambda row: f"Order ID: {row['Order_ID']}<br>" + 
                               f"Location: {row['Location']}<br>" + 
                               f"Date: {row['Date_Display']}<br>" + 
                               f"Total: {row['Total_Display']}", 
                    axis=1
                )
                
                # Create map with Plotly
                fig = px.scatter_mapbox(
                    map_df, 
                    lat="Latitude", 
                    lon="Longitude", 
                    size="Size",
                    color="Total",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    hover_name="Order_ID",
                    hover_data=["Date_Display", "Total_Display", "Location"],
                    zoom=12,
                    height=600,
                    template="custom_ggplot2"
                )
                
                # Update layout to use open street map
                fig.update_layout(
                    mapbox_style="open-street-map",
                    margin={"r":0,"t":0,"l":0,"b":0},
                    coloraxis_colorbar=dict(
                        title="Total (VND)",
                        tickformat=",",
                    )
                )
                
                return fig
            else:
                st.info("No orders with valid locations found in the selected time period.")
                return None
        else:
            st.info("No location data found in the sales records.")
            return None
            
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None

# Main app code
try:
    # Load sales data
    sales_df = pd.read_csv("data/sales.csv")
    
    if not sales_df.empty:
        # Convert Date column to datetime
        sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
        
        # Add time filter options
        time_options = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
        time_filter = st.selectbox("Time Period", options=time_options, index=0)
        
        # Create and display map
        map_fig = create_order_map(sales_df, time_filter)
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
            
        # Display order location data in table form
        st.subheader("Order Locations")
        
        # Apply time filter
        start_date, _ = utils.get_date_range(time_filter)
        filtered_df = sales_df[sales_df['Date'] >= start_date]
        
        if 'Location' in filtered_df.columns:
            # Get unique orders with locations
            order_groups = filtered_df.groupby('Order_ID')
            orders_with_location = []
            
            for order_id, group in order_groups:
                first_item = group.iloc[0]
                location = first_item.get('Location', '')
                
                if location:  # Only include orders with locations
                    date = first_item['Date']
                    total = group['Total'].sum()
                    
                    orders_with_location.append({
                        'Order_ID': order_id,
                        'Date': date,
                        'Location': location,
                        'Total': total
                    })
            
            if orders_with_location:
                # Create dataframe for table
                table_df = pd.DataFrame(orders_with_location)
                
                # Format for display
                table_df['Date'] = pd.to_datetime(table_df['Date']).dt.strftime('%d/%m/%y %H:%M')
                table_df['Total'] = table_df['Total'].apply(lambda x: utils.format_currency(x, include_currency=True))
                
                # Sort by date (newest first)
                table_df = table_df.sort_values('Date', ascending=False)
                
                # Display table
                st.dataframe(table_df, hide_index=True)
            else:
                st.info("No orders with location data in the selected time period.")
        else:
            st.info("No location data available in sales records. Please add locations to your orders.")
    else:
        st.info("No sales data available. Please create orders with location information.")
        
except FileNotFoundError:
    st.error("Sales data not found. Please make sure data/sales.csv exists.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check that your data files exist and are properly formatted.")