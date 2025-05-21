from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# Customer Request Models
class CustomerCreate(BaseModel):
    customer_group_id: int = 1
    store_id: int = 0
    language_id: int = 1
    firstname: str
    lastname: str
    email: EmailStr
    telephone: str
    fax: str = ""
    password: str
    newsletter: bool = False
    status: bool = True
    
    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    password: Optional[str] = None
    status: Optional[bool] = None
    
    class Config:
        from_attributes = True

# Customer Response Models
class CustomerInList(BaseModel):
    customer_id: int
    firstname: str
    lastname: str
    email: str
    telephone: str
    status: bool
    date_added: datetime
    
    class Config:
        from_attributes = True

class CustomerDetail(BaseModel):
    customer_id: int
    customer_group_id: int
    store_id: int
    language_id: int
    firstname: str
    lastname: str
    email: str
    telephone: str
    fax: str
    newsletter: bool
    status: bool
    date_added: datetime
    
    class Config:
        from_attributes = True