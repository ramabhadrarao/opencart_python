from typing import Optional
from pydantic import BaseModel

class AddressBase(BaseModel):
    firstname: str
    lastname: str
    company: str = ""
    address_1: str
    address_2: str = ""
    city: str
    postcode: str
    country_id: int
    zone_id: int
    custom_field: str = ""

    class Config:
        from_attributes = True

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    company: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country_id: Optional[int] = None
    zone_id: Optional[int] = None
    custom_field: Optional[str] = None

    class Config:
        from_attributes = True

class Address(AddressBase):
    address_id: int
    customer_id: int

    class Config:
        from_attributes = True