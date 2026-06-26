from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Defining Customer model
class Customer (BaseModel):
    email: str
    name: str
    city: str

# Database connection function
def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

# async route to get te whole Customers table
@app.get('/customers')
async def get_all_customers():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, email, name, city FROM customers')
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    "id": row[0],
                    "email": row[1],
                    "name": row[2],
                    "city": row[3]
                })
        return response
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
            "new_email": updated_row[0],
            "new_name": updated_row[1],
            "new_city": updated_row[2]
        }
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))