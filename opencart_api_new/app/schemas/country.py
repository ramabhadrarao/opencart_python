from typing import Optional
from pydantic import BaseModel

class CountryBase(BaseModel):
    name: str
    iso_code_2: str
    iso_code_3: str
    address_format: str
    postcode_required: bool
    status: bool

    class Config:
        from_attributes = True

class CountryCreate(CountryBase):
    pass

class CountryUpdate(BaseModel):
    name: Optional[str] = None
    iso_code_2: Optional[str] = None
    iso_code_3: Optional[str] = None
    address_format: Optional[str] = None
    postcode_required: Optional[bool] = None
    status: Optional[bool] = None

    class Config:
        from_attributes = True

class Country(CountryBase):
    country_id: int

    class Config:
        from_attributes = True