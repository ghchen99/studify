'use client';

import { ReactNode } from 'react';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from '@/lib/msalInstance';

export default function ClientProviders({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <MsalProvider instance={msalInstance}>
      {children}
    </MsalProvider>
  );
}
