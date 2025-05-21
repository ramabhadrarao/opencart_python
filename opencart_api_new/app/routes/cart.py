from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid

from app.database import get_db
from app.models.cart import Cart
from app.models.product import Product, ProductDescription
from app.schemas.cart import CartItem, CartItemCreate, CartItemUpdate, CartSummary
from app.utils.auth import get_current_customer, get_current_user

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
    responses={404: {"description": "Item not found"}},
)

def get_user_session_id(
    session_id: Optional[str] = Cookie(None),
    request: Request = None
):
    """Get the user's session ID from cookie or create one if not exists"""
    if not session_id and request:
        session_id = str(uuid.uuid4())
        # Note: we would normally set the cookie here, but that requires access to the response
        # which FastAPI doesn't support in dependencies. This is handled in the tracking middleware.
    return session_id or str(uuid.uuid4())

@router.get("/", response_model=CartSummary)
def get_cart(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the current user's cart
    """
    customer_id = 0
    if current_user and current_user["type"] == "customer":
        customer_id = current_user["user"].customer_id

    cart_items = db.query(Cart).filter(
        (Cart.customer_id == customer_id) if customer_id > 0 else (Cart.session_id == session_id)
    ).all()
    
    result_items = []
    total_price = 0.0
    
    for item in cart_items:
        # Get product info to include in response
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        product_desc = db.query(ProductDescription).filter(
            ProductDescription.product_id == item.product_id,
            ProductDescription.language_id == 1  # Default language
        ).first()
        
        if product and product_desc:
            price = float(product.price)
            total_item_price = price * item.quantity
            total_price += total_item_price
            
            options = {}
            if item.option:
                try:
                    options = json.loads(item.option)
                except:
                    # Handle case where option is not valid JSON
                    pass
            
            result_items.append(CartItem(
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                option=options,
                recurring_id=item.recurring_id,
                date_added=item.date_added,
                product_name=product_desc.name,
                product_image=product.image,
                price=price,
                total=total_item_price
            ))
    
    return CartSummary(
        items=result_items,
        total_items=len(result_items),
        total_price=total_price
    )

@router.post("/items", response_model=CartItem)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Add an item to the cart
    """
    # Check if product exists
    product = db.query(Product).filter(Product.product_id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get customer ID if authenticated
    customer_id = 0
    if current_user and current_user["type"] == "customer":
        customer_id = current_user["user"].customer_id
    
    # Check if item already in cart
    existing_item = db.query(Cart).filter(
        (Cart.customer_id == customer_id) if customer_id > 0 else (Cart.session_id == session_id),
        Cart.product_id == item_data.product_id,
        Cart.option == json.dumps(item_data.option)
    ).first()
    
    if existing_item:
        # Update quantity instead of adding new item
        existing_item.quantity += item_data.quantity
        db.commit()
        db.refresh(existing_item)
        cart_item = existing_item
    else:
        # Add new item to cart
        cart_item = Cart(
            api_id=0,
            customer_id=customer_id,
            session_id=session_id,
            product_id=item_data.product_id,
            recurring_id=item_data.recurring_id,
            option=json.dumps(item_data.option),
            quantity=item_data.quantity,
            date_added=datetime.now()
        )
        
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    
    # Get product description for response
    product_desc = db.query(ProductDescription).filter(
        ProductDescription.product_id == item_data.product_id,
        ProductDescription.language_id == 1  # Default language
    ).first()
    
    # Prepare response
    options = {}
    if cart_item.option:
        try:
            options = json.loads(cart_item.option)
        except:
            pass
    
    return CartItem(
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        option=options,
        recurring_id=cart_item.recurring_id,
        date_added=cart_item.date_added,
        product_name=product_desc.name if product_desc else "",
        product_image=product.image,
        price=float(product.price),
        total=float(product.price) * cart_item.quantity
    )

@router.put("/items/{cart_id}", response_model=CartItem)
def update_cart_item(
    cart_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Update an item in the cart
    """
    # Get customer ID if authenticated
    customer_id = 0
    if current_user and current_user["type"] == "customer":
        customer_id = current_user["user"].customer_id
    
    # Find the cart item
    cart_item = db.query(Cart).filter(
        Cart.cart_id == cart_id,
        (Cart.customer_id == customer_id) if customer_id > 0 else (Cart.session_id == session_id)
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Update fields if provided
    if item_data.quantity is not None:
        cart_item.quantity = item_data.quantity
    
    if item_data.option is not None:
        cart_item.option = json.dumps(item_data.option)
    
    db.commit()
    db.refresh(cart_item)
    
    # Get product info for response
    product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
    product_desc = db.query(ProductDescription).filter(
        ProductDescription.product_id == cart_item.product_id,
        ProductDescription.language_id == 1  # Default language
    ).first()
    
    # Prepare response
    options = {}
    if cart_item.option:
        try:
            options = json.loads(cart_item.option)
        except:
            pass
    
    return CartItem(
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        option=options,
        recurring_id=cart_item.recurring_id,
        date_added=cart_item.date_added,
        product_name=product_desc.name if product_desc else "",
        product_image=product.image if product else None,
        price=float(product.price) if product else 0.0,
        total=float(product.price) * cart_item.quantity if product else 0.0
    )

@router.delete("/items/{cart_id}", status_code=204)
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Remove an item from the cart
    """
    # Get customer ID if authenticated
    customer_id = 0
    if current_user and current_user["type"] == "customer":
        customer_id = current_user["user"].customer_id
    
    # Find the cart item
    cart_item = db.query(Cart).filter(
        Cart.cart_id == cart_id,
        (Cart.customer_id == customer_id) if customer_id > 0 else (Cart.session_id == session_id)
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return None

@router.delete("/", status_code=204)
def clear_cart(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Clear the entire cart
    """
    # Get customer ID if authenticated
    customer_id = 0
    if current_user and current_user["type"] == "customer":
        customer_id = current_user["user"].customer_id
    
    # Delete all items in the cart
    db.query(Cart).filter(
        (Cart.customer_id == customer_id) if customer_id > 0 else (Cart.session_id == session_id)
    ).delete()
    
    db.commit()
    
    return None