"""
Seed script to populate database with sample data for testing
"""
from database import SessionLocal
from models.client import Client, ClientInteraction, AcquisitionSource
from models.product import Product, ProductCategory
from models.order import Order, OrderItem, OrderStatus
from datetime import datetime, timedelta
import random

def seed_data(db):
    """Populate database with sample data"""
    try:
        print("Seeding clients...")
        clients = [
            Client(
                company_name="TechCorp Solutions",
                contact_person="John Smith",
                email="john@techcorp.com",
                phone="555-0101",
                address="123 Tech Street",
                city="San Francisco",
                state="CA",
                zip_code="94102",
                industry="Technology",
                acquisition_source=AcquisitionSource.WEBSITE,
                notes="Large tech company, interested in bulk orders"
            ),
            Client(
                company_name="Marketing Pros LLC",
                contact_person="Sarah Johnson",
                email="sarah@marketingpros.com",
                phone="555-0102",
                address="456 Marketing Ave",
                city="New York",
                state="NY",
                zip_code="10001",
                industry="Marketing",
                acquisition_source=AcquisitionSource.REFERRAL,
                notes="Referred by previous client"
            ),
            Client(
                company_name="Global Enterprises",
                contact_person="Michael Chen",
                email="michael@globalent.com",
                phone="555-0103",
                address="789 Enterprise Blvd",
                city="Chicago",
                state="IL",
                zip_code="60601",
                industry="Finance",
                acquisition_source=AcquisitionSource.TRADE_SHOW,
                notes="Met at industry conference"
            ),
            Client(
                company_name="StartUp Innovators",
                contact_person="Emily Davis",
                email="emily@startupinnovators.com",
                phone="555-0104",
                address="321 Innovation Way",
                city="Austin",
                state="TX",
                zip_code="78701",
                industry="Technology",
                acquisition_source=AcquisitionSource.SOCIAL_MEDIA,
                notes="Found us on LinkedIn"
            ),
            Client(
                company_name="Healthcare Plus",
                contact_person="Dr. Robert Williams",
                email="robert@healthcareplus.com",
                phone="555-0105",
                address="555 Medical Center Dr",
                city="Boston",
                state="MA",
                zip_code="02101",
                industry="Healthcare",
                acquisition_source=AcquisitionSource.COLD_OUTREACH,
                notes="Large healthcare provider"
            )
        ]

        for client in clients:
            db.add(client)

        db.commit()
        print(f"Created {len(clients)} clients")

        print("Seeding products...")
        products = [
            Product(
                sku="MUG-001",
                name="Ceramic Coffee Mug",
                description="High-quality ceramic mug, 11oz capacity",
                category=ProductCategory.DRINKWARE,
                base_cost=3.50,
                labor_hours=0.25,
                overhead_percentage=30.0,
                stock_quantity=500,
                reorder_level=50,
                allows_logo=True,
                allows_personalization=True,
                customization_cost=2.00
            ),
            Product(
                sku="TSHIRT-001",
                name="Cotton T-Shirt",
                description="100% cotton, various sizes",
                category=ProductCategory.APPAREL,
                base_cost=5.00,
                labor_hours=0.5,
                overhead_percentage=30.0,
                stock_quantity=300,
                reorder_level=30,
                allows_logo=True,
                allows_personalization=False,
                customization_cost=3.50
            ),
            Product(
                sku="PEN-001",
                name="Premium Ballpoint Pen",
                description="Metal body, smooth ink flow",
                category=ProductCategory.OFFICE_SUPPLIES,
                base_cost=1.50,
                labor_hours=0.1,
                overhead_percentage=30.0,
                stock_quantity=1000,
                reorder_level=100,
                allows_logo=True,
                allows_personalization=True,
                customization_cost=1.00
            ),
            Product(
                sku="BAG-001",
                name="Tote Bag",
                description="Canvas tote bag, eco-friendly",
                category=ProductCategory.BAGS,
                base_cost=4.00,
                labor_hours=0.3,
                overhead_percentage=30.0,
                stock_quantity=200,
                reorder_level=20,
                allows_logo=True,
                allows_personalization=False,
                customization_cost=2.50
            ),
            Product(
                sku="BOTTLE-001",
                name="Stainless Steel Water Bottle",
                description="24oz insulated water bottle",
                category=ProductCategory.DRINKWARE,
                base_cost=8.00,
                labor_hours=0.2,
                overhead_percentage=30.0,
                stock_quantity=150,
                reorder_level=15,
                allows_logo=True,
                allows_personalization=True,
                customization_cost=3.00
            ),
            Product(
                sku="USB-001",
                name="USB Flash Drive 16GB",
                description="16GB USB 3.0 flash drive",
                category=ProductCategory.TECH_ACCESSORIES,
                base_cost=6.00,
                labor_hours=0.15,
                overhead_percentage=30.0,
                stock_quantity=400,
                reorder_level=40,
                allows_logo=True,
                allows_personalization=False,
                customization_cost=2.00
            ),
            Product(
                sku="NOTE-001",
                name="Premium Notebook",
                description="Hardcover notebook, 100 pages",
                category=ProductCategory.OFFICE_SUPPLIES,
                base_cost=3.00,
                labor_hours=0.2,
                overhead_percentage=30.0,
                stock_quantity=250,
                reorder_level=25,
                allows_logo=True,
                allows_personalization=True,
                customization_cost=1.50
            ),
            Product(
                sku="MASK-001",
                name="Wellness Kit",
                description="Hand sanitizer, mask, and tissues",
                category=ProductCategory.WELLNESS,
                base_cost=7.50,
                labor_hours=0.3,
                overhead_percentage=30.0,
                stock_quantity=180,
                reorder_level=20,
                allows_logo=True,
                allows_personalization=False,
                customization_cost=2.00
            )
        ]

        for product in products:
            db.add(product)

        db.commit()
        print(f"Created {len(products)} products")

        print("Seeding orders...")
        # Create sample orders with different statuses
        order_data = [
            {
                'client_idx': 0,
                'status': OrderStatus.QUOTE,
                'items': [(0, 50, True, False), (2, 100, True, True)],  # (product_idx, qty, logo, personalization)
                'days_ago': 2
            },
            {
                'client_idx': 1,
                'status': OrderStatus.CONFIRMED,
                'items': [(1, 30, True, False), (3, 50, True, False)],
                'days_ago': 5
            },
            {
                'client_idx': 2,
                'status': OrderStatus.IN_PRODUCTION,
                'items': [(4, .75, True, True), (6, 75, True, False)],
                'days_ago': 10
            },
            {
                'client_idx': 3,
                'status': OrderStatus.SHIPPED,
                'items': [(5, 100, True, False), (7, 50, True, False)],
                'days_ago': 15
            },
            {
                'client_idx': 4,
                'status': OrderStatus.DELIVERED,
                'items': [(0, 200, True, True), (1, 100, True, False), (2, 200, True, False)],
                'days_ago': 30
            }
        ]

        for idx, order_info in enumerate(order_data):
            client = clients[order_info['client_idx']]
            order_date = datetime.utcnow() - timedelta(days=order_info['days_ago'])

            order = Order(
                client_id=client.id,
                status=order_info['status'],
                order_date=order_date,
                shipping_address=client.address,
                shipping_city=client.city,
                shipping_state=client.state,
                shipping_zip=client.zip_code,
                shipping_cost=25.00,
                tax_rate=8.5,
                discount_percentage=0.0,
                notes=f"Sample order for {client.company_name}",
                special_instructions="Please ensure logo is centered"
            )

            order.order_number = f"TW-{datetime.utcnow().strftime('%Y%m%d')}{1000 + idx}"

            # Add order items
            for product_idx, qty, has_logo, has_personalization in order_info['items']:
                product = products[product_idx]

                # Calculate pricing
                from utils.pricing_calculator import PricingCalculator
                has_customization = has_logo or has_personalization
                unit_price = PricingCalculator.calculate_unit_price(
                    base_cost=product.base_cost,
                    overhead_percentage=product.overhead_percentage,
                    quantity=qty,
                    has_customization=has_customization,
                    customization_cost=product.customization_cost if has_customization else 0.0
                )

                order_item = OrderItem(
                    product_id=product.id,
                    quantity=qty,
                    unit_price=unit_price,
                    has_logo=has_logo,
                    logo_details="Company logo" if has_logo else None,
                    has_personalization=has_personalization,
                    personalization_details="Employee names" if has_personalization else None,
                    customization_cost=product.customization_cost if has_customization else 0.0
                )

                order_item.calculate_costs(product)
                order_item.calculate_line_total()
                order.items.append(order_item)

            # Calculate order totals
            order.calculate_totals()

            # Set dates based on status
            if order.status in [OrderStatus.CONFIRMED, OrderStatus.IN_PRODUCTION, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                order.confirmed_date = order_date + timedelta(days=1)

            if order.status in [OrderStatus.IN_PRODUCTION, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                order.production_start_date = order.confirmed_date + timedelta(days=2)
                order.estimate_completion_date()

            if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                order.ship_date = order.production_start_date + timedelta(days=7)

            if order.status == OrderStatus.DELIVERED:
                order.delivery_date = order.ship_date + timedelta(days=3)

            db.add(order)

        db.commit()
        print(f"Created {len(order_data)} orders")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
