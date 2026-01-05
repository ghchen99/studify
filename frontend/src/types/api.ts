export interface Subtopic {
  id: string;
  title: string;
  status?: 'not_started' | 'in_progress' | 'completed';
  order?: number;
  duration?: number | null;
  concepts?: string[];
  lessonId?: string | null;
  generatedAt?: string | null;
}

export interface LessonPlan {
  // The API is inconsistent: 'id' in list view, 'lesson_plan_id' in detail view
  id?: string;             
  lesson_plan_id?: string; 
  subject: string;
  topic: string;
  description: string;
  status: string;
  subtopics: Subtopic[];
  subtopic_count?: number; 
}

export interface LessonSection {
  sectionId: string;
  title: string;
  content: string;
  keyPoints: string[];
  expanded?: string | null; // Added to store expanded content
}

export interface ActiveLesson {
  lesson_id: string;
  subject: string;
  topic: string;
  subtopic: string;
  introduction: string;
  sections: LessonSection[];
}

export interface QuizQuestion {
  questionId: string;
  type: 'multiple_choice' | 'short_answer' | 'long_answer';
  question: string;
  options?: string[];
  difficulty: string;
  maxMarks?: number;
}

export interface QuizMarkedResponse {
  questionId: string;
  questionText?: string; // legacy

  originalQuestion?: string | null;
  originalCorrectAnswer?: string | null;

  userAnswer?: string | null;
  

  isCorrect: boolean | null;
  marksAwarded: number;
  maxMarks: number;

  feedback: string;
  aiGeneratedAnswer?: string | null;
}


export interface QuizResult {
  score: { percentage: number; marksAwarded: number; maxMarks: number };
  trigger_tutor: boolean;
  next_action: string;
  weak_concepts: string[];
  mastery_level?: string;
  responses?: QuizMarkedResponse[]; // 👈 ADD THIS
}
