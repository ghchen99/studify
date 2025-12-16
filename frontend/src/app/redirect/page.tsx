'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { msalInstance } from '@/lib/msalInstance';

export default function RedirectPage() {
  const router = useRouter();

  useEffect(() => {
    msalInstance.handleRedirectPromise().then((resp) => {
      if (resp?.account) msalInstance.setActiveAccount(resp.account);
      else if (!msalInstance.getActiveAccount()) {
        const accounts = msalInstance.getAllAccounts();
        if (accounts.length) msalInstance.setActiveAccount(accounts[0]);
      }
      router.push('/');
    });
  }, [router]);

  return <p>Loading...</p>;
}
