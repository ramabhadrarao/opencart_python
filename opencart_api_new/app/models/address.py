from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Address(Base):
    __tablename__ = "oc_address"

    address_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("oc_customer.customer_id"), nullable=False)
    firstname = Column(String(32), nullable=False)
    lastname = Column(String(32), nullable=False)
    company = Column(String(40), nullable=False)
    address_1 = Column(String(128), nullable=False)
    address_2 = Column(String(128), nullable=False)
    city = Column(String(128), nullable=False)
    postcode = Column(String(10), nullable=False)
    country_id = Column(Integer, nullable=False, default=0)
    zone_id = Column(Integer, nullable=False, default=0)
    custom_field = Column(String, nullable=False)

    # Relationship
    customer = relationship("Customer", back_populates="addresses")