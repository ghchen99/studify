// src/app/layout.tsx
import './globals.css';
import type { Metadata } from 'next';
import { ReactNode } from 'react';
import ClientLayout from './ClientLayout';

export const metadata: Metadata = {
  title: 'Studify',
  description: 'An AI tutor for when your teacher makes zero sense.',
  icons: {
    icon: [
      { url: '/logo-big.png', sizes: '32x32', type: 'image/png' },
    ],
  },
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