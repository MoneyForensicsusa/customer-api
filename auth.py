from fastapi import Header, HTTPException, Depends
from keyvault import get_secret

def get_expected_api_key() -> str:
    return get_secret("customer-api-key")


def verify_api_key(api_key: str | None = Header(None, alias="X-Api-Key"),
    expected_api_key: str = Depends(get_expected_api_key)):
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )