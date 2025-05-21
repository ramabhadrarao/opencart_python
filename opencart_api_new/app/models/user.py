from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "oc_user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_group_id = Column(Integer, nullable=False)
    username = Column(String(20), nullable=False)
    password = Column(String(40), nullable=False)
    salt = Column(String(9), nullable=False)
    firstname = Column(String(32), nullable=False)
    lastname = Column(String(32), nullable=False)
    email = Column(String(96), nullable=False)
    image = Column(String(255), nullable=False)
    code = Column(String(40), nullable=False)
    ip = Column(String(40), nullable=False)
    status = Column(Boolean, nullable=False)
    date_added = Column(DateTime, nullable=False)