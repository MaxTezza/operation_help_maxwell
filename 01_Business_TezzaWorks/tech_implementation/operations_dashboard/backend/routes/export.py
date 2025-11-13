"""
Export routes for generating reports and data exports
"""
from flask import Blueprint, request, send_file, jsonify
from sqlalchemy.orm import Session
from database import SessionLocal
from models.order import Order, OrderItem
from models.client import Client
from models.product import Product
from datetime import datetime
import io
import csv

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

@export_bp.route('/orders', methods=['GET'])
def export_orders():
    """Export orders to CSV"""
    db = get_db()
    try:
        # Get filters from query parameters
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = db.query(Order)

        # Apply filters
        if status:
            from models.order import OrderStatus
            query = query.filter(Order.status == OrderStatus(status))
        if start_date:
            query = query.filter(Order.order_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Order.order_date <= datetime.fromisoformat(end_date))

        orders = query.all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Order Number',
            'Client',
            'Status',
            'Order Date',
            'Subtotal',
            'Tax',
            'Shipping',
            'Total Amount',
            'Profit Margin %',
            'Materials Cost',
            'Labor Hours',
            'Total Cost'
        ])

        # Write data
        for order in orders:
            writer.writerow([
                order.order_number,
                order.client.company_name if order.client else '',
                order.status.value if order.status else '',
                order.order_date.strftime('%Y-%m-%d') if order.order_date else '',
                f"${order.subtotal:.2f}" if order.subtotal else '$0.00',
                f"${order.tax_amount:.2f}" if order.tax_amount else '$0.00',
                f"${order.shipping_cost:.2f}" if order.shipping_cost else '$0.00',
                f"${order.total_amount:.2f}" if order.total_amount else '$0.00',
                f"{order.profit_margin:.1f}%" if order.profit_margin else '0.0%',
                f"${order.materials_cost:.2f}" if order.materials_cost else '$0.00',
                f"{order.labor_hours:.2f}" if order.labor_hours else '0.00',
                f"${order.total_cost:.2f}" if order.total_cost else '$0.00',
            ])

        # Prepare file for download
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tezzaworks_orders_{timestamp}.csv'

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@export_bp.route('/clients', methods=['GET'])
def export_clients():
    """Export clients to CSV"""
    db = get_db()
    try:
        clients = db.query(Client).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Company Name',
            'Contact Person',
            'Email',
            'Phone',
            'Address',
            'City',
            'State',
            'ZIP',
            'Country',
            'Industry',
            'Acquisition Source',
            'Created Date'
        ])

        # Write data
        for client in clients:
            writer.writerow([
                client.company_name,
                client.contact_person,
                client.email,
                client.phone or '',
                client.address or '',
                client.city or '',
                client.state or '',
                client.zip_code or '',
                client.country or '',
                client.industry or '',
                client.acquisition_source.value if client.acquisition_source else '',
                client.created_at.strftime('%Y-%m-%d') if client.created_at else ''
            ])

        # Prepare file for download
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tezzaworks_clients_{timestamp}.csv'

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@export_bp.route('/products', methods=['GET'])
def export_products():
    """Export products to CSV"""
    db = get_db()
    try:
        products = db.query(Product).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'SKU',
            'Name',
            'Category',
            'Description',
            'Base Cost',
            'Labor Hours',
            'Overhead %',
            'Stock Quantity',
            'Reorder Level',
            'Allows Logo',
            'Allows Personalization',
            'Customization Cost',
            'Active'
        ])

        # Write data
        for product in products:
            writer.writerow([
                product.sku,
                product.name,
                product.category.value if product.category else '',
                product.description or '',
                f"${product.base_cost:.2f}",
                f"{product.labor_hours:.2f}",
                f"{product.overhead_percentage:.1f}%",
                product.stock_quantity,
                product.reorder_level,
                'Yes' if product.allows_logo else 'No',
                'Yes' if product.allows_personalization else 'No',
                f"${product.customization_cost:.2f}",
                'Active' if product.is_active else 'Inactive'
            ])

        # Prepare file for download
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tezzaworks_products_{timestamp}.csv'

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@export_bp.route('/order-details/<int:order_id>', methods=['GET'])
def export_order_details(order_id):
    """Export detailed order information to CSV"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Order header information
        writer.writerow(['Order Information'])
        writer.writerow(['Order Number', order.order_number])
        writer.writerow(['Client', order.client.company_name if order.client else ''])
        writer.writerow(['Status', order.status.value if order.status else ''])
        writer.writerow(['Order Date', order.order_date.strftime('%Y-%m-%d') if order.order_date else ''])
        writer.writerow([])

        # Order items
        writer.writerow(['Order Items'])
        writer.writerow(['Product', 'SKU', 'Quantity', 'Unit Price', 'Line Total', 'Customization'])

        for item in order.items:
            customization = []
            if item.has_logo:
                customization.append('Logo')
            if item.has_personalization:
                customization.append('Personalization')

            writer.writerow([
                item.product.name if item.product else '',
                item.product.sku if item.product else '',
                item.quantity,
                f"${item.unit_price:.2f}",
                f"${item.line_total:.2f}",
                ', '.join(customization) if customization else 'None'
            ])

        writer.writerow([])

        # Order totals
        writer.writerow(['Order Totals'])
        writer.writerow(['Subtotal', f"${order.subtotal:.2f}"])
        writer.writerow(['Discount', f"-${order.discount_amount:.2f}"])
        writer.writerow(['Tax', f"${order.tax_amount:.2f}"])
        writer.writerow(['Shipping', f"${order.shipping_cost:.2f}"])
        writer.writerow(['Total', f"${order.total_amount:.2f}"])
        writer.writerow([])

        # Cost breakdown
        writer.writerow(['Cost Breakdown'])
        writer.writerow(['Materials Cost', f"${order.materials_cost:.2f}"])
        writer.writerow(['Labor Hours', f"{order.labor_hours:.2f}"])
        writer.writerow(['Labor Cost', f"${order.labor_cost:.2f}"])
        writer.writerow(['Overhead Cost', f"${order.overhead_cost:.2f}"])
        writer.writerow(['Total Cost', f"${order.total_cost:.2f}"])
        writer.writerow(['Profit Margin', f"{order.profit_margin:.1f}%"])

        # Prepare file for download
        output.seek(0)
        filename = f'order_{order.order_number}_{datetime.now().strftime("%Y%m%d")}.csv'

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
