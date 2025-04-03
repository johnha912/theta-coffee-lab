import pandas as pd
import os
from datetime import datetime, timedelta
import random

def initialize_data_files():
    """Initialize empty data files if they don't exist"""
    os.makedirs('data', exist_ok=True)
    
    # Create sales.csv if it doesn't exist
    if not os.path.exists('data/sales.csv'):
        sales_df = pd.DataFrame(columns=[
            'OrderID', 'Date', 'Time', 'Product', 'Quantity', 'Price', 'Total'
        ])
        sales_df.to_csv('data/sales.csv', index=False)
    
    # Create inventory.csv if it doesn't exist
    if not os.path.exists('data/inventory.csv'):
        inventory_df = pd.DataFrame(columns=[
            'ID', 'Name', 'Quantity', 'Unit', 'Avg_Cost', 'Date'
        ])
        inventory_df.to_csv('data/inventory.csv', index=False)
    
    # Create products.csv if it doesn't exist
    if not os.path.exists('data/products.csv'):
        products_df = pd.DataFrame(columns=[
            'Name', 'Price', 'COGS', 'Profit'
        ])
        products_df.to_csv('data/products.csv', index=False)
    
    # Create product_recipe.csv if it doesn't exist
    if not os.path.exists('data/product_recipe.csv'):
        recipe_df = pd.DataFrame(columns=[
            'Product', 'Ingredient', 'Amount', 'Unit'
        ])
        recipe_df.to_csv('data/product_recipe.csv', index=False)
    
    # Create expenses.csv if it doesn't exist
    if not os.path.exists('data/expenses.csv'):
        expenses_df = pd.DataFrame(columns=[
            'Date', 'Category', 'Amount', 'Note'
        ])
        expenses_df.to_csv('data/expenses.csv', index=False)

def generate_sample_data():
    """Generate sample data for demonstration purposes"""
    # Only generate if files are empty or don't exist
    os.makedirs('data', exist_ok=True)
    
    # Sample inventory items
    inventory_items = [
        {'Item': 'Coffee beans', 'Unit': 'g', 'Quantity': 5000, 'Cost': 500000, 'Date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')},
        {'Item': 'Milk', 'Unit': 'ml', 'Quantity': 10000, 'Cost': 300000, 'Date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')},
        {'Item': 'Sugar', 'Unit': 'g', 'Quantity': 3000, 'Cost': 100000, 'Date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')},
        {'Item': 'Chocolate powder', 'Unit': 'g', 'Quantity': 1000, 'Cost': 150000, 'Date': (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d')},
        {'Item': 'Tea leaves', 'Unit': 'g', 'Quantity': 2000, 'Cost': 400000, 'Date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')},
        {'Item': 'Cups', 'Unit': 'pcs', 'Quantity': 500, 'Cost': 500000, 'Date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')},
        {'Item': 'Straws', 'Unit': 'pcs', 'Quantity': 1000, 'Cost': 50000, 'Date': (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d')},
    ]
    
    # Sample products with recipes
    products = [
        {'Product': 'Espresso', 'Price': 30000, 'Category': 'Coffee', 'COGS': 15000},
        {'Product': 'Cappuccino', 'Price': 45000, 'Category': 'Coffee', 'COGS': 25000},
        {'Product': 'Latte', 'Price': 50000, 'Category': 'Coffee', 'COGS': 28000},
        {'Product': 'Americano', 'Price': 40000, 'Category': 'Coffee', 'COGS': 20000},
        {'Product': 'Green Tea', 'Price': 35000, 'Category': 'Tea', 'COGS': 18000},
        {'Product': 'Black Tea', 'Price': 35000, 'Category': 'Tea', 'COGS': 17000},
        {'Product': 'Hot Chocolate', 'Price': 45000, 'Category': 'Chocolate', 'COGS': 22000},
    ]
    
    # Sample recipes
    recipes = [
        {'Product': 'Espresso', 'Ingredient': 'Coffee beans', 'Amount': 20, 'Unit': 'g'},
        {'Product': 'Espresso', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
        
        {'Product': 'Cappuccino', 'Ingredient': 'Coffee beans', 'Amount': 20, 'Unit': 'g'},
        {'Product': 'Cappuccino', 'Ingredient': 'Milk', 'Amount': 100, 'Unit': 'ml'},
        {'Product': 'Cappuccino', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
        
        {'Product': 'Latte', 'Ingredient': 'Coffee beans', 'Amount': 20, 'Unit': 'g'},
        {'Product': 'Latte', 'Ingredient': 'Milk', 'Amount': 150, 'Unit': 'ml'},
        {'Product': 'Latte', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
        
        {'Product': 'Americano', 'Ingredient': 'Coffee beans', 'Amount': 25, 'Unit': 'g'},
        {'Product': 'Americano', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
        
        {'Product': 'Green Tea', 'Ingredient': 'Tea leaves', 'Amount': 10, 'Unit': 'g'},
        {'Product': 'Green Tea', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
        
        {'Product': 'Black Tea', 'Ingredient': 'Tea leaves', 'Amount': 10, 'Unit': 'g'},
        {'Product': 'Black Tea', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
        
        {'Product': 'Hot Chocolate', 'Ingredient': 'Chocolate powder', 'Amount': 25, 'Unit': 'g'},
        {'Product': 'Hot Chocolate', 'Ingredient': 'Milk', 'Amount': 200, 'Unit': 'ml'},
        {'Product': 'Hot Chocolate', 'Ingredient': 'Cups', 'Amount': 1, 'Unit': 'pcs'},
    ]
    
    # Sample expenses
    expenses = [
        {'Date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'), 'Category': 'Rent', 'Amount': 5000000, 'Note': 'Monthly rent'},
        {'Date': (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d'), 'Category': 'Utilities', 'Amount': 1500000, 'Note': 'Electricity and water'},
        {'Date': (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d'), 'Category': 'Salary', 'Amount': 10000000, 'Note': 'Staff salary'},
        {'Date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'), 'Category': 'Marketing', 'Amount': 2000000, 'Note': 'Online advertising'},
        {'Date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'), 'Category': 'Maintenance', 'Amount': 1000000, 'Note': 'Machine maintenance'},
    ]
    
    # Generate sample sales for the last 30 days
    sales = []
    order_id = 1
    
    for day in range(30, 0, -1):
        date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        
        # Generate 5-15 orders per day
        num_orders = random.randint(5, 15)
        
        for _ in range(num_orders):
            # Random time between 7 AM and 9 PM
            hour = random.randint(7, 21)
            minute = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}"
            
            # Random product
            product = random.choice(products)
            product_name = product['Product']
            product_price = product['Price']
            
            # Random quantity 1-3
            quantity = random.randint(1, 3)
            
            # Calculate total
            total = product_price * quantity
            
            # Add to sales list
            sales.append({
                'OrderID': order_id,
                'Date': date,
                'Time': time_str,
                'Product': product_name,
                'Quantity': quantity,
                'Price': product_price,
                'Total': total
            })
            
            order_id += 1
    
    # Save data if files don't exist or are empty
    if not os.path.exists('data/inventory.csv') or os.path.getsize('data/inventory.csv') <= len("Item,Unit,Quantity,Cost,Date\n"):
        pd.DataFrame(inventory_items).to_csv('data/inventory.csv', index=False)
    
    if not os.path.exists('data/products.csv') or os.path.getsize('data/products.csv') <= len("Product,Price,Category,COGS\n"):
        pd.DataFrame(products).to_csv('data/products.csv', index=False)
    
    if not os.path.exists('data/product_recipe.csv') or os.path.getsize('data/product_recipe.csv') <= len("Product,Ingredient,Amount,Unit\n"):
        pd.DataFrame(recipes).to_csv('data/product_recipe.csv', index=False)
    
    if not os.path.exists('data/expenses.csv') or os.path.getsize('data/expenses.csv') <= len("Date,Category,Amount,Note\n"):
        pd.DataFrame(expenses).to_csv('data/expenses.csv', index=False)
    
    if not os.path.exists('data/sales.csv') or os.path.getsize('data/sales.csv') <= len("OrderID,Date,Time,Product,Quantity,Price,Total\n"):
        pd.DataFrame(sales).to_csv('data/sales.csv', index=False)