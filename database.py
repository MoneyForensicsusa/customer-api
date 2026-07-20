from os import getenv

from dotenv import load_dotenv
from mssql_python import connect

from keyvault import get_secret


load_dotenv()


server = getenv("AZURE_SQL_SERVER")
database = getenv("AZURE_SQL_DATABASE")
username = getenv("AZURE_SQL_USERNAME")
password = get_secret("azure-sql-password")

if not all([server, database, username, password]):
    raise RuntimeError(
        "One or more Azure SQL configuration values are missing."
    )

connection_string = (
    f"Server=tcp:{server},1433;"
    f"Database={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)


def get_connection():
    """Open and return a new Azure SQL connection."""
    return connect(connection_string)