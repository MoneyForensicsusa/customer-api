from os import getenv

from dotenv import load_dotenv
from mssql_python import connect


load_dotenv()


def get_connection():
    """Open and return an Azure SQL connection."""

    server = getenv("AZURE_SQL_SERVER")
    database = getenv("AZURE_SQL_DATABASE")
    username = getenv("AZURE_SQL_USERNAME")
    password = getenv("AZURE_SQL_PASSWORD")

    if not all([server, database, username, password]):
        raise RuntimeError(
            "One or more Azure SQL environment variables are missing."
        )

    connection_string = (
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    return connect(connection_string)