import { Configuration, LogLevel } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: '7f63ef05-e7d4-40fc-bccd-90da58cc293c',
    authority: 'https://gpteducation.ciamlogin.com/gpteducation.onmicrosoft.com', // ✅ Added tenant domain
    redirectUri: 'http://localhost:3000/redirect',
    knownAuthorities: ['gpteducation.ciamlogin.com'], // ✅ Added this
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
            return;
          case LogLevel.Warning:
            console.warn(message);
            return;
        }
      },
    },
  },
};

export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};