import pandas as pd
import os
from datetime import datetime

def initialize_data_files():
    """Initialize empty data files if they don't exist"""
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Initialize inventory.csv with empty dataframe
    if not os.path.exists("data/inventory.csv"):
        inventory_df = pd.DataFrame(columns=['ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Date'])
        inventory_df.to_csv("data/inventory.csv", index=False)
    
    # Initialize products.csv with empty dataframe
    if not os.path.exists("data/products.csv"):
        products_df = pd.DataFrame(columns=['Name', 'Price', 'COGS', 'Profit'])
        products_df.to_csv("data/products.csv", index=False)
    
    # Initialize product_recipe.csv with empty dataframe
    if not os.path.exists("data/product_recipe.csv"):
        recipe_df = pd.DataFrame(columns=['Product', 'Ingredient', 'Quantity', 'Unit'])
        recipe_df.to_csv("data/product_recipe.csv", index=False)
    
    # Initialize sales.csv with empty dataframe
    if not os.path.exists("data/sales.csv"):
        sales_df = pd.DataFrame(columns=['Date', 'Order_ID', 'Product', 'Quantity', 'Unit_Price', 'Total'])
        sales_df.to_csv("data/sales.csv", index=False)
    
    # Initialize operational_costs.csv with empty dataframe
    if not os.path.exists("data/operational_costs.csv"):
        costs_df = pd.DataFrame(columns=['Date', 'Type', 'Amount'])
        costs_df.to_csv("data/operational_costs.csv", index=False)
    
    # Initialize inventory_transactions.csv with empty dataframe
    if not os.path.exists("data/inventory_transactions.csv"):
        transactions_df = pd.DataFrame(columns=['Date', 'Material', 'Quantity', 'Unit', 'Unit_Cost', 'Total_Cost', 'Type'])
        transactions_df.to_csv("data/inventory_transactions.csv", index=False)
