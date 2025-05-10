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
st.subheader("Visualize order locations using Google Plus Codes")

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

# Function to parse Google Plus Codes
def parse_plus_code(plus_code):
    """
    Parse a Google Plus Code and return approximate coordinates
    
    The function handles Plus Codes in format like: "QMMW+9Q District 3, Ho Chi Minh City, Vietnam"
    """
    # Dictionary of known Plus Codes for Ho Chi Minh City
    # Format: {plus_code_prefix: (latitude, longitude)}
    plus_code_map = {
        # District 1
        "QMPX": (10.7758, 106.7029),  # District 1 central area
        
        # District 3
        "QMMW": (10.7757, 106.6795),  # District 3 area
        
        # Binh Thanh
        "QPR7": (10.8106, 106.7176),  # Binh Thanh district
        
        # Default for Ho Chi Minh City if no specific code matches
        "HCM_DEFAULT": (10.7756, 106.6842)
    }
    
    # Extract the first 4 characters from the Plus Code (area code)
    if plus_code and isinstance(plus_code, str):
        # Extract the area code (first 4 characters)
        parts = plus_code.split('+')
        if len(parts) > 0:
            area_code = parts[0].strip()
            
            # Check if we have this area code in our dictionary
            if area_code in plus_code_map:
                return plus_code_map[area_code]
            # For codes starting with Q (Ho Chi Minh City)
            elif area_code.startswith('Q'):
                return plus_code_map["HCM_DEFAULT"]
    
    return None, None

# Function to geocode addresses - cached to reduce API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def geocode_address(address):
    """Convert address to coordinates using Google Plus Codes or geocoder"""
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
        
        # Check if this is a raw latitude,longitude format (e.g., "10.79151055938174, 106.69176363190014")
        if ',' in address and '.' in address:
            try:
                # Split by comma and attempt to parse as lat,lon
                parts = [p.strip() for p in address.split(',')]
                if len(parts) == 2:
                    # Try to convert both parts to float
                    lat, lon = float(parts[0]), float(parts[1])
                    
                    # Validate reasonable lat/lon ranges
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        # Đã tìm thấy tọa độ hợp lệ
                        return lat, lon
            except (ValueError, TypeError):
                # If parsing fails, continue with other methods
                pass
                
        # Next, check if this is a Google Plus Code (format: XXXX+XX)
        if '+' in address:
            # Try to parse as a Plus Code
            lat, lon = parse_plus_code(address)
            if lat is not None and lon is not None:
                return lat, lon
        
        # Dictionary of known locations for common Vietnamese addresses
        # Format: {partial_address: (latitude, longitude)}
        known_locations = {
            # Ho Chi Minh City locations
            "district 3": (10.7756, 106.6842),           # Quận 3
            "district 1": (10.7758, 106.7029),           # Quận 1
            "binh thanh": (10.8106, 106.7176),           # Bình Thạnh
            "ho chi minh city": (10.7756, 106.6842),     # Ho Chi Minh City
            "vietnam": (16.0544, 108.2022),              # Default for Vietnam
        }
        
        # Check for known locations first (case insensitive)
        address_lower = address.lower()
        for key, coords in known_locations.items():
            if key in address_lower:
                return coords
        
        # Use specific parameters to improve accuracy
        try:
            location = geocoder.geocode(
                address,
                exactly_one=True,
                addressdetails=True,
                language="vi"  # Vietnamese language
            )
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            # Silent error handling
            pass
        
        # Fallback: try with English language setting
        try:
            location = geocoder.geocode(
                address,
                exactly_one=True,
                addressdetails=True,
                language="en"
            )
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            # Silent error handling
            pass
        
        # If all geocoding attempts fail, return Ho Chi Minh City coordinates
        # for Vietnamese addresses as a last resort
        if 'vietnam' in address_lower or 'ho chi minh' in address_lower or 'hcm' in address_lower:
            return 10.7756, 106.6842  # Default coordinates for HCMC
            
        return None, None
    except Exception:
        # Silent error handling
        return None, None

# Function to create map of order locations
def create_order_map(sales_df, time_filter="All Time", color_scale="Reds"):
    """Create map visualization of order locations"""
    
    try:
        # Apply time filter
        start_date, end_date = utils.get_date_range(time_filter)
        # Convert dates to datetime64 for consistent comparison
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        # Filter within the date range
        filtered_df = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]
        
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
                # Adjust size calculation to make points more proportional to their value
                # Using a more moderate scaling to prevent extremes
                map_df['Size'] = map_df['Total'] / map_df['Total'].max() * 15 + 5  # Scale from 5 to 20
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
                    color_continuous_scale=getattr(px.colors.sequential, color_scale),  # Sử dụng thang màu đã chọn
                    range_color=[map_df['Total'].min(), map_df['Total'].max()],  # Đảm bảo thang màu từ nhỏ nhất đến lớn nhất
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
                        len=0.75,  # Chiều dài của colorbar
                        thickness=20,  # Độ dày của colorbar
                        dtick=map_df['Total'].max() / 5  # Số lượng điểm chia trên thanh màu
                    )
                )
                
                return fig
            else:
                st.info("No orders with valid locations found in the selected time period.")
                return None
        else:
            st.info("No location data found in the sales records.")
            return None
            
    except Exception:
        # Silent error handling
        st.info("Unable to create map. Please check your location data.")
        return None

# Main app code
try:
    # Checkbox để hiển thị debug thông tin
    show_debug = st.sidebar.checkbox("Show Debug Information", value=False)
    
    if show_debug:
        st.sidebar.info("Debug mode enabled - showing additional information")
        
        # Override geocode_address để hiển thị debug info
        original_geocode_address = geocode_address
        
        def debug_geocode_address(address):
            """Wrapper around geocode_address to show debug info"""
            st.sidebar.markdown(f"### Geocoding: `{address}`")
            
            # Check if this looks like lat, lng format
            if ',' in address and '.' in address:
                try:
                    parts = [p.strip() for p in address.split(',')]
                    if len(parts) == 2:
                        # Try to convert to floats
                        try:
                            lat, lon = float(parts[0]), float(parts[1])
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                st.sidebar.success(f"✅ Valid coordinates: {lat}, {lon}")
                            else:
                                st.sidebar.warning(f"⚠️ Coordinates out of range: {lat}, {lon}")
                        except:
                            st.sidebar.error("❌ Not valid coordinates format")
                except:
                    pass
            
            # Call original function
            lat, lon = original_geocode_address(address)
            
            if lat is not None and lon is not None:
                st.sidebar.success(f"✅ Final coordinates: {lat}, {lon}")
            else:
                st.sidebar.error("❌ Could not get coordinates")
                
            return lat, lon
        
        # Override with debug version
        geocode_address = debug_geocode_address
    
    # Load sales data
    sales_df = pd.read_csv("data/sales.csv")
    
    if not sales_df.empty:
        # Convert Date column to datetime
        sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='mixed')
        
        # Add time filter options
        time_options = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
        time_filter = st.selectbox("Time Period", options=time_options, index=5)  # Set default to "All Time"
        
        # Chọn dải màu
        color_options = {
            "Reds": "Đỏ - Tương phản nhất với bản đồ",
            "OrRd": "Cam đỏ - Nổi bật",
            "YlOrRd": "Vàng-Cam-Đỏ - Rực rỡ",
            "Purples": "Tím - Khác biệt với bản đồ",
            "RdPu": "Đỏ-Tím - Đậm nét"
        }
        selected_color = st.sidebar.selectbox(
            "Chọn dải màu cho bản đồ", 
            options=list(color_options.keys()),
            format_func=lambda x: color_options[x],
            index=0
        )
        
        # Create and display map
        map_fig = create_order_map(sales_df, time_filter, selected_color)
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
            
        # Display order location data in table form
        st.subheader("Order Locations")
        
        # Apply time filter
        start_date, end_date = utils.get_date_range(time_filter)
        # Convert dates to datetime64 for consistent comparison
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        # Filter within the date range
        filtered_df = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]
        
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
except Exception:
    st.info("Please check that your data files exist and are properly formatted.")