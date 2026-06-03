from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    JSON,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    product_type = Column(String, nullable=False, index=True)
    description = Column(String)
    # 12999 -> $129.99 - Avoids floating-point issues
    base_price = Column(Integer, nullable=False)

    # relationship: @OneToMany, @ManyToOne
    # One Product can appear in many Inventory rows
    # eg: Nike Air Max - exists in: Downtown, Eaton Centre, King West
    # back_populates - allows: inventory.product
    inventory = relationship("Inventory", back_populates="product")


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    area = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)

    # One Store contains many Inventory rows
    # back_populates - allows: inventory.store
    inventory = relationship("Inventory", back_populates="store")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    quantity = Column(Integer, nullable=False)
    '''
    JSON type:
    {
        "size":"10",
        "color":"black"
    }
    
    Different products have different properties:
        - { "size":"10", "color":"black" }
        - { "storage_size":"256GB", "color":"blue" }
        - { "material":"fabric", "color":"gray" }
    
    Equivalent:
    
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String,Object> attributes;
    '''
    attributes = Column(JSON, nullable=False, default={})

    product = relationship("Product", back_populates="inventory")
    store = relationship("Store", back_populates="inventory")


class CustomerSearch(Base):
    __tablename__ = "customer_searches"

    id = Column(Integer, primary_key=True)
    searched_product_name = Column(String, nullable=False)
    normalized_product_name = Column(String, nullable=False)
    area = Column(String, nullable=True)
    normalized_area = Column(String, nullable=True)
    product_status = Column(String, nullable=False)
    search_count = Column(Integer, nullable=False, default=1)
    # DateTime: 2026-06-03 12:00:00
    # func: database functions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_searched_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    '''
    __table_args__: extra table configuration
    
    UniqueConstraint("normalized_product_name", "normalized_area")
        - nike shoes + downtown
        - nike shoes + scarborough
    '''
    __table_args__ = (
        # Creates a unique index across multiple columns
        UniqueConstraint(
            "normalized_product_name",
            "normalized_area",
            name="uq_customer_search_product_area",
        ),
    )