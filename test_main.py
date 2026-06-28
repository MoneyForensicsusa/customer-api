from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#Test for get customers
def test_get_customers():
    response = client.get('/customers')
    assert response.status_code == 200
    data = response.json()
    assert 'customers' in data
    assert isinstance(data['customers'], list)

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
        'email': 'new@gmail.com',
        'name': 'new name',
        'city': 'new city'
    }
    response = client.put(f'/customers/{customer_id}', json=updated_data)
    assert response.status_code == 200

    data = response.json()
    assert data['email'] == 'new@gmail.com'
    assert data['name'] == 'new name'
    assert data['city'] == 'new city'

#Test for GET customers stats route
def test_get_customer_stats(test_customer):
    response = client.get('/customers/stats')
    assert response.status_code == 200

    data = response.json()
    assert 'total_customers' in data
    assert 'cities_stats' in data
    assert data["total_customers"] >= 1
    assert isinstance(data['cities_stats'], list) 

#Test for Search customers route
def test_search_customers():
    data = {'email': 'search@gmail.com', 'name': 'Search_test', 'city': 'Testcity'}
    created = client.post('/customers', json=data)
    customer_id = created.json()['id']

    response = client.get('/customers/search', params={'city': 'Testcity'})
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["city"] == "Testcity"

    client.delete(f'/customers/{customer_id}')

#Test for bulk Post route
def test_bulk_post():
    data = [
        {"email": "jamie.wilson@gmail.com", "name": "Jamie Wilson", "city": "Austin"},
        {"email": "sarai.johnson@gmail.com", "name": "Sarai Johnson", "city": "Dallas"},
        {"email": "michelle.brown@gmail.com", "name": "Michelle Brown", "city": "Houston"}
    ]
    response = client.post('/customers/bulk', json=data)
    assert response.status_code == 201
    posted = response.json()
    assert len(posted["ids"]) == 3
    
    ids = response.json()['ids']
    for id in ids:
        client.delete(f'/customers/{id}')