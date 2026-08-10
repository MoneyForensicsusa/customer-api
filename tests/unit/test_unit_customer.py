from mssql_python.exceptions import IntegrityError
import pytest
from fastapi.testclient import TestClient

from auth import get_expected_api_key
from database import get_db
from main import app


TEST_API_KEY = "test-api-key"


class FakeCursor:
    def __init__(self):
        self.executed_query = None
        self.executed_parameters = None
        self.was_closed = False
        self.raise_integrity_error = False

    def execute(self, query, parameters=None):
        self.executed_query = query
        self.executed_parameters = parameters
        if self.raise_integrity_error:
            raise IntegrityError(
                "Fake duplicate email error",
                "Fake underlying database error",
            )

    def fetchall(self):
        return [
            (1, "alice@example.com", "Alice", "Austin"),
            (2, "bob@example.com", "Bob", "Dallas"),
        ]

    def fetchone(self):
        return (123,)

    def close(self):
        self.was_closed = True


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()
        self.was_committed = False
        self.was_rolled_back = False

    def cursor(self):
        return self.fake_cursor
    
    def commit(self):
        self.was_committed = True
    
    def rollback(self):
        self.was_rolled_back = True


fake_connection = FakeConnection()


def fake_get_db():
    yield fake_connection


def fake_get_expected_api_key() -> str:
    return TEST_API_KEY

@pytest.fixture
def test_client():
    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_expected_api_key] = fake_get_expected_api_key

    client = TestClient(app)

    yield client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_expected_api_key, None)



def test_get_customers_page_two(test_client):
    response = test_client.get(
        "/customers",
        params={
            "page": 2,
            "page_size": 5,
        },
        headers={
            "X-Api-Key": TEST_API_KEY,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert len(data["customers"]) == 2
    assert data["customers"][0] == {
        "id": 1,
        "email": "alice@example.com",
        "name": "Alice",
        "city": "Austin",
    }
    assert fake_connection.fake_cursor.executed_parameters == (5, 5)

def test_add_customer_success(test_client):
    fake_connection.was_committed = False
    fake_connection.fake_cursor.was_closed = False

    response = test_client.post(
        "/customers",
        json={
            "email": "new@example.com",
            "name": "New Customer",
            "city": "Austin",
        },
        headers={
            "X-Api-Key": TEST_API_KEY,
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 123
    assert data["email"] == "new@example.com"
    assert data["name"] == "New Customer"
    assert data["city"] == "Austin"
    assert fake_connection.was_committed is True
    assert fake_connection.fake_cursor.was_closed is True

def test_add_customer_duplicate_email(test_client):
    fake_cursor = fake_connection.fake_cursor

    fake_cursor.raise_integrity_error = True
    fake_cursor.was_closed = False
    fake_connection.was_committed = False
    fake_connection.was_rolled_back = False

    response = test_client.post(
        "/customers",
        json={
            "email": "existing@example.com",
            "name": "Existing Customer",
            "city": "Austin",
        },
        headers={
            "X-Api-Key": TEST_API_KEY,
        },
    )
    assert response.status_code == 409
    assert fake_connection.was_rolled_back is True
    assert fake_connection.was_committed is False
    assert fake_cursor.was_closed is True