from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#Test for get customers
def test_get_customers():
    response = client.get('/customers')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

#Test for POST customer
def test_post_customers(test_customer):
    assert test_customer.status_code == 201
    data = test_customer.json()
    assert 'id' in data
    assert data['email'] == 'alpha.beta@gmail.com'
    assert data['name'] == 'Alpha beta'
    assert data['city'] =='Austin'
    