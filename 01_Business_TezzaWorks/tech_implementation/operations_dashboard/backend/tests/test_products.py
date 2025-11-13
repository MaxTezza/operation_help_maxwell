def test_get_products(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/products/' endpoint is requested (GET)
    THEN check that the response is valid and contains the expected number of products
    """
    response = seeded_client.get('/api/products/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 8

def test_create_product(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/products/' endpoint is requested (POST) with valid data
    THEN check that a new product is created and the response is valid
    """
    new_product_data = {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "A product for testing",
        "category": "drinkware",
        "base_cost": 10.0,
        "labor_hours": 1.0,
        "overhead_percentage": 20.0,
        "stock_quantity": 100,
        "reorder_level": 10,
        "allows_logo": True,
        "allows_personalization": True,
        "customization_cost": 5.0
    }
    response = client.post('/api/products/', json=new_product_data)
    assert response.status_code == 201
    
    response_data = response.json
    assert response_data["name"] == new_product_data["name"]
    assert response_data["sku"] == new_product_data["sku"]
    
    # Verify the product was actually created
    get_response = client.get(f'/api/products/{response_data["id"]}')
    assert get_response.status_code == 200
    assert get_response.json["name"] == new_product_data["name"]

def test_get_product(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/products/<id>' endpoint is requested (GET) for an existing product
    THEN check that the response is valid and contains the correct product data
    """
    # Get the first product from the list of all products
    response = seeded_client.get('/api/products/')
    first_product_id = response.json[0]['id']

    response = seeded_client.get(f'/api/products/{first_product_id}')
    assert response.status_code == 200
    assert response.json['id'] == first_product_id

def test_get_nonexistent_product(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/products/<id>' endpoint is requested (GET) for a nonexistent product
    THEN check that the response is a 404 error
    """
    response = client.get('/api/products/99999')
    assert response.status_code == 404
    assert response.json == {'error': 'Product not found'}

def test_update_product(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/products/<id>' endpoint is requested (PUT) with valid data
    THEN check that the product is updated and the response is valid
    """
    # Get the first product from the list of all products
    response = seeded_client.get('/api/products/')
    first_product_id = response.json[0]['id']

    update_data = {
        "name": "Updated Product Name",
        "base_cost": 15.0
    }
    response = seeded_client.put(f'/api/products/{first_product_id}', json=update_data)
    assert response.status_code == 200
    assert response.json['name'] == update_data['name']
    assert response.json['base_cost'] == update_data['base_cost']

    # Verify the product was actually updated
    get_response = seeded_client.get(f'/api/products/{first_product_id}')
    assert get_response.status_code == 200
    assert get_response.json['name'] == update_data['name']

def test_delete_product(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/products/<id>' endpoint is requested (DELETE) for an existing product
    THEN check that the product is deactivated
    """
    # Get the first product from the list of all products
    response = seeded_client.get('/api/products/')
    first_product_id = response.json[0]['id']

    response = seeded_client.delete(f'/api/products/{first_product_id}')
    assert response.status_code == 200
    assert response.json == {'message': 'Product deactivated successfully'}

    # Verify the product was actually deactivated
    get_response = seeded_client.get(f'/api/products/{first_product_id}')
    assert get_response.status_code == 200
    assert get_response.json['is_active'] == False
