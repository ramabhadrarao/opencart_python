from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None

class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str