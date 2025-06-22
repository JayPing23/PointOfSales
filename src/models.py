class Product:
    """
    Represents an item in the POS system. Can be a tangible product or a non-tangible item (service, subscription, booking, digital).
    :param product_id: Unique product ID
    :param name: Name of the item
    :param category: Category
    :param price: Price
    :param stock: Stock (for tangible products)
    :param description: Description
    :param type: 'product', 'service', 'subscription', 'booking', 'digital'
    :param unit: Unit of measure (for tangible products)
    """
    def __init__(self, product_id: str, name: str, category: str, price: float, stock: int = 0, description: str = "", type: str = "product", unit: str = "pcs"):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.description = description
        self.type = type  # 'product', 'service', 'subscription', 'booking', 'digital'
        self.unit = unit

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "type": self.type,
            "unit": self.unit
        }

    @staticmethod
    def from_dict(data: dict):
        return Product(
            product_id=data.get("product_id", ""),
            name=data.get("name", ""),
            category=data.get("category", ""),
            price=float(data.get("price", 0.0)),
            stock=int(data.get("stock", 0)),
            description=data.get("description", ""),
            type=data.get("type", "product"),
            unit=data.get("unit", "pcs")
        )

class CartItem:
    """
    Represents an item in the shopping cart.
    """
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

    def to_dict(self) -> dict:
        return {
            "product": self.product.to_dict(),
            "quantity": self.quantity
        }

    @staticmethod
    def from_dict(data: dict):
        return CartItem(
            product=Product.from_dict(data["product"]),
            quantity=int(data.get("quantity", 0))
        ) 