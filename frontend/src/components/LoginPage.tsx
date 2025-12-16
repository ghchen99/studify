'use client';

import { useMsal } from '@azure/msal-react';
import { loginRequest } from '@/lib/authConfig';
import { Button } from '@/components/ui/button';
import { GraduationCap, ShieldCheck } from 'lucide-react';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion'; // Use Framer Motion for animations

export default function LoginPage() {
  const { instance } = useMsal();
  const [loading, setLoading] = useState(false);

  const handleLogin = () => {
    setLoading(true);
    instance.loginRedirect(loginRequest);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-100 via-indigo-200 to-purple-300 opacity-80 -z-10" />


      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 relative z-10">
        
        {/* Header Section */}
        <motion.div 
          className="flex flex-col items-center text-center mb-8"
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          transition={{ duration: 1 }}
        >
          <div className="bg-blue-100 text-blue-600 p-3 rounded-full mb-4">
            <GraduationCap size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 leading-tight mb-4">
            Welcome to Learning.AI
          </h1>
          <p className="text-gray-600 mb-6">
            Sign in to access your courses, assignments, and learning resources. Let's get started!
          </p>
        </motion.div>

        {/* Login Button */}
        <motion.div 
          initial={{ scale: 1 }} 
          whileHover={{ scale: 1.05 }} 
          transition={{ duration: 0.2 }}
        >
          <Button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-base font-medium rounded-lg"
          >
            {loading ? 'Signing in...' : 'Sign in with Microsoft'}
          </Button>
        </motion.div>

        {/* Trust Section */}
        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
          <ShieldCheck size={16} />
          <span>Secure login powered by Microsoft</span>
        </div>

        {/* Footer Section */}
        <div className="mt-8 text-center text-xs text-gray-400">
          <p>
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
        </div>
      </div>
    </div>
  );
}
