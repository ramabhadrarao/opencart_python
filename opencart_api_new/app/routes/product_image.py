from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import math
from datetime import datetime
from pydantic import BaseModel  # Add this import

from app.database import get_db
from app.models.product import ProductImage, Product
from app.schemas.product import ProductImageBase
from app.utils.auth import get_current_admin  # Add this import

router = APIRouter(
    prefix="/product-images",
    tags=["product-images"],
    responses={404: {"description": "Product image not found"}},
)

class PaginatedProductImageResponse(BaseModel):
    items: List[ProductImageBase]
    total: int
    page: int
    size: int
    pages: int

@router.get("/", response_model=PaginatedProductImageResponse)
def get_product_images(
    db: Session = Depends(get_db),
    product_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Get list of product images with pagination
    """
    query = db.query(ProductImage)
    
    if product_id:
        query = query.filter(ProductImage.product_id == product_id)
    
    # Count total before pagination
    total = query.count()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 0
    
    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    
    product_images = query.all()
    
    return {
        "items": product_images,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.get("/{product_image_id}", response_model=ProductImageBase)
def get_product_image(product_image_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product image by ID
    """
    product_image = db.query(ProductImage).filter(ProductImage.product_image_id == product_image_id).first()
    
    if not product_image:
        raise HTTPException(status_code=404, detail="Product image not found")
    
    return product_image

@router.post("/", response_model=ProductImageBase)
def create_product_image(
    image_data: ProductImageBase, 
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can create product images
):
    """
    Create a new product image for a specific product (admin only)
    """
    # Verify product exists
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product_image = ProductImage(
        product_id=product_id,
        image=image_data.image,
        sort_order=image_data.sort_order
    )
    
    db.add(db_product_image)
    db.commit()
    db.refresh(db_product_image)
    
    return db_product_image

@router.put("/{product_image_id}", response_model=ProductImageBase)
def update_product_image(
    product_image_id: int, 
    image_data: ProductImageBase, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can update product images
):
    """
    Update a specific product image (admin only)
    """
    db_product_image = db.query(ProductImage).filter(ProductImage.product_image_id == product_image_id).first()
    
    if not db_product_image:
        raise HTTPException(status_code=404, detail="Product image not found")
    
    # Update fields
    if image_data.image is not None:
        db_product_image.image = image_data.image
    
    db_product_image.sort_order = image_data.sort_order
    
    db.commit()
    db.refresh(db_product_image)
    
    return db_product_image

@router.delete("/{product_image_id}", status_code=204)
def delete_product_image(
    product_image_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can delete product images
):
    """
    Delete a specific product image (admin only)
    """
    db_product_image = db.query(ProductImage).filter(ProductImage.product_image_id == product_image_id).first()
    
    if not db_product_image:
        raise HTTPException(status_code=404, detail="Product image not found")
    
    db.delete(db_product_image)
    db.commit()
    
    return None