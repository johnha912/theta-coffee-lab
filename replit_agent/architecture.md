# Architecture - Theta Coffee Lab Management System

## 1. Overview

The Theta Coffee Lab Management System is a comprehensive cafe management application designed to streamline operations including sales tracking, inventory management, product recipes, and financial reporting. The system provides a user-friendly interface for cafe staff to manage day-to-day operations, track financial performance, and make data-driven decisions.

The application is built as a single-page web application with multiple functional pages, using Streamlit as the primary framework. It follows a simple architecture pattern where the UI, business logic, and data storage are integrated within a unified application flow, optimized for rapid development and ease of use.

## 2. System Architecture

### 2.1 High-level Architecture

The system follows a monolithic architecture pattern with the following layers:

1. **Presentation Layer**: Streamlit-based UI components and pages
2. **Business Logic Layer**: Python functions that handle data processing, calculations, and business rules
3. **Data Access Layer**: Functions that read and write to the CSV-based data storage
4. **Data Storage**: CSV files acting as a simple database

```
┌─────────────────────────────────────────────┐
│                                             │
│  ┌─────────────────┐    ┌───────────────┐   │
│  │   Streamlit UI  │    │  Utility      │   │
│  │   Components    │◄──►│  Functions    │   │
│  └─────────────────┘    └───────────────┘   │
│           ▲                    ▲            │
│           │                    │            │
│           ▼                    ▼            │
│  ┌─────────────────┐    ┌───────────────┐   │
│  │  Page-specific  │    │  Data Access  │   │
│  │  Business Logic │◄──►│  Functions    │   │
│  └─────────────────┘    └───────────────┘   │
│                              ▲              │
│                              │              │
│                              ▼              │
│                     ┌───────────────────┐   │
│                     │     CSV Files     │   │
│                     │  (Data Storage)   │   │
│                     └───────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### 2.2 Component Interactions

- **User Interface (Streamlit)** handles all user interactions and displays information
- **Business Logic** processes user inputs, performs calculations, and manages state
- **Data Access Layer** abstracts the interaction with the CSV files
- **CSV Files** store all application data persistently

## 3. Key Components

### 3.1 Frontend Components

The application uses Streamlit for all UI components, providing a reactive interface that updates based on user interactions. The interface is organized into several pages:

1. **Dashboard** (`pages/1_dashboard.py`): Displays KPIs and performance metrics
2. **Order Management** (`pages/2_order.py`): Handles creation and management of orders
3. **Inventory Management** (`pages/3_inventory.py`): Tracks and manages inventory items
4. **Product Management** (`pages/4_product.py`): Manages product recipes and pricing
5. **Financial Reporting** (`pages/5_financial.py`): Provides financial analysis and reports
6. **Customer Map** (`pages/6_map.py`): Visualizes customer locations
7. **Settings** (`pages/7_settings.py`): Application preferences and configurations

### 3.2 Business Logic Components

Business logic is distributed across the various page files, with common utilities extracted to the `utils.py` file. Key business logic includes:

- Order processing and pricing calculations
- Inventory management and tracking
- Recipe management and COGS (Cost of Goods Sold) calculations
- Financial metrics and reporting
- Geolocation data processing

### 3.3 Data Storage

Data is stored in CSV files located in the `data/` directory:

1. **inventory.csv**: Tracks inventory items with quantities and costs
2. **inventory_transactions.csv**: Records all inventory movements (additions, edits, deletions)
3. **operational_costs.csv**: Tracks operational expenses
4. **product_recipe.csv**: Stores product recipes with ingredient requirements
5. **products.csv**: Product catalog with pricing and profit information
6. **sales.csv**: Records all sales transactions

The `data_init.py` file ensures these files exist with the correct structure when the application starts.

### 3.4 Utilities

The `utils.py` file contains shared utility functions used across the application, including:

- Session state initialization and management
- Date filtering and calculations
- Common data processing functions

## 4. Data Flow

### 4.1 Order Processing Flow

1. User enters order details in the Order Management page
2. System calculates order total based on product prices
3. Order is saved to the sales.csv file
4. Inventory is automatically updated based on product recipes
5. Inventory transactions are recorded in inventory_transactions.csv

### 4.2 Inventory Management Flow

1. User adds new inventory items or updates existing ones
2. System records the changes in inventory.csv
3. Transactions are logged in inventory_transactions.csv
4. Dashboard shows updated inventory levels
5. Alerts are generated for low stock items

### 4.3 Financial Reporting Flow

1. System loads sales data from sales.csv
2. Cost data is calculated using recipes and inventory costs
3. Financial metrics are computed (revenue, COGS, profit)
4. Results are displayed in charts and tables in the Financial Report page

### 4.4 Product Recipe Management Flow

1. User defines or modifies product recipes
2. System calculates COGS based on current inventory costs
3. Product information is saved to products.csv
4. Recipe details are saved to product_recipe.csv

## 5. External Dependencies

The application relies on the following key external libraries:

1. **Streamlit**: For the web interface and reactive components
2. **Pandas**: For data manipulation and analysis
3. **Plotly**: For interactive data visualization
4. **GeoPy**: For geocoding and location-based features
5. **NumPy**: For numerical operations

These dependencies are managed through the `pyproject.toml` file and installed via Python's package management system.

## 6. Deployment Strategy

The application is configured for deployment on Replit with the following characteristics:

### 6.1 Deployment Configuration

- **Platform**: Replit
- **Runtime**: Python 3.11
- **Port Configuration**: 5000 (internal) mapped to 80 (external)
- **Deployment Target**: Autoscale

### 6.2 Startup Process

1. The application is started with `streamlit run app.py --server.port 5000`
2. Initial data files are created if they don't exist
3. The Streamlit server serves the application UI
4. Users access the application through a web browser

### 6.3 CI/CD Workflow

The `.replit` file defines the workflow for automatic deployment:

1. Dependencies are installed from `pyproject.toml`
2. The application is started with the streamlit run command
3. The server port is monitored for availability

## 7. Architectural Decisions

### 7.1 Use of Streamlit for Frontend and Backend Integration

**Decision**: Use Streamlit as the sole framework for both UI and application logic.

**Rationale**: 
- Simplifies development by combining frontend and backend in a single Python codebase
- Provides built-in reactive UI components without requiring separate frontend technologies
- Allows rapid development and iteration for a business management application

**Trade-offs**:
- Limited customization compared to dedicated frontend frameworks
- Performance limitations for high-traffic applications
- Not designed for complex multi-user concurrent access patterns

### 7.2 CSV-based Data Storage

**Decision**: Use CSV files for data storage instead of a database system.

**Rationale**:
- Simplifies deployment without requiring database setup
- Sufficient for the expected data volume of a small cafe
- Easy to backup, inspect, and modify manually if needed

**Trade-offs**:
- Limited data integrity and relationship enforcement
- No concurrent write protection
- Performance limitations for large datasets
- Limited query capabilities compared to relational databases

### 7.3 Monolithic Architecture

**Decision**: Implement the application as a monolith rather than using microservices.

**Rationale**:
- Simplifies development and deployment
- Appropriate for the application scope and expected user base
- Reduces complexity for a small-scale business application

**Trade-offs**:
- Limited scalability for specific high-demand components
- All components must scale together
- Single point of failure

### 7.4 Page-based Modularization

**Decision**: Organize functionality into discrete pages rather than a single interface.

**Rationale**:
- Improves code organization and maintainability
- Provides clear separation of concerns for different business functions
- Follows Streamlit's convention for multi-page applications

**Trade-offs**:
- Requires state management across pages
- Navigation between pages requires page reloading
- Limited ability to compose interfaces across functional areas