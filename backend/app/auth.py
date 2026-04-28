from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def require_token(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> None:
    settings = get_settings()
    if credentials is None or credentials.credentials != settings.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "detail": "Missing or invalid bearer token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
