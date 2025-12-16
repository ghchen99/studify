'use client';

import './globals.css';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from '@/lib/msalInstance';
import { ReactNode } from 'react';

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 min-h-screen font-sans">
        {/* MSAL Provider wraps the whole app */}
        <MsalProvider instance={msalInstance}>
          <main className="container mx-auto p-4">
            {children}
          </main>
        </MsalProvider>
      </body>
    </html>
  );
}
