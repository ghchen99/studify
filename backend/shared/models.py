from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class User(BaseModel):
    id: str
    userId: str
    email: Optional[str]
    name: Optional[str]
    profile: Optional[Dict[str, Any]]
    createdAt: Optional[datetime]

class LessonPlanItem(BaseModel):
    subtopicId: str
    title: str
    order: int
    estimatedDuration: Optional[int]
    concepts: List[str] = []

class LessonPlan(BaseModel):
    id: str
    userId: str
    type: str = "lessonPlan"
    subject: str
    topic: str
    status: Optional[str] = None
    structure: List[LessonPlanItem] = []
    aiGeneratedAt: Optional[datetime] = None
    approvedAt: Optional[datetime] = None


class LessonSection(BaseModel):
    sectionId: str
    title: str
    content: str
    expanded: Optional[str] = None
    diagrams: List[str] = []

class Lesson(BaseModel):
    id: str
    userId: str
    type: str = "lesson"
    lessonPlanId: Optional[str] = None
    subtopicId: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    content: Dict[str, Any]
    mediaAssets: List[Dict[str, Any]] = []
    status: Optional[str] = None
    completedAt: Optional[datetime] = None


class Question(BaseModel):
    questionId: str
    type: str
    question: str
    options: Optional[List[str]] = None
    correctAnswer: Optional[Any] = None
    markScheme: Optional[List[str]] = None
    difficulty: Optional[str] = None

class Quiz(BaseModel):
    id: str
    userId: str
    type: str = "quiz"
    lessonId: Optional[str] = None
    subtopicId: Optional[str] = None
    questions: List[Question] = []
    createdAt: Optional[datetime]

class QuizAttemptResponse(BaseModel):
    questionId: str
    userAnswer: Optional[Any] = None
    aiGeneratedAnswer: Optional[str] = None
    marksAwarded: Optional[float] = None
    maxMarks: Optional[float] = None
    feedback: Optional[str] = None
    isCorrect: Optional[bool] = None
    timeSpent: Optional[int] = None

class QuizAttempt(BaseModel):
    id: str
    userId: str
    type: str = "quizAttempt"
    quizId: str
    lessonId: Optional[str] = None
    subtopicId: Optional[str] = None
    state: Literal["in_progress", "completed", "archived"]
    responses: List[QuizAttemptResponse] = []
    score: Optional[Dict[str, Any]] = None
    completedAt: Optional[datetime]

class TutorSession(BaseModel):
    id: str
    userId: str
    type: str = "tutorSession"
    trigger: Optional[str] = None
    context: Optional[Dict[str, Any]]
    conversation: Optional[List[Dict[str, Any]]] = []
    resolved: Optional[bool] = False
    createdAt: Optional[datetime]

class Progress(BaseModel):
    id: str
    userId: str
    type: str = "progress"
    lessonPlanId: Optional[str] = None
    subtopicProgress: Optional[Dict[str, Any]] = {}
    overallProgress: Optional[Dict[str, Any]] = {}
    updatedAt: Optional[datetime]