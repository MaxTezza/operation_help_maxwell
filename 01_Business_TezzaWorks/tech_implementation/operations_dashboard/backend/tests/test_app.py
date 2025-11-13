def test_health_check(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/health' endpoint is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}
