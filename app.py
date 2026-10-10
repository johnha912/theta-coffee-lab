import streamlit as st
import pandas as pd
import utils
from data_init import initialize_data_files

st.set_page_config(
    page_title="Theta Coffee Lab",
    page_icon=":material/coffee:",
    layout="wide",
)

utils.initialize_session_state()
initialize_data_files()

MODULES = [
    ("pages/1_dashboard.py", "Dashboard", ":material/space_dashboard:", "Revenue, orders, margin, and stock alerts at a glance."),
    ("pages/2_order.py", "Order", ":material/receipt_long:", "Ring up sales; every saved order deducts its recipe from stock."),
    ("pages/3_inventory.py", "Inventory", ":material/inventory_2:", "Stock levels with unit-aware low-stock thresholds."),
    ("pages/4_product.py", "Product", ":material/local_cafe:", "Build recipes and see cost of goods and profit per drink."),
    ("pages/5_financial.py", "Financial", ":material/monitoring:", "Gross and net profit, promotions, and operating costs."),
    ("pages/6_map.py", "Map", ":material/map:", "Where orders come from, plotted from Google Plus Codes."),
]


def home():
    hero, snapshot = st.columns([3, 2], gap="large", vertical_alignment="center")

    with hero:
        st.badge("Café operations", icon=":material/coffee:", color="primary")
        st.title("Theta Coffee Lab")
        st.markdown("Sales, recipes, stock, and profit for one café, in one place.")
        with st.container(horizontal=True):
            if st.button("Open dashboard", type="primary", icon=":material/arrow_forward:"):
                st.switch_page("pages/1_dashboard.py")
            if st.button("New order", icon=":material/add:"):
                st.switch_page("pages/2_order.py")

    with snapshot, st.container(border=True):
        st.caption("All-time snapshot")
        try:
            kpi = utils.sales_summary(pd.read_csv("data/sales.csv"), pd.read_csv("data/products.csv"))
            row1, row2 = st.columns(2), st.columns(2)
            row1[0].metric("Revenue", utils.format_currency(kpi['revenue']))
            row1[1].metric("Gross margin", f"{kpi['margin']:.1f}%")
            row2[0].metric("Orders", f"{kpi['orders']:,}")
            row2[1].metric("Cups sold", f"{kpi['cups']:,}")
        except Exception:
            st.caption("No sales yet. Save an order to see the snapshot.")

    st.space("medium")
    st.subheader("Modules")
    for row in (MODULES[:3], MODULES[3:]):
        for col, (path, title, icon, blurb) in zip(st.columns(3), row):
            with col, st.container(border=True, height="stretch"):
                st.markdown(f"#### {icon} {title}")
                st.caption(blurb)
                st.page_link(path, label=f"Open {title.lower()}", icon=":material/arrow_forward:")

    st.space("medium")
    st.caption("© 2025 Theta Coffee Lab")


st.logo("assets/logo.svg", size="large")
nav = st.navigation(
    [st.Page(home, title="Home", icon=":material/home:", default=True)]
    + [st.Page(path, title=title, icon=icon) for path, title, icon, _ in MODULES]
    + [st.Page("pages/7_settings.py", title="Settings", icon=":material/settings:")],
    position="top",
)
nav.run()
