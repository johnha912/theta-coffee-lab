import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils import initialize_session_state, format_currency, ensure_data_dir, calculate_product_cogs
from ui_utils import display_header, display_styled_table

# Initialize session state
initialize_session_state()

# Page config
st.set_page_config(
    page_title="Product Management - Theta Coffee Lab",
    page_icon="☕",
    layout="wide"
)

# Display common header
display_header()

# Main title
st.title("Product Management")

# Load data functions
def load_products_data():
    """Load products data"""
    ensure_data_dir()
    if not os.path.exists("data/products.csv"):
        pd.DataFrame(columns=['Product', 'Price', 'Category', 'COGS']).to_csv("data/products.csv", index=False)
        return pd.DataFrame(columns=['Product', 'Price', 'Category', 'COGS'])
    
    products_df = pd.read_csv("data/products.csv")
    return products_df

def load_recipe_data():
    """Load recipe data"""
    ensure_data_dir()
    if not os.path.exists("data/product_recipe.csv"):
        pd.DataFrame(columns=['Product', 'Ingredient', 'Amount', 'Unit']).to_csv("data/product_recipe.csv", index=False)
        return pd.DataFrame(columns=['Product', 'Ingredient', 'Amount', 'Unit'])
    
    recipe_df = pd.read_csv("data/product_recipe.csv")
    return recipe_df

def load_inventory_data():
    """Load inventory data"""
    if not os.path.exists("data/inventory.csv"):
        return pd.DataFrame()
    
    inventory_df = pd.read_csv("data/inventory.csv")
    return inventory_df

# Calculate COGS based on ingredients
def get_cogs(selected_ingredients):
    """Calculate Cost of Goods Sold based on selected ingredients"""
    inventory_df = load_inventory_data()
    if inventory_df.empty or not selected_ingredients:
        return 0
    
    total_cost = 0
    
    for ingredient, amount in selected_ingredients.items():
        # Find the ingredient in inventory
        ingredient_data = inventory_df[inventory_df['Item'] == ingredient]
        if not ingredient_data.empty:
            # Calculate cost per unit based on latest inventory entry
            latest_entry = ingredient_data.iloc[-1]
            unit_cost = latest_entry['Cost'] / latest_entry['Quantity']
            ingredient_cost = unit_cost * amount
            total_cost += ingredient_cost
    
    return total_cost

# Save product data
def save_product():
    """Save product to products.csv and recipe to product_recipe.csv"""
    if 'recipe_ingredients' not in st.session_state or not st.session_state.recipe_ingredients:
        st.error("Please add at least one ingredient to the recipe.")
        return False
    
    product_name = st.session_state.product_name
    price = st.session_state.product_price
    category = st.session_state.product_category
    
    # Calculate COGS based on recipe
    cogs = get_cogs(st.session_state.recipe_ingredients)
    
    # Add product to products.csv
    products_df = load_products_data()
    
    # Check if product already exists
    existing_product = products_df[products_df['Product'] == product_name]
    if not existing_product.empty:
        # Update existing product
        products_df.loc[products_df['Product'] == product_name, 'Price'] = price
        products_df.loc[products_df['Product'] == product_name, 'Category'] = category
        products_df.loc[products_df['Product'] == product_name, 'COGS'] = cogs
    else:
        # Add new product
        new_product = pd.DataFrame({
            'Product': [product_name],
            'Price': [price],
            'Category': [category],
            'COGS': [cogs]
        })
        products_df = pd.concat([products_df, new_product], ignore_index=True)
    
    # Save products
    products_df.to_csv("data/products.csv", index=False)
    
    # Save recipe to product_recipe.csv
    recipe_df = load_recipe_data()
    
    # Remove existing recipe for this product
    recipe_df = recipe_df[recipe_df['Product'] != product_name]
    
    # Add new recipe
    recipe_entries = []
    for ingredient, amount in st.session_state.recipe_ingredients.items():
        # Get unit from inventory
        inventory_df = load_inventory_data()
        ingredient_data = inventory_df[inventory_df['Item'] == ingredient]
        unit = ingredient_data.iloc[0]['Unit'] if not ingredient_data.empty else ""
        
        recipe_entries.append({
            'Product': product_name,
            'Ingredient': ingredient,
            'Amount': amount,
            'Unit': unit
        })
    
    recipe_df = pd.concat([recipe_df, pd.DataFrame(recipe_entries)], ignore_index=True)
    recipe_df.to_csv("data/product_recipe.csv", index=False)
    
    return True

# Add ingredient to recipe
def add_ingredient():
    """Add an ingredient to the recipe"""
    ingredient = st.session_state.recipe_ingredient
    amount = st.session_state.recipe_amount
    
    if ingredient and amount > 0:
        if 'recipe_ingredients' not in st.session_state:
            st.session_state.recipe_ingredients = {}
        
        st.session_state.recipe_ingredients[ingredient] = amount
        
        # Reset form
        st.session_state.recipe_amount = 0.0
        
        return True
    
    return False

# Remove ingredient from recipe
def remove_ingredient(ingredient_name):
    """Remove an ingredient from the recipe"""
    if 'recipe_ingredients' in st.session_state and ingredient_name in st.session_state.recipe_ingredients:
        del st.session_state.recipe_ingredients[ingredient_name]
        return True
    
    return False

# Load a product's data
def load_product(product_name):
    """Load a product's data into the form"""
    products_df = load_products_data()
    recipe_df = load_recipe_data()
    
    # Get product data
    product_data = products_df[products_df['Product'] == product_name]
    if not product_data.empty:
        # Set form values
        st.session_state.product_name = product_name
        st.session_state.product_price = product_data.iloc[0]['Price']
        st.session_state.product_category = product_data.iloc[0]['Category']
        
        # Load recipe
        product_recipe = recipe_df[recipe_df['Product'] == product_name]
        
        # Set recipe ingredients
        st.session_state.recipe_ingredients = {}
        for _, row in product_recipe.iterrows():
            st.session_state.recipe_ingredients[row['Ingredient']] = row['Amount']
        
        return True
    
    return False

# Delete a product
def delete_product(product_name):
    """Delete a product and its recipe"""
    products_df = load_products_data()
    recipe_df = load_recipe_data()
    
    # Remove product
    products_df = products_df[products_df['Product'] != product_name]
    products_df.to_csv("data/products.csv", index=False)
    
    # Remove recipe
    recipe_df = recipe_df[recipe_df['Product'] != product_name]
    recipe_df.to_csv("data/product_recipe.csv", index=False)
    
    return True

# Load data
products_df = load_products_data()
recipe_df = load_recipe_data()
inventory_df = load_inventory_data()

# Create layout with two columns
col1, col2 = st.columns([2, 3])

# Left column - Product form
with col1:
    st.subheader("Create/Edit Product")
    
    # Initialize recipe_ingredients if not exists
    if 'recipe_ingredients' not in st.session_state:
        st.session_state.recipe_ingredients = {}
    
    # Product selection for editing
    existing_products = products_df['Name'].tolist() if not products_df.empty else []
    
    product_action = st.radio("Action", ["Create New", "Edit Existing"], horizontal=True)
    
    if product_action == "Edit Existing" and existing_products:
        selected_product = st.selectbox("Select Product to Edit", 
                                       existing_products)
        
        if st.button("Load Product Data", use_container_width=True):
            if load_product(selected_product):
                st.success(f"Loaded product: {selected_product}")
            else:
                st.error("Failed to load product data.")
    
    # Product form
    with st.form("product_form", clear_on_submit=False):
        st.text_input("Product Name", key="product_name")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Price (VND)", min_value=0, step=1000, key="product_price")
        with col2:
            st.selectbox("Category", ["Coffee", "Tea", "Chocolate", "Food", "Other"], key="product_category")
        
        st.subheader("Recipe")
        
        # Ingredient selection
        if not inventory_df.empty:
            ingredient_options = inventory_df['Name'].unique().tolist()
            st.selectbox("Ingredient", ingredient_options, key="recipe_ingredient")
            st.number_input("Amount", min_value=0.0, step=0.1, key="recipe_amount")
            
            if st.form_submit_button("Add Ingredient", use_container_width=True):
                if add_ingredient():
                    st.success("Ingredient added to recipe.")
                    st.rerun()
                else:
                    st.error("Please select an ingredient and specify amount.")
        else:
            st.warning("No inventory items available. Please add inventory first.")
        
        # Display current recipe
        if st.session_state.recipe_ingredients:
            st.subheader("Current Recipe")
            for ingredient, amount in st.session_state.recipe_ingredients.items():
                ing_col, amt_col, btn_col = st.columns([2, 1, 1])
                with ing_col:
                    st.text(ingredient)
                with amt_col:
                    # Get unit
                    ing_data = inventory_df[inventory_df['Name'] == ingredient]
                    unit = ing_data.iloc[0]['Unit'] if not ing_data.empty else ""
                    st.text(f"{amount} {unit}")
                with btn_col:
                    if st.button("Remove", key=f"remove_{ingredient}", use_container_width=True):
                        if remove_ingredient(ingredient):
                            st.success(f"Removed {ingredient} from recipe.")
                            st.rerun()
            
            # Calculate and display COGS
            cogs = get_cogs(st.session_state.recipe_ingredients)
            st.info(f"Estimated COGS: {format_currency(cogs)}")
        
        # Save button
        if st.form_submit_button("Save Product", use_container_width=True):
            if st.session_state.product_name and st.session_state.product_price > 0:
                if save_product():
                    st.success(f"Product {st.session_state.product_name} saved successfully!")
                    # Clear form
                    st.session_state.product_name = ""
                    st.session_state.product_price = 0
                    st.session_state.recipe_ingredients = {}
                    st.rerun()
            else:
                st.error("Please enter product name and price.")

# Right column - Products list and analysis
with col2:
    st.subheader("Products List")
    
    if not products_df.empty:
        # Add profit margin to data
        analysis_df = products_df.copy()
        analysis_df['Profit'] = analysis_df['Price'] - analysis_df['COGS']
        analysis_df['Margin'] = (analysis_df['Profit'] / analysis_df['Price'] * 100).round(1)
        
        # Display table
        display_styled_table(analysis_df)
        
        # Delete product functionality
        st.subheader("Delete Product")
        product_to_delete = st.selectbox("Select Product to Delete", 
                                        products_df['Name'].tolist(),
                                        key="delete_product")
        
        if st.button("Delete Selected Product", use_container_width=True):
            confirm = st.checkbox("Confirm deletion? This cannot be undone.")
            if confirm:
                if delete_product(product_to_delete):
                    st.success(f"Product {product_to_delete} deleted successfully!")
                    st.rerun()
        
        # Product analysis
        st.subheader("Product Analysis")
        
        # Profit margin comparison
        fig_margin = px.bar(
            analysis_df.sort_values('Margin', ascending=False), 
            x='Name',
            y='Margin',
            color='Category',
            title='Profit Margin by Product (%)',
            template='ggplot2'
        )
        fig_margin.update_layout(
            xaxis_title='Product',
            yaxis_title='Profit Margin (%)',
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
        )
        st.plotly_chart(fig_margin, use_container_width=True)
        
        # Price vs COGS
        fig_price = px.scatter(
            analysis_df,
            x='COGS',
            y='Price',
            color='Category',
            size='Profit',
            hover_name='Name',
            title='Price vs COGS',
            template='ggplot2'
        )
        fig_price.update_layout(
            xaxis_title='COGS (VND)',
            yaxis_title='Price (VND)',
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
        )
        # Add 45-degree line (Price = COGS, profit = 0)
        max_val = max(analysis_df['Price'].max(), analysis_df['COGS'].max())
        fig_price.add_scatter(x=[0, max_val], y=[0, max_val], mode='lines', 
                            line=dict(color='red', dash='dash'), 
                            name='Break-Even Line', showlegend=True)
        
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No products available. Create products using the form.")