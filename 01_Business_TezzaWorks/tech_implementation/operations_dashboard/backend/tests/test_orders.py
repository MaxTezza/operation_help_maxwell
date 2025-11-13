def test_get_orders(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/orders/' endpoint is requested (GET)
    THEN check that the response is valid and contains the expected number of orders
    """
    response = seeded_client.get('/api/orders/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 5

def test_create_order(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/orders/' endpoint is requested (POST) with valid data
    THEN check that a new order is created and the response is valid
    """
    # Get a client and a product to create an order
    clients_response = seeded_client.get('/api/clients/')
    client_id = clients_response.json[0]['id']
    products_response = seeded_client.get('/api/products/')
    product_id = products_response.json[0]['id']

    new_order_data = {
        "client_id": client_id,
        "items": [
            {
                "product_id": product_id,
                "quantity": 10
            }
        ]
    }
    response = seeded_client.post('/api/orders/', json=new_order_data)
    assert response.status_code == 201
    
    response_data = response.json
    assert response_data["client_id"] == new_order_data["client_id"]
    assert len(response_data["items"]) == 1
    assert response_data["items"][0]["product_id"] == new_order_data["items"][0]["product_id"]
    
    # Verify the order was actually created
    get_response = seeded_client.get(f'/api/orders/{response_data["id"]}')
    assert get_response.status_code == 200
    assert get_response.json["client_id"] == new_order_data["client_id"]

def test_get_order(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/orders/<id>' endpoint is requested (GET) for an existing order
    THEN check that the response is valid and contains the correct order data
    """
    # Get the first order from the list of all orders
    response = seeded_client.get('/api/orders/')
    first_order_id = response.json[0]['id']

    response = seeded_client.get(f'/api/orders/{first_order_id}')
    assert response.status_code == 200
    assert response.json['id'] == first_order_id

def test_get_nonexistent_order(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/orders/<id>' endpoint is requested (GET) for a nonexistent order
    THEN check that the response is a 404 error
    """
    response = client.get('/api/orders/99999')
    assert response.status_code == 404
    assert response.json == {'error': 'Order not found'}

def test_update_order(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/orders/<id>/status' endpoint is requested (PUT) with valid data
    THEN check that the order is updated and the response is valid
    """
    # Get the first order from the list of all orders
    response = seeded_client.get('/api/orders/')
    first_order_id = response.json[0]['id']

    update_data = {
        "status": "shipped"
    }
    response = seeded_client.put(f'/api/orders/{first_order_id}/status', json=update_data)
    assert response.status_code == 200
    assert response.json['status'] == update_data['status']

    # Verify the order was actually updated
    get_response = seeded_client.get(f'/api/orders/{first_order_id}')
    assert get_response.status_code == 200
    assert get_response.json['status'] == update_data['status']

def test_delete_order(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/orders/<id>' endpoint is requested (DELETE) for an existing order
    THEN check that the order is deleted
    """
    # Get the first order from the list of all orders
    response = seeded_client.get('/api/orders/')
    first_order_id = response.json[0]['id']

    response = seeded_client.delete(f'/api/orders/{first_order_id}')
    assert response.status_code == 200
    assert response.json == {'message': 'Order deleted successfully'}

    # Verify the order was actually deleted
    get_response = seeded_client.get(f'/api/orders/{first_order_id}')
    assert get_response.status_code == 404
