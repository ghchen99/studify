"""
FastAPI Learning Platform API
RESTful API for the AI-powered learning platform
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter, Body
from users.auth import verify_access_token
from typing import List, Dict, Any
from datetime import datetime, timezone
import logging
import os

from learning_platform import LearningPlatform
from shared.models import (
    CreateLessonPlanRequest, LessonPlanResponse,
    LessonResponse,
    StartLessonRequest, ExpandSectionRequest, ExpandedSectionResponse,
    CompleteLessonRequest, CompletionResponse, QuizResponse,
    StartQuizRequest, QuizSubmissionRequest, QuizResultResponse
)

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

# CORS configuration
allowed_origins = [
    "http://localhost:3000",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(verify_access_token)]
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
                        "concepts": st.concepts,
                        "lessonId": st.lessonId,
                        "generatedAt": st.generatedAt.isoformat() if st.generatedAt else None
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


@api_router.post(
    "/lesson-plans/{plan_id}/subtopics/{subtopic_id}/mark-generated",
    summary="Mark subtopic as generated",
    description="Record that a lesson has been generated for a subtopic"
)
async def mark_subtopic_generated(plan_id: str, subtopic_id: str, payload: Dict[str, str] = Body(...)):
    """
    Mark a subtopic within a lesson plan as having an associated generated lesson.

    Expects JSON body: { "user_id": "<user>", "lessonId": "<lesson-id>" }
    """
    user_id = payload.get("user_id")
    lesson_id = payload.get("lessonId")
    if not user_id or not lesson_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id and lessonId required")
    try:
        plan = platform.lesson_plans.get_lesson_plan(user_id, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson plan not found")

        # find the subtopic and set lessonId/generatedAt
        found_item = None
        for item in plan.structure:
            if item.subtopicId == subtopic_id:
                item.lessonId = lesson_id
                item.generatedAt = datetime.now(timezone.utc)
                found_item = item
                break

        if not found_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtopic not found")

        # persist updated structure
        updated = platform.lesson_plans.update_lesson_plan_structure(user_id, plan_id, plan.structure)

        return {"ok": True, "lessonId": lesson_id, "generatedAt": found_item.generatedAt.isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking subtopic as generated: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to mark generated: {str(e)}")
    
@api_router.delete(
    "/lesson-plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a lesson plan",
    description="Delete a lesson plan and all associated lessons"
)
async def delete_lesson_plan(plan_id: str, user_id: str):
    try:
        # 🔥 Delete lessons first
        deleted_lessons = platform.lessons.delete_lessons_for_plan(
            user_id=user_id,
            lesson_plan_id=plan_id
        )

        # 🔥 Delete lesson plan
        deleted_plan = platform.lesson_plans.delete_lesson_plan(
            user_id=user_id,
            plan_id=plan_id
        )

        if not deleted_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson plan not found"
            )

        return {
            "ok": True,
            "deletedPlanId": plan_id,
            "deletedLessons": deleted_lessons
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lesson plan cascade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete lesson plan: {str(e)}"
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
        
        # Ensure `maxMarks` is present on each question for the frontend
        questions_with_marks = [
            {
                "questionId": q.get("questionId") or q.get("question_id"),
                "type": q.get("type"),
                "question": q.get("question"),
                "options": q.get("options") if q.get("type") == "multiple_choice" else None,
                "difficulty": q.get("difficulty"),
                "maxMarks": q.get("maxMarks") if q.get("maxMarks") is not None else q.get("max_marks") if q.get("max_marks") is not None else q.get("max") if q.get("max") is not None else None
            }
            for q in (result.get("questions") or [])
        ]

        return QuizResponse(
            quiz_id=result["quizId"],
            questions=questions_with_marks,
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "quizzes": "/api/quizzes"
        }
    }

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)