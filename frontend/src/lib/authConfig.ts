import { Configuration, LogLevel } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: '7f63ef05-e7d4-40fc-bccd-90da58cc293c',
    authority: 'https://gpteducation.ciamlogin.com/gpteducation.onmicrosoft.com',
    redirectUri: 'http://localhost:3000/redirect',
    knownAuthorities: ['gpteducation.ciamlogin.com'],
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            break;
          case LogLevel.Warning:
            console.warn(message);
            break;
          case LogLevel.Info:
            console.info(message);
            break;
        }
      },
    },
  },
};

export const loginRequest = {
  scopes: ['openid', 'profile', 'email', 'api://c36c0096-67af-4aba-9b01-e9a31f550c67/access_as_user'],
};
