import base64
from typing import Dict, Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# In-memory users store (username -> password). DO NOT use in production.
USERS: Dict[str, str] = {
    "admin": "changeme",
}

def verify_user(username: str, password: str) -> bool:
    return USERS.get(username) == password

def basic_auth_dep(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """FastAPI dependency that enforces HTTP Basic auth for HTTP routes."""
    if not verify_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Return the username for downstream handlers
    return credentials.username

def parse_basic_auth_header(auth_header: Optional[str]) -> Optional[Tuple[str, str]]:
    """Parse Authorization: Basic ... header, returning (username, password) if valid."""
    if not auth_header or not auth_header.lower().startswith("basic "):
        return None
    try:
        b64 = auth_header.split(" ", 1)[1]
        raw = base64.b64decode(b64).decode("utf-8")
        username, password = raw.split(":", 1)
        return username, password
    except Exception:
        return None
