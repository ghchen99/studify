import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '../app';
import { getMsalInstance } from './msalInstance';

const msalInstance = getMsalInstance();

const container = document.getElementById('root')!;
const root = createRoot(container);

// Ensure MSAL processes redirect responses and an active account is set
async function bootstrap() {
  try {
    const resp = await msalInstance.handleRedirectPromise();
    // If we got a response from redirect, set that account active
    if (resp && resp.account) {
      msalInstance.setActiveAccount(resp.account);
    } else {
      // Otherwise, if there's an account already in the cache, set the first one active
      const accounts = msalInstance.getAllAccounts();
      if (accounts && accounts.length > 0 && !msalInstance.getActiveAccount()) {
        msalInstance.setActiveAccount(accounts[0]);
      }
    }
  } catch (e) {
    // ignore - rendering will still happen and app can surface auth errors
    // console.error('MSAL redirect handling error', e);
  }

  root.render(
    <React.StrictMode>
      <App instance={msalInstance} />
    </React.StrictMode>
  );
}

bootstrap();
