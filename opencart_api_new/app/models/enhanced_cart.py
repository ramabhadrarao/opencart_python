from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class EnhancedCart(Base):
    """Enhanced shopping cart with additional analytics features"""
    __tablename__ = "api_cart"

    cart_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(40), nullable=False, index=True)
    customer_id = Column(Integer, nullable=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    options = Column(Text, nullable=True)  # JSON string of product options
    price = Column(Float, nullable=False, default=0.0)  # Price at time of adding to cart
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    saved_for_later = Column(Boolean, nullable=False, default=False)
    source = Column(String(50), nullable=True)  # How item was added: quick_add, product_page, etc.
    notes = Column(Text, nullable=True)  # Customer notes for this item
    

class CartHistory(Base):
    """Track changes to cart for analytics"""
    __tablename__ = "api_cart_history"

    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("api_cart.cart_id"), nullable=False)
    session_id = Column(String(40), nullable=False)
    customer_id = Column(Integer, nullable=True)
    product_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # add, update, remove
    quantity_before = Column(Integer, nullable=True)
    quantity_after = Column(Integer, nullable=True)
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to cart
    cart = relationship("EnhancedCart")


class AbandonedCart(Base):
    """Track abandoned carts for recovery"""
    __tablename__ = "api_abandoned_cart"

    abandoned_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(40), nullable=False)
    customer_id = Column(Integer, nullable=True, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(32), nullable=True)
    total_items = Column(Integer, nullable=False, default=0)
    total_value = Column(Float, nullable=False, default=0.0)
    cart_contents = Column(Text, nullable=True)  # JSON snapshot of cart
    abandoned_date = Column(DateTime, nullable=False)
    last_notification = Column(DateTime, nullable=True)
    notification_count = Column(Integer, nullable=False, default=0)
    recovery_status = Column(String(20), nullable=False, default="pending")  # pending, notified, recovered, expired
    recovered_order_id = Column(Integer, nullable=True)