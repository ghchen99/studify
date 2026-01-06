// src/app/layout.tsx
import './globals.css';
import type { Metadata } from 'next';
import { ReactNode } from 'react';
import ClientLayout from './ClientLayout';

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
      <body className="bg-white text-gray-900 font-sans overflow-hidden">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}