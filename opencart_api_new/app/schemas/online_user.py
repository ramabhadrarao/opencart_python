from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class OnlineUserBase(BaseModel):
    ip: str
    customer_id: int
    url: str
    referer: str
    date_added: datetime
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    page_title: Optional[str] = None
    time_spent: Optional[int] = None
    user_type: Optional[str] = None
    
    class Config:
        from_attributes = True

class OnlineUserCreate(OnlineUserBase):
    pass

class OnlineUser(OnlineUserBase):
    class Config:
        from_attributes = True