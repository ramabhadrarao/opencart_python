from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import math

from app.database import get_db
from app.models.product import ProductDescription, Product
from app.schemas.product import ProductDescriptionBase
from app.utils.auth import get_current_admin  # Add this import

router = APIRouter(
    prefix="/product-descriptions",
    tags=["product-descriptions"],
    responses={404: {"description": "Product description not found"}},
)

class PaginatedProductDescriptionResponse(BaseModel):
    items: List[ProductDescriptionBase]
    total: int
    page: int
    size: int
    pages: int

@router.get("/", response_model=PaginatedProductDescriptionResponse)
def get_product_descriptions(
    db: Session = Depends(get_db),
    product_id: Optional[int] = None,
    language_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Get list of product descriptions with pagination
    """
    query = db.query(ProductDescription)
    
    if product_id:
        query = query.filter(ProductDescription.product_id == product_id)
    
    if language_id:
        query = query.filter(ProductDescription.language_id == language_id)
    
    # Count total before pagination
    total = query.count()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 0
    
    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    
    product_descriptions = query.all()
    
    return {
        "items": product_descriptions,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.get("/{product_id}/{language_id}", response_model=ProductDescriptionBase)
def get_product_description(product_id: int, language_id: int, db: Session = Depends(get_db)):
    """
    Get product description by product ID and language ID
    """
    product_description = db.query(ProductDescription).filter(
        ProductDescription.product_id == product_id,
        ProductDescription.language_id == language_id
    ).first()
    
    if not product_description:
        raise HTTPException(status_code=404, detail="Product description not found")
    
    return product_description

@router.post("/", response_model=ProductDescriptionBase)
def create_product_description(
    description_data: ProductDescriptionBase, 
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can create product descriptions
):
    """
    Create a new product description for a specific product (admin only)
    """
    # Verify product exists
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if description already exists
    existing = db.query(ProductDescription).filter(
        ProductDescription.product_id == product_id,
        ProductDescription.language_id == description_data.language_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Description for product ID {product_id} with language ID {description_data.language_id} already exists"
        )
    
    db_product_description = ProductDescription(
        product_id=product_id,
        language_id=description_data.language_id,
        name=description_data.name,
        description=description_data.description,
        tag=description_data.tag,
        meta_title=description_data.meta_title,
        meta_description=description_data.meta_description,
        meta_keyword=description_data.meta_keyword
    )
    
    db.add(db_product_description)
    db.commit()
    db.refresh(db_product_description)
    
    return db_product_description

@router.put("/{product_id}/{language_id}", response_model=ProductDescriptionBase)
def update_product_description(
    product_id: int,
    language_id: int,
    description_data: ProductDescriptionBase,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can update product descriptions
):
    """
    Update a specific product description (admin only)
    """
    db_product_description = db.query(ProductDescription).filter(
        ProductDescription.product_id == product_id,
        ProductDescription.language_id == language_id
    ).first()
    
    if not db_product_description:
        raise HTTPException(status_code=404, detail="Product description not found")
    
    # Update fields
    db_product_description.name = description_data.name
    db_product_description.description = description_data.description
    db_product_description.tag = description_data.tag
    db_product_description.meta_title = description_data.meta_title
    db_product_description.meta_description = description_data.meta_description
    db_product_description.meta_keyword = description_data.meta_keyword
    
    db.commit()
    db.refresh(db_product_description)
    
    return db_product_description

@router.delete("/{product_id}/{language_id}", status_code=204)
def delete_product_description(
    product_id: int,
    language_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can delete product descriptions
):
    """
    Delete a specific product description (admin only)
    """
    db_product_description = db.query(ProductDescription).filter(
        ProductDescription.product_id == product_id,
        ProductDescription.language_id == language_id
    ).first()
    
    if not db_product_description:
        raise HTTPException(status_code=404, detail="Product description not found")
    
    db.delete(db_product_description)
    db.commit()
    
    return None