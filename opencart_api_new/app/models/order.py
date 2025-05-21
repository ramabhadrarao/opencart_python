from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "oc_order"

    order_id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(Integer, nullable=False, default=0)
    invoice_prefix = Column(String(26), nullable=False)
    store_id = Column(Integer, nullable=False, default=0)
    store_name = Column(String(64), nullable=False)
    store_url = Column(String(255), nullable=False)
    customer_id = Column(Integer, ForeignKey("oc_customer.customer_id"), nullable=False, default=0)
    customer_group_id = Column(Integer, nullable=False, default=0)
    firstname = Column(String(32), nullable=False)
    lastname = Column(String(32), nullable=False)
    email = Column(String(96), nullable=False)
    telephone = Column(String(32), nullable=False)
    fax = Column(String(32), nullable=False)
    custom_field = Column(Text, nullable=False)
    payment_firstname = Column(String(32), nullable=False)
    payment_lastname = Column(String(32), nullable=False)
    payment_company = Column(String(60), nullable=False)
    payment_address_1 = Column(String(128), nullable=False)
    payment_address_2 = Column(String(128), nullable=False)
    payment_city = Column(String(128), nullable=False)
    payment_postcode = Column(String(10), nullable=False)
    payment_country = Column(String(128), nullable=False)
    payment_country_id = Column(Integer, nullable=False)
    payment_zone = Column(String(128), nullable=False)
    payment_zone_id = Column(Integer, nullable=False)
    payment_address_format = Column(Text, nullable=False)
    payment_custom_field = Column(Text, nullable=False)
    payment_method = Column(String(128), nullable=False)
    payment_code = Column(String(128), nullable=False)
    shipping_firstname = Column(String(32), nullable=False)
    shipping_lastname = Column(String(32), nullable=False)
    shipping_company = Column(String(40), nullable=False)
    shipping_address_1 = Column(String(128), nullable=False)
    shipping_address_2 = Column(String(128), nullable=False)
    shipping_city = Column(String(128), nullable=False)
    shipping_postcode = Column(String(10), nullable=False)
    shipping_country = Column(String(128), nullable=False)
    shipping_country_id = Column(Integer, nullable=False)
    shipping_zone = Column(String(128), nullable=False)
    shipping_zone_id = Column(Integer, nullable=False)
    shipping_address_format = Column(Text, nullable=False)
    shipping_custom_field = Column(Text, nullable=False)
    shipping_method = Column(String(128), nullable=False)
    shipping_code = Column(String(128), nullable=False)
    comment = Column(Text, nullable=False)
    total = Column(Float, nullable=False, default=0.0)
    order_status_id = Column(Integer, nullable=False, default=0)
    affiliate_id = Column(Integer, nullable=False)
    commission = Column(Float, nullable=False)
    marketing_id = Column(Integer, nullable=False)
    tracking = Column(String(64), nullable=False)
    language_id = Column(Integer, nullable=False)
    currency_id = Column(Integer, nullable=False)
    currency_code = Column(String(3), nullable=False)
    currency_value = Column(Float, nullable=False, default=1.0)
    ip = Column(String(40), nullable=False)
    forwarded_ip = Column(String(40), nullable=False)
    user_agent = Column(String(255), nullable=False)
    accept_language = Column(String(255), nullable=False)
    date_added = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    products = relationship("OrderProduct", back_populates="order")
    history = relationship("OrderHistory", back_populates="order")


class OrderProduct(Base):
    __tablename__ = "oc_order_product"

    order_product_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("oc_order.order_id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    model = Column(String(64), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    tax = Column(Float, nullable=False, default=0.0)
    reward = Column(Integer, nullable=False)

    # Relationship
    order = relationship("Order", back_populates="products")


class OrderHistory(Base):
    __tablename__ = "oc_order_history"

    order_history_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("oc_order.order_id"), nullable=False)
    order_status_id = Column(Integer, nullable=False)
    notify = Column(Boolean, nullable=False, default=False)
    comment = Column(Text, nullable=False)
    date_added = Column(DateTime, nullable=False)

    # Relationship
    order = relationship("Order", back_populates="history")