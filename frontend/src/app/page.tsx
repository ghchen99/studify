'use client';

import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import LoginPage from '@/components/LoginPage';
import UserInfo from '@/components/UserInfo';

export default function HomePage() {
  return (
    <div>
      <UnauthenticatedTemplate>
        <LoginPage />
      </UnauthenticatedTemplate>
      <AuthenticatedTemplate>
        <UserInfo />
      </AuthenticatedTemplate>
    </div>
  );
}
