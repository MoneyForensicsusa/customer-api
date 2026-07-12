from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import List
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

#startup validation - fail fast if secrets missing
REQUIRED_ENV = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
missing =[]
for variable in REQUIRED_ENV:
    if not os.getenv(variable):
        missing.append(variable)
if missing:
    raise RuntimeError(f'Missing reuired environment variables: {missing}')

app = FastAPI()

# Defining Customer model
class Customer (BaseModel):
    email: EmailStr
    name: str
    city: str = Field(min_length=2)

# Database connection function
def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

# route for health check
@app.get('/health')
def check_health():
    return {
        "status": "ok"
    }

# version endpoint
@app.get('/version')
def version():
    return{
        "app": "customer-api",
        "version": "1.0.0"
    }

# async route to get te whole Customers table
@app.get('/customers')
async def get_all_customers(page: int = 1, page_size: int = 10):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            cursor.execute('SELECT id, email, name, city FROM customers ORDER BY id LIMIT %s OFFSET %s', (page_size, offset))
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    "id": row[0],
                    "email": row[1],
                    "name": row[2],
                    "city": row[3]
                })
        return {
            "page": page,
            "page_size": page_size,
            "customers": response}
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))


# async route to POST customer
@app.post('/customers', status_code=201)
async def add_customer(customer: Customer):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (email, name, city) VALUES (%s, %s, %s) RETURNING id",
            (customer.email, customer.name, customer.city))
            new_id = cursor.fetchone()[0]
            conn.commit()
        return {
            "id": new_id,
            "email": customer.email,
            "name": customer.name,
            "city": customer.city
        }
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))


# async route to GET customers stats
@app.get('/customers/stats')
async def get_customers_stats():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            total = cursor.fetchone()[0]

            cities = []
            cursor.execute("SELECT city, COUNT(*) AS total FROM customers GROUP BY city ORDER BY total DESC")
            rows = cursor.fetchall()
            for row in rows:
                cities.append({"city": row[0], "total": row[1]})
        return {
            'total_customers': total,
            'cities_stats': cities
        }
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))


#async route to search customers by city or name
@app.get('/customers/search')
async def search_customers(city: str = None, name: str = None):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            if city:
                cursor.execute("SELECT id, email, name, city FROM customers WHERE city ILIKE %s",
                (f'%{city}%',))
            elif name:
                cursor.execute("SELECT id, email, name, city FROM customers WHERE name ILIKE %s",
                (f'%{name}%',))
            else:
                raise HTTPException(status_code=400, detail='Provide city or name to search')
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append({
                    'id': row[0],
                    'email': row[1],
                    'name': row[2],
                    'city': row[3]
                })
        return data
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))


#async route that bulk imports list of customers
@app.post('/customers/bulk', status_code=201)
async def bulk_upload(customers: List[Customer]):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            values = []
            for c in customers:
                values.append((c.email, c.name, c.city))
            cursor.executemany("INSERT INTO customers (email, name, city) VALUES (%s, %s, %s)",
            values)
            emails = []
            for c in customers:
                emails.append(c.email)
            cursor.execute("SELECT id FROM customers WHERE email = ANY(%s)", (emails,))
            rows = cursor.fetchall()
            ids = []
            for row in rows:
                ids.append(row[0])
            conn.commit()
        return {
            'message': f'{len(customers)} customers imported successfully',
            'ids': ids
        }
    except psycopg2.errors.UniqueViolation as e:
        raise HTTPException(status_code=400, detail='One or more emails already exist')
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))



# async route for delete customer
@app.delete('/customers/{customer_id}')
async def delete_customer(customer_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Customer not found")
            conn.commit()
        return {"message": f"Customer {customer_id} deleted"}
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))

#async route to GET customer by id
@app.get('/customers/{customer_id}')
async def get_customer(customer_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(" SELECT id, email, name, city FROM customers WHERE id = %s",
            (customer_id,))
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail='Customer not found')
        return {
            "id": row[0],
            "email": row[1],
            'name': row[2],
            "city": row[3]
        }
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))

#async route to PUT customers
@app.put('/customers/{customer_id}')
async def update_customer(customer_id: int, customer: Customer):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE customers SET email = %s, name = %s, city = %s WHERE id = %s RETURNING id, email, name, city",
            (customer.email, customer.name, customer.city, customer_id))
            updated_row = cursor.fetchone()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail='Customer not found')
            conn.commit()
        return {
            "message": f"Customer {customer_id} updated",
            "email": updated_row[1],
            "name": updated_row[2],
            "city": updated_row[3]
        }
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))





