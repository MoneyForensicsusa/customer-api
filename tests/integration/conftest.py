import pytest
from fastapi.testclient import TestClient

from auth import get_expected_api_key
from main import app

TEST_API_KEY = "test-api-key"

def fake_get_expected_api_key() -> str:
    return TEST_API_KEY

app.dependency_overrides[get_expected_api_key] = fake_get_expected_api_key

client = TestClient(app)

TEST_HEADERS = {
    "X-Api-Key": TEST_API_KEY
}

@pytest.fixture
def test_customer():
    data = {"email": "alpha.beta@gmail.com", "name": "Alpha beta", "city": "Austin"}
    response = client.post('/customers/', json=data, headers=TEST_HEADERS)
    created = response.json()

    yield response

    client.delete(f'/customers/{created["id"]}', headers=TEST_HEADERS)

