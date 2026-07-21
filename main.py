from dotenv import load_dotenv
from monitoring import setup_monitoring

load_dotenv()

setup_monitoring()

from mssql_python.exceptions import OperationalError, IntegrityError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import List
from database import get_connection
import logging
from datetime import datetime
from monitoring import setup_monitoring
from fastapi import Request


app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

@app.middleware('http')
async def log_requests(request: Request, call_next):
    logging.info(f'{request.method} {request.url.path}')
    response = await call_next(request)
    return response

# Defining Customer model
class Customer (BaseModel):
    email: EmailStr
    name: str
    city: str = Field(min_length=2)

# Database connection function
def get_db():
    return get_connection()

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
@app.get("/customers")
def get_all_customers(page: int = 1, page_size: int = 10):
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            offset = (page - 1) * page_size

            cursor.execute(
                """
                SELECT
                    id,
                    email,
                    name,
                    city
                FROM dbo.customers
                ORDER BY id
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY;
                """,
                (offset, page_size),
            )

            rows = cursor.fetchall()

            response = []

            for row in rows:
                response.append(
                    {
                        "id": row[0],
                        "email": row[1],
                        "name": row[2],
                        "city": row[3],
                    }
                )

            cursor.close()

        return {
            "page": page,
            "page_size": page_size,
            "customers": response,
        }

    except OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))


# async route to POST customer
@app.post("/customers", status_code=201)
def add_customer(customer: Customer):
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO dbo.customers (email, name, city)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?);
                """,
                (
                    str(customer.email),
                    customer.name,
                    customer.city,
                ),
            )

            new_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()

        return {
            "id": new_id,
            "email": customer.email,
            "name": customer.name,
            "city": customer.city,
        }

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A customer with this email already exists.",
        )

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# async route to GET customers stats
@app.get("/customers/stats")
def get_customers_stats():
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.customers;
                """
            )

            total = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT
                    city,
                    COUNT(*) AS total
                FROM dbo.customers
                GROUP BY city
                ORDER BY total DESC;
                """
            )

            rows = cursor.fetchall()

            cities = []

            for row in rows:
                cities.append(
                    {
                        "city": row[0],
                        "total": row[1],
                    }
                )

            cursor.close()

        return {
            "total_customers": total,
            "cities_stats": cities,
        }

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


#async route to search customers by city or name
@app.get("/customers/search")
def search_customers(
    city: str | None = None,
    name: str | None = None,
):
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            if city:
                cursor.execute(
                    """
                    SELECT
                        id,
                        email,
                        name,
                        city
                    FROM dbo.customers
                    WHERE city LIKE ?;
                    """,
                    (f"%{city}%",),
                )

            elif name:
                cursor.execute(
                    """
                    SELECT
                        id,
                        email,
                        name,
                        city
                    FROM dbo.customers
                    WHERE name LIKE ?;
                    """,
                    (f"%{name}%",),
                )

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Provide city or name to search.",
                )

            rows = cursor.fetchall()

            data = []

            for row in rows:
                data.append(
                    {
                        "id": row[0],
                        "email": row[1],
                        "name": row[2],
                        "city": row[3],
                    }
                )

            cursor.close()

        return data

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


#async route that bulk imports list of customers
@app.post("/customers/bulk", status_code=201)
def bulk_upload(customers: List[Customer]):
    if not customers:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one customer.",
        )

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            ids = []

            try:
                for customer in customers:
                    cursor.execute(
                        """
                        INSERT INTO dbo.customers (email, name, city)
                        OUTPUT INSERTED.id
                        VALUES (?, ?, ?);
                        """,
                        (
                            str(customer.email),
                            customer.name,
                            customer.city,
                        ),
                    )

                    new_id = cursor.fetchone()[0]
                    ids.append(new_id)

                conn.commit()

            except IntegrityError:
                conn.rollback()

                raise HTTPException(
                    status_code=409,
                    detail="One or more emails already exist.",
                )

            finally:
                cursor.close()

        return {
            "message": f"{len(customers)} customers imported successfully",
            "ids": ids,
        }

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )



# async route for delete customer
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    DELETE FROM dbo.customers
                    OUTPUT DELETED.id
                    WHERE id = ?;
                    """,
                    (customer_id,),
                )

                deleted_row = cursor.fetchone()

                if deleted_row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer not found",
                    )

                conn.commit()

            finally:
                cursor.close()

        return {
            "message": f"Customer {customer_id} deleted"
        }

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

#async route to GET customer by id
@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        email,
                        name,
                        city
                    FROM dbo.customers
                    WHERE id = ?;
                    """,
                    (customer_id,),
                )

                row = cursor.fetchone()

            finally:
                cursor.close()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found",
            )

        return {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "city": row[3],
        }

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

#async route to PUT customers
@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: Customer):
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.customers
                    SET
                        email = ?,
                        name = ?,
                        city = ?
                    OUTPUT
                        INSERTED.id,
                        INSERTED.email,
                        INSERTED.name,
                        INSERTED.city
                    WHERE id = ?;
                    """,
                    (
                        str(customer.email),
                        customer.name,
                        customer.city,
                        customer_id,
                    ),
                )

                updated_row = cursor.fetchone()

                if updated_row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer not found",
                    )

                conn.commit()

            except IntegrityError:
                conn.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="A customer with this email already exists.",
                )

            finally:
                cursor.close()

        return {
            "message": f"Customer {customer_id} updated",
            "id": updated_row[0],
            "email": updated_row[1],
            "name": updated_row[2],
            "city": updated_row[3],
        }

    except OperationalError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )




