'use client';

import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import LoginPage from '@/components/LoginPage';
import Platform from '@/components/Platform';

export default function HomePage() {
  return (
    <div>
      <UnauthenticatedTemplate>
        <LoginPage />
      </UnauthenticatedTemplate>
      <AuthenticatedTemplate>
        <Platform />
      </AuthenticatedTemplate>
    </div>
  );
}
