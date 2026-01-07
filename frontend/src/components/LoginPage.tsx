'use client';

import { useMsal } from '@azure/msal-react';
import { loginRequest } from '@/lib/authConfig';
import { Button } from '@/components/ui/button';
import { ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const { instance } = useMsal();
  const [loading, setLoading] = useState(false);

  const handleLogin = () => {
    setLoading(true);
    instance.loginRedirect(loginRequest);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-indigo-100 via-blue-100 to-purple-200" />

      {/* Card */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        className="
          w-full max-w-lg rounded-3xl
          bg-white/75 backdrop-blur-xl
          border border-white/40
          shadow-[0_25px_60px_rgba(99,102,241,0.3)]
          p-10 text-center
        "
      >
        {/* Logo */}
        <motion.div
          animate={{ y: [0, -8, 0] }}
          transition={{ repeat: Infinity, duration: 5, ease: 'easeInOut' }}
          className="flex justify-center mb-6"
        >
          <Image
            src="/logo-big.png"
            alt="Studify Logo"
            width={120}
            height={120}
            priority
            className="object-contain drop-shadow-md"
          />
        </motion.div>

        {/* Heading */}
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 mb-4">
          Welcome to{' '}
          <span className="bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">
            Studify
          </span>
        </h1>

        {/* Subheading */}
        <p className="text-gray-600 mb-8 leading-relaxed">
          Your AI-powered study buddy for assignments, courses,
          and those moments when your teacher makes zero sense.
        </p>

        {/* Login Button */}
        <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
          <Button
            onClick={handleLogin}
            disabled={loading}
            className="
              w-full rounded-full py-4 text-base font-semibold text-white
              bg-gradient-to-r from-indigo-500 to-purple-500
              shadow-lg shadow-indigo-500/30
              transition-all
              hover:shadow-xl hover:shadow-purple-500/40
            "
          >
            {loading ? 'Signing you in…' : 'Sign in with Microsoft'}
          </Button>
        </motion.div>

        {/* Trust */}
        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
          <ShieldCheck size={16} />
          <span>Secure login powered by Microsoft</span>
        </div>

        {/* Footer */}
        <p className="mt-8 text-xs text-gray-400">
          By signing in, you agree to our{' '}
          <a href="/terms" className="underline hover:text-gray-600">
            Terms
          </a>{' '}
          and{' '}
          <a href="/privacy" className="underline hover:text-gray-600">
            Privacy Policy
          </a>
          .
        </p>
      </motion.div>
    </div>
  );
}
