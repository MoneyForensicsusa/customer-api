import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def test_customer():
    data = {"email": "alpha.beta@gmail.com", "name": "Alpha beta", "city": "Austin"}
    response = client.post('/customers/', json=data)
    created = response.json()

    yield response

    client.delete(f'/customers/{created["id"]}')

