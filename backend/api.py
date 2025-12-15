"""
FastAPI Learning Platform API
RESTful API for the AI-powered learning platform
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from edu_platform import LearningPlatform

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress verbose logs
logging.getLogger("azure.cosmos._cosmos_http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

# Initialize FastAPI app
app = FastAPI(
    title="Learning Platform API",
    description="AI-powered adaptive learning platform with lesson plans, quizzes, and tutoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize platform
platform = LearningPlatform()


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateLessonPlanRequest(BaseModel):
    """Request to create a new lesson plan"""
    user_id: str = Field(..., description="User identifier")
    subject: str = Field(..., description="Subject name (e.g., 'Math', 'Biology')")
    topic: str = Field(..., description="Topic name (e.g., 'Algebra', 'Cell Biology')")
    level: str = Field(default="GCSE", description="Education level")
    auto_approve: bool = Field(default=False, description="Automatically approve the plan")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "subject": "Math",
                "topic": "Algebra",
                "level": "GCSE",
                "auto_approve": False
            }
        }


class LessonPlanResponse(BaseModel):
    """Response containing lesson plan details"""
    lesson_plan_id: str
    subject: str
    topic: str
    status: str
    subtopics: List[Dict[str, Any]]
    progress_initialized: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_plan_id": "abc123",
                "subject": "Math",
                "topic": "Algebra",
                "status": "draft",
                "subtopics": [
                    {
                        "id": "sub1",
                        "title": "Introduction to Variables",
                        "order": 1,
                        "duration": 30,
                        "concepts": ["variables", "constants", "expressions"]
                    }
                ],
                "progress_initialized": False
            }
        }


class ApproveLessonPlanRequest(BaseModel):
    """Request to approve a lesson plan"""
    user_id: str
    plan_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "plan_id": "abc123"
            }
        }


class StartLessonRequest(BaseModel):
    """Request to start a lesson"""
    user_id: str
    lesson_plan_id: str
    subtopic_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "lesson_plan_id": "abc123",
                "subtopic_id": "sub1"
            }
        }


class LessonResponse(BaseModel):
    """Response containing lesson content"""
    lesson_id: str
    subject: str
    topic: str
    subtopic: str
    introduction: str
    sections: List[Dict[str, Any]]
    summary: str
    key_terms: List[str]
    status: str
    
    class Config:
        json_schema_extra = {
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
        }


class ExpandSectionRequest(BaseModel):
    """Request to expand a lesson section"""
    user_id: str
    lesson_id: str
    section_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "lesson_id": "lesson123",
                "section_id": "sec1"
            }
        }


class ExpandedSectionResponse(BaseModel):
    """Response with expanded section content"""
    section_id: str
    expanded_content: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "section_id": "sec1",
                "expanded_content": "Let's dive deeper into variables..."
            }
        }


class CompleteLessonRequest(BaseModel):
    """Request to complete a lesson"""
    user_id: str
    lesson_id: str
    study_time: int = Field(default=0, description="Time spent in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "lesson_id": "lesson123",
                "study_time": 25
            }
        }


class CompletionResponse(BaseModel):
    """Response after lesson completion"""
    lesson_completed: bool
    next_action: str
    progress: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_completed": True,
                "next_action": "quiz",
                "progress": {
                    "percent_complete": 12.5,
                    "total_study_time": 25
                }
            }
        }


class StartQuizRequest(BaseModel):
    """Request to start a quiz"""
    user_id: str
    lesson_id: str
    subtopic_id: str
    difficulty: str = Field(default="mixed", description="Question difficulty")
    question_count: int = Field(default=5, description="Number of questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "lesson_id": "lesson123",
                "subtopic_id": "sub1",
                "difficulty": "mixed",
                "question_count": 5
            }
        }


class QuizResponse(BaseModel):
    """Response containing quiz questions"""
    quiz_id: str
    questions: List[Dict[str, Any]]
    total_questions: int
    
    class Config:
        json_schema_extra = {
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
        }


class QuizSubmissionRequest(BaseModel):
    """Request to submit quiz answers"""
    user_id: str
    quiz_id: str
    responses: List[Dict[str, Any]] = Field(
        ...,
        description="List of responses with questionId and userAnswer/userBulletPoints"
    )
    
    class Config:
        json_schema_extra = {
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
                        "userAnswer": "Variables represent values that can change.",
                        "userBulletPoints": None
                    },
                    {
                        "questionId": "q3",
                        "userAnswer": None,
                        "userBulletPoints": [
                            "Variables can store different values",
                            "They are represented by letters",
                            "Used in equations and expressions"
                        ]
                    }
                ]
            }
        }


class QuizResultResponse(BaseModel):
    """Response with quiz results"""
    attempt_id: str
    score: Dict[str, Any]
    responses: List[Dict[str, Any]]
    mastery_level: str
    next_action: str
    trigger_tutor: bool
    weak_concepts: List[str]
    
    class Config:
        json_schema_extra = {
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
        }


class StartTutorRequest(BaseModel):
    """Request to start a tutor session"""
    user_id: str
    trigger: str = Field(..., description="What triggered the session (e.g., 'quiz_struggle', 'manual')")
    lesson_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    question_id: Optional[str] = None
    concept: Optional[str] = None
    initial_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "trigger": "quiz_struggle",
                "lesson_id": "lesson123",
                "subtopic_id": "sub1",
                "concept": "variables",
                "initial_message": "I'm confused about how variables work"
            }
        }


class TutorResponse(BaseModel):
    """Response from tutor"""
    session_id: str
    message: str
    context: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session123",
                "message": "I understand you're finding variables confusing. Let's break it down...",
                "context": {
                    "lesson_id": "lesson123",
                    "concept": "variables"
                }
            }
        }


class SendTutorMessageRequest(BaseModel):
    """Request to send message to tutor"""
    user_id: str
    session_id: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "alice123",
                "session_id": "session123",
                "message": "Can you give me an example?"
            }
        }


class DashboardResponse(BaseModel):
    """Response with user dashboard data"""
    user: Dict[str, Any]
    lesson_plans: List[Dict[str, Any]]
    active_tutor_sessions: int
    recommendations: List[str]
    
    class Config:
        json_schema_extra = {
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
                "active_tutor_sessions": 1,
                "recommendations": [
                    "Continue Math - Algebra (25% complete)",
                    "Review Biology - Cells (average score: 55%)"
                ]
            }
        }


# ==================== LESSON PLAN ENDPOINTS ====================

@app.post(
    "/api/lesson-plans",
    response_model=LessonPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lesson plan",
    description="Generate an AI-powered lesson plan for a given subject and topic"
)
async def create_lesson_plan(request: CreateLessonPlanRequest):
    """
    Create a new lesson plan using AI.
    
    The system will generate a structured lesson plan with multiple subtopics,
    each containing key concepts and estimated duration.
    """
    try:
        result = platform.create_lesson_plan(
            user_id=request.user_id,
            subject=request.subject,
            topic=request.topic,
            level=request.level,
            auto_approve=request.auto_approve
        )
        
        return LessonPlanResponse(
            lesson_plan_id=result["lessonPlan"].id,
            subject=result["lessonPlan"].subject,
            topic=result["lessonPlan"].topic,
            status=result["status"],
            subtopics=result["subtopics"],
            progress_initialized=result.get("progressInitialized", False)
        )
    except Exception as e:
        logger.error(f"Error creating lesson plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lesson plan: {str(e)}"
        )


@app.post(
    "/api/lesson-plans/approve",
    response_model=Dict[str, str],
    summary="Approve a lesson plan",
    description="Approve a lesson plan and initialize progress tracking"
)
async def approve_lesson_plan(request: ApproveLessonPlanRequest):
    """
    Approve a lesson plan and initialize progress tracking.
    
    Once approved, the student can start working through the lessons.
    """
    try:
        approved_plan = platform.approve_lesson_plan(
            user_id=request.user_id,
            plan_id=request.plan_id
        )
        
        return {
            "status": "approved",
            "lesson_plan_id": approved_plan.id,
            "message": "Lesson plan approved and progress initialized"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error approving lesson plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve lesson plan: {str(e)}"
        )


@app.get(
    "/api/lesson-plans/{user_id}",
    response_model=List[Dict[str, Any]],
    summary="Get all lesson plans for a user",
    description="Retrieve all lesson plans associated with a user"
)
async def get_lesson_plans(user_id: str):
    """Get all lesson plans for a user"""
    try:
        plans = platform.lesson_plans.get_user_lesson_plans(user_id)
        return [
            {
                "id": plan.id,
                "subject": plan.subject,
                "topic": plan.topic,
                "status": plan.status,
                "subtopic_count": len(plan.structure),
                "created_at": plan.aiGeneratedAt.isoformat() if plan.aiGeneratedAt else None
            }
            for plan in plans
        ]
    except Exception as e:
        logger.error(f"Error retrieving lesson plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve lesson plans: {str(e)}"
        )


# ==================== LESSON ENDPOINTS ====================

@app.post(
    "/api/lessons/start",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a lesson",
    description="Generate or retrieve lesson content for a subtopic"
)
async def start_lesson(request: StartLessonRequest):
    """
    Start a lesson for a specific subtopic.
    
    If the lesson already exists, it will be returned. Otherwise, new content
    will be generated using AI.
    """
    try:
        result = platform.start_lesson(
            user_id=request.user_id,
            lesson_plan_id=request.lesson_plan_id,
            subtopic_id=request.subtopic_id
        )
        
        return LessonResponse(
            lesson_id=result["lessonId"],
            subject=result["subject"],
            topic=result["topic"],
            subtopic=result["subtopic"],
            introduction=result["introduction"],
            sections=result["sections"],
            summary=result["summary"],
            key_terms=result["keyTerms"],
            status=result["status"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting lesson: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start lesson: {str(e)}"
        )


@app.post(
    "/api/lessons/expand-section",
    response_model=ExpandedSectionResponse,
    summary="Expand a lesson section",
    description="Get more detailed content for a specific lesson section"
)
async def expand_section(request: ExpandSectionRequest):
    """
    Expand a lesson section with more detailed content, examples, and explanations.
    """
    try:
        result = platform.expand_lesson_section(
            user_id=request.user_id,
            lesson_id=request.lesson_id,
            section_id=request.section_id
        )
        
        return ExpandedSectionResponse(
            section_id=result["sectionId"],
            expanded_content=result["expandedContent"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error expanding section: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expand section: {str(e)}"
        )


@app.post(
    "/api/lessons/complete",
    response_model=CompletionResponse,
    summary="Complete a lesson",
    description="Mark a lesson as complete and update progress"
)
async def complete_lesson(request: CompleteLessonRequest):
    """
    Mark a lesson as complete and update the student's progress.
    
    This will track study time and update overall completion percentage.
    """
    try:
        result = platform.complete_lesson(
            user_id=request.user_id,
            lesson_id=request.lesson_id,
            study_time=request.study_time
        )
        
        return CompletionResponse(
            lesson_completed=result["lessonCompleted"],
            next_action=result["nextAction"],
            progress=result["progress"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing lesson: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete lesson: {str(e)}"
        )


# ==================== QUIZ ENDPOINTS ====================

@app.post(
    "/api/quizzes/start",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a quiz",
    description="Generate a quiz for a completed lesson"
)
async def start_quiz(request: StartQuizRequest):
    """
    Generate a quiz with questions based on the lesson content.
    
    Questions can be multiple choice, short answer, or long answer format.
    """
    try:
        result = platform.start_quiz(
            user_id=request.user_id,
            lesson_id=request.lesson_id,
            subtopic_id=request.subtopic_id,
            difficulty=request.difficulty,
            question_count=request.question_count
        )
        
        return QuizResponse(
            quiz_id=result["quizId"],
            questions=result["questions"],
            total_questions=result["totalQuestions"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start quiz: {str(e)}"
        )


@app.post(
    "/api/quizzes/submit",
    response_model=QuizResultResponse,
    summary="Submit quiz answers",
    description="Submit quiz responses and receive AI-graded results"
)
async def submit_quiz(request: QuizSubmissionRequest):
    """
    Submit quiz answers and receive immediate AI-powered grading.
    
    The system will:
    - Grade multiple choice questions automatically
    - Use AI to grade written answers based on mark schemes
    - Convert bullet points to coherent answers
    - Provide detailed feedback on each response
    - Calculate mastery level
    - Determine if tutoring is needed
    """
    try:
        result = platform.submit_quiz(
            user_id=request.user_id,
            quiz_id=request.quiz_id,
            responses=request.responses
        )
        
        return QuizResultResponse(
            attempt_id=result["attemptId"],
            score=result["score"],
            responses=result["responses"],
            mastery_level=result["masteryLevel"],
            next_action=result["nextAction"],
            trigger_tutor=result["triggerTutor"],
            weak_concepts=result["weakConcepts"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quiz: {str(e)}"
        )


# ==================== TUTOR ENDPOINTS ====================

@app.post(
    "/api/tutor/start",
    response_model=TutorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a tutor session",
    description="Start an AI tutoring session for personalized help"
)
async def start_tutor_session(request: StartTutorRequest):
    """
    Start a one-on-one AI tutoring session.
    
    The AI tutor will:
    - Use Socratic method to guide learning
    - Provide hints rather than direct answers
    - Use analogies and examples
    - Be patient and encouraging
    """
    try:
        result = platform.start_tutor_session(
            user_id=request.user_id,
            trigger=request.trigger,
            lesson_id=request.lesson_id,
            subtopic_id=request.subtopic_id,
            question_id=request.question_id,
            concept=request.concept,
            initial_message=request.initial_message
        )
        
        return TutorResponse(
            session_id=result["sessionId"],
            message=result["message"],
            context=result["context"]
        )
    except Exception as e:
        logger.error(f"Error starting tutor session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start tutor session: {str(e)}"
        )


@app.post(
    "/api/tutor/message",
    response_model=TutorResponse,
    summary="Send message to tutor",
    description="Send a message in an active tutor session"
)
async def send_tutor_message(request: SendTutorMessageRequest):
    """
    Send a message to the AI tutor in an active session.
    
    The tutor maintains conversation context and provides personalized guidance.
    """
    try:
        result = platform.send_tutor_message(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message
        )
        
        return TutorResponse(
            session_id=result["sessionId"],
            message=result["message"],
            context={}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending tutor message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@app.post(
    "/api/tutor/end/{user_id}/{session_id}",
    response_model=Dict[str, str],
    summary="End tutor session",
    description="Mark a tutor session as resolved"
)
async def end_tutor_session(user_id: str, session_id: str):
    """
    End an active tutoring session.
    """
    try:
        platform.end_tutor_session(user_id, session_id)
        return {
            "status": "resolved",
            "session_id": session_id,
            "message": "Tutor session ended successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error ending tutor session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


# ==================== PROGRESS & DASHBOARD ENDPOINTS ====================

@app.get(
    "/api/dashboard/{user_id}",
    response_model=DashboardResponse,
    summary="Get user dashboard",
    description="Get comprehensive dashboard with progress, plans, and recommendations"
)
async def get_dashboard(user_id: str):
    """
    Get the complete user dashboard including:
    - Overall progress and statistics
    - All lesson plans with their progress
    - Active tutor sessions
    - Personalized recommendations
    """
    try:
        result = platform.get_dashboard(user_id)
        
        return DashboardResponse(
            user=result["user"],
            lesson_plans=result["lessonPlans"],
            active_tutor_sessions=result["activeTutorSessions"],
            recommendations=result["recommendations"]
        )
    except Exception as e:
        logger.error(f"Error retrieving dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )


@app.get(
    "/api/progress/{user_id}/{lesson_plan_id}",
    response_model=Dict[str, Any],
    summary="Get progress for a lesson plan",
    description="Get detailed progress for a specific lesson plan"
)
async def get_progress(user_id: str, lesson_plan_id: str):
    """
    Get detailed progress information for a specific lesson plan.
    
    Includes subtopic-by-subtopic progress, scores, and mastery levels.
    """
    try:
        progress = platform.progress.get_progress(user_id, lesson_plan_id)
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress not found"
            )
        
        return {
            "lesson_plan_id": progress.lessonPlanId,
            "subtopic_progress": progress.subtopicProgress,
            "overall_progress": progress.overallProgress,
            "updated_at": progress.updatedAt.isoformat() if progress.updatedAt else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve progress: {str(e)}"
        )


# ==================== HEALTH CHECK ====================

@app.get(
    "/health",
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ==================== ROOT ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Learning Platform API",
        "version": "1.0.0",
        "description": "AI-powered adaptive learning platform",
        "docs": "/docs",
        "endpoints": {
            "lesson_plans": "/api/lesson-plans",
            "lessons": "/api/lessons",
            "quizzes": "/api/quizzes",
            "tutor": "/api/tutor",
            "dashboard": "/api/dashboard/{user_id}",
            "progress": "/api/progress/{user_id}/{lesson_plan_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)