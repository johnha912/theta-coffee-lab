import pandas as pd
import os
from datetime import datetime, timedelta
import random

def initialize_data_files():
    """Initialize data files with sample data if they don't exist"""
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Initialize inventory.csv
    if not os.path.exists("data/inventory.csv"):
        inventory_data = [
            {'ID': 1, 'Name': 'Coffee Beans', 'Quantity': 5000, 'Unit': 'g', 'Avg_Cost': 0.5, 'Date': datetime.now().strftime('%Y-%m-%d')},
            {'ID': 2, 'Name': 'Fresh Milk', 'Quantity': 10000, 'Unit': 'ml', 'Avg_Cost': 0.03, 'Date': datetime.now().strftime('%Y-%m-%d')},
            {'ID': 3, 'Name': 'Sugar', 'Quantity': 2000, 'Unit': 'g', 'Avg_Cost': 0.02, 'Date': datetime.now().strftime('%Y-%m-%d')},
            {'ID': 4, 'Name': 'Chocolate Powder', 'Quantity': 1000, 'Unit': 'g', 'Avg_Cost': 0.1, 'Date': datetime.now().strftime('%Y-%m-%d')},
            {'ID': 5, 'Name': 'Vanilla Syrup', 'Quantity': 500, 'Unit': 'ml', 'Avg_Cost': 0.15, 'Date': datetime.now().strftime('%Y-%m-%d')},
            {'ID': 6, 'Name': 'Plastic Cup', 'Quantity': 200, 'Unit': 'pcs', 'Avg_Cost': 1000, 'Date': datetime.now().strftime('%Y-%m-%d')},
            {'ID': 7, 'Name': 'Paper Cup', 'Quantity': 150, 'Unit': 'pcs', 'Avg_Cost': 1500, 'Date': datetime.now().strftime('%Y-%m-%d')}
        ]
        pd.DataFrame(inventory_data).to_csv("data/inventory.csv", index=False)
    
    # Initialize products.csv
    if not os.path.exists("data/products.csv"):
        products_data = [
            {'Name': 'Espresso', 'Price': 25000, 'COGS': 5000, 'Profit': 20000},
            {'Name': 'Cappuccino', 'Price': 35000, 'COGS': 10000, 'Profit': 25000},
            {'Name': 'Latte', 'Price': 40000, 'COGS': 12000, 'Profit': 28000},
            {'Name': 'Mocha', 'Price': 45000, 'COGS': 15000, 'Profit': 30000},
            {'Name': 'Americano', 'Price': 30000, 'COGS': 6000, 'Profit': 24000}
        ]
        pd.DataFrame(products_data).to_csv("data/products.csv", index=False)
    
    # Initialize product_recipe.csv
    if not os.path.exists("data/product_recipe.csv"):
        recipe_data = [
            {'Product': 'Espresso', 'Ingredient': 'Coffee Beans', 'Quantity': 18, 'Unit': 'g'},
            {'Product': 'Espresso', 'Ingredient': 'Plastic Cup', 'Quantity': 1, 'Unit': 'pcs'},
            
            {'Product': 'Cappuccino', 'Ingredient': 'Coffee Beans', 'Quantity': 18, 'Unit': 'g'},
            {'Product': 'Cappuccino', 'Ingredient': 'Fresh Milk', 'Quantity': 120, 'Unit': 'ml'},
            {'Product': 'Cappuccino', 'Ingredient': 'Plastic Cup', 'Quantity': 1, 'Unit': 'pcs'},
            
            {'Product': 'Latte', 'Ingredient': 'Coffee Beans', 'Quantity': 18, 'Unit': 'g'},
            {'Product': 'Latte', 'Ingredient': 'Fresh Milk', 'Quantity': 180, 'Unit': 'ml'},
            {'Product': 'Latte', 'Ingredient': 'Plastic Cup', 'Quantity': 1, 'Unit': 'pcs'},
            
            {'Product': 'Mocha', 'Ingredient': 'Coffee Beans', 'Quantity': 18, 'Unit': 'g'},
            {'Product': 'Mocha', 'Ingredient': 'Fresh Milk', 'Quantity': 150, 'Unit': 'ml'},
            {'Product': 'Mocha', 'Ingredient': 'Chocolate Powder', 'Quantity': 10, 'Unit': 'g'},
            {'Product': 'Mocha', 'Ingredient': 'Plastic Cup', 'Quantity': 1, 'Unit': 'pcs'},
            
            {'Product': 'Americano', 'Ingredient': 'Coffee Beans', 'Quantity': 18, 'Unit': 'g'},
            {'Product': 'Americano', 'Ingredient': 'Plastic Cup', 'Quantity': 1, 'Unit': 'pcs'}
        ]
        pd.DataFrame(recipe_data).to_csv("data/product_recipe.csv", index=False)
    
    # Initialize sales.csv with sample data if it doesn't exist
    if not os.path.exists("data/sales.csv"):
        # Create sample sales data for the past 30 days
        sales_data = []
        products = ['Espresso', 'Cappuccino', 'Latte', 'Mocha', 'Americano']
        prices = {
            'Espresso': 25000,
            'Cappuccino': 35000,
            'Latte': 40000,
            'Mocha': 45000,
            'Americano': 30000
        }
        
        # Generate random sales for each day
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            # Random number of orders for this day (3-15)
            num_orders = random.randint(3, 15)
            
            for j in range(num_orders):
                order_id = f"ORD{i+1:02d}-{j+1:02d}"
                # Random number of items per order (1-3)
                num_items = random.randint(1, 3)
                
                for _ in range(num_items):
                    product = random.choice(products)
                    quantity = random.randint(1, 2)
                    unit_price = prices[product]
                    total = quantity * unit_price
                    
                    sales_data.append({
                        'Date': date,
                        'Order_ID': order_id,
                        'Product': product,
                        'Quantity': quantity,
                        'Unit_Price': unit_price,
                        'Total': total
                    })
        
        pd.DataFrame(sales_data).to_csv("data/sales.csv", index=False)
    
    # Initialize operational_costs.csv
    if not os.path.exists("data/operational_costs.csv"):
        cost_data = [
            {'Date': (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d'), 'Type': 'Rent', 'Amount': 5000000},
            {'Date': (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d'), 'Type': 'Salary', 'Amount': 8000000},
            {'Date': (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d'), 'Type': 'Utilities', 'Amount': 1200000},
            {'Date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'), 'Type': 'Marketing', 'Amount': 2000000},
            {'Date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), 'Type': 'Maintenance', 'Amount': 800000}
        ]
        pd.DataFrame(cost_data).to_csv("data/operational_costs.csv", index=False)
    
    # Initialize inventory_transactions.csv
    if not os.path.exists("data/inventory_transactions.csv"):
        # Empty file with columns
        pd.DataFrame(columns=['Date', 'Material', 'Quantity', 'Unit', 'Unit_Cost', 'Total_Cost', 'Type']).to_csv("data/inventory_transactions.csv", index=False)
