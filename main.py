"""
A complete, modern Point of Sale (POS) system built with Python and Tkinter.

This application provides a feature-rich GUI for small businesses to manage
sales and products. It is designed to be intuitive, visually appealing, and
easily extendable.

Features:
- Product Management: Add, edit, and delete products with real-time updates.
- POS Interface: A touch-friendly grid for selecting products.
- Cart System: A dynamic cart to add/remove items and see a running total.
- Checkout & Payment: A payment simulation with cash tendered and change calculation.
- Virtual Receipts: A clean, printable receipt is generated for each sale.
- Data Persistence: Products and sales are saved to human-readable TXT files.
- File Handling: Load and save the product database to different files.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import datetime
import uuid
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import csv
import collections

# File path for user-defined custom categories
CUSTOM_CATEGORIES_FILE = os.path.join('datas', 'custom_categories.json')

# --- Unified Category List ---
CATEGORIES = [
    # This is a flat list of all possible categories for legacy compatibility and dropdowns
    "Electronics", "Raw Materials", "Finished Goods", "Food & Beverage", "Clothing", "Equipment", "Supplies", "Bakery", "Cafe", "Grocery", "Household", "Stationery", "Beverages", "Snacks", "Personal Care", "Services", "Digital Products", "Subscription", "Booking", "Consulting", "Training", "IT", "Logistics", "General Store", "Other"
]

# --- Two-Level Category Tree ---
CATEGORY_TREE = {
    # Main categories as keys, each with a list of subcategories
    "Raw Materials": ["Metals", "Plastics", "Chemicals", "Other"],
    "Components": ["Electronics", "Mechanical", "Optical", "Other"],
    "Finished Goods": ["Electronics", "Furniture", "Apparel", "Other"],
    "Consumables": ["Food", "Beverage", "Office Supplies", "Other"],
    "Perishables": ["Produce", "Dairy", "Meat", "Other"],
    "Equipment": ["IT", "Manufacturing", "Office", "Other"],
    "Supplies": ["Cleaning", "Packaging", "Safety", "Other"],
    "Packaging": ["Boxes", "Bottles", "Wrapping", "Other"],
    "Service": ["Repair", "Installation", "Delivery", "Consulting", "Other"],
    "Digital": ["Software", "eBook", "Media", "License", "Other"],
    "Subscription": ["SaaS", "Maintenance", "Membership", "Other"],
    "Booking": ["Event", "Rental", "Appointment", "Other"],
    "Training": ["Staff", "Customer", "Other"],
    "Maintenance": ["Equipment", "IT", "Other"],
    "Other": ["Other"]
}

# On startup, load custom categories and merge with CATEGORY_TREE
# This allows users to extend the category system without losing defaults

def load_custom_categories():
    # Loads user-defined categories from a JSON file if it exists
    if os.path.exists(CUSTOM_CATEGORIES_FILE):
        with open(CUSTOM_CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_custom_categories(custom_tree):
    # Saves the current custom category tree to disk
    with open(CUSTOM_CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(custom_tree, f, indent=2)

# Merge default and custom trees
def get_full_category_tree():
    # Start with a copy of the default tree
    tree = {k: v[:] for k, v in CATEGORY_TREE.items()}
    custom = load_custom_categories()
    for main, subs in custom.items():
        if main not in tree:
            tree[main] = []
        for sub in subs:
            if sub not in tree[main]:
                tree[main].append(sub)
    return tree

CATEGORY_TREE = get_full_category_tree()

# --- CONFIGURATION & STYLING ---
# Centralized configuration for easy customization
CONFIG = {
    "tax_rate": 0.08,  # 8% sales tax
    "currency_symbol": "$",
    "products_file": os.path.join('datas', 'products.txt'),
    "sales_file": os.path.join('datas', 'sales.txt'),
}

# Modern color scheme for a professional look
COLORS = {
    'primary': '#4f46e5', 'primary_dark': '#4338ca',
    'secondary': '#64748b', 'secondary_dark': '#475569',
    'success': '#10b981', 'success_dark': '#059669',
    'danger': '#ef4444', 'danger_dark': '#dc2626',
    'light_bg': '#f8fafc',
    'dark_text': '#1e293b',
    'white': '#ffffff',
    'border': '#e2e8f0',
    'product_bg': '#ede9fe' # A light purple for product buttons
}

# --- MAIN APPLICATION CLASS ---
class POSApp:
    """The main class for the Point of Sale application."""
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Point of Sale System")
        self.root.geometry("1200x750")
        self.root.configure(bg=COLORS['light_bg'])

        self.products = []
        self.cart = []
        self.product_buttons = []
        
        self.setup_styles()
        self.create_notebook()
        self.load_data()

    def setup_styles(self):
        """Configure all the ttk styles for the application."""
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # General styles
        style.configure('TFrame', background=COLORS['light_bg'])
        style.configure('TLabel', background=COLORS['light_bg'], foreground=COLORS['dark_text'], font=('Segoe UI', 10))
        style.configure('Card.TFrame', background=COLORS['white'], relief='solid', borderwidth=1, bordercolor=COLORS['border'])
        
        # Button styles
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=(12, 8), borderwidth=0, foreground=COLORS['white'])
        style.map('TButton', background=[('active', COLORS['primary_dark']), ('!disabled', COLORS['primary'])])
        style.configure('Success.TButton', background=COLORS['success'])
        style.map('Success.TButton', background=[('active', COLORS['success_dark'])])
        style.configure('Danger.TButton', background=COLORS['danger'])
        style.map('Danger.TButton', background=[('active', COLORS['danger_dark'])])

        # Cart (Treeview) style
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=30, fieldbackground=COLORS['white'], borderwidth=0)
        style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'), padding=(10, 10))
        style.map('Treeview.Heading', relief=[('!active', 'flat')])
        
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        # POS Tab
        self.pos_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pos_frame, text="Point of Sale")
        self.create_widgets(self.pos_frame)
        # Sales Summary Tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Sales Summary")
        self.create_sales_summary(self.summary_frame)
        # Analytics Tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")
        self.create_analytics_tab(self.analytics_frame)
        # IMS Sync Tab
        self.sync_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sync_frame, text="IMS Sync")
        self.create_sync_tab(self.sync_frame)

    def create_widgets(self, parent):
        """Create the main layout and widgets of the application."""
        main_frame = ttk.Frame(parent, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid layout
        main_frame.grid_columnconfigure(0, weight=3) # Products area takes more space
        main_frame.grid_columnconfigure(1, weight=2) # Cart area
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Products Area (Left) ---
        products_container = ttk.Frame(main_frame, style='Card.TFrame')
        products_container.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        products_container.grid_rowconfigure(1, weight=1)
        products_container.grid_columnconfigure(0, weight=1)

        # Header with Manage Products button
        products_header = ttk.Frame(products_container, padding=10, style='Card.TFrame')
        products_header.grid(row=0, column=0, sticky='ew')
        ttk.Label(products_header, text="Available Products", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        manage_btn = ttk.Button(products_header, text="Manage Products", command=self.manage_products)
        manage_btn.pack(side=tk.RIGHT)

        # Scrollable frame for product buttons
        self.products_frame = ttk.Frame(products_container, padding=10)
        self.products_frame.grid(row=1, column=0, sticky='nsew')
        self.update_product_display()

        # --- Cart Area (Right) ---
        cart_container = ttk.Frame(main_frame, style='Card.TFrame')
        cart_container.grid(row=0, column=1, sticky='nsew')
        cart_container.grid_rowconfigure(1, weight=1)
        cart_container.grid_columnconfigure(0, weight=1)

        cart_header = ttk.Frame(cart_container, padding=10, style='Card.TFrame')
        cart_header.grid(row=0, column=0, columnspan=2, sticky='ew')
        ttk.Label(cart_header, text="Current Order", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)

        # Cart items display
        cart_cols = ('name', 'qty', 'price')
        self.cart_tree = ttk.Treeview(cart_container, columns=cart_cols, show='headings', height=10)
        self.cart_tree.heading('name', text='Item')
        self.cart_tree.heading('qty', text='Qty')
        self.cart_tree.heading('price', text='Price')
        self.cart_tree.column('name', width=200)
        self.cart_tree.column('qty', width=50, anchor='center')
        self.cart_tree.column('price', width=80, anchor='e')
        self.cart_tree.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
        
        # Remove item button
        remove_item_btn = ttk.Button(cart_container, text="Remove Selected Item", command=self.remove_from_cart, style='Danger.TButton')
        remove_item_btn.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=(0, 10))

        # Totals display
        totals_frame = ttk.Frame(cart_container, style='Card.TFrame', padding=15)
        totals_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10)
        totals_frame.grid_columnconfigure(1, weight=1)

        self.subtotal_var = tk.StringVar(value="$0.00")
        self.tax_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")
        
        ttk.Label(totals_frame, text="Subtotal:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(totals_frame, textvariable=self.subtotal_var, font=('Segoe UI', 11)).grid(row=0, column=1, sticky='e')
        ttk.Label(totals_frame, text="Tax:", font=('Segoe UI', 11, 'bold')).grid(row=1, column=0, sticky='w')
        ttk.Label(totals_frame, textvariable=self.tax_var, font=('Segoe UI', 11)).grid(row=1, column=1, sticky='e')
        ttk.Label(totals_frame, text="Total:", font=('Segoe UI', 14, 'bold')).grid(row=2, column=0, sticky='w', pady=(10,0))
        ttk.Label(totals_frame, textvariable=self.total_var, font=('Segoe UI', 14, 'bold')).grid(row=2, column=1, sticky='e', pady=(10,0))

        # Checkout button
        checkout_btn = ttk.Button(cart_container, text="Proceed to Checkout", command=self.checkout, style='Success.TButton')
        checkout_btn.grid(row=4, column=0, columnspan=2, sticky='ew', padx=10, pady=10, ipady=10)

    def create_sales_summary(self, parent):
        """
        Create the Sales Summary tab UI:
        - Show total sales, number of transactions, and a sales-over-time chart.
        - Show a clickable log of all sales (Treeview).
        - Clicking a sale shows the full receipt in a popup.
        """
        import re
        from tkinter import ttk
        sales_file = CONFIG['sales_file']
        sales = []
        # --- Parse sales.txt for all sales ---
        if os.path.exists(sales_file):
            with open(sales_file, 'r') as f:
                sale = {}
                items = []
                for line in f:
                    if line.startswith('--- SALE START ---'):
                        sale = {}
                        items = []
                    elif line.startswith('ID: '):
                        sale['sale_id'] = line.split(': ',1)[1].strip()
                    elif line.startswith('TIMESTAMP: '):
                        sale['timestamp'] = line.split(': ',1)[1].strip()
                    elif line.startswith('ITEM: '):
                        # Parse item line: id|name|qty|price|type|unit (type/unit optional)
                        parts = line.split(': ',1)[1].strip().split('|')
                        item = {
                            'id': parts[0] if len(parts) > 0 else '',
                            'name': parts[1] if len(parts) > 1 else '',
                            'quantity': int(parts[2]) if len(parts) > 2 else 0,
                            'price': float(parts[3]) if len(parts) > 3 else 0.0,
                            'type': parts[4] if len(parts) > 4 else 'product',
                            'unit': parts[5] if len(parts) > 5 else '',
                        }
                        items.append(item)
                    elif line.startswith('SUBTOTAL: '):
                        sale['subtotal'] = float(line.split(': ',1)[1].strip())
                    elif line.startswith('TOTAL: '):
                        sale['total'] = float(line.split(': ',1)[1].strip())
                    elif line.startswith('TENDERED: '):
                        sale['cash_tendered'] = float(line.split(': ',1)[1].strip())
                    elif line.startswith('--- SALE END ---'):
                        if sale:
                            sale['items'] = items.copy()
                            # Calculate tax if possible
                            if 'total' in sale and 'subtotal' in sale:
                                sale['tax'] = sale['total'] - sale['subtotal']
                            else:
                                sale['tax'] = 0.0
                            sales.append(sale)
        # --- Stats ---
        total_sales = sum(s['total'] for s in sales)
        num_sales = len(sales)
        ttk.Label(parent, text=f"Total Sales: {CONFIG['currency_symbol']}{total_sales:.2f}", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        ttk.Label(parent, text=f"Number of Transactions: {num_sales}", font=('Segoe UI', 12)).pack(pady=5)
        # --- Chart ---
        if sales:
            dates = [datetime.datetime.fromisoformat(s['timestamp']) for s in sales]
            totals = [s['total'] for s in sales]
            fig, ax = plt.subplots(figsize=(7,4))
            ax.plot(dates, totals, marker='o')
            ax.set_title('Sales Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('Total Sale')
            fig.autofmt_xdate()
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill=tk.BOTH, expand=True)
        else:
            ttk.Label(parent, text="No sales data available.").pack(pady=20)
            return
        # --- Sales Log (Treeview) ---
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        ttk.Label(log_frame, text="Sales Log (click to view receipt)", font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        columns = ("sale_id", "timestamp", "total", "num_items")
        tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=8)
        tree.heading("sale_id", text="Sale ID")
        tree.heading("timestamp", text="Date/Time")
        tree.heading("total", text="Total")
        tree.heading("num_items", text="# Items")
        tree.column("sale_id", width=120)
        tree.column("timestamp", width=160)
        tree.column("total", width=80, anchor='e')
        tree.column("num_items", width=80, anchor='center')
        # Insert sales into the log
        for sale in sales:
            tree.insert('', 'end', values=(
                sale.get('sale_id', '')[:8],
                sale.get('timestamp', '')[:19],
                f"{CONFIG['currency_symbol']}{sale.get('total', 0.0):.2f}",
                len(sale.get('items', []))
            ))
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        # --- Click handler to show receipt ---
        def on_log_click(event):
            selected = tree.focus()
            if not selected:
                return
            idx = tree.index(selected)
            if 0 <= idx < len(sales):
                sale = sales[idx]
                # Build sale_record for ReceiptWindow
                sale_record = {
                    "sale_id": sale.get('sale_id', ''),
                    "timestamp": sale.get('timestamp', ''),
                    "items": sale.get('items', []),
                    "subtotal": sale.get('subtotal', 0.0),
                    "tax": sale.get('tax', 0.0),
                    "total": sale.get('total', 0.0),
                    "cash_tendered": sale.get('cash_tendered', 0.0)
                }
                ReceiptWindow(self.root, sale_record)
        tree.bind('<Double-1>', on_log_click)
        # Add a note for the user
        ttk.Label(log_frame, text="Double-click a row to view the full receipt.", font=('Segoe UI', 9, 'italic')).pack(anchor='w', pady=(2,0))
        # Add Export to CSV button
        def export_sales_log():
            file_path = filedialog.asksaveasfilename(title="Export Sales Log", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if not file_path:
                return
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Sale ID", "Timestamp", "Total", "# Items"])
                for sale in sales:
                    writer.writerow([
                        sale.get('sale_id', '')[:8],
                        sale.get('timestamp', '')[:19],
                        f"{CONFIG['currency_symbol']}{sale.get('total', 0.0):.2f}",
                        len(sale.get('items', []))
                    ])
            messagebox.showinfo("Export Complete", f"Sales log exported to {os.path.basename(file_path)}")
        export_btn = ttk.Button(log_frame, text="Export Sales Log to CSV", command=export_sales_log)
        export_btn.pack(anchor='e', pady=(5,0))

    def create_analytics_tab(self, parent):
        """Create the analytics tab: top-selling products, sales by category, and sales by time period."""
        sales_file = CONFIG['sales_file']
        sales = []
        if os.path.exists(sales_file):
            with open(sales_file, 'r') as f:
                sale = {}
                items = []
                for line in f:
                    if line.startswith('--- SALE START ---'):
                        sale = {}
                        items = []
                    elif line.startswith('ID: '):
                        sale['sale_id'] = line.split(': ',1)[1].strip()
                    elif line.startswith('TIMESTAMP: '):
                        sale['timestamp'] = line.split(': ',1)[1].strip()
                    elif line.startswith('ITEM: '):
                        parts = line.split(': ',1)[1].strip().split('|')
                        item = {
                            'id': parts[0] if len(parts) > 0 else '',
                            'name': parts[1] if len(parts) > 1 else '',
                            'quantity': int(parts[2]) if len(parts) > 2 else 0,
                            'price': float(parts[3]) if len(parts) > 3 else 0.0,
                            'type': parts[4] if len(parts) > 4 else 'product',
                            'unit': parts[5] if len(parts) > 5 else '',
                        }
                        items.append(item)
                    elif line.startswith('--- SALE END ---'):
                        if sale:
                            sale['items'] = items.copy()
                            sales.append(sale)
        # Top-selling products
        product_counter = collections.Counter()
        for sale in sales:
            for item in sale.get('items', []):
                product_counter[item['name']] += item['quantity']
        top_products = product_counter.most_common(10)
        ttk.Label(parent, text="Top-Selling Products", font=('Segoe UI', 12, 'bold')).pack(pady=(10,0))
        tree1 = ttk.Treeview(parent, columns=("Product", "Quantity"), show='headings', height=6)
        tree1.heading("Product", text="Product")
        tree1.heading("Quantity", text="Quantity Sold")
        for name, qty in top_products:
            tree1.insert('', 'end', values=(name, qty))
        tree1.pack(fill=tk.X, padx=20, pady=5)
        # Sales by category
        category_counter = collections.Counter()
        for sale in sales:
            for item in sale.get('items', []):
                category_counter[item.get('type', 'product')] += item['quantity']
        ttk.Label(parent, text="Sales by Type", font=('Segoe UI', 12, 'bold')).pack(pady=(10,0))
        tree2 = ttk.Treeview(parent, columns=("Type", "Quantity"), show='headings', height=6)
        tree2.heading("Type", text="Type")
        tree2.heading("Quantity", text="Quantity Sold")
        for cat, qty in category_counter.items():
            tree2.insert('', 'end', values=(cat, qty))
        tree2.pack(fill=tk.X, padx=20, pady=5)
        # Sales by time period (day)
        date_counter = collections.Counter()
        for sale in sales:
            date = sale.get('timestamp', '')[:10]
            total = sale.get('total', 0.0)
            date_counter[date] += total
        ttk.Label(parent, text="Sales by Day", font=('Segoe UI', 12, 'bold')).pack(pady=(10,0))
        tree3 = ttk.Treeview(parent, columns=("Date", "Total Sales"), show='headings', height=6)
        tree3.heading("Date", text="Date")
        tree3.heading("Total Sales", text="Total Sales")
        for date, total in sorted(date_counter.items()):
            tree3.insert('', 'end', values=(date, f"{CONFIG['currency_symbol']}{total:.2f}"))
        tree3.pack(fill=tk.X, padx=20, pady=5)

    def create_sync_tab(self, parent):
        """Create IMS sync tab for import/export tangible items and show current active products file."""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="IMS ↔ POS Sync", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        ttk.Button(frame, text="Import Tangible Items from IMS", command=self.import_from_ims).pack(pady=10)
        ttk.Button(frame, text="Export Tangible Items to IMS", command=self.export_to_ims).pack(pady=10)
        self.sync_status = tk.StringVar(value="Ready.")
        ttk.Label(frame, textvariable=self.sync_status, font=('Segoe UI', 10)).pack(pady=10)
        # Show current active products file
        self.active_file_var = tk.StringVar(value=f"Active Products File: {os.path.basename(CONFIG['products_file'])}")
        self.active_file_label = ttk.Label(frame, textvariable=self.active_file_var, font=('Segoe UI', 9, 'italic'))
        self.active_file_label.pack(pady=(10,0))

    def import_from_ims(self):
        """Import items from IMS in any supported format, accepting all item types and fields."""
        file_path = filedialog.askopenfilename(title="Import from IMS", filetypes=[("All Supported", "*.json *.txt *.csv *.yaml *.yml"), ("All Files", "*.*")])
        if not file_path:
            return
        self.load_data(file_path)
        self.save_products()  # Save to current file for persistence
        self.refresh_main_window()
        self.sync_status.set(f"Imported items from {os.path.basename(file_path)}.")

    def export_to_ims(self):
        """Export all items to IMS in any supported format, including all fields."""
        file_path = filedialog.asksaveasfilename(title="Export to IMS", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("YAML Files", "*.yaml;*.yml"), ("All Files", "*.*")], defaultextension=".json")
        if not file_path:
            return
        self.save_products(file_path)
        self.sync_status.set(f"Exported items to {os.path.basename(file_path)}.")

    # --- DATA HANDLING ---
    def load_data(self, filepath=None):
        """Load products/items from JSON, TXT, CSV, or YAML. Accepts all item types and field variants."""
        import csv
        try:
            self.products.clear()
            path = filepath or CONFIG['products_file']
            if path.endswith('.json'):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        # Accept both 'id' and 'product_id', and all category fields
                        prod_id = item.get('id') or item.get('product_id') or f"prod_{uuid.uuid4().hex[:8]}"
                        name = item.get('name', 'Unknown')
                        category = item.get('category', '')
                        category_main = item.get('category_main', category)
                        category_sub = item.get('category_sub', '')
                        type_ = item.get('type', 'product')
                        price = float(item.get('price', 0.0))
                        stock = int(item.get('stock', 0))
                        unit = item.get('unit', 'pcs')
                        description = item.get('description', '')
                        self.products.append({
                            'id': prod_id,
                            'name': name,
                            'category': category,
                            'category_main': category_main,
                            'category_sub': category_sub,
                            'type': type_,
                            'price': price,
                            'stock': stock,
                            'unit': unit,
                            'description': description
                        })
            elif path.endswith('.csv'):
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for item in reader:
                        prod_id = item.get('id') or item.get('product_id') or f"prod_{uuid.uuid4().hex[:8]}"
                        name = item.get('name', 'Unknown')
                        category = item.get('category', '')
                        category_main = item.get('category_main', category)
                        category_sub = item.get('category_sub', '')
                        type_ = item.get('type', 'product')
                        price = float(item.get('price', 0.0))
                        stock = int(item.get('stock', 0))
                        unit = item.get('unit', 'pcs')
                        description = item.get('description', '')
                        self.products.append({
                            'id': prod_id,
                            'name': name,
                            'category': category,
                            'category_main': category_main,
                            'category_sub': category_sub,
                            'type': type_,
                            'price': price,
                            'stock': stock,
                            'unit': unit,
                            'description': description
                        })
            elif path.endswith('.yaml') or path.endswith('.yml'):
                import yaml
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    for item in data:
                        prod_id = item.get('id') or item.get('product_id') or f"prod_{uuid.uuid4().hex[:8]}"
                        name = item.get('name', 'Unknown')
                        category = item.get('category', '')
                        category_main = item.get('category_main', category)
                        category_sub = item.get('category_sub', '')
                        type_ = item.get('type', 'product')
                        price = float(item.get('price', 0.0))
                        stock = int(item.get('stock', 0))
                        unit = item.get('unit', 'pcs')
                        description = item.get('description', '')
                        self.products.append({
                            'id': prod_id,
                            'name': name,
                            'category': category,
                            'category_main': category_main,
                            'category_sub': category_sub,
                            'type': type_,
                            'price': price,
                            'stock': stock,
                            'unit': unit,
                            'description': description
                        })
            else:
                # TXT fallback: pipe-delimited, legacy and new format
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        parts = line.strip().split('|')
                        if len(parts) == 4:
                            prod_id, name, price, stock = parts[:4]
                            self.products.append({
                                'id': prod_id,
                                'name': name,
                                'category': '',
                                'category_main': '',
                                'category_sub': '',
                                'type': 'product',
                                'price': float(price),
                                'stock': int(stock),
                                'unit': 'pcs',
                                'description': ''
                            })
                        elif len(parts) >= 8:
                            prod_id, name, category, type_, price, stock, unit, description = parts[:8]
                            self.products.append({
                                'id': prod_id,
                                'name': name,
                                'category': category,
                                'category_main': category,
                                'category_sub': '',
                                'type': type_,
                                'price': float(price),
                                'stock': int(stock),
                                'unit': unit,
                                'description': description
                            })
            CONFIG['products_file'] = path
            # Update the active file label if it exists
            if hasattr(self, 'active_file_var'):
                self.active_file_var.set(f"Active Products File: {os.path.basename(CONFIG['products_file'])}")
        except Exception as e:
            messagebox.showerror("Error Loading Data", f"Could not load products: {e}")
        self.update_product_display()

    def save_products(self, filepath=None):
        """Save the current product list to JSON, TXT, CSV, or YAML, including all fields. Always save to the active file unless a new path is given."""
        import csv
        try:
            path = filepath or CONFIG['products_file']
            if path.endswith('.json'):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.products, f, indent=4)
            elif path.endswith('.csv'):
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    fieldnames = ['id','name','category','category_main','category_sub','type','price','stock','unit','description']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for product in self.products:
                        writer.writerow(product)
            elif path.endswith('.yaml') or path.endswith('.yml'):
                import yaml
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(self.products, f, allow_unicode=True)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    for product in self.products:
                        line = f"{product['id']}|{product['name']}|{product.get('category','')}|{product.get('type','product')}|{product.get('price',0.0)}|{product.get('stock',0)}|{product.get('unit','pcs')}|{product.get('description','')}\n"
                        f.write(line)
            CONFIG['products_file'] = path
            # Update the active file label if it exists
            if hasattr(self, 'active_file_var'):
                self.active_file_var.set(f"Active Products File: {os.path.basename(CONFIG['products_file'])}")
            return True
        except Exception as e:
            messagebox.showerror("Error Saving Data", f"Could not save products: {e}")
            return False

    # --- PRODUCT DISPLAY ---
    def update_product_display(self):
        """Clear and recreate the product buttons. Highlight low stock products."""
        for button in self.product_buttons:
            button.destroy()
        self.product_buttons.clear()

        row, col = 0, 0
        for product in self.products:
            # Highlight low stock (threshold = 5)
            low_stock = product.get('type', 'product') == 'product' and product.get('stock', 0) <= 5
            btn_bg = COLORS['danger'] if low_stock else COLORS['product_bg']
            btn_fg = COLORS['white'] if low_stock else COLORS['dark_text']
            btn = tk.Button(self.products_frame, 
                            text=f"{product['name']}\n{CONFIG['currency_symbol']}{product['price']:.2f}",
                            font=('Segoe UI', 10), 
                            wraplength=120,
                            justify='center',
                            bg=btn_bg,
                            fg=btn_fg,
                            relief='flat',
                            activebackground=COLORS['primary'],
                            activeforeground=COLORS['white'],
                            command=lambda p=product: self.add_to_cart(p))
            btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=5, ipadx=10, ipady=10)
            self.products_frame.grid_columnconfigure(col, weight=1)
            self.product_buttons.append(btn)
            col += 1
            if col > 3:
                col = 0
                row += 1
    
    # --- CART LOGIC ---
    def add_to_cart(self, product):
        """Add a product or item to the cart or increment its quantity."""
        # Find product in cart
        for item in self.cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                self.update_cart_display()
                return
        # Only check stock for tangible products
        if product.get('type', 'product') == 'product' and product.get('stock', 0) <= 0:
            messagebox.showwarning("Out of Stock", f"'{product['name']}' is out of stock.")
            return
        cart_item = {
            "id": product['id'],
            "name": product['name'],
            "type": product.get('type', 'product'),
            "unit": product.get('unit', ''),
            "price": product['price'],
            "quantity": 1
        }
        self.cart.append(cart_item)
        self.update_cart_display()

    def remove_from_cart(self):
        """Remove the selected item from the cart."""
        selected_items = self.cart_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an item in the cart to remove.")
            return
        
        for item_id_in_tree in selected_items:
            # The iid of the tree item is the product id
            self.cart = [item for item in self.cart if item['id'] != item_id_in_tree]

        self.update_cart_display()

    def update_cart_display(self):
        """Clear and repopulate the cart display and update totals."""
        # Clear tree
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        # Repopulate tree
        for item in self.cart:
            display_name = item['name']
            if item.get('type', 'product') != 'product':
                display_name += f" ({item['type']})"
            if item.get('unit') and item.get('type', 'product') == 'product':
                display_name += f" [{item['unit']}]"
            self.cart_tree.insert('', 'end', iid=item['id'], values=(display_name, item['quantity'], f"{CONFIG['currency_symbol']}{item['price'] * item['quantity']:.2f}"))
        self.update_totals()

    def update_totals(self):
        """Calculate and display the subtotal, tax, and total."""
        subtotal = sum(item['price'] * item['quantity'] for item in self.cart)
        tax = subtotal * CONFIG['tax_rate']
        total = subtotal + tax
        
        self.subtotal_var.set(f"{CONFIG['currency_symbol']}{subtotal:.2f}")
        self.tax_var.set(f"{CONFIG['currency_symbol']}{tax:.2f}")
        self.total_var.set(f"{CONFIG['currency_symbol']}{total:.2f}")

    # --- CHECKOUT PROCESS ---
    def checkout(self):
        """Initiate the checkout process."""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Cannot checkout with an empty cart.")
            return

        total_amount = sum(item['price'] * item['quantity'] for item in self.cart) * (1 + CONFIG['tax_rate'])
        
        # Open payment dialog
        PaymentDialog(self.root, total_amount, self.finalize_sale)
        
    def finalize_sale(self, total, tendered):
        """Finalize the sale, save data, and show receipt. Also sync IMS stock for tangible items (stub)."""
        # 1. Update stock quantities (only for tangible products)
        for cart_item in self.cart:
            for product in self.products:
                if product['id'] == cart_item['id'] and product.get('type', 'product') == 'product':
                    product['stock'] -= cart_item['quantity']
                    # --- IMS SYNC HOOK: update IMS stock here (API/file integration) ---
                    # Example: self.sync_ims_stock(product['id'], product['stock'])
                    break
        # 2. Record the sale to sales.txt
        sale_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        subtotal = sum(item['price'] * item['quantity'] for item in self.cart)
        try:
            with open(CONFIG['sales_file'], 'a') as f:
                f.write(f"--- SALE START ---\n")
                f.write(f"ID: {sale_id}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                for item in self.cart:
                    f.write(f"ITEM: {item['id']}|{item['name']}|{item['quantity']}|{item['price']}|{item.get('type','product')}|{item.get('unit','')}\n")
                f.write(f"SUBTOTAL: {subtotal:.2f}\n")
                f.write(f"TOTAL: {total:.2f}\n")
                f.write(f"TENDERED: {tendered:.2f}\n")
                f.write(f"--- SALE END ---\n\n")
        except Exception as e:
            messagebox.showerror("Sale Log Error", f"Could not write to sales file: {e}")
        # 3. Save updated product stock
        self.save_products()
        # Create sale_record for receipt window
        sale_record = {
            "sale_id": sale_id, "timestamp": timestamp, "items": self.cart,
            "subtotal": subtotal, "tax": total - subtotal, "total": total,
            "cash_tendered": tendered
        }
        # 4. Show receipt
        ReceiptWindow(self.root, sale_record)
        # 5. Reset for next sale
        self.cart = []
        self.update_cart_display()
        self.update_product_display()

    # --- PRODUCT MANAGEMENT ---
    def manage_products(self):
        ProductManager(self.root, self.products, self.refresh_main_window, self.save_products)

    def refresh_main_window(self):
        """Callback to refresh the main window after product changes."""
        self.load_data() # Reload from file to ensure consistency
        self.update_product_display()

    # --- IMS SYNC STUB (for future API/file integration) ---
    def sync_ims_stock(self, product_id, new_stock):
        """Stub: Sync stock with IMS (to be implemented with API or file integration)."""
        # Example: send update to IMS API or write to file
        pass

# --- HELPER DIALOGS & WINDOWS ---
class ProductManager(tk.Toplevel):
    """A Toplevel window for managing the product list with multi-select checkboxes."""
    def __init__(self, parent, products, refresh_callback, save_callback):
        super().__init__(parent)
        self.title("Product Management")
        self.geometry("1000x600")
        self.transient(parent)
        self.grab_set()
        self.products = products
        self.refresh_callback = refresh_callback
        self.save_callback = save_callback
        self.checked_ids = set()  # Track checked product IDs
        self.create_prod_widgets()

    def create_prod_widgets(self):
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Add New Item", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit Selected", command=self.edit_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Checked", command=self.delete_checked_products, style="Danger.TButton").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Import Items", command=self.import_products).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Save to File", command=self.save, style="Success.TButton").pack(side='right', padx=5)
        # Select All checkbox
        self.select_all_var = tk.BooleanVar(value=False)
        select_all_cb = tk.Checkbutton(self, text="Select All", variable=self.select_all_var, command=self.toggle_select_all)
        select_all_cb.pack(anchor='w', padx=18)
        # Treeview with checkbox column
        cols = ('checked', 'id', 'name', 'category', 'type', 'price', 'stock', 'unit', 'description')
        self.prod_tree = ttk.Treeview(self, columns=cols, show='headings')
        self._sort_orders = {col: False for col in cols if col != 'checked'}
        self.prod_tree.heading('checked', text='', anchor='center')
        self.prod_tree.column('checked', width=32, anchor='center')
        for col, label in zip(cols[1:], ["ID", "Name", "Category", "Type", "Price", "Stock", "Unit", "Description"]):
            self.prod_tree.heading(col, text=label, command=lambda c=col: self.sort_by_column(c))
        self.prod_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.prod_tree.bind('<Button-1>', self.on_treeview_click)
        self.refresh_prod_list()

    def on_treeview_click(self, event):
        # Detect if click is on checkbox column
        region = self.prod_tree.identify('region', event.x, event.y)
        col = self.prod_tree.identify_column(event.x)
        if region == 'cell' and col == '#1':
            row_id = self.prod_tree.identify_row(event.y)
            if row_id:
                prod_id = self.prod_tree.set(row_id, 'id')
                if prod_id in self.checked_ids:
                    self.checked_ids.remove(prod_id)
                else:
                    self.checked_ids.add(prod_id)
                self.refresh_prod_list()
        # Allow normal selection for other columns

    def toggle_select_all(self):
        if self.select_all_var.get():
            self.checked_ids = set(p.get('id', '') for p in self.products)
        else:
            self.checked_ids.clear()
        self.refresh_prod_list()

    def refresh_prod_list(self):
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        for p in self.products:
            prod_id = p.get('id', '')
            checked = '☑' if prod_id in self.checked_ids else '☐'
            values = (
                checked,
                prod_id,
                p.get('name', ''),
                p.get('category', ''),
                p.get('type', 'product'),
                f"{p.get('price', 0.0):.2f}",
                p.get('stock', 0) if p.get('type', 'product') == 'product' else '',
                p.get('unit', '') if p.get('type', 'product') == 'product' else '',
                p.get('description', '')
            )
            item_id = self.prod_tree.insert('', 'end', values=values)
            # Highlight low stock rows
            if p.get('type', 'product') == 'product' and p.get('stock', 0) <= 5:
                self.prod_tree.item(item_id, tags=('low_stock',))
        self.prod_tree.tag_configure('low_stock', background='#ffe5e5')  # Light red

    def delete_checked_products(self):
        if not self.checked_ids:
            messagebox.showwarning("No Selection", "Please check at least one item to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(self.checked_ids)} checked item(s)?"):
            self.products[:] = [p for p in self.products if p.get('id', '') not in self.checked_ids]
            self.checked_ids.clear()
            self.select_all_var.set(False)
            self.refresh_prod_list()

    def add_product(self):
        EditProductDialog(self, None, self.add_product_callback, categories=CATEGORIES)

    def add_product_callback(self, _, new_data):
        self.products.append(new_data)
        self.refresh_prod_list()

    def edit_product(self):
        selected = self.prod_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return
        item_id = selected[0]
        values = self.prod_tree.item(item_id, 'values')
        product = {
            'id': values[1],
            'name': values[2],
            'category': values[3],
            'type': values[4],
            'price': float(values[5]),
            'stock': int(values[6]) if values[6] else 0,
            'unit': values[7],
            'description': values[8]
        }
        EditProductDialog(self, product, self.update_product, categories=CATEGORIES)

    def update_product(self, old_id, new_data):
        for i, p in enumerate(self.products):
            if p['id'] == old_id:
                self.products[i] = new_data
                break
        self.refresh_prod_list()

    def save(self):
        if self.save_callback():
            messagebox.showinfo("Success", "Items saved successfully.")
            self.refresh_callback()
        else:
            messagebox.showerror("Error", "Failed to save items.")

    def import_products(self):
        file_path = filedialog.askopenfilename(title="Import Items", filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json"), ("All Files", "*.*")])
        if not file_path:
            return
        try:
            imported = 0
            if file_path.endswith('.json'):
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            prod_id = item.get('id') or item.get('product_id') or f"prod_{uuid.uuid4().hex[:8]}"
                            name = item.get('name', 'Unknown')
                            category = item.get('category', '')
                            type_ = item.get('type', 'product')
                            price = float(item.get('price', 0.0))
                            stock = int(item.get('stock', 0))
                            unit = item.get('unit', 'pcs')
                            description = item.get('description', '')
                            if not any(p['id'] == prod_id for p in self.products):
                                self.products.append({'id': prod_id, 'name': name, 'category': category, 'type': type_, 'price': price, 'stock': stock, 'unit': unit, 'description': description})
                                imported += 1
                        self.refresh_prod_list()
                        self.save_callback()
                        self.refresh_callback()
                        messagebox.showinfo("Import Complete", f"Imported {imported} items from JSON.")
                        return
            # Try pipe-delimited text
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    parts = line.strip().split('|')
                    if len(parts) == 4:
                        prod_id, name, price, stock = parts[:4]
                        if not any(p['id'] == prod_id for p in self.products):
                            self.products.append({'id': prod_id, 'name': name, 'category': '', 'type': 'product', 'price': float(price), 'stock': int(stock), 'unit': 'pcs', 'description': ''})
                            imported += 1
                    elif len(parts) >= 8:
                        prod_id, name, category, type_, price, stock, unit, description = parts[:8]
                        if not any(p['id'] == prod_id for p in self.products):
                            self.products.append({'id': prod_id, 'name': name, 'category': category, 'type': type_, 'price': float(price), 'stock': int(stock), 'unit': unit, 'description': description})
                            imported += 1
            self.refresh_prod_list()
            self.save_callback()
            self.refresh_callback()
            messagebox.showinfo("Import Complete", f"Imported {imported} items from text file.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import items: {e}")

class EditProductDialog(tk.Toplevel):
    def __init__(self, parent, product, callback, categories=None):
        super().__init__(parent)
        self.title("Edit Item" if product else "Add New Item")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        self.callback = callback
        self.old_id = product['id'] if product else None
        self.categories = categories if categories else []
        # Fields
        self.id_var = tk.StringVar(value=product['id'] if product else f"prod_{uuid.uuid4().hex[:8]}")
        self.name_var = tk.StringVar(value=product['name'] if product else "")
        self.main_category_var = tk.StringVar(value=product['category'] if product else "")
        self.sub_category_var = tk.StringVar(value=product['subcategory'] if product else "")
        self.type_var = tk.StringVar(value=product['type'] if product else "product")
        self.price_var = tk.StringVar(value=str(product['price']) if product else "0.0")
        self.stock_var = tk.StringVar(value=str(product['stock']) if product and product['type'] == 'product' else "0")
        self.unit_var = tk.StringVar(value=product['unit'] if product and product['type'] == 'product' else "pcs")
        self.description_var = tk.StringVar(value=product['description'] if product else "")
        # Layout
        row = 0
        tk.Label(self, text="Product ID:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        tk.Entry(self, textvariable=self.id_var).grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        tk.Label(self, text="Name:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        tk.Entry(self, textvariable=self.name_var).grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        tk.Label(self, text="Main Category:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        self.main_category_combo = ttk.Combobox(self, textvariable=self.main_category_var, values=self.categories, state='normal')
        self.main_category_combo.grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        tk.Label(self, text="Sub Category:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        self.sub_category_combo = ttk.Combobox(self, textvariable=self.sub_category_var, values=CATEGORY_TREE.get(self.main_category_var.get(), []), state="readonly")
        self.sub_category_combo.grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        tk.Label(self, text="Type:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        type_combo = ttk.Combobox(self, textvariable=self.type_var, values=["product", "service", "subscription", "booking", "digital"], state="readonly")
        type_combo.grid(row=row, column=1, sticky='w', padx=10, pady=8)
        type_combo.bind("<<ComboboxSelected>>", self.toggle_fields)
        row += 1
        tk.Label(self, text="Price:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        tk.Entry(self, textvariable=self.price_var).grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        self.stock_label = tk.Label(self, text="Stock:")
        self.stock_entry = tk.Entry(self, textvariable=self.stock_var)
        self.unit_label = tk.Label(self, text="Unit:")
        self.unit_entry = ttk.Combobox(self, textvariable=self.unit_var, values=["pcs", "kg", "g", "L", "ml", "pack", "box", "hour", "service", "other"])
        self.stock_label.grid(row=row, column=0, sticky='e', padx=10, pady=8)
        self.stock_entry.grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        self.unit_label.grid(row=row, column=0, sticky='e', padx=10, pady=8)
        self.unit_entry.grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        tk.Label(self, text="Description:").grid(row=row, column=0, sticky='e', padx=10, pady=8)
        tk.Entry(self, textvariable=self.description_var).grid(row=row, column=1, sticky='w', padx=10, pady=8)
        row += 1
        ttk.Button(self, text="Save", command=self.save).grid(row=row, column=0, columnspan=2, pady=20)
        self.toggle_fields()
    def toggle_fields(self, event=None):
        t = self.type_var.get()
        if t == 'product':
            self.stock_label.grid()
            self.stock_entry.grid()
            self.unit_label.grid()
            self.unit_entry.grid()
        else:
            self.stock_label.grid_remove()
            self.stock_entry.grid_remove()
            self.unit_label.grid_remove()
            self.unit_entry.grid_remove()
    def save(self):
        t = self.type_var.get()
        new_data = {
            'id': self.id_var.get(),
            'name': self.name_var.get(),
            'category': self.main_category_var.get(),
            'subcategory': self.sub_category_var.get(),
            'type': t,
            'price': float(self.price_var.get()),
            'stock': int(self.stock_var.get()) if t == 'product' else 0,
            'unit': self.unit_var.get() if t == 'product' else '',
            'description': self.description_var.get()
        }
        # Add new category to the session list if not present
        if new_data['category'] and new_data['category'] not in self.categories:
            self.categories.append(new_data['category'])
            self.main_category_combo['values'] = self.categories
        self.callback(self.old_id, new_data)
        self.destroy()

class PaymentDialog(tk.Toplevel):
    """Dialog for entering cash tendered and calculating change."""
    def __init__(self, parent, total, callback):
        super().__init__(parent)
        self.title("Payment")
        self.geometry("350x200")
        self.transient(parent)
        self.grab_set()
        
        self.total = total
        self.callback = callback

        self.configure(bg=COLORS['light_bg'])
        
        ttk.Label(self, text=f"Total Due: {CONFIG['currency_symbol']}{total:.2f}", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        ttk.Label(self, text="Cash Tendered:", font=('Segoe UI', 10)).pack(pady=(10,0))
        self.tendered_entry = ttk.Entry(self, font=('Segoe UI', 12))
        self.tendered_entry.pack(pady=5, padx=20, fill='x')
        self.tendered_entry.focus_set()

        process_btn = ttk.Button(self, text="Process Payment", command=self.process, style='Success.TButton')
        process_btn.pack(pady=15, ipady=5, fill='x', padx=20)

        self.bind('<Return>', lambda e: self.process())

    def process(self):
        try:
            tendered = float(self.tendered_entry.get())
            if tendered < self.total:
                messagebox.showerror("Insufficient Funds", "Cash tendered is less than the total amount.", parent=self)
                return
            
            change = tendered - self.total
            messagebox.showinfo("Payment Complete", f"Change Due: {CONFIG['currency_symbol']}{change:.2f}", parent=self)
            
            self.callback(self.total, tendered) # Finalize the sale
            self.destroy()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for cash tendered.", parent=self)

class ReceiptWindow(tk.Toplevel):
    """A window to display a formatted virtual receipt."""
    def __init__(self, parent, sale_record):
        super().__init__(parent)
        self.title(f"Receipt: {sale_record['sale_id'][:8]}")
        self.geometry("400x550")
        self.configure(bg=COLORS['white'])

        receipt_text = tk.Text(self, font=('Courier', 10), bd=0, bg=COLORS['white'])
        receipt_text.pack(padx=20, pady=20, fill='both', expand=True)

        # --- Build Receipt String ---
        receipt = f"*** SALE RECEIPT ***\n\n"
        receipt += f"Sale ID: {sale_record['sale_id']}\n"
        receipt += f"Date: {datetime.datetime.fromisoformat(sale_record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        receipt += "-"*40 + "\n"
        
        # Items
        for item in sale_record['items']:
            line_total = item['price'] * item['quantity']
            receipt += f"{item['name']:<25} {item['quantity']}x {item['price']:.2f} {line_total:>8.2f}\n"
        
        receipt += "-"*40 + "\n"
        
        # Totals
        receipt += f"{'Subtotal:':>30} {sale_record['subtotal']:>8.2f}\n"
        receipt += f"{'Tax:':>30} {sale_record['tax']:>8.2f}\n"
        receipt += f"{'Total:':>30} {sale_record['total']:>8.2f}\n"
        receipt += "-"*40 + "\n"
        
        # Payment
        receipt += f"{'Cash Tendered:':>30} {sale_record['cash_tendered']:>8.2f}\n"
        receipt += f"{'Change Due:':>30} {sale_record['cash_tendered'] - sale_record['total']:>8.2f}\n\n"
        
        receipt += "*** Thank You! ***"

        receipt_text.insert('1.0', receipt)
        receipt_text.config(state='disabled') # Make it read-only

class CategoryManagerDialog(tk.Toplevel):
    def __init__(self, parent, category_tree, on_save):
        super().__init__(parent)
        self.title('Manage Categories')
        self.geometry('500x400')
        self.category_tree = category_tree
        self.on_save = on_save
        self.tree = ttk.Treeview(self, columns=('Color', 'Icon'))
        self.tree.heading('#0', text='Main Category')
        self.tree.heading('Color', text='Color')
        self.tree.heading('Icon', text='Icon')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.populate_tree()
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text='Add Main', command=self.add_main).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Add Sub', command=self.add_sub).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Rename', command=self.rename_cat).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Delete', command=self.delete_cat).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Set Color', command=self.set_color).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Set Icon', command=self.set_icon).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Save', command=self.save).pack(side='right', padx=5)
    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for main, subs in self.category_tree.items():
            main_id = self.tree.insert('', 'end', text=main, values=(self.get_color(main), self.get_icon(main)))
            for sub in subs:
                self.tree.insert(main_id, 'end', text=sub, values=(self.get_color(main, sub), self.get_icon(main, sub)))
    def get_color(self, main, sub=None):
        # Placeholder: return color from category data
        return ''
    def get_icon(self, main, sub=None):
        # Placeholder: return icon from category data
        return ''
    def add_main(self): pass
    def add_sub(self): pass
    def rename_cat(self): pass
    def delete_cat(self): pass
    def set_color(self): pass
    def set_icon(self): pass
    def save(self):
        self.on_save(self.category_tree)
        self.destroy()

# --- RUN APPLICATION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()