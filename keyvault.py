from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from os import getenv
from dotenv import load_dotenv


load_dotenv()

vault_url = getenv("KEY_VAULT_URL")

if not vault_url:
    raise RuntimeError("KEY_VAULT_URL environment variable is missing")

credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url=vault_url,
    credential=credential
)

def get_secret(secret_name: str) -> str:
    secret = secret_client.get_secret(secret_name)
    return secret.value

if __name__ == "__main__":
    get_secret("azure-sql-password")
    print("Secret retrieved successfully from Key Vault")