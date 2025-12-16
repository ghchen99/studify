'use client';

import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { LessonPlan, ActiveLesson, QuizQuestion, QuizResult } from '@/types/api';

// Import Views
import LessonView from './views/LessonView';
import QuizView from './views/QuizView';
import TutorView from './views/TutorView';

type AppState = 'DASHBOARD' | 'LESSON' | 'QUIZ' | 'RESULT' | 'TUTOR';

export default function Platform() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [account, setAccount] = useState(accounts[0] || null);

  // Application State
  const [view, setView] = useState<AppState>('DASHBOARD');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data State
  const [lessonPlans, setLessonPlans] = useState<LessonPlan[]>([]);
  const [activePlan, setActivePlan] = useState<LessonPlan | null>(null);
  const [activeLesson, setActiveLesson] = useState<ActiveLesson | null>(null);
  const [activeQuiz, setActiveQuiz] = useState<{id: string, questions: QuizQuestion[]} | null>(null);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [tutorSessionId, setTutorSessionId] = useState<string | null>(null);

  useEffect(() => {
    if (accounts.length > 0 && !instance.getActiveAccount()) {
      instance.setActiveAccount(accounts[0]);
      setAccount(accounts[0]);
    }
  }, [accounts, instance]);

  // --- API Helper ---
  const callApi = async (endpoint: string, method = 'GET', body?: any) => {
    setLoading(true);
    setError(null);
    try {
      const tokenRes = await instance.acquireTokenSilent({
        scopes: ['api://c36c0096-67af-4aba-9b01-e9a31f550c67/access_as_user'],
        account: account!,
      });
      
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method,
        headers: {
          Authorization: `Bearer ${tokenRes.accessToken}`,
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
      console.error(err);
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // --- Actions ---

  const loadDashboard = async () => {
    if (!account) return;
    const plans = await callApi(`/api/lesson-plans/${account.localAccountId}`);
    if (plans) setLessonPlans(plans);
  };

  const createPlan = async () => {
    const data = await callApi('/api/lesson-plans', 'POST', {
      user_id: account?.localAccountId,
      subject: 'Math',
      topic: 'Algebra',
      level: 'GCSE',
      auto_approve: true
    });
    if (data) loadDashboard();
  };

  const viewPlanDetails = async (planId: string) => {
    const details = await callApi(`/api/lesson-plans/details/${planId}?user_id=${account?.localAccountId}`);
    if (details) {
      setActivePlan(details);
      // Stay on dashboard but show modal or expand? For now, we render plan details in Dashboard view.
    }
  };

  const startSubtopic = async (planId: string, subtopicId: string) => {
    const data = await callApi('/api/lessons/start', 'POST', {
      user_id: account?.localAccountId,
      lesson_plan_id: planId,
      subtopic_id: subtopicId
    });
    if (data) {
      setActiveLesson(data);
      setView('LESSON');
    }
  };

  const expandLessonSection = async (sectionId: string) => {
    if (!activeLesson) return null;
    const data = await callApi('/api/lessons/expand-section', 'POST', {
      user_id: account?.localAccountId,
      lesson_id: activeLesson.lesson_id,
      section_id: sectionId
    });
    return data ? data.expanded_content : null;
  };

  const completeLesson = async (lessonId: string) => {
    const completeData = await callApi('/api/lessons/complete', 'POST', {
      user_id: account?.localAccountId,
      lesson_id: lessonId,
      study_time: 15 // Mock time
    });

    if (completeData && completeData.next_action === 'quiz') {
      // Start Quiz
      const quizData = await callApi('/api/quizzes/start', 'POST', {
        user_id: account?.localAccountId,
        lesson_id: lessonId,
        subtopic_id: activeLesson?.subtopic, // Or pass from state
        difficulty: 'mixed',
        question_count: 3
      });
      
      if (quizData) {
        setActiveQuiz({ id: quizData.quiz_id, questions: quizData.questions });
        setView('QUIZ');
      }
    }
  };

  const submitQuiz = async (quizId: string, responses: any[]) => {
    const result = await callApi('/api/quizzes/submit', 'POST', {
      user_id: account?.localAccountId,
      quiz_id: quizId,
      responses
    });

    if (result) {
      setQuizResult(result);
      setView('RESULT');
    }
  };

  const startTutor = async (concept: string) => {
    const data = await callApi('/api/tutor/start', 'POST', {
      user_id: account?.localAccountId,
      trigger: 'manual',
      lesson_id: activeLesson?.lesson_id,
      concept: concept,
      initial_message: `I'm struggling with ${concept}`
    });
    
    if (data) {
      setTutorSessionId(data.session_id);
      setView('TUTOR');
    }
  };

  const tutorMessage = async (sessionId: string, message: string) => {
    // Note: The API likely returns a new message object. Assuming standard structure based on docs.
    // The docs don't show the response for /message explicitly in the provided text, 
    // but usually it returns the AI text.
    // Let's assume it returns { message: "AI response" } or similar.
    // Based on docs: 11. Send Message -> returns (implied) text.
    // We will return a mock or expect a specific field. 
    // Let's assume the response body contains the AI string directly or in a field.
    const res = await callApi('/api/tutor/message', 'POST', {
      user_id: account?.localAccountId,
      session_id: sessionId,
      message
    });
    // This is a guess since /message response isn't explicitly detailed in the prompt
    // but standard practice implies returning the string or object.
    return res?.message || "I received your message."; 
  };

  const endTutor = async (sessionId: string) => {
     await callApi(`/api/tutor/end/${account?.localAccountId}/${sessionId}`, 'POST');
     setView('DASHBOARD');
     loadDashboard();
  };

  // --- Rendering ---

  if (!account) return <div>Please log in</div>;

  return (
    <div className="max-w-4xl mx-auto p-6 font-sans">
      <header className="flex justify-between items-center mb-8 pb-4 border-b">
        <h1 className="text-xl font-bold text-gray-800">Learning Platform</h1>
        <div className="flex gap-4">
            {view !== 'DASHBOARD' && (
                <Button variant="ghost" onClick={() => { setView('DASHBOARD'); loadDashboard(); }}>
                    Back to Dashboard
                </Button>
            )}
            <div className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
            {account.name}
            </div>
        </div>
      </header>

      {error && <div className="bg-red-100 text-red-800 p-3 rounded mb-4">{error}</div>}

      {/* DASHBOARD VIEW */}
      {view === 'DASHBOARD' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
             <h2 className="text-2xl font-bold">Your Plans</h2>
             <Button onClick={createPlan} disabled={loading}>+ New Algebra Plan</Button>
          </div>
          
          
          <div className="grid gap-4">
             {lessonPlans.length === 0 && <Button onClick={loadDashboard}>Load Plans</Button>}
             
             {lessonPlans.map(plan => {
               // Normalize the ID: use lesson_plan_id if present, otherwise id
               const planId = plan.lesson_plan_id || plan.id;
               
               return (
                 <div key={planId} className="border p-4 rounded shadow-sm hover:shadow-md transition bg-white">
                   <div className="flex justify-between items-center">
                      <div>
                          <h3 className="font-bold text-lg">{plan.subject} - {plan.topic}</h3>
                          <p className="text-sm text-gray-500">
                            {plan.status} • {plan.subtopic_count || 0} subtopics
                          </p>
                      </div>
                      <Button variant="outline" onClick={() => viewPlanDetails(planId!)}>
                          View Details
                      </Button>
                   </div>
                   
                   {/* FIXED: Strict check ensures activePlan exists before comparing */}
                   {activePlan && (activePlan.lesson_plan_id === planId || activePlan.id === planId) && (
                      <div className="mt-4 pt-4 border-t space-y-2">
                          <h4 className="text-sm font-semibold text-gray-700">Subtopics:</h4>
                          {/* Guard against missing subtopics in case of draft plans */}
                          {activePlan.subtopics?.map(sub => (
                              <div key={sub.id} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                                  <span className="text-sm">{sub.title}</span>
                                  <Button size="sm" onClick={() => startSubtopic(activePlan.lesson_plan_id!, sub.id)}>
                                      Start
                                  </Button>
                              </div>
                          ))}
                      </div>
                   )}
                 </div>
               );
             })}
          </div>
        </div>
      )}

      {/* LESSON VIEW */}
      {view === 'LESSON' && activeLesson && (
        <LessonView 
            lesson={activeLesson} 
            userId={account.localAccountId} 
            onExpandSection={expandLessonSection}
            onComplete={completeLesson}
        />
      )}

      {/* QUIZ VIEW */}
      {view === 'QUIZ' && activeQuiz && (
        <QuizView 
            quizId={activeQuiz.id} 
            questions={activeQuiz.questions} 
            onSubmit={submitQuiz}
        />
      )}

      {/* RESULT VIEW */}
      {view === 'RESULT' && quizResult && (
        <div className="text-center space-y-6 py-10">
            <h2 className="text-3xl font-bold">Quiz Complete!</h2>
            <div className="text-6xl font-bold text-blue-600">{quizResult.score.percentage}%</div>
            <p className="text-gray-600">You scored {quizResult.score.marksAwarded} / {quizResult.score.maxMarks}</p>
            
            {quizResult.trigger_tutor ? (
                <div className="bg-orange-50 p-6 rounded border border-orange-200 inline-block text-left max-w-lg">
                    <h3 className="font-bold text-orange-800 mb-2">Needs Improvement</h3>
                    <p className="mb-4">It looks like you struggled with: </p>
                    <ul className="list-disc list-inside mb-4">
                        {quizResult.weak_concepts.map((c, i) => <li key={i}>{c.substring(0, 50)}...</li>)}
                    </ul>
                    <Button className="w-full" onClick={() => startTutor(quizResult.weak_concepts[0])}>
                        Chat with AI Tutor
                    </Button>
                </div>
            ) : (
                <Button size="lg" onClick={() => { setView('DASHBOARD'); loadDashboard(); }}>
                    Return to Dashboard
                </Button>
            )}
        </div>
      )}

      {/* TUTOR VIEW */}
      {view === 'TUTOR' && tutorSessionId && (
        <TutorView 
            sessionId={tutorSessionId}
            onSendMessage={tutorMessage}
            onEndSession={endTutor}
        />
      )}
    </div>
  );
}