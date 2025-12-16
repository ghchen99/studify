import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { useState, useEffect } from 'react';

interface LessonPlanResponse {
  lesson_plan_id: string;
  subject: string;
  topic: string;
  status: string;
  subtopics: any[];
  progress_initialized: boolean;
}

interface LessonResponse {
  lesson_id: string;
  subject: string;
  topic: string;
  subtopic: string;
  introduction: string;
  sections: any[];
  summary: string;
  key_terms: string[];
  status: string;
}

const UserInfo = () => {
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

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API Error: ${response.status} ${text}`);
      }

      return await response.json();
    } catch (err: any) {
      setApiError(err.message);
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // ================= API CALLS =================
  const createLessonPlan = async () => {
    if (!account) return;
    const body = {
      user_id: account.localAccountId,
      subject: 'Mathematics',
      topic: 'Algebra Basics',
      level: 'Beginner',
      auto_approve: true
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
      subtopic_id
    };

    const data = await callApi('/api/lessons/start', 'POST', body);
    if (data) setLesson(data);
  };

  // =================================================

  if (!account) return <p>Loading account info...</p>;

  return (
    <div style={{ padding: '50px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>✅ Logged in as {account.name || account.username}</h1>

      {/* Lesson Plan Section */}
      <div style={{ marginTop: '20px', padding: '20px', background: '#e8f4f8', borderRadius: '8px' }}>
        <h2>Lesson Plan</h2>
        <button onClick={createLessonPlan} disabled={loading} style={{ marginBottom: '10px' }}>
          {loading ? 'Creating...' : 'Create Lesson Plan'}
        </button>
        {lessonPlan && (
          <div>
            <p><strong>Lesson Plan ID:</strong> {lessonPlan.lesson_plan_id}</p>
            <p><strong>Topic:</strong> {lessonPlan.topic}</p>
            <p><strong>Status:</strong> {lessonPlan.status}</p>
            <p><strong>Subtopics:</strong> {lessonPlan.subtopics.map(s => s.name).join(', ')}</p>
          </div>
        )}
        <button onClick={getLessonPlans} style={{ marginTop: '10px' }}>Get All Lesson Plans</button>
      </div>

      {/* Lesson Section */}
      {lessonPlan && (
        <div style={{ marginTop: '20px', padding: '20px', background: '#f0f0f0', borderRadius: '8px' }}>
          <h2>Lesson</h2>
          <button onClick={startLesson} disabled={loading}>
            {loading ? 'Starting...' : 'Start Lesson'}
          </button>
          {lesson && (
            <div>
              <p><strong>Lesson ID:</strong> {lesson.lesson_id}</p>
              <p><strong>Subtopic:</strong> {lesson.subtopic}</p>
              <p><strong>Introduction:</strong> {lesson.introduction}</p>
            </div>
          )}
        </div>
      )}

      {apiError && (
        <div style={{ marginTop: '20px', padding: '10px', background: '#f8d7da', borderRadius: '4px', color: '#721c24' }}>
          <p>❌ {apiError}</p>
        </div>
      )}
    </div>
  );
};

export default UserInfo;
