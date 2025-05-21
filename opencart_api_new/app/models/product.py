from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "oc_product"

    product_id = Column(Integer, primary_key=True, index=True)
    model = Column(String(64), nullable=False)
    sku = Column(String(100), nullable=False)
    upc = Column(String(100), nullable=False)
    ean = Column(String(100), nullable=False)
    jan = Column(String(100), nullable=False)
    isbn = Column(String(17), nullable=False)
    mpn = Column(String(64), nullable=False)
    location = Column(String(128), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    stock_status_id = Column(Integer, nullable=False)
    image = Column(String(255))
    manufacturer_id = Column(Integer, nullable=False)
    shipping = Column(Boolean, nullable=False, default=True)
    price = Column(Float, nullable=False, default=0.0)
    points = Column(Integer, nullable=False, default=0)
    tax_class_id = Column(Integer, nullable=False)
    date_available = Column(DateTime)
    weight = Column(Float, nullable=False, default=0.0)
    weight_class_id = Column(Integer, nullable=False, default=0)
    length = Column(Float, nullable=False, default=0.0)
    width = Column(Float, nullable=False, default=0.0)
    height = Column(Float, nullable=False, default=0.0)
    length_class_id = Column(Integer, nullable=False, default=0)
    subtract = Column(Boolean, nullable=False, default=True)
    minimum = Column(Integer, nullable=False, default=1)
    sort_order = Column(Integer, nullable=False, default=0)
    status = Column(Boolean, nullable=False, default=False)
    viewed = Column(Integer, nullable=False, default=0)
    date_added = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)

    # Relationships
    descriptions = relationship("ProductDescription", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    categories = relationship("ProductToCategory", back_populates="product")
    product_options = relationship("ProductOption", back_populates="product")
    attributes = relationship("ProductAttribute", back_populates="product")
    discounts = relationship("ProductDiscount", back_populates="product")
    specials = relationship("ProductSpecial", back_populates="product")
    filters = relationship("ProductFilter", back_populates="product")
    related_as_source = relationship("ProductRelated", 
                                    foreign_keys="ProductRelated.product_id",
                                    back_populates="source_product")
    related_as_target = relationship("ProductRelated", 
                                    foreign_keys="ProductRelated.related_id", 
                                    back_populates="related_product")

    # Also from the custom tables
    specifications = relationship("ProductSpecification", back_populates="product")


class ProductDescription(Base):
    __tablename__ = "oc_product_description"

    product_id = Column(Integer, ForeignKey("oc_product.product_id"), primary_key=True)
    language_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    tag = Column(Text, nullable=False)
    meta_title = Column(String(255), nullable=False)
    meta_description = Column(String(255), nullable=False)
    meta_keyword = Column(String(255), nullable=False)

    # Relationship
    product = relationship("Product", back_populates="descriptions")


class ProductImage(Base):
    __tablename__ = "oc_product_image"

    product_image_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("oc_product.product_id"), nullable=False)
    image = Column(String(255))
    sort_order = Column(Integer, nullable=False, default=0)

    # Relationship
    product = relationship("Product", back_populates="images")


class ProductOption(Base):
    __tablename__ = "oc_product_option"

    product_option_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("oc_product.product_id"), nullable=False)
    option_id = Column(Integer, nullable=False)
    value = Column(Text, nullable=False)
    required = Column(Boolean, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="product_options")
    option_values = relationship("ProductOptionValue", back_populates="product_option")


class ProductOptionValue(Base):
    __tablename__ = "oc_product_option_value"

    product_option_value_id = Column(Integer, primary_key=True, index=True)
    product_option_id = Column(Integer, ForeignKey("oc_product_option.product_option_id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    option_id = Column(Integer, nullable=False)
    option_value_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtract = Column(Boolean, nullable=False)
    uploaded_files = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    price_prefix = Column(String(1), nullable=False)
    points = Column(Integer, nullable=False)
    points_prefix = Column(String(1), nullable=False)
    weight = Column(Float, nullable=False)
    weight_prefix = Column(String(1), nullable=False)

    # Relationship
    product_option = relationship("ProductOption", back_populates="option_values")


class ProductAttribute(Base):
    __tablename__ = "oc_product_attribute"

    product_id = Column(Integer, ForeignKey("oc_product.product_id"), primary_key=True)
    attribute_id = Column(Integer, primary_key=True)
    language_id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)

    # Relationship
    product = relationship("Product", back_populates="attributes")


class ProductDiscount(Base):
    __tablename__ = "oc_product_discount"

    product_discount_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("oc_product.product_id"), nullable=False)
    customer_group_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    priority = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False, default=0.0)
    date_start = Column(DateTime)
    date_end = Column(DateTime)

    # Relationship
    product = relationship("Product", back_populates="discounts")


class ProductSpecial(Base):
    __tablename__ = "oc_product_special"

    product_special_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("oc_product.product_id"), nullable=False)
    customer_group_id = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False, default=0.0)
    date_start = Column(DateTime)
    date_end = Column(DateTime)

    # Relationship
    product = relationship("Product", back_populates="specials")


class ProductFilter(Base):
    __tablename__ = "oc_product_filter"

    product_id = Column(Integer, ForeignKey("oc_product.product_id"), primary_key=True)
    filter_id = Column(Integer, primary_key=True)

    # Relationship
    product = relationship("Product", back_populates="filters")


class ProductRelated(Base):
    __tablename__ = "oc_product_related"

    product_id = Column(Integer, ForeignKey("oc_product.product_id"), primary_key=True)
    related_id = Column(Integer, ForeignKey("oc_product.product_id"), primary_key=True)

    # Relationships
    source_product = relationship("Product", foreign_keys=[product_id], back_populates="related_as_source")
    related_product = relationship("Product", foreign_keys=[related_id], back_populates="related_as_target")


class ProductToCategory(Base):
    __tablename__ = "oc_product_to_category"

    product_id = Column(Integer, ForeignKey("oc_product.product_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("oc_category.category_id"), primary_key=True)

    # Relationships
    product = relationship("Product", back_populates="categories")
    category = relationship("Category", back_populates="products")


# Custom table for product specifications
class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    product_specification_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(11), ForeignKey("oc_product.product_id"), nullable=False)
    machine_name = Column(Text, nullable=False)
    price = Column(String(5), nullable=False)
    image = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)

    # Relationship
    product = relationship("Product", back_populates="specifications")


# Additional table from the custom setup
class AddProduct(Base):
    __tablename__ = "addproduct"

    product_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, nullable=False)
    productname = Column(String(30), nullable=False)
    product_image = Column(Text, nullable=False)
    product_image2 = Column(Text, nullable=False)
    product_image3 = Column(Text, nullable=False)
    code = Column(String(10), nullable=False)
    design_specification = Column(Text, nullable=False)
    stitches = Column(String(30), nullable=False)
    area_height_width = Column(Text, nullable=False)
    colour_needles = Column(Text, nullable=False)
    concept = Column(Text, nullable=False)
    publish_status = Column(String(10), nullable=False)
    product_price = Column(String(5), nullable=False)
    discount = Column(String(2), nullable=False)
    status = Column(String(1), nullable=False)
    date = Column(DateTime, nullable=False)