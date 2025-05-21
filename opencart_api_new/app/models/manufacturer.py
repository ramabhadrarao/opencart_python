from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Manufacturer(Base):
    __tablename__ = "oc_manufacturer"

    manufacturer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    image = Column(String(255))
    sort_order = Column(Integer, nullable=False)