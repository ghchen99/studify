import { 
  MsalProvider, 
  AuthenticatedTemplate, 
  UnauthenticatedTemplate,
  useMsal,
  useIsAuthenticated
} from '@azure/msal-react';
import { IPublicClientApplication } from '@azure/msal-browser';
import { loginRequest } from './authConfig';
import UserInfo from './UserInfo'; // your updated UserInfo component

interface AppProps {
  instance: IPublicClientApplication;
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
