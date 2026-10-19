Author: **Daniel Levi**
## Overview
Nightly job imports the Greenleaf point-of-sale CSV export, cleans it and loads it into PostgreSQL. The dashboard reads from a small REST API.
## Components
- **Importer** – Python script, runs at 02:00 every night
- **Database** – PostgreSQL 16, tables: stores, products, sales, stock_levels
- **API** – FastAPI, endpoints /sales/daily, /products/top, /stock/alerts
## Open questions
- How long should raw CSV files be kept? (Daniel suggests 90 days)
- Does Greenleaf need real-time stock updates? Ask Sarah Kim.