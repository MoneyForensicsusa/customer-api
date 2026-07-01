# Customer Database API

A REST API for managing customer data built with FastAPI and PostgreSQL.

## Tech Stack
- FastAPI
- PostgreSQL
- psycopg2
- pytest

## Setup

1. Clone the repo
2. Create virtual environment:
   python -m venv .venv
   .venv\Scripts\Activate.ps1

3. Install dependencies:
   pip install -r requirements.txt

4. Create .env file:
   DB_HOST=localhost
   DB_NAME=customer_db
   DB_USER=postgres
   DB_PASSWORD=your_password_here

5. Create the database and table in pgAdmin:
   CREATE TABLE customers (
       id SERIAL PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       name TEXT NOT NULL,
       city TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT NOW()
   );

6. Run the server:
   python -m uvicorn main:app --reload

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /customers | Get all customers with pagination |
| POST | /customers | Create a new customer |
| GET | /customers/{id} | Get a specific customer |
| PUT | /customers/{id} | Update a customer |
| DELETE | /customers/{id} | Delete a customer |
| GET | /customers/search | Search by city or name |
| GET | /customers/stats | Get customer statistics |
| POST | /customers/bulk | Bulk import customers |

## Example Requests

### Create a Customer
POST /customers
{
    "email": "wonderful@gmail.com",
    "name": "Wonderful",
    "city": "Austin"
}

Response:
{
    "id": 1,
    "email": "wonderful@gmail.com",
    "name": "Wonderful",
    "city": "Austin"
}

### Search Customers
GET /customers/search?city=Austin

Response:
[
    {
        "id": 1,
        "email": "wonderful@gmail.com",
        "name": "Wonderful",
        "city": "Austin"
    }
]

## Running Tests
python -m pytest