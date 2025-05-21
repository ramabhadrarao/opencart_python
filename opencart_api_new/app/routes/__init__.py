from fastapi import APIRouter
from app.routes import ( 
    product, category, customer, order,
     product_image, product_description, product_option, product_option_value,
     auth,address, country, zone, analytics, cart 
)

router = APIRouter()
router.include_router(auth.router)  # Include auth router

router.include_router(product.router)
router.include_router(category.router)
router.include_router(customer.router)
router.include_router(order.router)
router.include_router(product_image.router)
router.include_router(product_description.router)
router.include_router(product_option.router)
router.include_router(product_option_value.router)
router.include_router(address.router)  # Add new router
router.include_router(country.router)  # Add new router
router.include_router(zone.router)     # Add new router
router.include_router(analytics.router)  # Add analytics router
router.include_router(cart.router)       # Add cart router