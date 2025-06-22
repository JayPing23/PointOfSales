# Point of Sale (POS) System

A modern, modular, and user-friendly Point of Sale application built with Python and Tkinter. Designed for small businesses to manage sales, products, and reporting with a beautiful GUI and robust features.

## Features
- Product management: Add, edit, delete, and import products
- POS interface: Touch-friendly product grid, cart, and checkout
- Sales summary: Tabbed dashboard with charts and stats (matplotlib)
- Data persistence: All data stored in `datas/` (NoSQL-style, txt/json)
- File dialogs for import/export
- User-friendly error handling
- Modular OOP codebase (SOLID principles)

## Folder Structure
```
PointOfSales/
├── datas/              # All product and sales data files
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
├── src/                # Source code (managers, models, utils)
└── ...                 # Virtualenv, git, IDE files, etc.
```

## Requirements
- Python 3.13.5
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

## Usage Notes
- All data is saved in the `datas/` folder.
- Use the "Manage Products" button to add/edit/delete/import products.
- Use the "Sales Summary" tab for sales analytics and charts.
- For best results, use Python 3.13.5 or newer.

## Support
For issues or questions, please open an issue or contact the maintainer. 