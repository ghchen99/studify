'use client';

import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import LoginButton from '@/components/LoginButton';
import UserInfo from '@/components/UserInfo';

export default function HomePage() {
  return (
    <div>
      <UnauthenticatedTemplate>
        <LoginButton />
      </UnauthenticatedTemplate>
      <AuthenticatedTemplate>
        <UserInfo />
      </AuthenticatedTemplate>
    </div>
  );
}
