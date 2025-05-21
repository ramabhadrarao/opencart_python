import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

def generate_password_reset_token(length: int = 32) -> str:
    """
    Generate a secure random token for password reset
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def format_price(price: float) -> str:
    """
    Format price for display
    """
    return f"${price:.2f}"

def calculate_order_total(products: list) -> float:
    """
    Calculate order total from products list
    """
    return sum(p.price * p.quantity for p in products)