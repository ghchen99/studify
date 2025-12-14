"""
Learning Platform Facade
Unified interface for all learning platform operations
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from .lesson_plans.lesson_plan_service import LessonPlanService
from .lessons.lesson_service import LessonService
from .quizzes.quiz_service import QuizService
from .tutor.tutor_service import TutorService
from .progress.progress_service import ProgressService

from .shared.models import (
    LessonPlan, LessonPlanItem
)

logger = logging.getLogger(__name__)


class LearningPlatform:
    """
    Unified interface for the learning platform
    
    This facade simplifies frontend interactions by providing
    a single entry point for all learning operations.
    """
    
    def __init__(self):
        self.lesson_plans = LessonPlanService()
        self.lessons = LessonService()
        self.quizzes = QuizService()
        self.tutor = TutorService()
        self.progress = ProgressService()
    
    # ==================== LESSON PLAN WORKFLOWS ====================
    
    def create_lesson_plan(
        self,
        user_id: str,
        subject: str,
        topic: str,
        level: str = "GCSE",
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new lesson plan
        
        Args:
            user_id: User identifier
            subject: Subject name (e.g., "Math", "Biology")
            topic: Topic name (e.g., "Algebra", "Cell Biology")
            level: Education level
            auto_approve: If True, automatically approve and initialize progress
        
        Returns:
            Dict with lesson plan and status
        """
        logger.info(f"Creating lesson plan: {subject} - {topic}")
        
        # Generate the lesson plan
        lesson_plan = self.lesson_plans.generate_lesson_plan(
            user_id=user_id,
            subject=subject,
            topic=topic,
            level=level
        )
        
        result = {
            "lessonPlan": lesson_plan,
            "status": lesson_plan.status,
            "subtopics": [
                {
                    "id": st.subtopicId,
                    "title": st.title,
                    "order": st.order,
                    "duration": st.estimatedDuration,
                    "concepts": st.concepts
                }
                for st in lesson_plan.structure
            ]
        }
        
        # Auto-approve if requested
        if auto_approve:
            approved_plan = self.approve_lesson_plan(user_id, lesson_plan.id)
            result["lessonPlan"] = approved_plan
            result["status"] = "approved"
            result["progressInitialized"] = True
        
        return result
    
    def approve_lesson_plan(
        self,
        user_id: str,
        plan_id: str,
        modified_structure: Optional[List[LessonPlanItem]] = None
    ) -> LessonPlan:
        """
        Approve a lesson plan and initialize progress tracking
        
        Args:
            user_id: User identifier
            plan_id: Lesson plan ID
            modified_structure: Optional modified structure
        
        Returns:
            Approved lesson plan
        """
        # Approve the plan
        approved_plan = self.lesson_plans.approve_lesson_plan(
            user_id=user_id,
            plan_id=plan_id,
            modified_structure=modified_structure
        )
        
        # Initialize progress tracking
        self.progress.initialize_progress(user_id, plan_id)
        
        return approved_plan
    
    # ==================== LESSON WORKFLOWS ====================
    
    def start_lesson(
        self,
        user_id: str,
        lesson_plan_id: str,
        subtopic_id: str
    ) -> Dict[str, Any]:
        """
        Start a lesson for a subtopic
        
        Args:
            user_id: User identifier
            lesson_plan_id: Lesson plan ID
            subtopic_id: Subtopic ID
        
        Returns:
            Dict with lesson content and metadata
        """
        logger.info(f"Starting lesson for subtopic: {subtopic_id}")
        
        # Check if lesson already exists
        existing_lesson = self.lessons.get_lesson_for_subtopic(user_id, subtopic_id)
        
        if existing_lesson:
            lesson = existing_lesson
        else:
            # Generate new lesson
            lesson = self.lessons.generate_lesson(
                user_id=user_id,
                lesson_plan_id=lesson_plan_id,
                subtopic_id=subtopic_id
            )
        
        return {
            "lessonId": lesson.id,
            "subject": lesson.subject,
            "topic": lesson.topic,
            "subtopic": lesson.subtopic,
            "introduction": lesson.content.get("introduction"),
            "sections": lesson.content.get("sections"),
            "summary": lesson.content.get("summary"),
            "keyTerms": lesson.content.get("keyTerms"),
            "status": lesson.status
        }
    
    def expand_lesson_section(
        self,
        user_id: str,
        lesson_id: str,
        section_id: str
    ) -> Dict[str, Any]:
        """
        Expand a section for more detail
        
        Returns:
            Dict with expanded content
        """
        updated_lesson = self.lessons.expand_section(
            user_id=user_id,
            lesson_id=lesson_id,
            section_id=section_id
        )
        
        # Find the expanded section
        section = next(
            (s for s in updated_lesson.content.get("sections", [])
             if s.get("sectionId") == section_id),
            None
        )
        
        return {
            "sectionId": section_id,
            "expandedContent": section.get("expanded") if section else None
        }
    
    def complete_lesson(
        self,
        user_id: str,
        lesson_id: str,
        study_time: int = 0
    ) -> Dict[str, Any]:
        """
        Mark lesson as complete and update progress
        
        Args:
            user_id: User identifier
            lesson_id: Lesson ID
            study_time: Time spent in minutes
        
        Returns:
            Dict with completion status and updated progress
        """
        # Mark lesson complete
        lesson = self.lessons.mark_lesson_complete(user_id, lesson_id)
        
        # Update progress
        progress = self.progress.update_lesson_completion(
            user_id=user_id,
            lesson_id=lesson_id,
            study_time=study_time
        )
        
        return {
            "lessonCompleted": True,
            "nextAction": "quiz",
            "progress": {
                "percentComplete": progress.overallProgress.get("percentComplete"),
                "totalStudyTime": progress.overallProgress.get("totalStudyTime")
            }
        }
    
    # ==================== QUIZ WORKFLOWS ====================
    
    def start_quiz(
        self,
        user_id: str,
        lesson_id: str,
        subtopic_id: str,
        difficulty: str = "mixed",
        question_count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate and start a quiz
        
        Args:
            user_id: User identifier
            lesson_id: Lesson ID
            subtopic_id: Subtopic ID
            difficulty: Difficulty level
            question_count: Number of questions
        
        Returns:
            Dict with quiz questions
        """
        logger.info(f"Starting quiz for lesson: {lesson_id}")
        
        # Generate quiz
        quiz = self.quizzes.generate_quiz(
            user_id=user_id,
            lesson_id=lesson_id,
            subtopic_id=subtopic_id,
            difficulty=difficulty,
            count=question_count
        )
        
        return {
            "quizId": quiz.id,
            "questions": [
                {
                    "questionId": q.questionId,
                    "type": q.type,
                    "question": q.question,
                    "options": q.options if q.type == "multiple_choice" else None,
                    "difficulty": q.difficulty
                }
                for q in quiz.questions
            ],
            "totalQuestions": len(quiz.questions)
        }
    
    def submit_quiz(
        self,
        user_id: str,
        quiz_id: str,
        responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Submit quiz and get results
        
        Args:
            user_id: User identifier
            quiz_id: Quiz ID
            responses: List of responses
        
        Returns:
            Dict with results and next actions
        """
        logger.info(f"Submitting quiz: {quiz_id}")
        
        # Submit and grade
        attempt = self.quizzes.submit_quiz(
            user_id=user_id,
            quiz_id=quiz_id,
            responses=responses
        )
        
        # Update progress
        progress = self.progress.update_quiz_completion(
            user_id=user_id,
            quiz_attempt_id=attempt.id
        )
        
        # Prepare results
        score_data = attempt.score
        trigger_tutor = score_data.get("triggerTutor", False)
        weak_concepts = score_data.get("weakConcepts", [])
        
        result = {
            "attemptId": attempt.id,
            "score": {
                "percentage": score_data.get("percentage"),
                "marksAwarded": score_data.get("marksAwarded"),
                "maxMarks": score_data.get("maxMarks")
            },
            "responses": [
                {
                    "questionId": r.questionId,
                    "isCorrect": r.isCorrect,
                    "marksAwarded": r.marksAwarded,
                    "maxMarks": r.maxMarks,
                    "feedback": r.feedback,
                    "aiGeneratedAnswer": r.aiGeneratedAnswer
                }
                for r in attempt.responses
            ],
            "masteryLevel": progress.subtopicProgress.get(attempt.subtopicId, {}).get("masteryLevel"),
            "nextAction": "tutor" if trigger_tutor else "continue",
            "triggerTutor": trigger_tutor,
            "weakConcepts": weak_concepts
        }
        
        return result
    
    # ==================== TUTOR WORKFLOWS ====================
    
    def start_tutor_session(
        self,
        user_id: str,
        trigger: str,
        lesson_id: Optional[str] = None,
        subtopic_id: Optional[str] = None,
        question_id: Optional[str] = None,
        concept: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start an AI tutor session
        
        Args:
            user_id: User identifier
            trigger: What triggered the session
            lesson_id: Optional lesson context
            subtopic_id: Optional subtopic context
            question_id: Optional question context
            concept: Optional concept being discussed
            initial_message: Optional initial student message
        
        Returns:
            Dict with session info and opening message
        """
        context = {
            "lessonId": lesson_id,
            "subtopicId": subtopic_id,
            "questionId": question_id,
            "concept": concept or "this topic"
        }
        
        session = self.tutor.start_session(
            user_id=user_id,
            trigger=trigger,
            context=context,
            initial_message=initial_message
        )
        
        # Get the tutor's opening message
        opening_msg = session.conversation[-1] if session.conversation else None
        
        return {
            "sessionId": session.id,
            "message": opening_msg.get("content") if opening_msg else "",
            "context": context
        }
    
    def send_tutor_message(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a message in tutor session
        
        Returns:
            Dict with tutor's response
        """
        session = self.tutor.send_message(
            user_id=user_id,
            session_id=session_id,
            message=message
        )
        
        # Get the latest tutor response
        tutor_msg = session.conversation[-1] if session.conversation else None
        
        return {
            "sessionId": session.id,
            "message": tutor_msg.get("content") if tutor_msg else "",
            "timestamp": tutor_msg.get("timestamp") if tutor_msg else None
        }
    
    def end_tutor_session(self, user_id: str, session_id: str):
        """End a tutor session"""
        return self.tutor.resolve_session(user_id, session_id)
    
    # ==================== PROGRESS & ANALYTICS ====================
    
    def get_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete dashboard for user
        
        Returns:
            Dict with all progress, plans, and recommendations
        """
        # Get all lesson plans
        plans = self.lesson_plans.get_user_lesson_plans(user_id)
        
        # Get progress summary
        progress_summary = self.progress.get_progress_summary(user_id)
        
        # Get active tutor sessions
        active_sessions = self.tutor.get_user_sessions(user_id, resolved=False)
        
        return {
            "user": {
                "totalStudyTime": progress_summary.get("totalStudyTime"),
                "overallProgress": progress_summary.get("overallPercentComplete"),
                "averageScore": progress_summary.get("overallAverageScore")
            },
            "lessonPlans": [
                {
                    "id": plan.id,
                    "subject": plan.subject,
                    "topic": plan.topic,
                    "status": plan.status,
                    "subtopicCount": len(plan.structure),
                    "progress": next(
                            (p for p in progress_summary.get("lessonPlans", [])
                             if p["lessonPlanId"] == plan.id),
                            {}
                        )
                }
                for plan in plans
            ],
            "activeTutorSessions": len(active_sessions),
            "recommendations": self._generate_recommendations(user_id, plans, progress_summary)
        }
    
    def _generate_recommendations(
        self,
        user_id: str,
        plans: List[LessonPlan],
        progress_summary: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Check for incomplete lesson plans
        for plan_prog in progress_summary.get("lessonPlans", []):
            if plan_prog["percentComplete"] < 100:
                plan = next((p for p in plans if p.id == plan_prog["lessonPlanId"]), None)
                if plan:
                    recommendations.append(
                        f"Continue {plan.subject} - {plan.topic} "
                        f"({plan_prog['percentComplete']:.0f}% complete)"
                    )
        
        # Check for low scores
        for plan_prog in progress_summary.get("lessonPlans", []):
            if 0 < plan_prog["averageScore"] < 60:
                plan = next((p for p in plans if p.id == plan_prog["lessonPlanId"]), None)
                if plan:
                    recommendations.append(
                        f"Review {plan.subject} - {plan.topic} "
                        f"(average score: {plan_prog['averageScore']:.0f}%)"
                    )
        
        # Suggest new topics if doing well
        if progress_summary.get("overallAverageScore", 0) > 70:
            recommendations.append("Start a new topic - you're doing great!")
        
        return recommendations[:3]  # Top 3 recommendations