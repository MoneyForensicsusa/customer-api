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

#Test for DELETE customer
def test_delete_customer(test_customer):
    customer_id = test_customer.json()['id']
    response = client.delete(f'/customers/{customer_id}')
    assert response.status_code == 200
    get_response = client.get(f'/customers/{customer_id}')
    assert get_response.status_code == 404

#Test for GET customer
def test_get_customer(test_customer):
    customer_id = test_customer.json()['id']
    response = client.get(f'/customers/{customer_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data 
    assert data['email'] == 'alpha.beta@gmail.com'
    assert data['name'] == 'Alpha beta'
    assert data['city'] == 'Austin'

#Test for PUT customer
def test_put_customer(test_customer):
    customer_id = test_customer.json()['id']
    updated_data = {
        'email': 'new.gmail.com',
        'name': 'new name',
        'city': 'new city'
    }
    response = client.put(f'/customers/{customer_id}', json=updated_data)
    assert response.status_code == 200

    data = response.json()
    assert data['email'] == 'new.gmail.com'
    assert data['name'] == 'new name'
    assert data['city'] == 'new city'
