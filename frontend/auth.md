How the Flask Implementation Works
The Flask example uses server-side rendering with session-based authentication:

Authentication Flow:

User visits the app → redirected to Microsoft Entra login
After successful login, Microsoft redirects back to REDIRECT_URI
The identity.flask.Auth library handles the OAuth2 callback, validates the token, and creates a server-side session
User info is stored in the session cookie


Protected Routes:

@auth.login_required decorator checks if user has a valid session
The context parameter contains user info and access tokens
Each request is authenticated via the session cookie


API Calls:

When calling downstream APIs, it uses the access token from the context
Token is passed in the Authorization header



How the React SPA Implementation Works
The React example uses client-side authentication with token storage in the browser:

Authentication Flow:

MSAL library initializes with your tenant configuration
User clicks "Sign up" → loginRedirect() redirects to Microsoft
After login, Microsoft redirects to /redirect with an authorization code
MSAL exchanges the code for tokens and stores them in sessionStorage


Token Management:

msalInstance manages tokens in the browser
getActiveAccount() retrieves the current user's claims
Tokens are automatically refreshed by MSAL when needed


Component-Level Protection:

<AuthenticatedTemplate> only renders for logged-in users
<UnauthenticatedTemplate> shows login UI for guests


Why These Are "Individual"
Flask: Backend handles everything - authentication, sessions, and API calls
React SPA: Frontend handles everything - authentication happens entirely in the browser

Adapting for FastAPI + React TypeScript
For your architecture where the React frontend makes requests to a FastAPI backend using UserID, you'll want a hybrid approach:

authConfig.ts
import { Configuration, LogLevel } from '@azure/msal-browser';

/**
 * MSAL Configuration for Microsoft Entra External ID
 */
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.REACT_APP_CLIENT_ID || '', // Your app's client ID
    authority: process.env.REACT_APP_AUTHORITY || 'https://yourtenantname.ciamlogin.com/', 
    redirectUri: process.env.REACT_APP_REDIRECT_URI || 'http://localhost:3000/redirect',
    postLogoutRedirectUri: '/',
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: 'sessionStorage', // More secure than localStorage
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;
        
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            return;
          case LogLevel.Info:
            console.info(message);
            return;
          case LogLevel.Verbose:
            console.debug(message);
            return;
          case LogLevel.Warning:
            console.warn(message);
            return;
        }
      },
    },
  },
};

/**
 * Scopes for login - MSAL automatically adds openid, profile, email
 */
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};

/**
 * Scopes for API access - if you need to call downstream APIs
 */
export const apiRequest = {
  scopes: [process.env.REACT_APP_API_SCOPE || 'api://your-api-id/.default'],
};

main.py
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import jwt
from jwt import PyJWKClient
import os
from pydantic import BaseModel

app = FastAPI()

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Microsoft Entra configuration
TENANT_NAME = os.getenv("TENANT_NAME", "yourtenantname")
AUTHORITY = f"https://{TENANT_NAME}.ciamlogin.com/{TENANT_NAME}.onmicrosoft.com"
CLIENT_ID = os.getenv("CLIENT_ID")
JWKS_URI = f"{AUTHORITY}/discovery/v2.0/keys"

# Initialize JWKS client for token validation (optional but recommended)
jwks_client = PyJWKClient(JWKS_URI)


class UserProfile(BaseModel):
    id: str
    name: str
    email: str


# APPROACH 1: Simple UserID header (trust the frontend)
# Use this if your frontend and backend are in a trusted environment
async def get_current_user_simple(x_user_id: str = Header(...)) -> str:
    """
    Extract user ID from custom header.
    Note: This trusts the frontend. Only use in trusted environments.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    return x_user_id


# APPROACH 2: Validate access token from frontend (more secure)
# Use this if you want the backend to verify the token
async def get_current_user_secure(authorization: str = Header(None)) -> dict:
    """
    Validate the access token and extract user claims.
    This is more secure as the backend validates the token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Get the signing key from Microsoft's JWKS endpoint
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and validate the token
        decoded_token = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,  # Validate it's for your app
            options={"verify_exp": True}
        )
        
        return decoded_token
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/")
async def root():
    return {"message": "FastAPI with Microsoft Entra External ID"}


# Example endpoint using simple approach (UserID header)
@app.get("/api/profile")
async def get_profile(user_id: str = Depends(get_current_user_simple)):
    """
    Get user profile using the UserID from header.
    In production, you'd fetch this from your database.
    """
    # Here you would query your database using user_id
    # For example: user = db.query(User).filter(User.id == user_id).first()
    
    return UserProfile(
        id=user_id,
        name="John Doe",  # From your database
        email="john@example.com"  # From your database
    )


# Example endpoint using secure approach (token validation)
@app.get("/api/secure-profile")
async def get_secure_profile(claims: dict = Depends(get_current_user_secure)):
    """
    Get user profile by validating the access token.
    This is more secure as the backend verifies the token.
    """
    user_id = claims.get("oid") or claims.get("sub")
    
    return {
        "id": user_id,
        "name": claims.get("name"),
        "email": claims.get("preferred_username") or claims.get("email"),
        "claims": claims  # All token claims for debugging
    }


# Example: Create a resource for the authenticated user
@app.post("/api/resources")
async def create_resource(
    resource_data: dict,
    user_id: str = Depends(get_current_user_simple)
):
    """
    Create a resource owned by the authenticated user.
    """
    # In production, save to database with user_id
    return {
        "message": "Resource created",
        "resource": resource_data,
        "owner_id": user_id
    }


# Example: Get all resources for the authenticated user
@app.get("/api/resources")
async def get_resources(user_id: str = Depends(get_current_user_simple)):
    """
    Get all resources owned by the authenticated user.
    """
    # In production, query database: 
    # resources = db.query(Resource).filter(Resource.owner_id == user_id).all()
    
    return {
        "user_id": user_id,
        "resources": [
            {"id": 1, "name": "Resource 1", "owner_id": user_id},
            {"id": 2, "name": "Resource 2", "owner_id": user_id},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


useApi.ts
import { useState, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import { ApiClient } from './apiClient';

/**
 * Custom hook for making authenticated API calls
 */
export function useApi() {
  const { instance } = useMsal();
  const [apiClient, setApiClient] = useState<ApiClient | null>(null);

  useEffect(() => {
    const client = new ApiClient(instance);
    setApiClient(client);
  }, [instance]);

  return apiClient;
}

/**
 * Custom hook for fetching data with loading and error states
 */
export function useApiQuery<T>(
  fetcher: (client: ApiClient) => Promise<T>,
  dependencies: any[] = []
) {
  const apiClient = useApi();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!apiClient) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetcher(apiClient);
        setData(result);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiClient, ...dependencies]);

  return { data, loading, error };
}

// Example usage in a component:
/*
import { useApiQuery } from './useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const ProfileComponent = () => {
  const { data: profile, loading, error } = useApiQuery(
    (client) => client.getUserProfile()
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!profile) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{profile.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Email: {profile.email}</p>
        <p>ID: {profile.id}</p>
      </CardContent>
    </Card>
  );
};
*/

index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { PublicClientApplication, EventType, EventMessage } from '@azure/msal-browser';
import { msalConfig } from './authConfig';
import './index.css';

/**
 * Initialize MSAL instance outside of component tree
 * This prevents re-instantiation on re-renders
 */
const msalInstance = new PublicClientApplication(msalConfig);

/**
 * Initialize MSAL and set up event listeners
 */
const initializeMsal = async () => {
  try {
    // Initialize MSAL (required for redirect flows)
    await msalInstance.initialize();

    // Handle redirect promise (important for redirect flow)
    await msalInstance.handleRedirectPromise();

    // Set active account if one exists
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      msalInstance.setActiveAccount(accounts[0]);
    }

    // Listen for sign-in events and set active account
    msalInstance.addEventCallback((event: EventMessage) => {
      if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
        const payload = event.payload as any;
        const account = payload.account;
        msalInstance.setActiveAccount(account);
        console.log('Login successful:', account);
      }

      if (event.eventType === EventType.LOGOUT_SUCCESS) {
        console.log('Logout successful');
      }

      if (event.eventType === EventType.ACQUIRE_TOKEN_SUCCESS) {
        console.log('Token acquired successfully');
      }

      if (event.eventType === EventType.ACQUIRE_TOKEN_FAILURE) {
        console.error('Token acquisition failed:', event.error);
      }
    });

    // Render the app
    const root = ReactDOM.createRoot(
      document.getElementById('root') as HTMLElement
    );

    root.render(
      <React.StrictMode>
        <App instance={msalInstance} />
      </React.StrictMode>
    );
  } catch (error) {
    console.error('MSAL initialization failed:', error);
  }
};

// Start the application
initializeMsal();

.env.example
# ============================================
# React Frontend Environment Variables
# ============================================

# Microsoft Entra External ID Configuration
REACT_APP_CLIENT_ID=your-client-id-here
REACT_APP_AUTHORITY=https://yourtenantname.ciamlogin.com/
REACT_APP_REDIRECT_URI=http://localhost:3000/redirect

# Optional: API scope if you need access tokens for backend validation
REACT_APP_API_SCOPE=api://your-api-id/.default

# ============================================
# FastAPI Backend Environment Variables
# ============================================

# Microsoft Entra Configuration (for token validation)
TENANT_NAME=yourtenantname
CLIENT_ID=your-client-id-here

# Optional: If using client credentials flow or additional validation
CLIENT_SECRET=your-client-secret-here

# Database connection (example)
DATABASE_URL=postgresql://user:password@localhost/dbname

# ============================================
# Setup Instructions
# ============================================

# 1. Register your application in Microsoft Entra admin center:
#    https://entra.microsoft.com/
#
# 2. Configure redirect URIs:
#    - Add http://localhost:3000/redirect for development
#    - Add your production URL for deployment
#
# 3. Enable ID tokens in Authentication section
#
# 4. If using API authentication, expose an API scope:
#    - Go to "Expose an API"
#    - Add a scope (e.g., "access_as_user")
#    - Set the scope to REACT_APP_API_SCOPE
#
# 5. Copy this file to .env and fill in your values


Summary: Key Differences and Your Implementation
How They Work:

Flask (Server-Side):

User authenticates → server stores session cookie
Every request includes session cookie
Server validates session and makes API calls with access tokens


React SPA (Client-Side):

User authenticates → tokens stored in browser (sessionStorage)
Frontend manages all authentication
No backend involved



Your FastAPI + React Architecture:
You'll use a hybrid approach where:
Frontend (React):

Handles authentication using MSAL
Stores tokens in browser
Extracts oid (User ID) from token claims
Sends User ID to FastAPI in requests (via header or token)

Backend (FastAPI):

Receives User ID in custom header (X-User-ID)
OR validates access token to extract User ID (more secure)
Uses User ID to query/modify user-specific data

Two Security Approaches:
Option 1: Trust Frontend (Simpler)
typescript// Frontend sends User ID
headers: { 'X-User-ID': userId }

// Backend trusts it
user_id = Header("X-User-ID")
Option 2: Validate Token (More Secure)
typescript// Frontend sends access token
headers: { 'Authorization': `Bearer ${accessToken}` }

// Backend validates and extracts User ID
decoded = jwt.decode(token)
user_id = decoded['oid']
Required Packages:
Frontend:
bashnpm install @azure/msal-browser @azure/msal-react
Backend:
bashpip install fastapi uvicorn pyjwt cryptography
The key insight is that in your architecture, the frontend handles authentication (like the React SPA example), but the backend uses the User ID for authorization (similar to how Flask's context['user'] works). You're essentially splitting the responsibilities!