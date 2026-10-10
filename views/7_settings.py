import streamlit as st
import pandas as pd
import datetime
import utils
import store

# Initialize session_state
utils.initialize_session_state()


st.title("Settings")
st.caption("Configure application preferences")

# Save settings function
def save_settings():
    st.session_state.currency = currency
    st.session_state.usd_rate = usd_rate
    st.session_state.alert_threshold = alert_threshold
    st.session_state.default_time_filter = default_time_filter
    st.session_state.username = username
    st.success("Settings saved successfully!")

# Settings form
st.header("Application Settings")

col1, col2 = st.columns(2)

with col1:
    # Inventory alert threshold
    alert_threshold = st.number_input(
        "Inventory Alert Threshold",
        min_value=1.0,  # Ensure all numeric values are float
        value=float(st.session_state.alert_threshold),
        step=1.0,
        help="Set the minimum inventory level that will trigger alerts"
    )
    
    # Currency selection
    currency_options = ["VND", "USD"]
    currency = st.selectbox(
        "Currency",
        options=currency_options,
        index=currency_options.index(st.session_state.currency),
        help="Select the currency to display throughout the application"
    )
    usd_rate = st.number_input(
        "VND per 1 USD",
        min_value=1.0,
        value=float(st.session_state.usd_rate),
        step=100.0,
        format="%.0f",
        help="Amounts are stored in VND; the USD view divides by this rate. Set it to today's rate."
    )

with col2:
    # Default time filter
    time_filter_options = ["Today", "Last 7 Days", "Last 30 Days", "All Time"]
    default_time_filter = st.selectbox(
        "Default Time Filter",
        options=time_filter_options,
        index=time_filter_options.index(st.session_state.default_time_filter),
        help="Set the default time filter for reports and dashboard"
    )
    
    # Username
    username = st.text_input(
        "Username",
        value=st.session_state.username,
        help="Enter your name or username for the application"
    )

# Save settings button
st.button("Save Settings", on_click=save_settings, type="primary")
st.caption(":material/contrast: Light and dark mode follow your system. To switch, open the ⋮ menu → Settings.")

# Data management
st.header("Data Management")

# Export data
with st.expander("Export Data", icon=":material/download:"):
    st.write("Download every table as CSV files in one ZIP. The same file can be imported back.")
    st.download_button(
        "Download ZIP",
        data=store.export_zip(),
        file_name=f"theta-coffee-lab-{datetime.date.today():%Y-%m-%d}.zip",
        mime="application/zip",
        icon=":material/folder_zip:",
    )

# Import data
with st.expander("Import Data", icon=":material/upload:"):
    st.write("Upload an exported ZIP, or CSV files named after their table (for example `sales.csv`). "
             "Each uploaded table replaces the current one; all of them commit together or not at all.")
    uploads = st.file_uploader("Data files", type=["csv", "zip"], accept_multiple_files=True)
    if uploads:
        try:
            frames = {}
            for f in uploads:
                frames.update(store.read_upload(f.name, f.getvalue()))
            st.caption("Will replace: " + ", ".join(f"{t} ({len(df)} rows)" for t, df in frames.items()))
            if st.button("Import", type="primary", icon=":material/upload:"):
                store.import_frames(frames)
                st.success(f"Imported {len(frames)} table(s).")
        except Exception as e:
            st.error(f"Import failed, nothing was changed: {e}")

# Reset application
with st.expander("Reset Application", icon=":material/restart_alt:"):
    st.write("Replace all data with the bundled sample data in `data/*.csv` and restore default settings.")
    confirm = st.checkbox("I understand this deletes every order, cost, and stock change made in the app")
    if st.button("Reset Application", key="reset_button", disabled=not confirm):
        store.reset()
        st.session_state.clear()
        st.success("All data and settings were reset.")

# About section
st.header("About")

st.markdown("""
### Cafe Management System
Version 2.0

This application helps you manage your cafe operations including:
- Sales tracking and order management
- Inventory management
- Product recipe design
- Financial reporting and analysis

For support or feedback, please contact the developer.
""")

# System information
st.subheader("System Information")

st.caption(f"Database: {store.engine().dialect.name}")
st.dataframe(
    pd.DataFrame([{"Table": t, "Rows": len(store.load(t))} for t in store.SCHEMA]),
    hide_index=True,
)
