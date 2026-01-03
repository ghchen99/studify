'use client';

import './globals.css';
import { ReactNode, useState } from 'react';
import ClientProviders from './providers';
import AITutorChat from '@/components/AITutorChat';

interface ClientLayoutProps {
  children: ReactNode;
}

export default function ClientLayout({ children }: ClientLayoutProps) {
  const [chatState, setChatState] = useState<{
    isOpen: boolean;
    isExpanded: boolean;
  }>({ isOpen: false, isExpanded: false });

  return (
    <ClientProviders>
      <div className="flex h-screen w-screen overflow-hidden">
        {/* Main Content Area */}
        <main
          className={`flex-1 h-screen overflow-y-auto transition-all duration-300 ease-in-out ${
            chatState.isOpen
              ? chatState.isExpanded
                ? 'md:mr-[75vw] lg:mr-[66.666vw]'
                : 'md:mr-[50vw] lg:mr-[40vw]'
              : ''
          }`}
        >
          <div className="container mx-auto p-4 min-h-full">
            {children}
          </div>
        </main>

        {/* AI Tutor Chat */}
        <AITutorChat onStateChange={setChatState} />
      </div>
    </ClientProviders>
  );
}