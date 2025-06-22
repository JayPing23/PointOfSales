import json
import os
from typing import List, Optional
from ..models import Product, CartItem

class POSManager:
    """
    Manages POS operations: cart, checkout, sales transactions, save/load, and receipts.
    """
    def __init__(self):
        self.products: List[Product] = []
        self.cart: List[CartItem] = []
        self.sales: List[dict] = []

    def add_to_cart(self, product: Product, quantity: int) -> None:
        for item in self.cart:
            if item.product.product_id == product.product_id:
                item.quantity += quantity
                return
        self.cart.append(CartItem(product, quantity))

    def remove_from_cart(self, product_id: str) -> bool:
        for i, item in enumerate(self.cart):
            if item.product.product_id == product_id:
                del self.cart[i]
                return True
        return False

    def clear_cart(self) -> None:
        self.cart.clear()

    def get_cart_total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.cart)

    def checkout(self, cash_tendered: float) -> Optional[dict]:
        total = self.get_cart_total()
        if cash_tendered < total:
            return None
        change = cash_tendered - total
        transaction = {
            "items": [item.to_dict() for item in self.cart],
            "total": total,
            "cash_tendered": cash_tendered,
            "change": change
        }
        self.sales.append(transaction)
        self.clear_cart()
        return transaction

    def save_sales_to_json(self, filepath: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.sales, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving sales to JSON: {e}")
            return False

    def load_sales_from_json(self, filepath: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                self.sales = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading sales from JSON: {e}")
            return False

    def save_receipt(self, transaction: dict, filepath: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("RECEIPT\n")
                f.write("="*30 + "\n")
                for item in transaction["items"]:
                    f.write(f"{item['product']['name']} x{item['quantity']} @ {item['product']['price']:.2f}\n")
                f.write(f"Total: {transaction['total']:.2f}\n")
                f.write(f"Cash: {transaction['cash_tendered']:.2f}\n")
                f.write(f"Change: {transaction['change']:.2f}\n")
            return True
        except Exception as e:
            print(f"Error saving receipt: {e}")
            return False

    def save_products_to_json(self, filepath: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.products], f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving products to JSON: {e}")
            return False

    def load_products_from_json(self, filepath: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = [Product.from_dict(item) for item in data]
            return True
        except Exception as e:
            print(f"Error loading products from JSON: {e}")
            return False

    def load_products_from_txt(self, filepath: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                self.products = []
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 8:
                        self.products.append(Product(
                            product_id=parts[0],
                            name=parts[1],
                            category=parts[2],
                            type=parts[3],
                            price=float(parts[4]),
                            stock=int(parts[5]),
                            unit=parts[6],
                            description=parts[7]
                        ))
            return True
        except Exception as e:
            print(f"Error loading products from TXT: {e}")
            return False

    def load_products_from_csv(self, filepath: str) -> bool:
        try:
            import csv
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.products = []
                for row in reader:
                    self.products.append(Product(
                        product_id=row.get('product_id', ''),
                        name=row.get('name', ''),
                        category=row.get('category', ''),
                        type=row.get('type', 'product'),
                        price=float(row.get('price', 0.0)),
                        stock=int(row.get('stock', 0)),
                        unit=row.get('unit', 'pcs'),
                        description=row.get('description', '')
                    ))
            return True
        except Exception as e:
            print(f"Error loading products from CSV: {e}")
            return False

    def load_products_from_yaml(self, filepath: str) -> bool:
        try:
            import yaml
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.products = [Product.from_dict(item) for item in data]
            return True
        except Exception as e:
            print(f"Error loading products from YAML: {e}")
            return False 