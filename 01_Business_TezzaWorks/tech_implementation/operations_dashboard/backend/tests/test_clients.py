def test_get_clients(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/clients' endpoint is requested (GET)
    THEN check that the response is valid and contains the expected number of clients
    """
    response = seeded_client.get('/api/clients/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 5

def test_create_client(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/clients/' endpoint is requested (POST) with valid data
    THEN check that a new client is created and the response is valid
    """
    new_client_data = {
        "company_name": "Test Company",
        "contact_person": "Test Person",
        "email": "test@company.com",
        "phone": "123-456-7890",
        "acquisition_source": "website"
    }
    response = client.post('/api/clients/', json=new_client_data)
    assert response.status_code == 201
    
    response_data = response.json
    assert response_data["company_name"] == new_client_data["company_name"]
    assert response_data["email"] == new_client_data["email"]
    
    # Verify the client was actually created
    get_response = client.get(f'/api/clients/{response_data["id"]}')
    assert get_response.status_code == 200
    assert get_response.json["company_name"] == new_client_data["company_name"]

def test_get_client(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/clients/<id>' endpoint is requested (GET) for an existing client
    THEN check that the response is valid and contains the correct client data
    """
    # Get the first client from the list of all clients
    response = seeded_client.get('/api/clients/')
    first_client_id = response.json[0]['id']

    response = seeded_client.get(f'/api/clients/{first_client_id}')
    assert response.status_code == 200
    assert response.json['id'] == first_client_id

def test_get_nonexistent_client(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/clients/<id>' endpoint is requested (GET) for a nonexistent client
    THEN check that the response is a 404 error
    """
    response = client.get('/api/clients/99999')
    assert response.status_code == 404
    assert response.json == {'error': 'Client not found'}

def test_update_client(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/clients/<id>' endpoint is requested (PUT) with valid data
    THEN check that the client is updated and the response is valid
    """
    # Get the first client from the list of all clients
    response = seeded_client.get('/api/clients/')
    first_client_id = response.json[0]['id']

    update_data = {
        "company_name": "Updated Company Name",
        "contact_person": "Updated Contact Person"
    }
    response = seeded_client.put(f'/api/clients/{first_client_id}', json=update_data)
    assert response.status_code == 200
    assert response.json['company_name'] == update_data['company_name']
    assert response.json['contact_person'] == update_data['contact_person']

    # Verify the client was actually updated
    get_response = seeded_client.get(f'/api/clients/{first_client_id}')
    assert get_response.status_code == 200
    assert get_response.json['company_name'] == update_data['company_name']

def test_delete_client(seeded_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/clients/<id>' endpoint is requested (DELETE) for an existing client
    THEN check that the client is deleted
    """
    # Get the first client from the list of all clients
    response = seeded_client.get('/api/clients/')
    first_client_id = response.json[0]['id']

    response = seeded_client.delete(f'/api/clients/{first_client_id}')
    assert response.status_code == 200
    assert response.json == {'message': 'Client deleted successfully'}

    # Verify the client was actually deleted
    get_response = seeded_client.get(f'/api/clients/{first_client_id}')
    assert get_response.status_code == 404
