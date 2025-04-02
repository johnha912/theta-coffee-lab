import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import uuid
import utils

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

st.set_page_config(page_title="Product Management", page_icon="☕", layout="wide")

st.title("Product Management")
st.subheader("Design and manage product recipes")

def get_cogs(selected_ingredients):
    """Calculate Cost of Goods Sold based on selected ingredients"""
    total_cogs = 0
    
    for item in selected_ingredients:
        ingredient = item['ingredient']
        quantity = item['quantity']
        
        # Get cost from inventory
        if not inventory_df.empty:
            inventory_row = inventory_df[inventory_df['Name'] == ingredient]
            if not inventory_row.empty:
                unit_cost = inventory_row.iloc[0]['Avg_Cost']
                total_cogs += quantity * unit_cost
    
    return total_cogs

def save_product():
    """Save product to products.csv and recipe to product_recipe.csv"""
    if not product_name:
        st.error("Product name is required")
        return
    
    if not selected_ingredients:
        st.error("At least one ingredient is required")
        return
    
    try:
        # Load products data
        try:
            products_df = pd.read_csv("data/products.csv")
        except FileNotFoundError:
            products_df = pd.DataFrame(columns=['Name', 'Price', 'COGS', 'Profit'])
        
        # Check if product already exists
        product_exists = product_name in products_df['Name'].values
        
        # Calculate COGS
        cogs = get_cogs(selected_ingredients)
        profit = selling_price - cogs
        
        if product_exists:
            # Update existing product
            idx = products_df[products_df['Name'] == product_name].index[0]
            products_df.loc[idx, 'Price'] = selling_price
            products_df.loc[idx, 'COGS'] = cogs
            products_df.loc[idx, 'Profit'] = profit
        else:
            # Add new product
            new_product = {
                'Name': product_name,
                'Price': selling_price,
                'COGS': cogs,
                'Profit': profit
            }
            products_df = pd.concat([products_df, pd.DataFrame([new_product])], ignore_index=True)
        
        # Save products data
        products_df.to_csv("data/products.csv", index=False)
        
        # Save recipe data
        try:
            recipe_df = pd.read_csv("data/product_recipe.csv")
        except FileNotFoundError:
            recipe_df = pd.DataFrame(columns=['Product', 'Ingredient', 'Quantity', 'Unit'])
        
        # Remove old recipe if it exists
        if product_exists:
            recipe_df = recipe_df[recipe_df['Product'] != product_name]
        
        # Add new recipe
        new_recipes = []
        for item in selected_ingredients:
            ingredient = item['ingredient']
            quantity = item['quantity']
            
            # Get unit from inventory
            unit = ""
            if not inventory_df.empty:
                inventory_row = inventory_df[inventory_df['Name'] == ingredient]
                if not inventory_row.empty:
                    unit = inventory_row.iloc[0]['Unit']
            
            new_recipe = {
                'Product': product_name,
                'Ingredient': ingredient,
                'Quantity': quantity,
                'Unit': unit
            }
            new_recipes.append(new_recipe)
        
        # Add new recipes
        recipe_df = pd.concat([recipe_df, pd.DataFrame(new_recipes)], ignore_index=True)
        
        # Save recipe data
        recipe_df.to_csv("data/product_recipe.csv", index=False)
        
        st.success(f"Product {product_name} saved successfully!")
        
        # Clear selections for new product
        st.session_state.selected_ingredients = []
        st.session_state.product_name = ""
        st.session_state.selling_price = 25000.0
        
        # Force rerun to show updated data
        st.rerun()
        
    except Exception as e:
        st.error(f"Error saving product: {str(e)}")

def add_ingredient():
    """Add an ingredient to the recipe"""
    if not new_ingredient or new_quantity <= 0:
        st.error("Please select an ingredient and enter a valid quantity")
        return
    
    # Check if ingredient already in list
    for item in st.session_state.selected_ingredients:
        if item['ingredient'] == new_ingredient:
            item['quantity'] = new_quantity
            st.success(f"Updated {new_ingredient} quantity to {new_quantity}")
            return
    
    # Add new ingredient
    st.session_state.selected_ingredients.append({
        'ingredient': new_ingredient,
        'quantity': new_quantity
    })
    st.success(f"Added {new_ingredient} to recipe")

def remove_ingredient(ingredient_name):
    """Remove an ingredient from the recipe"""
    st.session_state.selected_ingredients = [
        item for item in st.session_state.selected_ingredients 
        if item['ingredient'] != ingredient_name
    ]
    st.success(f"Removed {ingredient_name} from recipe")

def load_product(product_name):
    """Load a product's data into the form"""
    # Set product name and price
    product_row = products_df[products_df['Name'] == product_name].iloc[0]
    st.session_state.product_name = product_name
    st.session_state.selling_price = product_row['Price']
    
    # Load recipe ingredients
    recipe_items = recipe_df[recipe_df['Product'] == product_name]
    
    # Clear current ingredients
    st.session_state.selected_ingredients = []
    
    # Add recipe ingredients
    for _, row in recipe_items.iterrows():
        st.session_state.selected_ingredients.append({
            'ingredient': row['Ingredient'],
            'quantity': row['Quantity']
        })
    
    st.success(f"Loaded product: {product_name}")

def delete_product(product_name):
    """Delete a product and its recipe"""
    try:
        # Remove from products.csv
        global products_df
        products_df = products_df[products_df['Name'] != product_name]
        products_df.to_csv("data/products.csv", index=False)
        
        # Remove from product_recipe.csv
        global recipe_df
        recipe_df = recipe_df[recipe_df['Product'] != product_name]
        recipe_df.to_csv("data/product_recipe.csv", index=False)
        
        st.success(f"Deleted product: {product_name}")
        
        # Clear form if the deleted product was selected
        if st.session_state.product_name == product_name:
            st.session_state.product_name = ""
            st.session_state.selling_price = 25000.0
            st.session_state.selected_ingredients = []
        
        # Force rerun to show updated data
        st.rerun()
        
    except Exception as e:
        st.error(f"Error deleting product: {str(e)}")

# Initialize session state for recipe
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = []

# Initialize session state for product form
if 'product_name' not in st.session_state:
    st.session_state.product_name = ""
if 'selling_price' not in st.session_state:
    st.session_state.selling_price = 25000.0

try:
    # Load data
    try:
        inventory_df = pd.read_csv("data/inventory.csv")
    except FileNotFoundError:
        inventory_df = pd.DataFrame(columns=['ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Date'])
    
    try:
        products_df = pd.read_csv("data/products.csv")
    except FileNotFoundError:
        products_df = pd.DataFrame(columns=['Name', 'Price', 'COGS', 'Profit'])
        products_df.to_csv("data/products.csv", index=False)
    
    try:
        recipe_df = pd.read_csv("data/product_recipe.csv")
    except FileNotFoundError:
        recipe_df = pd.DataFrame(columns=['Product', 'Ingredient', 'Quantity', 'Unit'])
        recipe_df.to_csv("data/product_recipe.csv", index=False)
    
    # Product list and management
    st.header("Product List")
    
    if not products_df.empty:
        # Format for display
        display_df = products_df.copy()
        display_df['Price'] = display_df['Price'].apply(utils.format_currency)
        display_df['COGS'] = display_df['COGS'].apply(utils.format_currency)
        display_df['Profit'] = display_df['Profit'].apply(utils.format_currency)
        display_df['Profit Margin'] = (products_df['Profit'] / products_df['Price'] * 100).round(2).astype(str) + '%'
        
        st.dataframe(display_df)
        
        # Product selection for editing
        st.subheader("Edit Existing Product")
        
        # Select product to edit
        selected_product = st.selectbox(
            "Select a product to edit",
            options=[""] + products_df['Name'].tolist()
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if selected_product:
                st.button("Load Product", on_click=load_product, args=(selected_product,))
        
        with col2:
            if selected_product:
                st.button("Delete Product", on_click=delete_product, args=(selected_product,))
    else:
        st.info("No products created yet")
    
    # Create or edit product form
    st.header("Create or Edit Product")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Product name input
        product_name = st.text_input("Product Name", value=st.session_state.product_name)
        
        # Selling price input
        selling_price = st.number_input("Selling Price (VND)", 
                                       min_value=0.0, 
                                       value=st.session_state.selling_price, 
                                       step=1000.0)
    
    with col2:
        # Calculate COGS and profit
        selected_ingredients = st.session_state.selected_ingredients
        cogs = get_cogs(selected_ingredients)
        profit = selling_price - cogs
        profit_margin = (profit / selling_price * 100) if selling_price > 0 else 0
        
        st.metric("COGS", utils.format_currency(cogs))
        st.metric("Profit per Unit", utils.format_currency(profit))
        st.metric("Profit Margin", f"{profit_margin:.2f}%")
    
    # Recipe ingredients form
    st.subheader("Recipe Ingredients")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Available ingredients from inventory
        available_ingredients = inventory_df['Name'].unique().tolist() if not inventory_df.empty else []
        
        new_ingredient = st.selectbox("Select Ingredient", options=available_ingredients if available_ingredients else ["No ingredients available"])
        
        # Ingredient quantity
        new_quantity = st.number_input("Quantity", min_value=0.0, value=10.0, step=1.0)
        
        # Add to recipe button
        if available_ingredients:  # Only enable if ingredients are available
            st.button("Add to Recipe", on_click=add_ingredient)
    
    with col2:
        # Show current recipe ingredients
        if selected_ingredients:
            st.write("Current Recipe:")
            
            for item in selected_ingredients:
                ingredient = item['ingredient']
                quantity = item['quantity']
                
                # Get unit from inventory
                unit = ""
                if not inventory_df.empty:
                    inventory_row = inventory_df[inventory_df['Name'] == ingredient]
                    if not inventory_row.empty:
                        unit = inventory_row.iloc[0]['Unit']
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{ingredient}: {quantity} {unit}")
                with col2:
                    st.button("Remove", key=f"remove_{ingredient}", on_click=remove_ingredient, args=(ingredient,))
        else:
            st.info("No ingredients added to recipe yet")
    
    # Save product button
    st.button("Save Product", on_click=save_product)
    
    # Visualizations
    if not products_df.empty:
        st.header("Product Analysis")
        
        # Profit margin comparison
        fig1 = px.bar(
            products_df,
            x='Name',
            y='Profit',
            color='Name',
            title='Profit per Product',
            labels={'Name': 'Product', 'Profit': 'Profit (VND)'}
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Price breakdown
        fig2 = px.bar(
            products_df,
            x='Name',
            y=['COGS', 'Profit'],
            title='Price Breakdown (COGS vs Profit)',
            labels={'Name': 'Product', 'value': 'Amount (VND)', 'variable': 'Component'}
        )
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Error in product management: {str(e)}")
    st.write("Please check that your data files exist and are properly formatted.")
