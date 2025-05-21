from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class OnlineUser(Base):
    __tablename__ = "oc_customer_online"

    # Use only the columns that actually exist in the database
    ip = Column(String(40), primary_key=True)
    customer_id = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    referer = Column(Text, nullable=False)
    date_added = Column(DateTime, nullable=False)