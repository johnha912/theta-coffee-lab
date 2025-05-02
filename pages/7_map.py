import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import datetime
from geopy.geocoders import Nominatim, Photon
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
    try:
        # Try Photon first (better with international addresses)
        return Photon(user_agent="theta_coffee_lab_app")
    except:
        # Fall back to Nominatim
        return Nominatim(user_agent="theta_coffee_lab_app")

geocoder = get_geocoder()

# Function to geocode addresses - cached to reduce API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def geocode_address(address):
    """Convert address to coordinates using geocoder"""
    if not address:
        return None, None
    
    try:
        # Ensure address is a string (handle case where it might be a float or other type)
        if not isinstance(address, str):
            # Try to convert to string
            try:
                address = str(address)
                # If it's a number (like NaN), return None
                if address.lower() == 'nan':
                    return None, None
            except:
                return None, None
        
        # Skip empty addresses
        if not address.strip():
            return None, None
        
        # Dictionary of known locations for common Vietnamese addresses
        # Format: {partial_address: (latitude, longitude)}
        known_locations = {
            # Ho Chi Minh City locations
            "tran cao van street": (10.7752, 106.6901),  # Trần Cao Vân
            "tran cao van": (10.7752, 106.6901),         # Trần Cao Vân
            "district 3": (10.7756, 106.6842),           # Quận 3
            "ward 6": (10.7718, 106.6880),               # Phường 6
            "41 tran cao van": (10.7752, 106.6901),      # 41 Trần Cao Vân
            "hcmc": (10.7756, 106.6842),                 # Ho Chi Minh City
            "ho chi minh city": (10.7756, 106.6842),     # Ho Chi Minh City
            "700000": (10.7756, 106.6842),               # HCMC postal code
            "vietnam": (16.0544, 108.2022),              # Default for Vietnam
            # Exact match for the address in the data
            "41 tran cao van street, ward 6, district 3, hcmc, vietnam 700000, ho chi minh city": (10.7752, 106.6901)
        }
        
        # Check for known locations first (case insensitive)
        address_lower = address.lower()
        for key, coords in known_locations.items():
            if key in address_lower:
                st.success(f"✅ Found in known locations: {key} → {coords}")
                return coords
        
        # For Vietnamese addresses, add country code if not present
        if not address_lower.endswith('vietnam') and not address_lower.endswith('việt nam'):
            if 'hcm' in address_lower or 'ho chi minh' in address_lower or 'tphcm' in address_lower:
                # Ensure Ho Chi Minh City is properly formatted for geocoding
                if not any(term in address_lower for term in ['ho chi minh city', 'hồ chí minh', 'thành phố hồ chí minh']):
                    address = address + ', Ho Chi Minh City'
            # Add Vietnam to the address
            address = address + ', Vietnam'
            
        # Debug information
        st.write(f"Geocoding address: {address}")
        
        # Use specific parameters to improve accuracy
        try:
            location = geocoder.geocode(
                address,
                exactly_one=True,
                addressdetails=True,
                language="vi"  # Vietnamese language
            )
            if location:
                st.success(f"✅ Found coordinates: {location.latitude}, {location.longitude}")
                return location.latitude, location.longitude
            else:
                st.warning("⚠️ Vietnamese geocoding failed, trying English...")
        except Exception as e:
            st.error(f"❌ Geocoding error (VI): {str(e)}")
        
        # Fallback: try with English language setting
        try:
            location = geocoder.geocode(
                address,
                exactly_one=True,
                addressdetails=True,
                language="en"
            )
            if location:
                st.success(f"✅ Found coordinates with EN: {location.latitude}, {location.longitude}")
                return location.latitude, location.longitude
            else:
                st.error("❌ Both Vietnamese and English geocoding failed")
        except Exception as e:
            st.error(f"❌ Geocoding error (EN): {str(e)}")
        
        # If all geocoding attempts fail, return Ho Chi Minh City coordinates
        # for Vietnamese addresses as a last resort
        if 'vietnam' in address_lower or 'ho chi minh' in address_lower or 'hcm' in address_lower or 'tphcm' in address_lower:
            st.warning("⚠️ Using default Ho Chi Minh City coordinates")
            return 10.7756, 106.6842  # Default coordinates for HCMC
            
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
        # Convert start_date to datetime64 for consistent comparison
        start_date = pd.to_datetime(start_date)
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
                
                # Make sure location is a valid string, not float or NaN
                if isinstance(location, float):
                    location = str(location) if not pd.isna(location) else ""
                
                if location and location.strip() and location.lower() != "nan":  # Only include valid locations
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
        time_filter = st.selectbox("Time Period", options=time_options, index=5)  # Set default to "All Time"
        
        # Create and display map
        map_fig = create_order_map(sales_df, time_filter)
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
            
        # Display order location data in table form
        st.subheader("Order Locations")
        
        # Apply time filter
        start_date, _ = utils.get_date_range(time_filter)
        # Convert start_date to datetime64 for consistent comparison
        start_date = pd.to_datetime(start_date)
        filtered_df = sales_df[sales_df['Date'] >= start_date]
        
        if 'Location' in filtered_df.columns:
            # Get unique orders with locations
            order_groups = filtered_df.groupby('Order_ID')
            orders_with_location = []
            
            for order_id, group in order_groups:
                first_item = group.iloc[0]
                location = first_item.get('Location', '')
                
                # Make sure location is a valid string, not float or NaN
                if isinstance(location, float):
                    location = str(location) if not pd.isna(location) else ""
                
                if location and location.strip() and location.lower() != "nan":  # Only include valid locations
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