'use client';

import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { LessonPlan, ActiveLesson, QuizQuestion, QuizResult } from '@/types/api';
import { LoadingButtonContent } from '@/components/ui/LoadingButtonContent';

// Import Views
import LessonView from './views/LessonView';
import QuizView from './views/QuizView';
import TutorView from './views/TutorView';
import CreateCourseView from './views/CreateCourseView';
import QuizResultView from './views/QuizResultView';

type AppState = 'DASHBOARD' | 'LESSON' | 'QUIZ' | 'RESULT' | 'TUTOR' | 'CREATE_COURSE' | 'PLAN_DETAILS';

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
  
  // Track which lessons have been generated and which is currently generating
  const [generatedLessons, setGeneratedLessons] = useState<Set<string>>(new Set());
  const [generatingLessonId, setGeneratingLessonId] = useState<string | null>(null);

  useEffect(() => {
    if (accounts.length > 0 && !instance.getActiveAccount()) {
      instance.setActiveAccount(accounts[0]);
      setAccount(accounts[0]);
    }
  }, [accounts, instance]);

  useEffect(() => {
    if (account) {
      loadDashboard();
    }
  }, [account]);

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

  const createCourse = async (data: {
    subject: string;
    topic: string;
    level: string;
  }) => {
    const res = await callApi('/api/lesson-plans', 'POST', {
      user_id: account?.localAccountId,
      subject: data.subject,
      topic: data.topic,
      level: data.level,
      auto_approve: false,
    });

    if (res) {
      setView('DASHBOARD');
      loadDashboard();
    }
  };

  const handleLogout = () => {
    instance.logoutRedirect({
      postLogoutRedirectUri: '/',
    });
  };

  const viewPlanDetails = async (planId: string) => {
    const details = await callApi(`/api/lesson-plans/details/${planId}?user_id=${account?.localAccountId}`);
    if (details) {
      setActivePlan(details);
      
      // Mark subtopics that already have an associated lessonId as generated
      const generated = new Set<string>();
      details.subtopics?.forEach((sub: any) => {
        if (sub.lessonId) generated.add(sub.id);
      });
      setGeneratedLessons(generated);
      
      setView('PLAN_DETAILS');
    }
  };

  const startSubtopic = async (planId: string, subtopicId: string) => {
    const isGenerated = generatedLessons.has(subtopicId);
    
    if (!isGenerated) {
      setGeneratingLessonId(subtopicId);
    }
    
    const data = await callApi('/api/lessons/start', 'POST', {
      user_id: account?.localAccountId,
      lesson_plan_id: planId,
      subtopic_id: subtopicId
    });
    
    if (data) {
      setGeneratedLessons(prev => new Set([...prev, subtopicId]));
      // Persist lessonId back to lesson plan so frontend and backend agree
      try {
        await callApi(`/api/lesson-plans/${planId}/subtopics/${subtopicId}/mark-generated`, 'POST', {
          user_id: account?.localAccountId,
          lessonId: data.lesson_id || data.lessonId || null
        });
      } catch (err) {
        console.warn('Failed to mark subtopic as generated on server', err);
      }
      setActiveLesson(data);
      setView('LESSON');
    }
    
    setGeneratingLessonId(null);
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
      study_time: 15
    });

    if (completeData && completeData.next_action === 'quiz') {
      const quizData = await callApi('/api/quizzes/start', 'POST', {
        user_id: account?.localAccountId,
        lesson_id: lessonId,
        subtopic_id: activeLesson?.subtopic,
        difficulty: 'mixed',
        question_count: 3
      });
      
      if (quizData) {
            const normalized = (quizData.questions || []).map((q: any) => ({
              questionId: q.questionId || q.question_id,
              type: q.type,
              question: q.question,
              options: q.options,
              difficulty: q.difficulty,
              maxMarks: q.maxMarks ?? q.max_marks ?? (q.max ? q.max : undefined)
            }));
            setActiveQuiz({ id: quizData.quiz_id, questions: normalized });
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
    const res = await callApi('/api/tutor/message', 'POST', {
      user_id: account?.localAccountId,
      session_id: sessionId,
      message
    });
    return res?.message || "I received your message."; 
  };

  const endTutor = async (sessionId: string) => {
      await callApi(`/api/tutor/end/${account?.localAccountId}/${sessionId}`, 'POST');
      setView('DASHBOARD');
      loadDashboard();
  };

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
            <div className="flex items-center gap-3">
              <div className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
                {account.username}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                Log out
              </Button>
            </div>
        </div>
      </header>

      {error && <div className="bg-red-100 text-red-800 p-3 rounded mb-4">{error}</div>}

      {/* DASHBOARD VIEW */}
      {view === 'DASHBOARD' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
             <h2 className="text-2xl font-bold text-gray-900">Your Courses</h2>
             <Button onClick={() => setView('CREATE_COURSE')}>
              + Create New Course
              </Button>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
             {lessonPlans.length === 0 && !loading && (
                <div className="col-span-full text-center py-12 border rounded-lg bg-gray-50">
                  <h3 className="text-xl font-semibold mb-2">No courses yet</h3>
                  <p className="text-gray-600 mb-6">
                    Create your first course by choosing a subject and topics you want to learn.
                  </p>
                  <Button size="lg" onClick={() => setView('CREATE_COURSE')}>
                    Create Your First Course
                  </Button>
                </div>
              )}
             
             {lessonPlans.map(plan => {
               const planId = plan.lesson_plan_id || plan.id;
               
               return (
                 <div 
                   key={planId} 
                   className="flex flex-col border p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow bg-white border-gray-200"
                 >
                   <div className="mb-4">
                      
                      <h3 className="font-bold text-lg leading-tight text-gray-900">
                        {plan.subject}
                      </h3>
                      <p className="text-sm font-medium text-gray-500 mb-3">
                        {plan.topic}
                      </p>
                      
                      {plan.description && (
                        <p className="text-sm text-gray-600 line-clamp-3 mb-4 italic">
                          "{plan.description}"
                        </p>
                      )}
                   </div>

                   <div className="mt-auto pt-4 border-t border-gray-50 flex justify-between items-center">
                      <span className="text-xs text-gray-500 font-medium">
                        {plan.subtopic_count || 0} Lessons
                      </span>
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        onClick={() => viewPlanDetails(planId!)}
                        className="hover:bg-blue-600 hover:text-white transition-colors"
                      >
                        Open Course
                      </Button>
                   </div>
                 </div>
               );
             })}
          </div>
        </div>
      )}

      {/* PLAN DETAILS VIEW */}
      {view === 'PLAN_DETAILS' && activePlan && (
        <div className="space-y-6">
          <div className="border-b pb-4">
            <h2 className="text-3xl font-bold text-gray-900">{activePlan.subject}</h2>
            <p className="text-xl text-gray-600">{activePlan.topic}</p>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Course Curriculum</h3>
            <div className="grid gap-3">
              {activePlan.subtopics?.map((sub, index) => {
                const isGenerated = generatedLessons.has(sub.id);
                const isGenerating = generatingLessonId === sub.id;
                
                return (
                  <div key={sub.id} className="flex justify-between items-center bg-white border p-4 rounded-lg shadow-sm">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-sm">
                        {index + 1}
                      </span>
                      <div>
                        <div className="font-medium">{sub.title}</div>
                      </div>
                    </div>
                    <Button 
                      onClick={() => startSubtopic(activePlan.lesson_plan_id!, sub.id)}
                      disabled={isGenerating}
                      className={`
                        gap-2 transition-all
                        ${isGenerated
                          ? 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 focus-visible:ring-2 focus-visible:ring-blue-400'
                          : 'bg-blue-100 text-blue-800 hover:bg-blue-200 active:bg-blue-300'}
                      `}
                    >
                      <LoadingButtonContent
                        loading={isGenerating}
                        loadingText="Generating..."
                        idleIcon={isGenerated ? "▶" : "✨"}
                        idleText={isGenerated ? "View Lesson" : "Generate Lesson"}
                      />
                    </Button>

                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {view === 'CREATE_COURSE' && (
        <CreateCourseView onCreate={createCourse} />
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
        <QuizResultView
          result={quizResult}
          onReturnDashboard={() => {
            setView('DASHBOARD');
            loadDashboard();
          }}
          onStartTutor={(concept) => startTutor(concept)}
        />
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