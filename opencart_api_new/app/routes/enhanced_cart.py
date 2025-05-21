from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import uuid

from app.database import get_db
from app.models.enhanced_cart import EnhancedCart, CartHistory, AbandonedCart
from app.models.product import Product, ProductDescription
from app.schemas.enhanced_cart import EnhancedCart as EnhancedCartSchema
from app.schemas.enhanced_cart import EnhancedCartCreate, EnhancedCartUpdate
from app.utils.auth import get_current_customer, get_current_user

router = APIRouter(
    prefix="/cart/v2",
    tags=["enhanced-cart"],
    responses={404: {"description": "Item not found"}},
)

def get_user_session_id(
    session_id: Optional[str] = Cookie(None),
    request: Request = None
):
    """Get the user's session ID from cookie or create one if not exists"""
    if not session_id and request:
        session_id = str(uuid.uuid4())
    return session_id or str(uuid.uuid4())

@router.get("/", response_model=Dict[str, Any])
def get_cart(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user),
    include_saved: bool = False
):
    """
    Get the current user's cart with enhanced details
    """
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id

    # Build query for cart items
    query = db.query(EnhancedCart)
    
    if customer_id:
        query = query.filter(EnhancedCart.customer_id == customer_id)
    else:
        query = query.filter(EnhancedCart.session_id == session_id)
    
    # Filter by saved state if not including saved items
    if not include_saved:
        query = query.filter(EnhancedCart.saved_for_later == False)
    
    cart_items = query.all()
    
    active_items = []
    saved_items = []
    total_price = 0.0
    
    for item in cart_items:
        # Get product info
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        product_desc = db.query(ProductDescription).filter(
            ProductDescription.product_id == item.product_id,
            ProductDescription.language_id == 1  # Default language
        ).first()
        
        if product and product_desc:
            total_item_price = item.price * item.quantity
            
            # Parse options
            options = {}
            if item.options:
                try:
                    options = json.loads(item.options)
                except:
                    pass
            
            cart_item = {
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "product_name": product_desc.name,
                "product_image": product.image,
                "quantity": item.quantity,
                "price": item.price,
                "options": options,
                "total": total_item_price,
                "saved_for_later": item.saved_for_later,
                "notes": item.notes,
                "date_added": item.date_added
            }
            
            if item.saved_for_later:
                saved_items.append(cart_item)
            else:
                active_items.append(cart_item)
                total_price += total_item_price
    
    return {
        "cart": {
            "items": active_items,
            "total_items": len(active_items),
            "total_price": total_price,
            "saved_items": saved_items if include_saved else None,
            "total_saved_items": len(saved_items) if include_saved else 0
        }
    }

@router.post("/items", response_model=Dict[str, Any])
def add_to_cart(
    item_data: EnhancedCartCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Add an item to the enhanced cart
    """
    # Check if product exists
    product = db.query(Product).filter(Product.product_id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get customer ID if authenticated
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id
    
    # Check if item already in cart
    existing_item = None
    
    if customer_id:
        existing_item = db.query(EnhancedCart).filter(
            EnhancedCart.customer_id == customer_id,
            EnhancedCart.product_id == item_data.product_id,
            EnhancedCart.options == item_data.options,
            EnhancedCart.saved_for_later == item_data.saved_for_later
        ).first()
    else:
        existing_item = db.query(EnhancedCart).filter(
            EnhancedCart.session_id == session_id,
            EnhancedCart.product_id == item_data.product_id,
            EnhancedCart.options == item_data.options,
            EnhancedCart.saved_for_later == item_data.saved_for_later
        ).first()
    
    if existing_item:
        # Record history before update
        history = CartHistory(
            cart_id=existing_item.cart_id,
            session_id=session_id,
            customer_id=customer_id,
            product_id=item_data.product_id,
            action="update",
            quantity_before=existing_item.quantity,
            quantity_after=existing_item.quantity + item_data.quantity
        )
        db.add(history)
        
        # Update quantity instead of adding new item
        existing_item.quantity += item_data.quantity
        existing_item.last_updated = datetime.utcnow()
        if item_data.notes:
            existing_item.notes = item_data.notes
        
        db.commit()
        db.refresh(existing_item)
        cart_item = existing_item
    else:
        # Add new item to cart
        cart_item = EnhancedCart(
            session_id=session_id,
            customer_id=customer_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            options=item_data.options,
            price=item_data.price or float(product.price),
            saved_for_later=item_data.saved_for_later,
            source=item_data.source,
            notes=item_data.notes,
            date_added=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        
        # Record history
        history = CartHistory(
            cart_id=cart_item.cart_id,
            session_id=session_id,
            customer_id=customer_id,
            product_id=item_data.product_id,
            action="add",
            quantity_before=0,
            quantity_after=item_data.quantity
        )
        db.add(history)
        db.commit()
    
    # Get product description for response
    product_desc = db.query(ProductDescription).filter(
        ProductDescription.product_id == item_data.product_id,
        ProductDescription.language_id == 1  # Default language
    ).first()
    
    # Parse options
    options = {}
    if cart_item.options:
        try:
            options = json.loads(cart_item.options)
        except:
            pass
    
    # Prepare response
    result = {
        "cart_item": {
            "cart_id": cart_item.cart_id,
            "product_id": cart_item.product_id,
            "product_name": product_desc.name if product_desc else "",
            "product_image": product.image,
            "quantity": cart_item.quantity,
            "price": cart_item.price,
            "options": options,
            "total": cart_item.price * cart_item.quantity,
            "saved_for_later": cart_item.saved_for_later,
            "notes": cart_item.notes,
            "date_added": cart_item.date_added
        }
    }
    
    return result

@router.put("/items/{cart_id}", response_model=Dict[str, Any])
def update_cart_item(
    cart_id: int,
    item_data: EnhancedCartUpdate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Update an item in the enhanced cart
    """
    # Get customer ID if authenticated
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id
    
    # Find the cart item
    cart_item = None
    if customer_id:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.customer_id == customer_id
        ).first()
    else:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.session_id == session_id
        ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Record history before update
    history = CartHistory(
        cart_id=cart_item.cart_id,
        session_id=session_id,
        customer_id=customer_id,
        product_id=cart_item.product_id,
        action="update",
        quantity_before=cart_item.quantity,
        quantity_after=item_data.quantity if item_data.quantity is not None else cart_item.quantity
    )
    db.add(history)
    
    # Update fields if provided
    if item_data.quantity is not None:
        cart_item.quantity = item_data.quantity
    
    if item_data.options is not None:
        cart_item.options = item_data.options
    
    if item_data.saved_for_later is not None:
        cart_item.saved_for_later = item_data.saved_for_later
    
    if item_data.notes is not None:
        cart_item.notes = item_data.notes
    
    cart_item.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(cart_item)
    
    # Get product info
    product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
    product_desc = None
    if product:
        product_desc = db.query(ProductDescription).filter(
            ProductDescription.product_id == cart_item.product_id,
            ProductDescription.language_id == 1  # Default language
        ).first()
    
    # Parse options
    options = {}
    if cart_item.options:
        try:
            options = json.loads(cart_item.options)
        except:
            pass
    
    # Prepare response
    result = {
        "cart_item": {
            "cart_id": cart_item.cart_id,
            "product_id": cart_item.product_id,
            "product_name": product_desc.name if product_desc else "",
            "product_image": product.image if product else None,
            "quantity": cart_item.quantity,
            "price": cart_item.price,
            "options": options,
            "total": cart_item.price * cart_item.quantity,
            "saved_for_later": cart_item.saved_for_later,
            "notes": cart_item.notes,
            "date_added": cart_item.date_added
        }
    }
    
    return result

@router.delete("/items/{cart_id}", status_code=200)
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Remove an item from the enhanced cart
    """
    # Get customer ID if authenticated
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id
    
    # Find the cart item
    cart_item = None
    if customer_id:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.customer_id == customer_id
        ).first()
    else:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.session_id == session_id
        ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Record history before delete
    history = CartHistory(
        cart_id=cart_item.cart_id,
        session_id=session_id,
        customer_id=customer_id,
        product_id=cart_item.product_id,
        action="remove",
        quantity_before=cart_item.quantity,
        quantity_after=0
    )
    db.add(history)
    
    product_id = cart_item.product_id
    
    # Delete the cart item
    db.delete(cart_item)
    db.commit()
    
    return {"success": True, "message": f"Item {product_id} removed from cart"}

@router.delete("/", status_code=200)
def clear_cart(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user),
    include_saved: bool = False
):
    """
    Clear all items from the enhanced cart
    """
    # Get customer ID if authenticated
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id
    
    # Build base query
    query = db.query(EnhancedCart)
    
    if customer_id:
        query = query.filter(EnhancedCart.customer_id == customer_id)
    else:
        query = query.filter(EnhancedCart.session_id == session_id)
    
    # Exclude saved items if flag is set
    if not include_saved:
        query = query.filter(EnhancedCart.saved_for_later == False)
    
    # Get items before deleting for history
    items = query.all()
    
    # Record history for each item
    for item in items:
        history = CartHistory(
            cart_id=item.cart_id,
            session_id=session_id,
            customer_id=customer_id,
            product_id=item.product_id,
            action="remove",
            quantity_before=item.quantity,
            quantity_after=0
        )
        db.add(history)
    
    # Delete items
    count = query.delete()
    db.commit()
    
    return {"success": True, "message": f"Cart cleared, {count} items removed"}

@router.post("/save-for-later/{cart_id}", status_code=200)
def save_for_later(
    cart_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Save an item for later (move from cart to saved items)
    """
    # Get customer ID if authenticated
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id
    
    # Find the cart item
    cart_item = None
    if customer_id:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.customer_id == customer_id
        ).first()
    else:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.session_id == session_id
        ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Update the item
    cart_item.saved_for_later = True
    cart_item.last_updated = datetime.utcnow()
    
    # Record history
    history = CartHistory(
        cart_id=cart_item.cart_id,
        session_id=session_id,
        customer_id=customer_id,
        product_id=cart_item.product_id,
        action="save_for_later",
        quantity_before=cart_item.quantity,
        quantity_after=cart_item.quantity
    )
    db.add(history)
    
    db.commit()
    
    return {"success": True, "message": "Item saved for later"}

@router.post("/move-to-cart/{cart_id}", status_code=200)
def move_to_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_user_session_id),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Move an item from saved to active cart
    """
    # Get customer ID if authenticated
    customer_id = None
    if current_user and current_user.get("type") == "customer":
        customer_id = current_user["user"].customer_id
    
    # Find the saved item
    cart_item = None
    if customer_id:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.customer_id == customer_id,
            EnhancedCart.saved_for_later == True
        ).first()
    else:
        cart_item = db.query(EnhancedCart).filter(
            EnhancedCart.cart_id == cart_id,
            EnhancedCart.session_id == session_id,
            EnhancedCart.saved_for_later == True
        ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Saved item not found")
    
    # Update the item
    cart_item.saved_for_later = False
    cart_item.last_updated = datetime.utcnow()
    
    # Record history
    history = CartHistory(
        cart_id=cart_item.cart_id,
        session_id=session_id,
        customer_id=customer_id,
        product_id=cart_item.product_id,
        action="move_to_cart",
        quantity_before=cart_item.quantity,
        quantity_after=cart_item.quantity
    )
    db.add(history)
    
    db.commit()
    
    return {"success": True, "message": "Item moved to cart"}