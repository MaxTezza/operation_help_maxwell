"""
Product routes for inventory and catalog management
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from database import SessionLocal
from models.product import Product, ProductCategory
from utils.pricing_calculator import PricingCalculator

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

@products_bp.route('/', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    db = get_db()
    try:
        # Query parameters
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        active_only = request.args.get('active', 'true').lower() == 'true'

        query = db.query(Product)

        # Apply filters
        if active_only:
            query = query.filter(Product.is_active == True)

        if category:
            query = query.filter(Product.category == ProductCategory(category))

        if search:
            query = query.filter(
                (Product.name.ilike(f'%{search}%')) |
                (Product.sku.ilike(f'%{search}%')) |
                (Product.description.ilike(f'%{search}%'))
            )

        products = query.order_by(Product.name).all()
        return jsonify([product.to_dict() for product in products]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify(product.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/', methods=['POST'])
def create_product():
    """Create a new product"""
    db = get_db()
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('sku') or not data.get('name') or not data.get('base_cost'):
            return jsonify({'error': 'SKU, name, and base cost are required'}), 400

        # Check if SKU already exists
        existing = db.query(Product).filter(Product.sku == data['sku']).first()
        if existing:
            return jsonify({'error': 'Product with this SKU already exists'}), 400

        # Create new product
        product = Product(
            sku=data['sku'],
            name=data['name'],
            description=data.get('description'),
            category=ProductCategory(data['category']) if data.get('category') else ProductCategory.CUSTOM,
            base_cost=float(data['base_cost']),
            labor_hours=float(data.get('labor_hours', 0.0)),
            overhead_percentage=float(data.get('overhead_percentage', 30.0)),
            stock_quantity=int(data.get('stock_quantity', 0)),
            reorder_level=int(data.get('reorder_level', 10)),
            is_active=data.get('is_active', True),
            allows_logo=data.get('allows_logo', True),
            allows_personalization=data.get('allows_personalization', False),
            customization_cost=float(data.get('customization_cost', 0.0)),
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return jsonify(product.to_dict()), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        data = request.get_json()

        # Update fields
        if 'sku' in data:
            product.sku = data['sku']
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'category' in data:
            product.category = ProductCategory(data['category'])
        if 'base_cost' in data:
            product.base_cost = float(data['base_cost'])
        if 'labor_hours' in data:
            product.labor_hours = float(data['labor_hours'])
        if 'overhead_percentage' in data:
            product.overhead_percentage = float(data['overhead_percentage'])
        if 'stock_quantity' in data:
            product.stock_quantity = int(data['stock_quantity'])
        if 'reorder_level' in data:
            product.reorder_level = int(data['reorder_level'])
        if 'is_active' in data:
            product.is_active = data['is_active']
        if 'allows_logo' in data:
            product.allows_logo = data['allows_logo']
        if 'allows_personalization' in data:
            product.allows_personalization = data['allows_personalization']
        if 'customization_cost' in data:
            product.customization_cost = float(data['customization_cost'])

        db.commit()
        db.refresh(product)

        return jsonify(product.to_dict()), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product (soft delete by marking inactive)"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Soft delete
        product.is_active = False
        db.commit()

        return jsonify({'message': 'Product deactivated successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>/pricing', methods=['POST'])
def calculate_pricing(product_id):
    """Calculate pricing for a product with given quantity"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        data = request.get_json()
        quantity = int(data.get('quantity', 1))
        has_customization = data.get('has_customization', False)

        # Calculate unit price with volume discount
        unit_price = PricingCalculator.calculate_unit_price(
            base_cost=product.base_cost,
            overhead_percentage=product.overhead_percentage,
            quantity=quantity,
            has_customization=has_customization,
            customization_cost=product.customization_cost if has_customization else 0.0
        )

        # Calculate suggested retail price
        suggested_price = PricingCalculator.calculate_suggested_retail_price(
            base_cost=product.base_cost,
            overhead_percentage=product.overhead_percentage,
            target_margin=40.0
        )

        # Get volume discount
        volume_discount = PricingCalculator.get_volume_discount(quantity) * 100

        # Calculate profit margin
        total_cost = product.base_cost * (1 + product.overhead_percentage / 100)
        profit_margin = PricingCalculator.calculate_profit_margin(unit_price, total_cost)

        pricing = {
            'product_id': product_id,
            'product_name': product.name,
            'quantity': quantity,
            'base_cost': product.base_cost,
            'unit_price': unit_price,
            'suggested_retail_price': suggested_price,
            'volume_discount_percentage': volume_discount,
            'line_total': round(unit_price * quantity, 2),
            'profit_margin_percentage': profit_margin,
            'has_customization': has_customization,
        }

        return jsonify(pricing), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/low-stock', methods=['GET'])
def get_low_stock_products():
    """Get products that are at or below reorder level"""
    db = get_db()
    try:
        products = db.query(Product).filter(
            Product.stock_quantity <= Product.reorder_level,
            Product.is_active == True
        ).order_by(Product.stock_quantity).all()

        return jsonify([product.to_dict() for product in products]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    categories = [{'value': cat.value, 'label': cat.value.replace('_', ' ').title()}
                  for cat in ProductCategory]
    return jsonify(categories), 200
