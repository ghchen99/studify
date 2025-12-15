# Simple Microsoft Entra Login + FastAPI Test - Setup

## Part 1: React Frontend Setup

### 1. Install Dependencies

```bash
npm install @azure/msal-browser @azure/msal-react
```

### 2. Configure Microsoft Entra (Azure Portal)

1. Go to [Microsoft Entra admin center](https://entra.microsoft.com/)
2. Navigate to **Applications** > **App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: My Test App
   - **Supported account types**: Choose your option (usually "Accounts in this organizational directory only")
   - **Redirect URI**: 
     - Platform: **Single-page application (SPA)**
     - URI: `http://localhost:3000`
5. Click **Register**

### 3. Get Your Configuration Values

After registration, you'll see:
- **Application (client) ID** - Copy this, you'll need it!
- **Directory (tenant) ID** - You'll need this too

Find your authority URL:
- For Microsoft Entra External ID: `https://YOUR_TENANT_NAME.ciamlogin.com/`
- For regular Azure AD: `https://login.microsoftonline.com/YOUR_TENANT_ID`

### 4. Update authConfig.ts

```typescript
export const msalConfig: Configuration = {
  auth: {
    clientId: 'YOUR_CLIENT_ID_HERE', // Paste your Application (client) ID
    authority: 'https://YOUR_TENANT.ciamlogin.com/', // Paste your authority URL
    redirectUri: 'http://localhost:3000',
  },
  // ... rest stays the same
};
```

### 5. Enable ID Tokens (Important!)

In Azure Portal, for your app:
1. Go to **Authentication**
2. Under **Implicit grant and hybrid flows**
3. Check ✅ **ID tokens**
4. Click **Save**

### 6. Run React App

```bash
npm start
```

Visit `http://localhost:3000`

---

## Part 2: FastAPI Backend Setup

### 1. Install Python Dependencies

```bash
pip install fastapi uvicorn
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Run FastAPI Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

FastAPI will be available at `http://localhost:8000`

### 3. Check API Docs

Visit `http://localhost:8000/docs` to see the interactive API documentation

---

## Testing the Full Flow

1. **Start FastAPI** (Terminal 1):
   ```bash
   python main.py
   ```

2. **Start React** (Terminal 2):
   ```bash
   npm start
   ```

3. **Test the flow**:
   - Click "Sign In with Microsoft"
   - Login with your Microsoft account
   - You'll see your user info
   - Click "📡 Call FastAPI" button
   - You should see: ✅ "Successfully received user ID!"

---

## What's Happening?

1. **Login**: React → Microsoft → React (with token)
2. **Extract User ID**: React gets `oid` from token claims
3. **Call API**: React → FastAPI with `X-User-ID` header
4. **Response**: FastAPI confirms it received the user ID

---

## Troubleshooting

### Frontend Issues

**Error: "AADSTS50011: Reply URL mismatch"**
- Make sure redirect URI in code matches Azure Portal exactly
- Must be `http://localhost:3000` (no trailing slash)

**Error: "AADSTS700016: Application not found"**
- Check your client ID is correct
- Make sure you're in the right tenant

**Nothing happens after login**
- Check browser console for errors
- Make sure ID tokens are enabled in Azure Portal

### Backend Issues

**Error: "Connection refused" when calling API**
- Make sure FastAPI is running on port 8000
- Check `http://localhost:8000` in browser

**CORS errors in browser console**
- Make sure FastAPI CORS middleware allows `http://localhost:3000`
- Check the `allow_origins` in main.py

**API returns 401 or 422 error**
- Check browser Network tab to see if `X-User-ID` header is being sent
- Verify the user ID is not empty/null

---

## Next Steps

Once this works, you can:
1. Add more API endpoints that use the user ID
2. Connect a database and store user-specific data
3. Add more complex authentication (token validation)
4. Deploy to production with proper security