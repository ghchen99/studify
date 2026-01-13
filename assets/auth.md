
## 🔐 Authentication: Microsoft Entra ID External (CIAM)

This project uses **two app registrations**:

1. **Frontend (SPA) App Registration**
2. **Backend (Web API) App Registration**

This follows Microsoft best practises for SPA → API security.

---

### 1️⃣ Backend App Registration (API)

**Purpose**: Protect the FastAPI backend and validate access tokens.

#### Configuration

- **Platform type**: Web API
- **Issuer**:
  ```
  https://<TENANT_ID>.ciamlogin.com/<TENANT_ID>/v2.0
  ```
- **Expose an API**:
  - Application ID URI:
    ```
    api://<BACKEND_CLIENT_ID>
    ```
  - Scope:
    ```
    access_as_user
    ```

#### Token Validation (FastAPI)

The backend validates JWTs using the Entra ID JWKS endpoint:

- Verifies:
  - Signature (RS256)
  - Issuer
  - Audience (`CLIENT_ID`)

See `backend/users/auth.py`.

---

### 2️⃣ Frontend App Registration (SPA)

**Purpose**: Authenticate users and acquire access tokens.

#### Configuration

- **Platform**: Single-page application (SPA)
- **Redirect URI**:
  ```
  http://localhost:3000
  ```
- **Allowed scopes**:
  - `openid`
  - `profile`
  - `email`
  - `api://<BACKEND_CLIENT_ID>/access_as_user`

#### MSAL Setup

- Uses `@azure/msal-browser` and `@azure/msal-react`
- Tokens acquired silently and attached as `Authorization: Bearer <token>`
- See:
  - `frontend/src/lib/authConfig.ts`
  - `frontend/src/lib/msalInstance.ts`

---

## 🔄 API Authentication Flow

1. User logs in via Entra External ID (CIAM)
2. Frontend acquires access token using MSAL
3. Token includes API scope: `access_as_user`
4. Token sent as `Authorization: Bearer <token>`
5. FastAPI validates token and processes request

---