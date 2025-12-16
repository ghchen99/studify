import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from '../authConfig';

export function getMsalInstance() {
  return new PublicClientApplication(msalConfig);
}
