from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Simple Auth Test API")

# Enable CORS for your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserResponse(BaseModel):
    message: str
    user_id: str
    received_from: str


@app.get("/")
def root():
    return {
        "message": "FastAPI is running!",
        "endpoints": {
            "test_auth": "/api/test-auth",
            "docs": "/docs"
        }
    }


@app.get("/api/test-auth", response_model=UserResponse)
def test_auth(x_user_id: str = Header(..., description="User ID from frontend")):
    """
    Simple endpoint to test that user ID is being received from frontend.
    
    The frontend will send the user's 'oid' claim in the X-User-ID header.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="No user ID provided")
    
    return UserResponse(
        message="✅ Successfully received user ID!",
        user_id=x_user_id,
        received_from="X-User-ID header"
    )


@app.get("/api/whoami")
def whoami(x_user_id: Optional[str] = Header(None)):
    """
    Another simple test endpoint that shows what user is making the request.
    """
    if not x_user_id:
        return {
            "authenticated": False,
            "message": "No user ID found in request"
        }
    
    return {
        "authenticated": True,
        "user_id": x_user_id,
        "message": f"You are logged in as {x_user_id}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)