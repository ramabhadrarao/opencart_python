from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class Zone(Base):
    __tablename__ = "oc_zone"

    zone_id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("oc_country.country_id"), nullable=False)
    name = Column(String(128), nullable=False)
    code = Column(String(32), nullable=False)
    status = Column(Boolean, nullable=False, default=True)