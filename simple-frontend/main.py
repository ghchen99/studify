from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your config - same values from authConfig.ts
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT = "gpteducation"
JWKS_URL = f"https://{TENANT}.ciamlogin.com/{TENANT}.onmicrosoft.com/discovery/v2.0/keys"

jwks_client = PyJWKClient(JWKS_URL)
security = HTTPBearer()


class UserResponse(BaseModel):
    message: str
    user_id: str
    user_name: str


# Simple dependency that validates token (like Flask's @auth.login_required)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience=CLIENT_ID)
        return claims
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/")
def root():
    return {"message": "FastAPI with secure auth"}


# Secure endpoint - just add Depends(get_current_user)
@app.get("/api/secure-data", response_model=UserResponse)
def get_data(user: dict = Depends(get_current_user)):
    return UserResponse(
        message="✅ Token validated!",
        user_id=user.get("oid"),
        user_name=user.get("name", "N/A")
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)