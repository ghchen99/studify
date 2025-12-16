'use client';

import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

interface LessonPlanResponse {
  lesson_plan_id: string;
  subject: string;
  topic: string;
  status: string;
  subtopics: { id: string; name: string }[];
}

interface LessonResponse {
  lesson_id: string;
  subject: string;
  topic: string;
  subtopic: string;
  introduction: string;
}

export default function UserInfo() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [account, setAccount] = useState(accounts[0] || null);

  const [lessonPlan, setLessonPlan] = useState<LessonPlanResponse | null>(null);
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (accounts.length > 0 && !instance.getActiveAccount()) {
      instance.setActiveAccount(accounts[0]);
      setAccount(accounts[0]);
    }
  }, [accounts, instance]);

  const acquireToken = async () => {
    if (!account) return null;
    const tokenResponse = await instance.acquireTokenSilent({
      scopes: ['api://c36c0096-67af-4aba-9b01-e9a31f550c67/access_as_user'],
      account,
    });
    return tokenResponse.accessToken;
  };

  const callApi = async (endpoint: string, method = 'GET', body?: any) => {
    setLoading(true);
    setApiError(null);
    try {
      const token = await acquireToken();
      if (!token) throw new Error('No access token');

      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API Error: ${res.status} ${text}`);
      }

      return await res.json();
    } catch (err: any) {
      setApiError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const createLessonPlan = async () => {
    if (!account) return;
    const body = {
      user_id: account.localAccountId,
      subject: 'Mathematics',
      topic: 'Algebra Basics',
      level: 'Beginner',
      auto_approve: true,
    };
    const data = await callApi('/api/lesson-plans', 'POST', body);
    if (data) setLessonPlan(data);
  };

  const getLessonPlans = async () => {
    if (!account) return;
    const data = await callApi(`/api/lesson-plans/${account.localAccountId}`);
    console.log('User lesson plans:', data);
  };

  const startLesson = async () => {
    if (!account || !lessonPlan) return;
    const subtopic_id = lessonPlan.subtopics?.[0]?.id;
    if (!subtopic_id) {
      setApiError('No subtopics found in lesson plan');
      return;
    }

    const body = {
      user_id: account.localAccountId,
      lesson_plan_id: lessonPlan.lesson_plan_id,
      subtopic_id,
    };

    const data = await callApi('/api/lessons/start', 'POST', body);
    if (data) setLesson(data);
  };

  if (!account) return <p>Loading account info...</p>;

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold text-green-700">✅ Logged in as {account.name || account.username}</h1>

      {/* Lesson Plan Section */}
      <div className="bg-blue-50 p-4 rounded-lg space-y-2">
        <h2 className="text-xl font-semibold">Lesson Plan</h2>
        <Button onClick={createLessonPlan} disabled={loading}>
          {loading ? 'Creating...' : 'Create Lesson Plan'}
        </Button>
        {lessonPlan && (
          <div className="mt-2">
            <p><strong>Lesson Plan ID:</strong> {lessonPlan.lesson_plan_id}</p>
            <p><strong>Topic:</strong> {lessonPlan.topic}</p>
            <p><strong>Status:</strong> {lessonPlan.status}</p>
            <p><strong>Subtopics:</strong> {lessonPlan.subtopics.map(s => s.name).join(', ')}</p>
          </div>
        )}
        <Button onClick={getLessonPlans} variant="outline">
          Get All Lesson Plans
        </Button>
      </div>

      {/* Lesson Section */}
      {lessonPlan && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-2">
          <h2 className="text-xl font-semibold">Lesson</h2>
          <Button onClick={startLesson} disabled={loading}>
            {loading ? 'Starting...' : 'Start Lesson'}
          </Button>
          {lesson && (
            <div className="mt-2">
              <p><strong>Lesson ID:</strong> {lesson.lesson_id}</p>
              <p><strong>Subtopic:</strong> {lesson.subtopic}</p>
              <p><strong>Introduction:</strong> {lesson.introduction}</p>
            </div>
          )}
        </div>
      )}

      {/* API Error */}
      {apiError && (
        <div className="bg-red-100 text-red-800 p-2 rounded">
          ❌ {apiError}
        </div>
      )}
    </div>
  );
}
