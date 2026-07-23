from os import getenv
from fastapi import Header, HTTPException

EXPECTED_API_KEY = getenv("API_KEY")

if EXPECTED_API_KEY is None:
    raise RuntimeError('API_KEY environment variable is not set')

def verify_api_key(api_key: str | None = Header(None, alias="X-Api-Key")):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )