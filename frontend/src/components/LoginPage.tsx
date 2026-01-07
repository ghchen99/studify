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
      <div className="fixed inset-0 bg-gradient-to-br from-blue-100 via-indigo-200 to-purple-300 -z-10" />

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        className="w-full max-w-lg rounded-3xl bg-white/80 backdrop-blur-xl shadow-2xl p-10 text-center"
      >
        {/* Logo */}
        <motion.div
          animate={{ y: [0, -8, 0] }}
          transition={{ repeat: Infinity, duration: 4, ease: 'easeInOut' }}
          className="flex justify-center mb-6"
        >
          <Image
            src="/logo-big.png"
            alt="Studify Logo"
            width={120}
            height={120}
            priority
            className="object-contain"
          />
        </motion.div>

        {/* Heading */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-blue-600">Studify</span>
        </h1>

        <p className="text-gray-600 mb-8 leading-relaxed">
          Your personalized learning hub for courses, assignments, and academic success.
        </p>

        {/* Login Button */}
        <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.98 }}>
          <Button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 text-base font-semibold rounded-xl shadow-lg"
          >
            {loading ? 'Signing in...' : 'Sign in with Microsoft'}
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
