"""
Order routes for order management system
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import SessionLocal
from models.order import Order, OrderItem, OrderStatus
from models.product import Product
from models.client import Client
from utils.pricing_calculator import PricingCalculator
from datetime import datetime, timedelta

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

@orders_bp.route('/', methods=['GET'])
def get_orders():
    """Get all orders with optional filtering"""
    db = get_db()
    try:
        # Query parameters
        status = request.args.get('status', '')
        client_id = request.args.get('client_id', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')

        query = db.query(Order)

        # Apply filters
        if status:
            query = query.filter(Order.status == OrderStatus(status))

        if client_id:
            query = query.filter(Order.client_id == int(client_id))

        if start_date:
            query = query.filter(Order.order_date >= datetime.fromisoformat(start_date))

        if end_date:
            query = query.filter(Order.order_date <= datetime.fromisoformat(end_date))

        orders = query.order_by(Order.created_at.desc()).all()

        # Include client info in response
        result = []
        for order in orders:
            order_dict = order.to_dict(include_items=False)
            if order.client:
                order_dict['client_name'] = order.client.company_name
                order_dict['client_contact'] = order.client.contact_person
            result.append(order_dict)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID with full details"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        order_dict = order.to_dict(include_items=True)

        # Add client info
        if order.client:
            order_dict['client'] = order.client.to_dict()

        # Add product info to items
        for i, item in enumerate(order.items):
            if item.product:
                order_dict['items'][i]['product'] = item.product.to_dict()

        return jsonify(order_dict), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/', methods=['POST'])
def create_order():
    """Create a new order"""
    db = get_db()
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('client_id') or not data.get('items'):
            return jsonify({'error': 'Client ID and items are required'}), 400

        # Verify client exists
        client = db.query(Client).filter(Client.id == data['client_id']).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        # Create order
        order = Order(
            client_id=data['client_id'],
            status=OrderStatus(data.get('status', 'quote')),
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes'),
            special_instructions=data.get('special_instructions'),
            shipping_address=data.get('shipping_address'),
            shipping_city=data.get('shipping_city'),
            shipping_state=data.get('shipping_state'),
            shipping_zip=data.get('shipping_zip'),
            shipping_country=data.get('shipping_country', 'USA'),
            shipping_cost=float(data.get('shipping_cost', 0.0)),
            tax_rate=float(data.get('tax_rate', 8.5)),
            discount_percentage=float(data.get('discount_percentage', 0.0)),
        )

        # Generate order number
        order.order_number = order.generate_order_number()

        # Add items
        for item_data in data['items']:
            product = db.query(Product).filter(Product.id == item_data['product_id']).first()
            if not product:
                return jsonify({'error': f"Product {item_data['product_id']} not found"}), 404

            # Calculate pricing
            quantity = int(item_data['quantity'])
            has_customization = item_data.get('has_logo', False) or item_data.get('has_personalization', False)

            unit_price = PricingCalculator.calculate_unit_price(
                base_cost=product.base_cost,
                overhead_percentage=product.overhead_percentage,
                quantity=quantity,
                has_customization=has_customization,
                customization_cost=product.customization_cost if has_customization else 0.0
            )

            # Create order item
            order_item = OrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                has_logo=item_data.get('has_logo', False),
                logo_details=item_data.get('logo_details'),
                has_personalization=item_data.get('has_personalization', False),
                personalization_details=item_data.get('personalization_details'),
                customization_cost=product.customization_cost if has_customization else 0.0,
                production_notes=item_data.get('production_notes'),
            )

            # Calculate costs
            order_item.calculate_costs(product)
            order_item.calculate_line_total()

            order.items.append(order_item)

        # Calculate order totals
        order.calculate_totals()

        db.add(order)
        db.commit()
        db.refresh(order)

        return jsonify(order.to_dict(include_items=True)), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        data = request.get_json()

        # Update basic fields
        if 'notes' in data:
            order.notes = data['notes']
        if 'internal_notes' in data:
            order.internal_notes = data['internal_notes']
        if 'special_instructions' in data:
            order.special_instructions = data['special_instructions']
        if 'shipping_address' in data:
            order.shipping_address = data['shipping_address']
        if 'shipping_city' in data:
            order.shipping_city = data['shipping_city']
        if 'shipping_state' in data:
            order.shipping_state = data['shipping_state']
        if 'shipping_zip' in data:
            order.shipping_zip = data['shipping_zip']
        if 'shipping_cost' in data:
            order.shipping_cost = float(data['shipping_cost'])
        if 'discount_percentage' in data:
            order.discount_percentage = float(data['discount_percentage'])

        # Recalculate if needed
        if 'shipping_cost' in data or 'discount_percentage' in data:
            order.calculate_totals()

        db.commit()
        db.refresh(order)

        return jsonify(order.to_dict(include_items=True)), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'Status is required'}), 400

        order.update_status(OrderStatus(new_status))
        db.commit()
        db.refresh(order)

        return jsonify(order.to_dict(include_items=False)), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        db.delete(order)
        db.commit()

        return jsonify({'message': 'Order deleted successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/kanban', methods=['GET'])
def get_kanban_board():
    """Get orders organized by status for kanban view"""
    db = get_db()
    try:
        orders = db.query(Order).filter(
            Order.status.in_([
                OrderStatus.QUOTE,
                OrderStatus.CONFIRMED,
                OrderStatus.IN_PRODUCTION,
                OrderStatus.SHIPPED
            ])
        ).all()

        kanban = {
            'quote': [],
            'confirmed': [],
            'in_production': [],
            'shipped': [],
        }

        for order in orders:
            order_dict = order.to_dict(include_items=False)
            if order.client:
                order_dict['client_name'] = order.client.company_name
            kanban[order.status.value].append(order_dict)

        return jsonify(kanban), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get order analytics and key metrics"""
    db = get_db()
    try:
        # Date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = db.query(Order)

        if start_date:
            query = query.filter(Order.order_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Order.order_date <= datetime.fromisoformat(end_date))

        orders = query.all()

        # Calculate metrics
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Revenue by status
        revenue_by_status = {}
        orders_by_status = {}
        for order in orders:
            status = order.status.value
            revenue_by_status[status] = revenue_by_status.get(status, 0) + order.total_amount
            orders_by_status[status] = orders_by_status.get(status, 0) + 1

        # Top products
        from sqlalchemy import func
        top_products = db.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.line_total).label('total_revenue')
        ).join(OrderItem).join(Order).filter(
            Order.order_date >= datetime.fromisoformat(start_date) if start_date else True,
            Order.order_date <= datetime.fromisoformat(end_date) if end_date else True
        ).group_by(Product.name).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()

        # Monthly revenue trend (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_revenue = db.query(
            extract('year', Order.order_date).label('year'),
            extract('month', Order.order_date).label('month'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.order_date >= six_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()

        analytics = {
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(avg_order_value, 2),
            'revenue_by_status': {k: round(v, 2) for k, v in revenue_by_status.items()},
            'orders_by_status': orders_by_status,
            'top_products': [
                {
                    'name': p.name,
                    'quantity': int(p.total_quantity),
                    'revenue': round(float(p.total_revenue), 2)
                }
                for p in top_products
            ],
            'monthly_revenue': [
                {
                    'year': int(m.year),
                    'month': int(m.month),
                    'revenue': round(float(m.revenue), 2)
                }
                for m in monthly_revenue
            ]
        }

        return jsonify(analytics), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@orders_bp.route('/quote', methods=['POST'])
def generate_quote():
    """Generate a quote without creating an order"""
    try:
        data = request.get_json()

        if not data.get('items'):
            return jsonify({'error': 'Items are required'}), 400

        # Prepare items for pricing calculator
        items = []
        db = get_db()

        for item_data in data['items']:
            product = db.query(Product).filter(Product.id == item_data['product_id']).first()
            if not product:
                db.close()
                return jsonify({'error': f"Product {item_data['product_id']} not found"}), 404

            has_logo = item_data.get('has_logo', False)
            has_personalization = item_data.get('has_personalization', False)

            items.append({
                'name': product.name,
                'base_cost': product.base_cost,
                'overhead_percentage': product.overhead_percentage,
                'labor_hours': product.labor_hours,
                'quantity': item_data['quantity'],
                'has_logo': has_logo,
                'has_personalization': has_personalization,
                'customization_cost': product.customization_cost if (has_logo or has_personalization) else 0.0,
            })

        db.close()

        # Generate quote
        quote = PricingCalculator.generate_quote(
            items=items,
            discount_percentage=float(data.get('discount_percentage', 0.0)),
            tax_rate=float(data.get('tax_rate', 8.5)),
            shipping_cost=float(data.get('shipping_cost', 0.0))
        )

        return jsonify(quote), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
