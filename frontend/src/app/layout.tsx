import './globals.css';
import type { Metadata } from 'next';
import { ReactNode } from 'react';
import ClientProviders from './providers';

export const metadata: Metadata = {
  title: 'gpt-edu',
  description: 'AI-powered learning platform',
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 min-h-screen font-sans">
        <ClientProviders>
          <main className="container mx-auto p-4">
            {children}
          </main>
        </ClientProviders>
      </body>
    </html>
  );
}
