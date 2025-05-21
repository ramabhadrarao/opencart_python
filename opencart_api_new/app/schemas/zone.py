from typing import Optional
from pydantic import BaseModel

class ZoneBase(BaseModel):
    country_id: int
    name: str
    code: str
    status: bool

    class Config:
        from_attributes = True

class ZoneCreate(ZoneBase):
    pass

class ZoneUpdate(BaseModel):
    country_id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[bool] = None

    class Config:
        from_attributes = True

class Zone(ZoneBase):
    zone_id: int

    class Config:
        from_attributes = True