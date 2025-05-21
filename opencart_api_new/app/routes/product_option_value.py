from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import math

from app.database import get_db
from app.models.product import ProductOptionValue, ProductOption
from app.schemas.product import ProductOptionValueBase
from app.utils.auth import get_current_admin  # Add this import

router = APIRouter(
    prefix="/product-option-values",
    tags=["product-option-values"],
    responses={404: {"description": "Product option value not found"}},
)

class PaginatedProductOptionValueResponse(BaseModel):
    items: List[ProductOptionValueBase]
    total: int
    page: int
    size: int
    pages: int

@router.get("/", response_model=PaginatedProductOptionValueResponse)
def get_product_option_values(
    db: Session = Depends(get_db),
    product_option_id: Optional[int] = None,
    product_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Get list of product option values with pagination
    """
    query = db.query(ProductOptionValue)
    
    if product_option_id:
        query = query.filter(ProductOptionValue.product_option_id == product_option_id)
    
    if product_id:
        query = query.filter(ProductOptionValue.product_id == product_id)
    
    # Count total before pagination
    total = query.count()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 0
    
    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    
    product_option_values = query.all()
    
    return {
        "items": product_option_values,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.get("/{product_option_value_id}", response_model=ProductOptionValueBase)
def get_product_option_value(product_option_value_id: int, db: Session = Depends(get_db)):
    """
    Get product option value by ID
    """
    product_option_value = db.query(ProductOptionValue).filter(
        ProductOptionValue.product_option_value_id == product_option_value_id
    ).first()
    
    if not product_option_value:
        raise HTTPException(status_code=404, detail="Product option value not found")
    
    return product_option_value

@router.post("/", response_model=ProductOptionValueBase)
def create_product_option_value(
    option_value_data: ProductOptionValueBase, 
    product_option_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can create product option values
):
    """
    Create a new product option value for a specific product option (admin only)
    """
    # Verify product option exists
    product_option = db.query(ProductOption).filter(ProductOption.product_option_id == product_option_id).first()
    if not product_option:
        raise HTTPException(status_code=404, detail="Product option not found")
    
    db_product_option_value = ProductOptionValue(
        product_option_id=product_option_id,
        product_id=product_option.product_id,
        option_id=option_value_data.option_id,
        option_value_id=option_value_data.option_value_id,
        quantity=option_value_data.quantity,
        subtract=option_value_data.subtract,
        uploaded_files="",
        price=option_value_data.price,
        price_prefix=option_value_data.price_prefix,
        points=option_value_data.points,
        points_prefix=option_value_data.points_prefix,
        weight=option_value_data.weight,
        weight_prefix=option_value_data.weight_prefix
    )
    
    db.add(db_product_option_value)
    db.commit()
    db.refresh(db_product_option_value)
    
    return db_product_option_value

@router.put("/{product_option_value_id}", response_model=ProductOptionValueBase)
def update_product_option_value(
    product_option_value_id: int,
    option_value_data: ProductOptionValueBase,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can update product option values
):
    """
    Update a specific product option value (admin only)
    """
    db_product_option_value = db.query(ProductOptionValue).filter(
        ProductOptionValue.product_option_value_id == product_option_value_id
    ).first()
    
    if not db_product_option_value:
        raise HTTPException(status_code=404, detail="Product option value not found")
    
    # Update fields
    db_product_option_value.option_id = option_value_data.option_id
    db_product_option_value.option_value_id = option_value_data.option_value_id
    db_product_option_value.quantity = option_value_data.quantity
    db_product_option_value.subtract = option_value_data.subtract
    db_product_option_value.price = option_value_data.price
    db_product_option_value.price_prefix = option_value_data.price_prefix
    db_product_option_value.points = option_value_data.points
    db_product_option_value.points_prefix = option_value_data.points_prefix
    db_product_option_value.weight = option_value_data.weight
    db_product_option_value.weight_prefix = option_value_data.weight_prefix
    
    db.commit()
    db.refresh(db_product_option_value)
    
    return db_product_option_value

@router.delete("/{product_option_value_id}", status_code=204)
def delete_product_option_value(
    product_option_value_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can delete product option values
):
    """
    Delete a specific product option value (admin only)
    """
    db_product_option_value = db.query(ProductOptionValue).filter(
        ProductOptionValue.product_option_value_id == product_option_value_id
    ).first()
    
    if not db_product_option_value:
        raise HTTPException(status_code=404, detail="Product option value not found")
    
    db.delete(db_product_option_value)
    db.commit()
    
    return None