"""
Order and OrderItem models for order management system
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base
import enum

class OrderStatus(enum.Enum):
    QUOTE = "quote"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False, index=True)

    # Order details
    status = Column(Enum(OrderStatus), default=OrderStatus.QUOTE, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    confirmed_date = Column(DateTime)
    production_start_date = Column(DateTime)
    estimated_completion_date = Column(DateTime)
    ship_date = Column(DateTime)
    delivery_date = Column(DateTime)

    # Shipping information
    shipping_address = Column(Text)
    shipping_city = Column(String(100))
    shipping_state = Column(String(50))
    shipping_zip = Column(String(20))
    shipping_country = Column(String(100), default="USA")
    shipping_cost = Column(Float, default=0.0)

    # Financial
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)

    # Production tracking
    materials_cost = Column(Float, default=0.0)
    labor_hours = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)

    # Notes and special instructions
    notes = Column(Text)
    internal_notes = Column(Text)
    special_instructions = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, number={self.order_number}, status={self.status})>"

    def generate_order_number(self):
        """Generate unique order number"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"TW-{timestamp}"

    def calculate_totals(self):
        """Calculate order totals from items"""
        self.subtotal = sum(item.line_total for item in self.items)

        # Apply discount
        self.discount_amount = self.subtotal * (self.discount_percentage / 100)
        subtotal_after_discount = self.subtotal - self.discount_amount

        # Calculate tax
        self.tax_amount = subtotal_after_discount * (self.tax_rate / 100)

        # Calculate total
        self.total_amount = subtotal_after_discount + self.tax_amount + self.shipping_cost

        # Calculate costs
        self.materials_cost = sum(item.total_cost for item in self.items)
        self.labor_hours = sum(item.labor_hours for item in self.items)
        self.labor_cost = self.labor_hours * 25.0  # $25/hour default labor rate
        self.overhead_cost = sum(item.overhead_cost for item in self.items)
        self.total_cost = self.materials_cost + self.labor_cost + self.overhead_cost

        # Calculate profit margin
        if self.total_amount > 0:
            self.profit_margin = ((self.total_amount - self.total_cost) / self.total_amount) * 100

    def estimate_completion_date(self):
        """Estimate completion date based on production time"""
        if self.production_start_date:
            # Calculate total production days (1 item per day + 2 days buffer)
            total_items = sum(item.quantity for item in self.items)
            production_days = (total_items // 10) + 2  # 10 items per day capacity
            self.estimated_completion_date = self.production_start_date + timedelta(days=production_days)

    def update_status(self, new_status):
        """Update order status and set relevant dates"""
        self.status = new_status
        now = datetime.utcnow()

        if new_status == OrderStatus.CONFIRMED and not self.confirmed_date:
            self.confirmed_date = now
        elif new_status == OrderStatus.IN_PRODUCTION and not self.production_start_date:
            self.production_start_date = now
            self.estimate_completion_date()
        elif new_status == OrderStatus.SHIPPED and not self.ship_date:
            self.ship_date = now
        elif new_status == OrderStatus.DELIVERED and not self.delivery_date:
            self.delivery_date = now

    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'client_id': self.client_id,
            'status': self.status.value if self.status else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'confirmed_date': self.confirmed_date.isoformat() if self.confirmed_date else None,
            'production_start_date': self.production_start_date.isoformat() if self.production_start_date else None,
            'estimated_completion_date': self.estimated_completion_date.isoformat() if self.estimated_completion_date else None,
            'ship_date': self.ship_date.isoformat() if self.ship_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_state': self.shipping_state,
            'shipping_zip': self.shipping_zip,
            'shipping_country': self.shipping_country,
            'shipping_cost': self.shipping_cost,
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'discount_percentage': self.discount_percentage,
            'discount_amount': self.discount_amount,
            'materials_cost': self.materials_cost,
            'labor_hours': self.labor_hours,
            'labor_cost': self.labor_cost,
            'overhead_cost': self.overhead_cost,
            'total_cost': self.total_cost,
            'profit_margin': self.profit_margin,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'special_instructions': self.special_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)

    # Item details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

    # Customization
    has_logo = Column(Boolean, default=False)
    logo_details = Column(Text)
    has_personalization = Column(Boolean, default=False)
    personalization_details = Column(Text)
    customization_cost = Column(Float, default=0.0)

    # Cost tracking
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    labor_hours = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)

    # Production notes
    production_notes = Column(Text)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"

    def calculate_line_total(self):
        """Calculate line total with customization costs"""
        base_total = self.unit_price * self.quantity
        customization_total = self.customization_cost * self.quantity
        self.line_total = base_total + customization_total

    def calculate_costs(self, product):
        """Calculate costs based on product"""
        self.unit_cost = product.base_cost
        self.total_cost = self.unit_cost * self.quantity
        self.labor_hours = product.labor_hours * self.quantity
        self.overhead_cost = self.total_cost * (product.overhead_percentage / 100)

        # Add customization labor if applicable
        if self.has_logo or self.has_personalization:
            self.labor_hours += 0.25 * self.quantity  # 15 minutes per item

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'line_total': self.line_total,
            'has_logo': self.has_logo,
            'logo_details': self.logo_details,
            'has_personalization': self.has_personalization,
            'personalization_details': self.personalization_details,
            'customization_cost': self.customization_cost,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost,
            'labor_hours': self.labor_hours,
            'overhead_cost': self.overhead_cost,
            'production_notes': self.production_notes,
        }
