'use client';

import { useMsal } from '@azure/msal-react';
import { loginRequest } from '@/lib/authConfig';
import { Button } from '@/components/ui/button';

export default function LoginButton() {
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  return (
    <div className="flex flex-col items-center justify-center h-[60vh]">
      <h1 className="text-3xl font-bold mb-6">Simple Login Test</h1>
      <Button onClick={handleLogin} className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg">
        Sign In with Microsoft
      </Button>
    </div>
  );
}
