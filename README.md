<img src="assets/logo.svg" width="96" alt="Theta Coffee Lab logo: a pour-over dripper over a carafe">

# Theta Coffee Lab

A comprehensive cafe management system with real-time analytics, inventory tracking, and financial reporting.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.65-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

Theta Coffee Lab Management System is a full-stack business intelligence application designed to streamline cafe operations. Built with Python and Streamlit, it provides an intuitive interface for managing sales, inventory, recipes, and financial performance.

## Features

| Feature | Description |
|---------|-------------|
| 📊 **Dashboard** | Real-time KPIs including revenue, orders, gross profit margin, and performance trends |
| 🛒 **Order Management** | Process sales transactions with automatic inventory deduction |
| 📦 **Inventory Control** | Track stock levels with intelligent low-stock alerts based on unit types |
| 🍵 **Recipe Builder** | Create and manage product recipes with automatic COGS calculation |
| 💰 **Financial Analytics** | Comprehensive reports with revenue breakdown, cost analysis, and profitability metrics |
| 🗺️ **Geospatial Analysis** | Visualize customer locations using Google Plus Codes integration |
| 🗄️ **Transactional Storage** | SQLite by default, PostgreSQL via `DATABASE_URL`; a sale and its stock deduction commit together |
| 💾 **Export, Import, Reset** | Download every table as a ZIP, restore it, or reset to the sample data |
| 💱 **Currency** | View amounts in VND or USD at a rate you set |
| ✉️ **Daily Email Report** | Yesterday's sales and low-stock items, sent by `report.py` on a schedule |

## Tech Stack

- **Framework**: Streamlit 1.65 (top navigation, native light and dark themes)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly 7 (interactive charts, MapLibre maps)
- **Geolocation**: GeoPy
- **Storage**: SQLAlchemy 2 over SQLite (default) or PostgreSQL; the CSV files in `data/` are seed data
- **Email**: Python's `smtplib`

## What's New in v2

### Interface

The interface was rebuilt on Streamlit's native theming instead of hand-written CSS:

- **Top navigation** with Material icons replaces the default sidebar page list, plus the pour-over logo.
- **Two designed themes**, light and dark, in `.streamlit/config.toml`: Geist typography, a single cobalt accent on neutral surfaces, rounded cards, and pill buttons. The app follows the viewer's system setting; the ⋮ menu switches it.
- **One chart style everywhere**: `utils.chart()` puts every Plotly figure in a bordered card with thin marks and rounded bar ends. Six copy-pasted ggplot templates are gone, and chart colors come from a colorblind-checked categorical palette.
- **Better chart choices**: pies with 10+ slices became sorted bar charts, single-series bars use one color instead of a rainbow, and the financial chart has a unified hover.
- **Financial**: a waterfall walks from gross revenue through promotions, COGS, and operating costs to net profit, and a zoomable treemap shows where every dong of spend goes (with a table view).
- **Dashboard**: seven KPI tiles with icons and daily sparklines in two even rows, a time-period segmented control, a full-width revenue trend, and two same-height rankings side by side.
- **Home**: a hero with an all-time snapshot and a module grid.

### Backend

- **A real database with transactions.** `store.py` replaces 65 direct CSV reads and writes in the pages. Saving or deleting an order now writes the sale and the stock change in one transaction, and so do inventory edits (stock plus history) and products (product plus recipe). Before, a failure between the two writes could record a sale without deducting stock, and deleting an order went ahead even when restoring stock failed.
- **SQLite or PostgreSQL.** With no setup the app uses `data/theta.db`, created and seeded from `data/*.csv` on first run. Set `DATABASE_URL` to a PostgreSQL URL and the same code runs there; tests and a UI round trip were checked on PostgreSQL 17.
- **Settings that work.** Export downloads every table as CSV in a ZIP, Import restores a ZIP or CSV files (all tables commit together, or nothing changes if a column is missing), and Reset returns to the sample data. The VND/USD setting now converts every formatted amount at a rate you set.
- **Daily email report.** `report.py` emails a day's revenue, profit, orders, top products, and low-stock items.
- **Low-stock fix.** Thresholds for items stocked in liters or kilograms were multiplied by 1,000 instead of divided, so those items always showed as low.

### Fixes

- **Direct links**: right after the server started, the first visitor to open a page URL such as `/settings` got the old sidebar layout, because Streamlit auto-loads a folder named `pages/`. The page scripts now live in `views/`, so `st.navigation` alone drives routing.
- **Customer Map**: Plotly 7 removed `scatter_mapbox`, and the old Carto tiles showed "API KEY REQUIRED". The map now uses MapLibre `scatter_map` and centers on the orders.
- **Settings**: "Toggle Theme Now" rewrote `config.toml` at runtime. It is removed; theme switching is built in.
- **Dependencies**: `requirements.txt` now exists, and `pyproject.toml` and `uv.lock` pin Streamlit 1.65 and Plotly 7.

## Architecture

```mermaid
graph TB
    A[Presentation Layer<br/>Streamlit pages]
    R[report.py<br/>Scheduled email]
    B[Business Logic Layer<br/>utils.py: KPIs, COGS, low stock]
    C[Data Access Layer<br/>store.py: load, save, transaction]
    D[(SQLite or PostgreSQL)]
    S[data/*.csv<br/>Seed data]

    A --> B
    R --> B
    B --> C
    A --> C
    C --> D
    S -. first run .-> D

    style A fill:#2a78d6,stroke:#1c5cab,color:#fff
    style R fill:#2a78d6,stroke:#1c5cab,color:#fff
    style B fill:#256abf,stroke:#184f95,color:#fff
    style C fill:#1c5cab,stroke:#104281,color:#fff
    style D fill:#104281,stroke:#0d366b,color:#fff
```

## Project Structure

```
theta-coffee-lab/
├── app.py                 # Navigation, theme setup, and the Home page
├── store.py               # Database access: load, save, transactions, export/import
├── utils.py               # Shared helpers: currency, dates, KPIs, low stock, charts
├── report.py              # Daily email report (run on a schedule)
├── requirements.txt
├── .streamlit/config.toml # Light and dark themes
├── assets/                # Logo and favicon
├── tests/
│   ├── test_pages.py      # Every page renders without errors
│   └── test_backend.py    # Transactions, import/export, currency, report
├── views/                 # One script per page (not pages/, so st.navigation alone drives routing)
│   ├── 1_dashboard.py     # Analytics dashboard
│   ├── 2_order.py         # Order management
│   ├── 3_inventory.py     # Inventory tracking
│   ├── 4_product.py       # Recipe management
│   ├── 5_financial.py     # Financial reports
│   ├── 6_map.py           # Customer location map
│   └── 7_settings.py      # Application settings
└── data/                  # Seed data; theta.db (SQLite) is created here and git-ignored
    ├── sales.csv
    ├── inventory.csv
    ├── products.csv
    ├── product_recipe.csv
    ├── inventory_transactions.csv
    └── operational_costs.csv
```

## Installation

```bash
# Clone the repository
git clone https://github.com/johnha912/theta-coffee-lab.git
cd theta-coffee-lab

# Install dependencies
pip install -r requirements.txt

# Run the application (opens on port 5000, set in .streamlit/config.toml)
streamlit run app.py

# Optional: run the tests (they use a throwaway database)
python tests/test_pages.py
python tests/test_backend.py
```

### Use PostgreSQL instead of SQLite

```bash
pip install "psycopg[binary]"
export DATABASE_URL=postgresql://user:password@host:5432/theta   # Windows: set DATABASE_URL=...
streamlit run app.py   # creates and seeds the tables on first run
```

### Daily email report

```bash
python report.py --dry-run --date 2025-05-07   # print one day's report
python report.py                               # email yesterday's report
```

Sending needs `SMTP_HOST`, `SMTP_PORT` (default 587), `SMTP_USER`, `SMTP_PASSWORD`, and `REPORT_TO`. Schedule it with cron (`0 7 * * * cd /path/to/theta-coffee-lab && python report.py`) or Windows Task Scheduler. A scheduler on another machine, such as GitHub Actions, needs the PostgreSQL setup so it can reach the data.

## Key Technical Highlights

- **Reactive UI**: Leverages Streamlit's reactive paradigm for real-time updates
- **Intelligent Alerting**: Dynamic inventory thresholds based on unit types (ml, g, pcs)
- **Automatic COGS Calculation**: Recipe-based cost computation for accurate profit margins
- **Data Visualization**: Interactive Plotly charts styled by the app theme, in light and dark
- **Atomic Writes**: Multi-table changes share one database transaction
- **Session State Management**: User preferences persist across page navigation

## Screenshots

> **Note:** For customer privacy and financial security reasons, all figures shown in these screenshots have been modified and are for demonstration purposes only to help users understand how the application works.

### Before and after

The "before" shots run the previous release on its locked versions (Streamlit 1.44, Plotly 6). Both sides use the same data and the "All Time" period.

| | Before | After |
|---|---|---|
| **Home** | ![Home before](docs/screenshots/before-home.webp) | ![Home after](docs/screenshots/after-home.webp) |
| **Dashboard** | ![Dashboard before](docs/screenshots/before-dashboard.webp) | ![Dashboard after](docs/screenshots/after-dashboard.webp) |
| **Financial** | ![Financial before](docs/screenshots/before-financial.webp) | ![Financial after](docs/screenshots/after-financial.webp) |
| **Map** | ![Map before](docs/screenshots/before-map.webp) | ![Map after](docs/screenshots/after-map.webp) |

### Light theme

| Home | Dashboard | Financial |
|---|---|---|
| ![Home, light](docs/screenshots/after-light-home.webp) | ![Dashboard, light](docs/screenshots/after-light-dashboard.webp) | ![Financial, light](docs/screenshots/after-light-financial.webp) |

### Other pages

| Order | Inventory |
|---|---|
| ![Order](docs/screenshots/after-order.webp) | ![Inventory](docs/screenshots/after-inventory.webp) |
| **Product** | **Settings** |
| ![Product](docs/screenshots/after-product.webp) | ![Settings](docs/screenshots/after-settings.webp) |

## Future Enhancements

- [ ] Save Settings in the database; they currently reset when the browser tab reloads
- [ ] Apply the USD view to chart axes and input fields (they stay in VND today)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
