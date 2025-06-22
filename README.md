# Point of Sale (POS) System

A modern, feature-rich Point of Sale system built with Python and Tkinter, designed for small businesses to manage sales and products efficiently.

## 🚀 Features

### Core Functionality
- **Product Management**: Add, edit, and delete products with real-time updates
- **POS Interface**: Touch-friendly grid layout for easy product selection
- **Shopping Cart**: Dynamic cart system with add/remove functionality and running totals
- **Checkout System**: Complete payment processing with cash tendered and change calculation
- **Virtual Receipts**: Clean, printable receipts generated for each sale
- **Data Persistence**: Products and sales data saved to human-readable TXT files

### User Interface
- **Modern Design**: Professional color scheme with intuitive layout
- **Responsive Layout**: Adaptive grid system that works on different screen sizes
- **Visual Feedback**: Clear visual indicators for all user interactions
- **Touch-Friendly**: Large buttons and clear typography for easy operation

### Data Management
- **File Import/Export**: Load and save product databases to different files
- **Sales Tracking**: Complete transaction history with timestamps
- **Inventory Management**: Stock tracking for all products
- **Data Validation**: Error handling for malformed data files

## 📋 Requirements

- **Python**: 3.8 or higher (latest Python version recommended)
- **Tkinter**: Usually included with Python installation
- **Operating System**: Windows, macOS, or Linux

## 🛠️ Installation

1. **Clone or Download** the project to your local machine
2. **Navigate** to the project directory:
   ```bash
   cd PointOfSales
   ```
3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   ```
4. **Activate the virtual environment**:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
5. **Run the application**:
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### Starting the Application
Launch the POS system by running `main.py`. The main interface will display:
- **Left Panel**: Available products in a grid layout
- **Right Panel**: Current order cart and checkout options

### Managing Products
1. Click **"Manage Products"** in the top-right of the products area
2. Use the product manager to:
   - Add new products with ID, name, price, and stock quantity
   - Edit existing product details
   - Delete products from inventory
   - Save changes to update the main display

### Processing Sales
1. **Add Items**: Click on product buttons to add them to the cart
2. **Modify Quantities**: Items with multiple quantities will show in the cart
3. **Remove Items**: Select items in the cart and click "Remove Selected Item"
4. **Checkout**: Click "Proceed to Checkout" when ready
5. **Payment**: Enter cash amount tendered to calculate change
6. **Complete Sale**: Review receipt and finalize the transaction

### File Management
- **Products File**: `products.txt` stores all product information
- **Sales File**: `sales.txt` records all completed transactions
- **Import/Export**: Use the product manager to load/save different product files

## 📁 File Structure

```
PointOfSales/
├── main.py              # Main application file
├── products.txt         # Product database (pipe-delimited)
├── sales.txt           # Sales transaction history
├── README.md           # This file
├── .venv/              # Virtual environment (created during setup)
└── .git/               # Git repository files
```

## 📊 Data Format

### Products File (`products.txt`)
Each line contains product information separated by pipes:
```
product_id|product_name|price|stock_quantity
```

Example:
```
prod_1001|Cafe Latte|4.5|100
prod_1002|Cappuccino|4.75|100
```

### Sales File (`sales.txt`)
Stores completed transactions in JSON format with:
- Transaction ID
- Timestamp
- Items sold
- Payment details
- Total amount

## ⚙️ Configuration

The application uses a centralized configuration system in `main.py`:

```python
CONFIG = {
    "tax_rate": 0.08,           # 8% sales tax
    "currency_symbol": "$",     # Currency display
    "products_file": "products.txt",
    "sales_file": "sales.txt",
}
```

## 🎨 Customization

### Color Scheme
Modify the `COLORS` dictionary in `main.py` to change the application's appearance:

```python
COLORS = {
    'primary': '#4f46e5',       # Main brand color
    'secondary': '#64748b',     # Secondary elements
    'success': '#10b981',       # Success/checkout buttons
    'danger': '#ef4444',        # Remove/delete buttons
    # ... more color definitions
}
```

### Tax Rate
Update the tax rate in the `CONFIG` dictionary to match your local requirements.

## 🔧 Troubleshooting

### Common Issues

1. **Tkinter Not Found**
   - Ensure Python is properly installed with Tkinter
   - On Linux: `sudo apt-get install python3-tk`

2. **File Permission Errors**
   - Ensure the application has write permissions in the project directory
   - Check that `products.txt` and `sales.txt` are not read-only

3. **Data Loading Errors**
   - Verify `products.txt` follows the correct format
   - Check for malformed lines or invalid data types

4. **Display Issues**
   - Try adjusting your screen resolution
   - The application is designed for 1200x750 minimum resolution

## 🚀 Future Enhancements

Potential improvements for future versions:
- **Barcode Scanner Support**: Integration with hardware barcode scanners
- **Receipt Printer**: Direct printing to thermal receipt printers
- **Database Integration**: SQLite or MySQL database backend
- **User Authentication**: Multi-user support with role-based access
- **Reporting**: Sales reports and analytics
- **Backup System**: Automated data backup and recovery
- **Network Support**: Multi-terminal setup for larger businesses

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

For support or questions:
1. Check the troubleshooting section above
2. Review the code comments in `main.py`
3. Open an issue in the project repository

---

**Built with Python and Tkinter** | **Version**: Latest Python | **Last Updated**: 2024 