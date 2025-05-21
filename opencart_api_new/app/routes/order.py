from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.database import get_db
from app.models.order import Order, OrderProduct, OrderHistory
from app.schemas.order import OrderInList, OrderDetail, OrderCreate, OrderUpdate
from app.utils.auth import get_current_admin, get_current_customer, get_current_user  # Add this import

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Order not found"}},
)

@router.get("/", response_model=List[OrderInList])
def get_orders(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_admin = Depends(get_current_admin)  # Only admin can view all orders
):
    """
    Get list of all orders (admin only)
    """
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@router.get("/my-orders", response_model=List[OrderInList])
def get_my_orders(
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer),  # Get current customer
    skip: int = 0,
    limit: int = 100
):
    """
    Get list of orders for the current customer
    """
    orders = db.query(Order).filter(Order.customer_id == current_customer.customer_id).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderDetail)
def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Either customer or admin
):
    """
    Get detailed information about a specific order
    (Customers can only view their own orders, admin can view any order)
    """
    order = db.query(Order).options(
        joinedload(Order.products),
        joinedload(Order.history)
    ).filter(Order.order_id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # If user is a customer, verify they own this order
    if current_user["type"] == "customer" and order.customer_id != current_user["user"].customer_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@router.post("/", response_model=OrderDetail, status_code=201)
def create_order(
    order_data: OrderCreate, 
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)  # Only authenticated customers can create orders
):
    """
    Create a new order (authenticated customers only)
    """
    # Ensure the customer can only create orders for themselves
    if order_data.customer_id != current_customer.customer_id:
        raise HTTPException(status_code=403, detail="Cannot create orders for other customers")
    
    # In a real implementation, you'd generate a proper invoice prefix
    new_order = Order(
        invoice_no=0,
        invoice_prefix="INV",
        store_id=0,
        store_name="Default Store",
        store_url="http://localhost/",
        customer_id=current_customer.customer_id,  # Use the authenticated customer ID
        customer_group_id=current_customer.customer_group_id,
        firstname=order_data.firstname,
        lastname=order_data.lastname,
        email=current_customer.email,  # Use the authenticated customer email
        telephone=order_data.telephone,
        fax="",
        custom_field="",
        payment_firstname=order_data.payment_firstname,
        payment_lastname=order_data.payment_lastname,
        payment_company="",
        payment_address_1=order_data.payment_address_1,
        payment_address_2="",
        payment_city=order_data.payment_city,
        payment_postcode=order_data.payment_postcode,
        payment_country=order_data.payment_country,
        payment_country_id=0,
        payment_zone="",
        payment_zone_id=0,
        payment_address_format="",
        payment_custom_field="",
        payment_method=order_data.payment_method,
        payment_code=order_data.payment_code,
        shipping_firstname=order_data.shipping_firstname,
        shipping_lastname=order_data.shipping_lastname,
        shipping_company="",
        shipping_address_1=order_data.shipping_address_1,
        shipping_address_2="",
        shipping_city=order_data.shipping_city,
        shipping_postcode=order_data.shipping_postcode,
        shipping_country=order_data.shipping_country,
        shipping_country_id=0,
        shipping_zone="",
        shipping_zone_id=0,
        shipping_address_format="",
        shipping_custom_field="",
        shipping_method=order_data.shipping_method,
        shipping_code=order_data.shipping_code,
        comment=order_data.comment,
        total=sum(p.price * p.quantity for p in order_data.products),
        order_status_id=1,  # Pending
        affiliate_id=0,
        commission=0,
        marketing_id=0,
        tracking="",
        language_id=1,
        currency_id=1,
        currency_code="USD",
        currency_value=1.0,
        ip="",
        forwarded_ip="",
        user_agent="",
        accept_language="",
        date_added=datetime.now(),
        date_modified=datetime.now()
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Add order products
    for product in order_data.products:
        db.add(OrderProduct(
            order_id=new_order.order_id,
            product_id=product.product_id,
            name=product.name,
            model=product.model,
            quantity=product.quantity,
            price=product.price,
            total=product.price * product.quantity,
            tax=product.tax,
            reward=product.reward
        ))
    
    # Add initial order history
    db.add(OrderHistory(
        order_id=new_order.order_id,
        order_status_id=1,  # Pending
        notify=False,
        comment="Order created",
        date_added=datetime.now()
    ))
    
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.put("/{order_id}", response_model=OrderDetail)
def update_order(
    order_id: int, 
    order_data: OrderUpdate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admin can update order status
):
    """
    Update an order's status (admin only)
    """
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status if provided
    if order_data.order_status_id is not None:
        order.order_status_id = order_data.order_status_id
    
    order.date_modified = datetime.now()
    
    # Add order history entry
    db.add(OrderHistory(
        order_id=order_id,
        order_status_id=order_data.order_status_id or order.order_status_id,
        notify=False,
        comment=order_data.comment or "Status updated",
        date_added=datetime.now()
    ))
    
    db.commit()
    db.refresh(order)
    
    return order