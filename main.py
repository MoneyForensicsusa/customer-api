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
                    "id": row['id'],
                    "email": row['email'],
                    "name": row["name"],
                    "city": row["city"]
                })
        return response
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))
