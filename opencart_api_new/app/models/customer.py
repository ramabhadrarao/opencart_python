from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = "oc_customer"

    customer_id = Column(Integer, primary_key=True, index=True)
    customer_group_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False, default=0)
    language_id = Column(Integer, nullable=False)
    firstname = Column(String(32), nullable=False)
    lastname = Column(String(32), nullable=False)
    email = Column(String(96), nullable=False)
    telephone = Column(String(32), nullable=False)
    fax = Column(String(32), nullable=False)
    password = Column(String(40), nullable=False)
    salt = Column(String(9), nullable=False)
    cart = Column(Text)
    wishlist = Column(Text)
    newsletter = Column(Boolean, nullable=False, default=False)
    address_id = Column(Integer, nullable=False, default=0)
    custom_field = Column(Text, nullable=False)
    ip = Column(String(40), nullable=False)
    status = Column(Boolean, nullable=False)
    safe = Column(Boolean, nullable=False)
    token = Column(Text, nullable=False)
    code = Column(String(40), nullable=False)
    date_added = Column(DateTime, nullable=False)
    verifymobile = Column(Integer, nullable=False)

    # Relationships
    # For Address relationship, use string reference to prevent circular import
    addresses = relationship("Address", back_populates="customer")
    orders = relationship("Order", back_populates="customer")