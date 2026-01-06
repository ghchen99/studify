from pydantic import BaseModel, Field, ConfigDict
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
    status: str = "not_started"
    lessonId: Optional[str] = None
    generatedAt: Optional[datetime] = None

class LessonPlan(BaseModel):
    id: str
    userId: str
    type: str = "lessonPlan"
    subject: str
    topic: str
    description: Optional[str] = None  # ADD THIS LINE
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
    status: str = "not_started"
    completedAt: Optional[datetime] = None


class Question(BaseModel):
    questionId: str
    type: str
    question: str
    options: Optional[List[str]] = None
    correctAnswer: Optional[Any] = None
    markScheme: Optional[List[str]] = None
    maxMarks: Optional[float] = None
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

# TutorSession removed

class Progress(BaseModel):
    id: str
    userId: str
    type: str = "progress"
    lessonPlanId: Optional[str] = None
    subtopicProgress: Optional[Dict[str, Any]] = {}
    overallProgress: Optional[Dict[str, Any]] = {}
    updatedAt: Optional[datetime]

    # ==================== REQUEST/RESPONSE MODELS ====================

class CreateLessonPlanRequest(BaseModel):
    """Request to create a new lesson plan"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "alice123",
            "subject": "Math",
            "topic": "Algebra",
            "level": "GCSE",
            "auto_approve": False
        }
    })
    
    user_id: str = Field(..., description="User identifier")
    subject: str = Field(..., description="Subject name (e.g., 'Math', 'Biology')")
    topic: str = Field(..., description="Topic name (e.g., 'Algebra', 'Cell Biology')")
    level: str = Field(default="GCSE", description="Education level")
    auto_approve: bool = Field(default=False, description="Automatically approve the plan")


class LessonPlanResponse(BaseModel):
    """Response containing lesson plan details"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "lesson_plan_id": "abc123",
            "subject": "Math",
            "topic": "Algebra",
            "description": "An introduction to algebraic concepts.",
            "subtopics": [
                {
                    "id": "sub1",
                    "title": "Introduction to Variables",
                    "order": 1,
                    "duration": 30,
                    "concepts": ["variables", "constants", "expressions"]
                }
            ],
        }
    })
    
    lesson_plan_id: str
    subject: str
    topic: str
    description: str
    subtopics: List[Dict[str, Any]]


# Note: ApproveLessonPlanRequest removed; lesson plan status/progress flag removed


class StartLessonRequest(BaseModel):
    """Request to start a lesson"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "alice123",
            "lesson_plan_id": "abc123",
            "subtopic_id": "sub1"
        }
    })
    
    user_id: str
    lesson_plan_id: str
    subtopic_id: str


class LessonResponse(BaseModel):
    """Response containing lesson content"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "lesson_id": "lesson123",
            "subject": "Math",
            "topic": "Algebra",
            "subtopic": "Introduction to Variables",
            "introduction": "Variables are fundamental building blocks...",
            "sections": [
                {
                    "section_id": "sec1",
                    "title": "What is a Variable?",
                    "content": "A variable is a symbol...",
                    "key_points": ["Represents unknown values", "Can change"],
                    "expanded": None
                }
            ],
            "summary": "Variables allow us to represent...",
            "key_terms": ["variable", "constant", "expression"],
            "status": "active"
        }
    })
    
    lesson_id: str
    subject: str
    topic: str
    subtopic: str
    introduction: str
    sections: List[Dict[str, Any]]
    summary: str
    key_terms: List[str]
    status: str


class ExpandSectionRequest(BaseModel):
    """Request to expand a lesson section"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "alice123",
            "lesson_id": "lesson123",
            "section_id": "sec1"
        }
    })
    
    user_id: str
    lesson_id: str
    section_id: str


class ExpandedSectionResponse(BaseModel):
    """Response with expanded section content"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "section_id": "sec1",
            "expanded_content": "Let's dive deeper into variables..."
        }
    })
    
    section_id: str
    expanded_content: str


class CompleteLessonRequest(BaseModel):
    """Request to complete a lesson"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "alice123",
            "lesson_id": "lesson123",
            "study_time": 25
        }
    })
    
    user_id: str
    lesson_id: str
    study_time: int = Field(default=0, description="Time spent in minutes")


class CompletionResponse(BaseModel):
    """Response after lesson completion"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "lesson_completed": True,
            "next_action": "quiz",
            "progress": {
                "percent_complete": 12.5,
                "total_study_time": 25
            }
        }
    })
    
    lesson_completed: bool
    next_action: str
    progress: Dict[str, Any]


class StartQuizRequest(BaseModel):
    """Request to start a quiz"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "alice123",
            "lesson_id": "lesson123",
            "subtopic_id": "sub1",
            "difficulty": "mixed",
            "question_count": 5
        }
    })
    
    user_id: str
    lesson_id: str
    subtopic_id: str
    difficulty: str = Field(default="mixed", description="Question difficulty")
    question_count: int = Field(default=5, description="Number of questions")


class QuizResponse(BaseModel):
    """Response containing quiz questions"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "quiz_id": "quiz123",
            "questions": [
                {
                    "question_id": "q1",
                    "type": "multiple_choice",
                    "question": "What is a variable?",
                    "options": ["A fixed value", "A symbol for unknown", "A number", "An operator"],
                    "difficulty": "easy"
                }
            ],
            "total_questions": 5
        }
    })
    
    quiz_id: str
    questions: List[Dict[str, Any]]
    total_questions: int


class QuizSubmissionRequest(BaseModel):
    """Request to submit quiz answers"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "alice123",
            "quiz_id": "quiz123",
            "responses": [
                {
                    "questionId": "q1",
                    "userAnswer": "A symbol for unknown"
                },
                {
                    "questionId": "q2",
                    "userAnswer": "Variables represent values that can change."
                },
                {
                    "questionId": "q3",
                    "userAnswer": "Variables can store different values. They are represented by letters and used in equations."
                }
            ]
        }
    })
    
    user_id: str
    quiz_id: str
    responses: List[Dict[str, Any]] = Field(
        ...,
        description="List of responses with questionId and userAnswer"
    )


class QuizResultResponse(BaseModel):
    """Response with quiz results"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "attempt_id": "attempt123",
            "score": {
                "percentage": 75.0,
                "marks_awarded": 15.0,
                "max_marks": 20.0
            },
            "responses": [
                {
                    "question_id": "q1",
                    "is_correct": True,
                    "marks_awarded": 1.0,
                    "max_marks": 1.0,
                    "feedback": "Correct!",
                    "ai_generated_answer": None
                }
            ],
            "mastery_level": "intermediate",
            "next_action": "continue",
            "trigger_tutor": False,
            "weak_concepts": []
        }
    })
    
    attempt_id: str
    score: Dict[str, Any]
    responses: List[Dict[str, Any]]
    mastery_level: Optional[str] = "unranked"
    next_action: str
    trigger_tutor: bool
    weak_concepts: List[str]


# Tutor request/response models removed


class DashboardResponse(BaseModel):
    """Response with user dashboard data"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user": {
                "total_study_time": 150,
                "overall_progress": 25.5,
                "average_score": 72.3
            },
            "lesson_plans": [
                {
                    "id": "abc123",
                    "subject": "Math",
                    "topic": "Algebra",
                    "status": "approved",
                    "subtopic_count": 8,
                    "progress": {
                        "percent_complete": 25.0,
                        "average_score": 75.0
                    }
                }
            ],
            
            "recommendations": [
                "Continue Math - Algebra (25% complete)",
                "Review Biology - Cells (average score: 55%)"
            ]
        }
    })
    
    user: Dict[str, Any]
    lesson_plans: List[Dict[str, Any]]
    # active_tutor_sessions removed
    recommendations: List[str]
