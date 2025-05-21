from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import math

from app.database import get_db
from app.models.product import ProductOption, Product
from app.schemas.product import ProductOptionBase
from app.utils.auth import get_current_admin  # Add this import

router = APIRouter(
    prefix="/product-options",
    tags=["product-options"],
    responses={404: {"description": "Product option not found"}},
)

class PaginatedProductOptionResponse(BaseModel):
    items: List[ProductOptionBase]
    total: int
    page: int
    size: int
    pages: int

@router.get("/", response_model=PaginatedProductOptionResponse)
def get_product_options(
    db: Session = Depends(get_db),
    product_id: Optional[int] = None,
    option_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Get list of product options with pagination
    """
    query = db.query(ProductOption)
    
    if product_id:
        query = query.filter(ProductOption.product_id == product_id)
    
    if option_id:
        query = query.filter(ProductOption.option_id == option_id)
    
    # Count total before pagination
    total = query.count()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 0
    
    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    
    product_options = query.all()
    
    return {
        "items": product_options,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.get("/{product_option_id}", response_model=ProductOptionBase)
def get_product_option(product_option_id: int, db: Session = Depends(get_db)):
    """
    Get product option by ID
    """
    product_option = db.query(ProductOption).filter(ProductOption.product_option_id == product_option_id).first()
    
    if not product_option:
        raise HTTPException(status_code=404, detail="Product option not found")
    
    return product_option

@router.post("/", response_model=ProductOptionBase)
def create_product_option(
    option_data: ProductOptionBase, 
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can create product options
):
    """
    Create a new product option for a specific product (admin only)
    """
    # Verify product exists
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product_option = ProductOption(
        product_id=product_id,
        option_id=option_data.option_id,
        value=option_data.value,
        required=option_data.required
    )
    
    db.add(db_product_option)
    db.commit()
    db.refresh(db_product_option)
    
    return db_product_option

@router.put("/{product_option_id}", response_model=ProductOptionBase)
def update_product_option(
    product_option_id: int,
    option_data: ProductOptionBase,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can update product options
):
    """
    Update a specific product option (admin only)
    """
    db_product_option = db.query(ProductOption).filter(ProductOption.product_option_id == product_option_id).first()
    
    if not db_product_option:
        raise HTTPException(status_code=404, detail="Product option not found")
    
    # Update fields
    db_product_option.option_id = option_data.option_id
    db_product_option.value = option_data.value
    db_product_option.required = option_data.required
    
    db.commit()
    db.refresh(db_product_option)
    
    return db_product_option

@router.delete("/{product_option_id}", status_code=204)
def delete_product_option(
    product_option_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can delete product options
):
    """
    Delete a specific product option (admin only)
    """
    db_product_option = db.query(ProductOption).filter(ProductOption.product_option_id == product_option_id).first()
    
    if not db_product_option:
        raise HTTPException(status_code=404, detail="Product option not found")
    
    db.delete(db_product_option)
    db.commit()
    
    return None