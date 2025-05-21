from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Country(Base):
    __tablename__ = "oc_country"

    country_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    iso_code_2 = Column(String(2), nullable=False)
    iso_code_3 = Column(String(3), nullable=False)
    address_format = Column(String, nullable=False)
    postcode_required = Column(Boolean, nullable=False)
    status = Column(Boolean, nullable=False, default=True)