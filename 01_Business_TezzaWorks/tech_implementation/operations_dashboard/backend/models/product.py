"""
Product model for inventory and catalog management
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class ProductCategory(enum.Enum):
    APPAREL = "apparel"
    DRINKWARE = "drinkware"
    TECH_ACCESSORIES = "tech_accessories"
    OFFICE_SUPPLIES = "office_supplies"
    BAGS = "bags"
    WELLNESS = "wellness"
    OUTDOOR = "outdoor"
    CUSTOM = "custom"

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(ProductCategory), nullable=False)

    # Pricing
    base_cost = Column(Float, nullable=False)  # Material cost
    labor_hours = Column(Float, default=0.0)  # Hours needed for production
    overhead_percentage = Column(Float, default=30.0)  # Overhead allocation percentage

    # Inventory
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)

    # Customization options
    allows_logo = Column(Boolean, default=True)
    allows_personalization = Column(Boolean, default=False)
    customization_cost = Column(Float, default=0.0)  # Additional cost per item

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"

    def calculate_unit_price(self, quantity=1, include_customization=False):
        """Calculate price per unit based on quantity and customization"""
        # Base cost + overhead
        base_price = self.base_cost * (1 + self.overhead_percentage / 100)

        # Volume discount tiers
        if quantity >= 500:
            discount = 0.25  # 25% discount
        elif quantity >= 101:
            discount = 0.15  # 15% discount
        elif quantity >= 26:
            discount = 0.10  # 10% discount
        elif quantity >= 1:
            discount = 0.0   # No discount
        else:
            discount = 0.0

        discounted_price = base_price * (1 - discount)

        # Add customization cost if applicable
        if include_customization:
            discounted_price += self.customization_cost

        return round(discounted_price, 2)

    def calculate_profit_margin(self, selling_price):
        """Calculate profit margin percentage"""
        total_cost = self.base_cost * (1 + self.overhead_percentage / 100)
        if selling_price > 0:
            margin = ((selling_price - total_cost) / selling_price) * 100
            return round(margin, 2)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'base_cost': self.base_cost,
            'labor_hours': self.labor_hours,
            'overhead_percentage': self.overhead_percentage,
            'stock_quantity': self.stock_quantity,
            'reorder_level': self.reorder_level,
            'is_active': self.is_active,
            'allows_logo': self.allows_logo,
            'allows_personalization': self.allows_personalization,
            'customization_cost': self.customization_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
