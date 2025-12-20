import { Configuration, LogLevel } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID!,
    authority: process.env.NEXT_PUBLIC_AZURE_AUTHORITY!,
    redirectUri: process.env.NEXT_PUBLIC_AZURE_REDIRECT_URI!,
    knownAuthorities: [process.env.NEXT_PUBLIC_AZURE_KNOWN_AUTHORITY!],
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
  scopes: [
    'openid',
    'profile',
    'email',
    process.env.NEXT_PUBLIC_API_SCOPE!,
  ],
};
