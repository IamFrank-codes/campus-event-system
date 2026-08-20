"""JWT validation for service-to-service and client authorization."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)

def current_claims(token: str = Depends(oauth2_scheme)) -> dict:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        if not claims.get("sub"):
            raise error
        return claims
    except JWTError:
        raise error

def require_roles(*roles: str):
    def dependency(claims: dict = Depends(current_claims)) -> dict:
        if claims.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return claims
    return dependency
