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
        self.load_data()
        self.create_notebook()

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
        # Parse sales.txt and show summary stats and a matplotlib chart
        import re
        sales_file = CONFIG['sales_file']
        sales = []
        if os.path.exists(sales_file):
            with open(sales_file, 'r') as f:
                sale = {}
                for line in f:
                    if line.startswith('--- SALE START ---'):
                        sale = {}
                    elif line.startswith('ID: '):
                        sale['id'] = line.split(': ',1)[1].strip()
                    elif line.startswith('TIMESTAMP: '):
                        sale['timestamp'] = line.split(': ',1)[1].strip()
                    elif line.startswith('TOTAL: '):
                        sale['total'] = float(line.split(': ',1)[1].strip())
                    elif line.startswith('--- SALE END ---'):
                        if sale:
                            sales.append(sale)
        # Stats
        total_sales = sum(s['total'] for s in sales)
        num_sales = len(sales)
        ttk.Label(parent, text=f"Total Sales: {CONFIG['currency_symbol']}{total_sales:.2f}", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        ttk.Label(parent, text=f"Number of Transactions: {num_sales}", font=('Segoe UI', 12)).pack(pady=5)
        # Chart
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

    def create_sync_tab(self, parent):
        """Create IMS sync tab for import/export tangible items."""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="IMS ↔ POS Sync", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        ttk.Button(frame, text="Import Tangible Items from IMS", command=self.import_from_ims).pack(pady=10)
        ttk.Button(frame, text="Export Tangible Items to IMS", command=self.export_to_ims).pack(pady=10)
        self.sync_status = tk.StringVar(value="Ready.")
        ttk.Label(frame, textvariable=self.sync_status, font=('Segoe UI', 10)).pack(pady=10)

    def import_from_ims(self):
        """Import tangible items (type == 'product') from IMS JSON or TXT file."""
        file_path = filedialog.askopenfilename(title="Import from IMS", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")])
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
                            if item.get('type', 'product') == 'product':
                                prod_id = item.get('id') or item.get('product_id') or f"prod_{uuid.uuid4().hex[:8]}"
                                name = item.get('name', 'Unknown')
                                category = item.get('category', '')
                                price = float(item.get('price', 0.0))
                                stock = int(item.get('stock', 0))
                                unit = item.get('unit', 'pcs')
                                description = item.get('description', '')
                                if not any(p['id'] == prod_id for p in self.products):
                                    self.products.append({'id': prod_id, 'name': name, 'category': category, 'type': 'product', 'price': price, 'stock': stock, 'unit': unit, 'description': description})
                                    imported += 1
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        parts = line.strip().split('|')
                        if len(parts) >= 8 and parts[3] == 'product':
                            prod_id, name, category, type_, price, stock, unit, description = parts[:8]
                            if not any(p['id'] == prod_id for p in self.products):
                                self.products.append({'id': prod_id, 'name': name, 'category': category, 'type': 'product', 'price': float(price), 'stock': int(stock), 'unit': unit, 'description': description})
                                imported += 1
            self.save_products()
            self.refresh_main_window()
            self.sync_status.set(f"Imported {imported} tangible items from IMS.")
        except Exception as e:
            self.sync_status.set(f"Import failed: {e}")

    def export_to_ims(self):
        """Export current tangible items (type == 'product') to IMS as JSON or TXT."""
        file_path = filedialog.asksaveasfilename(title="Export to IMS", filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")], defaultextension=".json")
        if not file_path:
            return
        try:
            tangible = [p for p in self.products if p.get('type', 'product') == 'product']
            if file_path.endswith('.json'):
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(tangible, f, indent=4)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for p in tangible:
                        line = f"{p['id']}|{p['name']}|{p.get('category','')}|product|{p.get('price',0.0)}|{p.get('stock',0)}|{p.get('unit','pcs')}|{p.get('description','')}\n"
                        f.write(line)
            self.sync_status.set(f"Exported {len(tangible)} tangible items to IMS.")
        except Exception as e:
            self.sync_status.set(f"Export failed: {e}")

    # --- DATA HANDLING ---
    def load_data(self, filepath=None):
        """Load products from a pipe-delimited TXT file or JSON file."""
        self.products.clear()
        try:
            path = filepath or CONFIG['products_file']
            if path.endswith('.json'):
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.products.append({
                            'id': item.get('id') or item.get('product_id'),
                            'name': item.get('name', ''),
                            'category': item.get('category', ''),
                            'type': item.get('type', 'product'),
                            'price': float(item.get('price', 0.0)),
                            'stock': int(item.get('stock', 0)),
                            'unit': item.get('unit', 'pcs'),
                            'description': item.get('description', '')
                        })
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        parts = line.strip().split('|')
                        # Legacy: id|name|price|stock
                        if len(parts) == 4:
                            self.products.append({
                                'id': parts[0],
                                'name': parts[1],
                                'category': '',
                                'type': 'product',
                                'price': float(parts[2]),
                                'stock': int(parts[3]),
                                'unit': 'pcs',
                                'description': ''
                            })
                        # New: id|name|category|type|price|stock|unit|description
                        elif len(parts) >= 8:
                            self.products.append({
                                'id': parts[0],
                                'name': parts[1],
                                'category': parts[2],
                                'type': parts[3],
                                'price': float(parts[4]),
                                'stock': int(parts[5]),
                                'unit': parts[6],
                                'description': parts[7]
                            })
            CONFIG['products_file'] = path # Update current file
        except (FileNotFoundError) as e:
            messagebox.showerror("Error Loading Data", f"Products file not found: {e}\nStarting with an empty product list.")
        except (IndexError, ValueError) as e:
            messagebox.showerror("Data Format Error", f"Could not parse products file: {e}\nCheck for malformed lines.")

    def save_products(self, filepath=None):
        """Save the current product list to a pipe-delimited TXT file."""
        try:
            path = filepath or CONFIG['products_file']
            if path.endswith('.json'):
                import json
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.products, f, indent=4)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    for product in self.products:
                        # Save all fields pipe-delimited
                        line = f"{product['id']}|{product['name']}|{product.get('category','')}|{product.get('type','product')}|{product.get('price',0.0)}|{product.get('stock',0)}|{product.get('unit','pcs')}|{product.get('description','')}\n"
                    f.write(line)
            CONFIG['products_file'] = path
            return True
        except Exception as e:
            messagebox.showerror("Error Saving Data", f"Could not save products file: {e}")
            return False

    # --- PRODUCT DISPLAY ---
    def update_product_display(self):
        """Clear and recreate the product buttons."""
        for button in self.product_buttons:
            button.destroy()
        self.product_buttons.clear()

        row, col = 0, 0
        for product in self.products:
            btn = tk.Button(self.products_frame, 
                            text=f"{product['name']}\n{CONFIG['currency_symbol']}{product['price']:.2f}",
                            font=('Segoe UI', 10), 
                            wraplength=120,
                            justify='center',
                            bg=COLORS['product_bg'],
                            fg=COLORS['dark_text'],
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
    """A Toplevel window for managing the product list."""
    def __init__(self, parent, products, refresh_callback, save_callback):
        super().__init__(parent)
        self.title("Product Management")
        self.geometry("1000x600")
        self.transient(parent)
        self.grab_set()
        self.products = products
        self.refresh_callback = refresh_callback
        self.save_callback = save_callback
        self.create_prod_widgets()

    def create_prod_widgets(self):
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Add New Item", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit Selected", command=self.edit_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_product, style="Danger.TButton").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Import Items", command=self.import_products).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Save to File", command=self.save, style="Success.TButton").pack(side='right', padx=5)

        # Treeview to display products
        cols = ('id', 'name', 'category', 'type', 'price', 'stock', 'unit', 'description')
        self.prod_tree = ttk.Treeview(self, columns=cols, show='headings')
        self._sort_orders = {col: False for col in cols}
        for col, label in zip(cols, ["ID", "Name", "Category", "Type", "Price", "Stock", "Unit", "Description"]):
            self.prod_tree.heading(col, text=label, command=lambda c=col: self.sort_by_column(c))
        self.prod_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.refresh_prod_list()

    def sort_by_column(self, col):
        data = [(self.prod_tree.set(k, col), k) for k in self.prod_tree.get_children('')]
        # Try to convert to float for numeric columns
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] != '' else float('-inf'), reverse=self._sort_orders[col])
        except ValueError:
            data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=self._sort_orders[col])
        for index, (val, k) in enumerate(data):
            self.prod_tree.move(k, '', index)
        self._sort_orders[col] = not self._sort_orders[col]

    def refresh_prod_list(self):
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        for p in self.products:
            self.prod_tree.insert('', 'end', values=(
                p.get('id', ''),
                p.get('name', ''),
                p.get('category', ''),
                p.get('type', 'product'),
                f"{p.get('price', 0.0):.2f}",
                p.get('stock', 0) if p.get('type', 'product') == 'product' else '',
                p.get('unit', '') if p.get('type', 'product') == 'product' else '',
                p.get('description', '')
            ))

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
            'id': values[0],
            'name': values[1],
            'category': values[2],
            'type': values[3],
            'price': float(values[4]),
            'stock': int(values[5]) if values[5] else 0,
            'unit': values[6],
            'description': values[7]
        }
        EditProductDialog(self, product, self.update_product, categories=CATEGORIES)

    def update_product(self, old_id, new_data):
        for i, p in enumerate(self.products):
            if p['id'] == old_id:
                self.products[i] = new_data
                break
        self.refresh_prod_list()

    def delete_product(self):
        selected = self.prod_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected item(s)?"):
            for item_id in selected:
                values = self.prod_tree.item(item_id, 'values')
                self.products = [p for p in self.products if p['id'] != values[0]]
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