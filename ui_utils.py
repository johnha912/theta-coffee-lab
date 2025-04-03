import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# Hàm để hiển thị header chung cho tất cả các trang
def display_header():
    """Hiển thị header chung cho tất cả các trang"""
    # Tải CSS từ file
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
    # Header
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists('assets/logo.svg'):
            st.image('assets/logo.svg', width=100)
    with col2:
        st.markdown("""
        <div class="dashboard-header">
            <h1 style="color: white; margin: 0; padding: 10px;">Theta Coffee Lab Management</h1>
        </div>
        """, unsafe_allow_html=True)

# Hiển thị thẻ thông tin dạng card
def display_card(title, content, icon=None):
    """Hiển thị nội dung trong một thẻ card"""
    icon_html = f'<i class="fa fa-{icon}"></i> ' if icon else ''
    st.markdown(f"""
    <div class="card">
        <h3>{icon_html}{title}</h3>
        {content}
    </div>
    """, unsafe_allow_html=True)

# Sử dụng để hiển thị DataFrame với style
def display_styled_table(df, hide_index=True, height=None):
    """Hiển thị bảng dữ liệu với style"""
    # Format numeric columns
    for col in df.select_dtypes(include=['float', 'int']).columns:
        if 'Price' in col or 'Cost' in col or 'Amount' in col or 'Total' in col or 'Revenue' in col or 'Profit' in col:
            df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
    
    # Hide index if needed
    if hide_index:
        hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
    
    # Set height if specified
    if height:
        st.dataframe(df, height=height, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

# Hiển thị bảng thông tin KPI 
def display_kpi_card(title, value, change=None, unit="", help=""):
    """Hiển thị thẻ KPI với kiểu card"""
    delta = None if change is None else f"{change} {unit}"
    st.metric(
        label=title,
        value=f"{value:,} {unit}" if isinstance(value, (int, float)) else f"{value} {unit}",
        delta=delta,
        help=help
    )

# Tạo bảng thông tin dashboard
def display_summary_metrics(metrics_dict):
    """Hiển thị bảng thông tin tóm tắt với nhiều chỉ số"""
    cols = st.columns(len(metrics_dict))
    for i, (title, data) in enumerate(metrics_dict.items()):
        with cols[i]:
            delta = data.get('change', None)
            unit = data.get('unit', '')
            display_kpi_card(
                title, 
                data['value'], 
                delta, 
                unit, 
                data.get('help', '')
            )

# Tạo tabs với icons
def create_tabs_with_icons(tabs_dict):
    """Tạo tabs với icons"""
    tab_objects = st.tabs(list(tabs_dict.keys()))
    return dict(zip(tabs_dict.values(), tab_objects))