"""
FastAPI Learning Platform API
RESTful API for the AI-powered learning platform
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from auth import verify_access_token
from typing import List, Dict, Any
from datetime import datetime
import logging

from learning_platform import LearningPlatform
from shared.models import (
    CreateLessonPlanRequest, LessonPlanResponse,
    LessonResponse,
    StartLessonRequest, ExpandSectionRequest, ExpandedSectionResponse,
    CompleteLessonRequest, CompletionResponse, QuizResponse,
    StartQuizRequest, QuizSubmissionRequest, QuizResultResponse, TutorResponse,
    StartTutorRequest, SendTutorMessageRequest, DashboardResponse)

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

api_router = APIRouter(
    prefix="/api",
    # dependencies=[Depends(verify_access_token)]
)

# Initialize platform
platform = LearningPlatform()

# ==================== LESSON PLAN ENDPOINTS ====================

@api_router.post(
    "/lesson-plans",
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
            description=result["lessonPlan"].description,
            subtopics=result["subtopics"],
        )
    except Exception as e:
        logger.error(f"Error creating lesson plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lesson plan: {str(e)}"
        )


# Note: approve endpoint removed; lesson-plan approval/status handled differently now


@api_router.get(
    "/lesson-plans/{user_id}",
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
                "description": plan.description, 
                
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

@api_router.get(
    "/lesson-plans/details/{plan_id}",
    response_model=LessonPlanResponse,
    summary="Get detailed lesson plan",
    description="Retrieve full details of a specific lesson plan including all subtopics"
)
async def get_lesson_plan_details(plan_id: str, user_id: str):
    """
    Get detailed information about a specific lesson plan.
    
    Returns the same detailed response as when creating a lesson plan,
    including all subtopics with their concepts.
    
    Args:
        plan_id: The lesson plan ID
        user_id: The user ID (query parameter for authentication)
    """
    try:
        # Get the lesson plan
        plan = platform.lesson_plans.get_lesson_plan(user_id, plan_id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson plan {plan_id} not found"
            )
        
        return LessonPlanResponse(
            lesson_plan_id=plan.id,
            subject=plan.subject,
            topic=plan.topic,
            description=plan.description,
            subtopics=[
                {
                    "id": st.subtopicId,
                    "title": st.title,
                    "order": st.order,
                    "duration": st.estimatedDuration,
                    "concepts": st.concepts
                }
                for st in plan.structure
            ],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lesson plan details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve lesson plan details: {str(e)}"
        )

# ==================== LESSON ENDPOINTS ====================

@api_router.post(
    "/lessons/start",
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


@api_router.post(
    "/lessons/expand-section",
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


@api_router.post(
    "/lessons/complete",
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

@api_router.post(
    "/quizzes/start",
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


@api_router.post(
    "/quizzes/submit",
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

@api_router.post(
    "/tutor/start",
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


@api_router.post(
    "/tutor/message",
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


@api_router.post(
    "/tutor/end/{user_id}/{session_id}",
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

@api_router.get(
    "/dashboard/{user_id}",
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


@api_router.get(
    "/progress/{user_id}/{lesson_plan_id}",
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

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)