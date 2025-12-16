from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests

TENANT_ID = "c7abd11f-7e42-4817-aeb6-69456e02dbb2"
API_CLIENT_ID = "c36c0096-67af-4aba-9b01-e9a31f550c67"

ISSUER = f"https://{TENANT_ID}.ciamlogin.com/{TENANT_ID}/v2.0"
JWKS_URL = f"https://{TENANT_ID}.ciamlogin.com/{TENANT_ID}/discovery/v2.0/keys"

security = HTTPBearer()

# Cache keys on startup (fine for dev)
jwks = requests.get(JWKS_URL).json()

def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        key = next(k for k in jwks["keys"] if k["kid"] == kid)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=API_CLIENT_ID,
            issuer=ISSUER,
        )

        return payload

    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signing key",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )
