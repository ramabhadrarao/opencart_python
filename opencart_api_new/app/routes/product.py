from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from datetime import datetime

from app.database import get_db
from app.models.product import Product, ProductDescription, ProductImage, ProductToCategory, ProductSpecification, ProductOption
from app.schemas.product import ProductInList, ProductDetail, ProductCreate, ProductUpdate
from app.utils.auth import get_current_admin, get_current_user  # Add this import

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Product not found"}},
)

@router.get("/", response_model=List[ProductInList])
def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: Optional[bool] = None,
):
    """
    Get list of products with optional filtering
    """
    query = db.query(Product).join(
        ProductDescription, 
        Product.product_id == ProductDescription.product_id
    )
    
    if search:
        query = query.filter(
            or_(
                ProductDescription.name.ilike(f"%{search}%"),
                Product.model.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.join(
            ProductToCategory,
            Product.product_id == ProductToCategory.product_id
        ).filter(ProductToCategory.category_id == category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if status is not None:
        query = query.filter(Product.status == status)
    
    products = query.offset(skip).limit(limit).all()
    
    result = []
    for product in products:
        if product.descriptions:
            description = product.descriptions[0]  # Get first description (usually default language)
            result.append({
                "product_id": product.product_id,
                "model": product.model,
                "name": description.name,
                "price": product.price,
                "quantity": product.quantity,
                "status": product.status,
                "image": product.image,
            })
    
    return result

@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific product
    """
    product = db.query(Product).options(
        joinedload(Product.descriptions),
        joinedload(Product.images),
        joinedload(Product.product_options).joinedload(ProductOption.option_values),
        joinedload(Product.attributes),
        joinedload(Product.specifications)
    ).filter(Product.product_id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.post("/", response_model=ProductDetail, status_code=201)
def create_product(
    product_data: ProductCreate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can create products
):
    """
    Create a new product (admin only)
    """
    # Create new product
    new_product = Product(
        model=product_data.model,
        sku=product_data.sku,
        upc=product_data.upc,
        ean=product_data.ean,
        jan=product_data.jan,
        isbn=product_data.isbn,
        mpn=product_data.mpn,
        location=product_data.location,
        quantity=product_data.quantity,
        stock_status_id=product_data.stock_status_id,
        image=product_data.image,
        manufacturer_id=product_data.manufacturer_id,
        shipping=product_data.shipping,
        price=product_data.price,
        points=product_data.points,
        tax_class_id=product_data.tax_class_id,
        date_available=product_data.date_available,
        weight=product_data.weight,
        weight_class_id=product_data.weight_class_id,
        length=product_data.length,
        width=product_data.width,
        height=product_data.height,
        length_class_id=product_data.length_class_id,
        subtract=product_data.subtract,
        minimum=product_data.minimum,
        sort_order=product_data.sort_order,
        status=product_data.status,
        date_added=datetime.now(),
        date_modified=datetime.now()
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Add descriptions
    for desc in product_data.descriptions:
        db.add(ProductDescription(
            product_id=new_product.product_id,
            language_id=desc.language_id,
            name=desc.name,
            description=desc.description,
            tag=desc.tag,
            meta_title=desc.meta_title,
            meta_description=desc.meta_description,
            meta_keyword=desc.meta_keyword
        ))
    
    # Add images
    for img in product_data.images:
        db.add(ProductImage(
            product_id=new_product.product_id,
            image=img.image,
            sort_order=img.sort_order
        ))
    
    # Add categories
    for category_id in product_data.categories:
        db.add(ProductToCategory(
            product_id=new_product.product_id,
            category_id=category_id
        ))
    
    # Add specifications
    for spec in product_data.specifications:
        db.add(ProductSpecification(
            product_id=str(new_product.product_id),
            machine_name=spec.machine_name,
            price=spec.price,
            image=spec.image,
            date=datetime.now()
        ))
    
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.put("/{product_id}", response_model=ProductDetail)
def update_product(
    product_id: int, 
    product_data: ProductUpdate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can update products
):
    """
    Update a product (admin only)
    """
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product fields if provided
    if product_data.model is not None:
        product.model = product_data.model
    if product_data.sku is not None:
        product.sku = product_data.sku
    if product_data.image is not None:
        product.image = product_data.image
    if product_data.quantity is not None:
        product.quantity = product_data.quantity
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.status is not None:
        product.status = product_data.status
    
    product.date_modified = datetime.now()
    
    # Update descriptions if provided
    if product_data.descriptions:
        # Delete existing descriptions
        db.query(ProductDescription).filter(
            ProductDescription.product_id == product_id
        ).delete()
        
        # Add new descriptions
        for desc in product_data.descriptions:
            db.add(ProductDescription(
                product_id=product_id,
                language_id=desc.language_id,
                name=desc.name,
                description=desc.description,
                tag=desc.tag,
                meta_title=desc.meta_title,
                meta_description=desc.meta_description,
                meta_keyword=desc.meta_keyword
            ))
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can delete products
):
    """
    Delete a product (admin only)
    """
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete related records in other tables
    db.query(ProductDescription).filter(ProductDescription.product_id == product_id).delete()
    db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
    db.query(ProductToCategory).filter(ProductToCategory.product_id == product_id).delete()
    db.query(ProductSpecification).filter(ProductSpecification.product_id == str(product_id)).delete()
    
    # Delete the product itself
    db.delete(product)
    db.commit()
    
    return None