from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Cart(Base):
    __tablename__ = "oc_cart"

    cart_id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=False)
    session_id = Column(String(32), nullable=False)
    product_id = Column(Integer, nullable=False)
    recurring_id = Column(Integer, nullable=False)
    option = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    date_added = Column(DateTime, nullable=False)