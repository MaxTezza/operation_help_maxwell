"""
Client routes for CRM functionality
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from database import SessionLocal
from models.client import Client, ClientInteraction, AcquisitionSource
from datetime import datetime

clients_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, close in route functions

@clients_bp.route('/', methods=['GET'])
def get_clients():
    """Get all clients with optional filtering"""
    db = get_db()
    try:
        # Query parameters for filtering
        search = request.args.get('search', '')
        source = request.args.get('source', '')

        query = db.query(Client)

        # Apply filters
        if search:
            query = query.filter(
                (Client.company_name.ilike(f'%{search}%')) |
                (Client.contact_person.ilike(f'%{search}%')) |
                (Client.email.ilike(f'%{search}%'))
            )

        if source:
            query = query.filter(Client.acquisition_source == AcquisitionSource(source))

        clients = query.order_by(Client.created_at.desc()).all()
        return jsonify([client.to_dict() for client in clients]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client by ID"""
    db = get_db()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        return jsonify(client.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/', methods=['POST'])
def create_client():
    """Create a new client"""
    db = get_db()
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('company_name') or not data.get('email'):
            return jsonify({'error': 'Company name and email are required'}), 400

        # Check if email already exists
        existing = db.query(Client).filter(Client.email == data['email']).first()
        if existing:
            return jsonify({'error': 'Client with this email already exists'}), 400

        # Create new client
        client = Client(
            company_name=data['company_name'],
            contact_person=data.get('contact_person', ''),
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            country=data.get('country', 'USA'),
            industry=data.get('industry'),
            acquisition_source=AcquisitionSource(data['acquisition_source']) if data.get('acquisition_source') else AcquisitionSource.OTHER,
            preferences=data.get('preferences'),
            notes=data.get('notes'),
        )

        db.add(client)
        db.commit()
        db.refresh(client)

        return jsonify(client.to_dict()), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update an existing client"""
    db = get_db()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        data = request.get_json()

        # Update fields
        if 'company_name' in data:
            client.company_name = data['company_name']
        if 'contact_person' in data:
            client.contact_person = data['contact_person']
        if 'email' in data:
            client.email = data['email']
        if 'phone' in data:
            client.phone = data['phone']
        if 'address' in data:
            client.address = data['address']
        if 'city' in data:
            client.city = data['city']
        if 'state' in data:
            client.state = data['state']
        if 'zip_code' in data:
            client.zip_code = data['zip_code']
        if 'country' in data:
            client.country = data['country']
        if 'industry' in data:
            client.industry = data['industry']
        if 'acquisition_source' in data:
            client.acquisition_source = AcquisitionSource(data['acquisition_source'])
        if 'preferences' in data:
            client.preferences = data['preferences']
        if 'notes' in data:
            client.notes = data['notes']
        if 'next_follow_up' in data:
            client.next_follow_up = datetime.fromisoformat(data['next_follow_up'])

        db.commit()
        db.refresh(client)

        return jsonify(client.to_dict()), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client"""
    db = get_db()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        db.delete(client)
        db.commit()

        return jsonify({'message': 'Client deleted successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/<int:client_id>/interactions', methods=['GET'])
def get_client_interactions(client_id):
    """Get all interactions for a client"""
    db = get_db()
    try:
        interactions = db.query(ClientInteraction).filter(
            ClientInteraction.client_id == client_id
        ).order_by(ClientInteraction.interaction_date.desc()).all()

        return jsonify([interaction.to_dict() for interaction in interactions]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/<int:client_id>/interactions', methods=['POST'])
def create_interaction(client_id):
    """Create a new interaction for a client"""
    db = get_db()
    try:
        # Verify client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        data = request.get_json()

        interaction = ClientInteraction(
            client_id=client_id,
            interaction_type=data.get('interaction_type'),
            subject=data.get('subject'),
            notes=data.get('notes'),
            created_by=data.get('created_by'),
            interaction_date=datetime.fromisoformat(data['interaction_date']) if data.get('interaction_date') else datetime.utcnow()
        )

        # Update client's last contact date
        client.last_contact_date = interaction.interaction_date

        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return jsonify(interaction.to_dict()), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@clients_bp.route('/<int:client_id>/stats', methods=['GET'])
def get_client_stats(client_id):
    """Get statistics for a client"""
    db = get_db()
    try:
        from models.order import Order, OrderStatus

        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        # Get order statistics
        orders = db.query(Order).filter(Order.client_id == client_id).all()

        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Orders by status
        orders_by_status = {}
        for order in orders:
            status = order.status.value
            orders_by_status[status] = orders_by_status.get(status, 0) + 1

        stats = {
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(avg_order_value, 2),
            'orders_by_status': orders_by_status,
            'last_order_date': max([o.order_date for o in orders]).isoformat() if orders else None,
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
