# Point of Sale (POS) System

A modern, modular, and user-friendly Point of Sale application built with Python and Tkinter. Designed for small businesses to manage sales, products, and reporting with a beautiful GUI and robust features.

## Features
- **Product Management:** Add, edit, delete, and import products with automatic product ID generation and description fields
- **Two-Level Category System:** Main and subcategories for all items, with persistent custom categories, color-coding, and icons
- **POS Interface:** Touch-friendly product grid, cart, and checkout
- **Sales Summary:** Tabbed dashboard with charts and stats (matplotlib)
- **Data Persistence:** All data stored in `datas/` (NoSQL-style: JSON, TXT, CSV, YAML supported)
- **Multi-Format Import/Export:** Load and save data in JSON, TXT, CSV, YAML; auto-detect file type; export/import for IMS
- **IMS Sync:** Import/export tangible items to/from Inventory Management System
- **Category Manager:** Hierarchical UI for managing categories, colors, and icons
- **Robust File Handling:** User-friendly error handling, auto-backup, and format conversion
- **Modern OOP Codebase:** SOLID principles, modular structure, easy to extend

## Folder Structure
```
PointOfSales/
├── datas/              # All product and sales data files (JSON, demo data, etc.)
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
├── src/                # Source code (managers, models, utils)
└── ...                 # Virtualenv, git, IDE files, etc.
```

## Requirements
- Python 3.13.5 or newer
- pip (Python package manager)
- See `requirements.txt` for pip-installable dependencies:
  - matplotlib>=3.8.0
  - numpy>=1.21.0
  - (Tkinter is included with Python)

## Installation
1. Clone or download this repository.
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
From the `PointOfSales` directory, run:
```bash
python main.py
```

## Usage Guide
- All data is saved in the `datas/` folder. Demo data for various business types is included.
- Use the **Manage Products** button to add/edit/delete/import products. Products support main/subcategory, color, and icon.
- Use the **Category Manager** (in product dialogs) to add/rename/delete categories, set colors/icons, and manage custom categories.
- Use the **Sales Summary** tab for analytics and charts.
- Use the **IMS Sync** tab to import/export tangible items to/from the Inventory Management System.
- Data files can be loaded/saved in JSON, TXT, CSV, or YAML. The system auto-detects file type.
- All demo data files are available in JSON format for easy import/export.

## Data Format
- Products are stored as JSON objects with fields: `product_id`, `name`, `category_main`, `category_sub`, `type`, `price`, `stock`, `unit`, `description`, etc.
- Example:
```json
{
  "product_id": "GROC-0001",
  "name": "Apple",
  "category_main": "Consumables",
  "category_sub": "Food",
  "type": "product",
  "price": 0.50,
  "stock": 120,
  "unit": "pcs",
  "description": "Fresh red apples"
}
```

## Extensibility
- Add new business types by creating new demo data files in `datas/`.
- Extend categories, colors, and icons via the Category Manager UI or by editing `custom_categories.json`.
- Modular codebase: add new features or integrations in the `src/` directory.

## Troubleshooting
- If you encounter file format errors, ensure your data files match the expected JSON structure.
- For import/export issues, check file permissions and supported formats.
- For UI or category issues, reset custom categories via the Category Manager.

## Support
For issues or questions, please open an issue or contact the maintainer. 