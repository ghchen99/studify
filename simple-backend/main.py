from fastapi import FastAPI, Depends
from auth import verify_access_token
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # allows Authorization, Content-Type, etc.
)

@app.get("/api/secure-data")
def secure_data(user=Depends(verify_access_token)):
    return {
        "message": "Protected API call successful",
        "user_id": user["oid"],
        "user_name": user.get("preferred_username") or user.get("email"),
        "scopes": user.get("scp"),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)