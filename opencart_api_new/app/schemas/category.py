from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Base category schemas
class CategoryDescriptionBase(BaseModel):
    language_id: int
    name: str
    description: str
    meta_title: str
    meta_description: str
    meta_keyword: str
    
    class Config:
        from_attributes = True

# Category Request Models
class CategoryCreate(BaseModel):
    parent_id: int = 0
    top: bool = False
    column: int = 1
    sort_order: int = 0
    status: bool = True
    image: Optional[str] = None
    descriptions: List[CategoryDescriptionBase]
    
    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    parent_id: Optional[int] = None
    status: Optional[bool] = None
    sort_order: Optional[int] = None
    image: Optional[str] = None
    descriptions: Optional[List[CategoryDescriptionBase]] = None
    
    class Config:
        from_attributes = True

# Category Response Models
class CategoryInList(BaseModel):
    category_id: int
    name: str
    parent_id: int
    sort_order: int
    status: bool
    
    class Config:
        from_attributes = True

class CategoryDetail(BaseModel):
    category_id: int
    parent_id: int
    top: bool
    column: int
    sort_order: int
    status: bool
    image: Optional[str] = None
    date_added: datetime
    date_modified: datetime
    descriptions: List[CategoryDescriptionBase]
    
    class Config:
        from_attributes = True