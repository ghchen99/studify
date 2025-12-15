import { 
  MsalProvider, 
  AuthenticatedTemplate, 
  UnauthenticatedTemplate,
  useMsal 
} from '@azure/msal-react';
import { IPublicClientApplication } from '@azure/msal-browser';
import { loginRequest } from './authConfig';
import { useState } from 'react';

interface AppProps {
  instance: IPublicClientApplication;
}

interface ApiResponse {
  message: string;
  user_id: string;
  received_from: string;
}

const LoginButton = () => {
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Simple Login Test</h1>
      <button 
        onClick={handleLogin}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          cursor: 'pointer',
          backgroundColor: '#0078d4',
          color: 'white',
          border: 'none',
          borderRadius: '4px'
        }}
      >
        Sign In with Microsoft
      </button>
    </div>
  );
};

const UserInfo = () => {
  const { instance } = useMsal();
  const account = instance.getActiveAccount();
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogout = () => {
    instance.logoutRedirect();
  };

  const testApi = async () => {
    setLoading(true);
    setApiError(null);
    setApiResponse(null);

    try {
      // Get user ID from token claims
      const userId = account?.idTokenClaims?.oid;
      
      if (!userId) {
        throw new Error('User ID not found in token');
      }

      // Call FastAPI backend
      const response = await fetch('http://localhost:8000/api/test-auth', {
        method: 'GET',
        headers: {
          'X-User-ID': userId, // Send user ID in header
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '50px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>✅ Login Successful!</h1>
      
      <div style={{ 
        backgroundColor: '#f0f0f0', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>User Information:</h2>
        <p><strong>Name:</strong> {account?.name || 'N/A'}</p>
        <p><strong>Email:</strong> {account?.username || 'N/A'}</p>
        <p><strong>User ID (oid):</strong> {account?.idTokenClaims?.oid || 'N/A'}</p>
        
        <details style={{ marginTop: '20px' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
            View All Claims
          </summary>
          <pre style={{ 
            backgroundColor: 'white', 
            padding: '10px', 
            borderRadius: '4px',
            overflow: 'auto',
            fontSize: '12px',
            marginTop: '10px'
          }}>
            {JSON.stringify(account?.idTokenClaims, null, 2)}
          </pre>
        </details>
      </div>

      {/* API Test Section */}
      <div style={{
        backgroundColor: '#e8f4f8',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>🧪 Test FastAPI Connection</h2>
        <p style={{ fontSize: '14px', color: '#666' }}>
          This will send your User ID to the FastAPI backend
        </p>
        
        <button 
          onClick={testApi}
          disabled={loading}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer',
            backgroundColor: loading ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            marginTop: '10px'
          }}
        >
          {loading ? 'Calling API...' : '📡 Call FastAPI'}
        </button>

        {/* API Response */}
        {apiResponse && (
          <div style={{
            backgroundColor: '#d4edda',
            border: '1px solid #c3e6cb',
            padding: '15px',
            borderRadius: '4px',
            marginTop: '15px'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#155724' }}>
              ✅ {apiResponse.message}
            </h3>
            <p><strong>User ID received:</strong> {apiResponse.user_id}</p>
            <p><strong>Method:</strong> {apiResponse.received_from}</p>
          </div>
        )}

        {/* API Error */}
        {apiError && (
          <div style={{
            backgroundColor: '#f8d7da',
            border: '1px solid #f5c6cb',
            padding: '15px',
            borderRadius: '4px',
            marginTop: '15px',
            color: '#721c24'
          }}>
            <h3 style={{ margin: '0 0 10px 0' }}>❌ Error</h3>
            <p>{apiError}</p>
            <p style={{ fontSize: '12px', marginTop: '10px' }}>
              Make sure FastAPI is running on http://localhost:8000
            </p>
          </div>
        )}
      </div>

      <button 
        onClick={handleLogout}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          fontSize: '16px',
          cursor: 'pointer',
          backgroundColor: '#d13438',
          color: 'white',
          border: 'none',
          borderRadius: '4px'
        }}
      >
        Sign Out
      </button>
    </div>
  );
};

const MainContent = () => {
  return (
    <>
      <UnauthenticatedTemplate>
        <LoginButton />
      </UnauthenticatedTemplate>
      
      <AuthenticatedTemplate>
        <UserInfo />
      </AuthenticatedTemplate>
    </>
  );
};

const App = ({ instance }: AppProps) => {
  return (
    <MsalProvider instance={instance}>
      <MainContent />
    </MsalProvider>
  );
};

export default App;