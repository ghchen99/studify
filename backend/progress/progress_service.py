"""
Progress Service
Tracks and manages student progress across lessons and quizzes
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

from ..shared.models import Progress, LessonPlan, QuizAttempt, Lesson
from ..shared.cosmos_client import get_cosmos_service

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for managing student progress"""
    
    def __init__(self):
        self.cosmos = get_cosmos_service()
    
    def initialize_progress(
        self,
        user_id: str,
        lesson_plan_id: str
    ) -> Progress:
        """Initialize progress tracking for a lesson plan"""
        logger.info(f"Initializing progress for lesson plan: {lesson_plan_id}")
        
        lesson_plan = self.cosmos.get_item(
            container="LessonPlans",
            item_id=lesson_plan_id,
            partition_key=user_id,
            model_class=LessonPlan
        )
        
        if not lesson_plan:
            raise ValueError(f"Lesson plan {lesson_plan_id} not found")
        
        subtopic_progress = {}
        for subtopic in lesson_plan.structure:
            subtopic_progress[subtopic.subtopicId] = {
                "status": "not_started",
                "lessonCompleted": False,
                "quizAttempts": 0,
                "bestScore": 0.0,
                "averageScore": 0.0,
                "masteryLevel": "not_started",
                "weakConcepts": [],
                "lastAttemptAt": None
            }
        
        progress = Progress(
            id=f"progress_{lesson_plan_id}",
            userId=user_id,
            lessonPlanId=lesson_plan_id,
            subtopicProgress=subtopic_progress,
            overallProgress={
                "totalSubtopics": len(lesson_plan.structure),
                "completedSubtopics": 0,
                "percentComplete": 0.0,
                "totalStudyTime": 0,
                "averageScore": 0.0
            },
            updatedAt=datetime.utcnow()
        )
        
        created_progress = self.cosmos.upsert_item("Progress", progress)
        logger.info(f"Initialized progress: {created_progress.id}")
        
        return created_progress
    
    def update_lesson_completion(
        self,
        user_id: str,
        lesson_id: str,
        study_time: int = 0
    ) -> Progress:
        """Update progress when a lesson is completed"""
        logger.info(f"Updating lesson completion for: {lesson_id}")
        
        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=lesson_id,
            partition_key=user_id,
            model_class=Lesson
        )
        
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        progress = self._get_or_create_progress(user_id, lesson.lessonPlanId)
        
        subtopic_id = lesson.subtopicId
        if subtopic_id in progress.subtopicProgress:
            progress.subtopicProgress[subtopic_id]["lessonCompleted"] = True
            progress.subtopicProgress[subtopic_id]["status"] = "in_progress"
        
        progress.overallProgress["totalStudyTime"] += study_time
        progress.updatedAt = datetime.utcnow()
        
        self._recalculate_overall_progress(progress)
        
        return self.cosmos.update_item("Progress", progress)
    
    def update_quiz_completion(
        self,
        user_id: str,
        quiz_attempt_id: str
    ) -> Progress:
        """Update progress when a quiz is completed"""
        logger.info(f"Updating quiz completion for attempt: {quiz_attempt_id}")
        
        attempts = self.cosmos.query_items(
            container="QuizAttempts",
            query="SELECT * FROM c WHERE c.id = @attemptId",
            partition_key=user_id,
            model_class=QuizAttempt,
            parameters=[{"name": "@attemptId", "value": quiz_attempt_id}]
        )
        
        if not attempts:
            raise ValueError(f"Quiz attempt {quiz_attempt_id} not found")
        
        attempt = attempts[0]

        # The QuizAttempt.lessonId is a Lesson id; progress is tracked per LessonPlan.
        # Retrieve the Lesson to get its parent lessonPlanId.
        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=attempt.lessonId,
            partition_key=user_id,
            model_class=Lesson
        )

        if not lesson:
            raise ValueError(f"Lesson {attempt.lessonId} not found")

        progress = self._get_or_create_progress(user_id, lesson.lessonPlanId)
        
        subtopic_id = attempt.subtopicId
        if subtopic_id in progress.subtopicProgress:
            subprog = progress.subtopicProgress[subtopic_id]
            
            subprog["quizAttempts"] += 1
            
            score_pct = attempt.score.get("percentage", 0)
            subprog["bestScore"] = max(subprog.get("bestScore", 0), score_pct)
            
            all_attempts = self.cosmos.get_items_by_filter(
                container="QuizAttempts",
                filters={"subtopicId": subtopic_id},
                partition_key=user_id,
                model_class=QuizAttempt
            )
            
            if all_attempts:
                avg = sum(a.score.get("percentage", 0) for a in all_attempts) / len(all_attempts)
                subprog["averageScore"] = avg
            
            subprog["masteryLevel"] = self._calculate_mastery_level(
                best_score=subprog["bestScore"],
                avg_score=subprog["averageScore"],
                attempts=subprog["quizAttempts"]
            )
            
            weak_concepts = attempt.score.get("weakConcepts", [])
            if weak_concepts:
                subprog["weakConcepts"] = weak_concepts
            
            if subprog["masteryLevel"] == "mastered":
                subprog["status"] = "completed"
            elif subprog["quizAttempts"] > 0:
                subprog["status"] = "in_progress"
            
            subprog["lastAttemptAt"] = attempt.completedAt.isoformat() if attempt.completedAt else None
        
        progress.updatedAt = datetime.utcnow()
        
        self._recalculate_overall_progress(progress)
        
        return self.cosmos.update_item("Progress", progress)
    
    def get_progress(
        self,
        user_id: str,
        lesson_plan_id: str
    ) -> Optional[Progress]:
        """Get progress for a lesson plan"""
        progress_id = f"progress_{lesson_plan_id}"
        return self.cosmos.get_item(
            container="Progress",
            item_id=progress_id,
            partition_key=user_id,
            model_class=Progress
        )
    
    def get_all_progress(self, user_id: str) -> List[Progress]:
        """Get all progress records for a user"""
        return self.cosmos.get_items_by_user(
            container="Progress",
            user_id=user_id,
            model_class=Progress,
            item_type="progress"
        )
    
    def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of all progress for a user"""
        all_progress = self.get_all_progress(user_id)
        
        total_subtopics = 0
        completed_subtopics = 0
        total_study_time = 0
        all_scores = []
        
        plans_summary = []
        
        for prog in all_progress:
            total_subtopics += prog.overallProgress.get("totalSubtopics", 0)
            completed_subtopics += prog.overallProgress.get("completedSubtopics", 0)
            total_study_time += prog.overallProgress.get("totalStudyTime", 0)
            
            avg_score = prog.overallProgress.get("averageScore", 0)
            if avg_score > 0:
                all_scores.append(avg_score)
            
            lesson_plan = self.cosmos.get_item(
                container="LessonPlans",
                item_id=prog.lessonPlanId,
                partition_key=user_id,
                model_class=LessonPlan
            )
            
            plans_summary.append({
                "lessonPlanId": prog.lessonPlanId,
                "subject": lesson_plan.subject if lesson_plan else "Unknown",
                "topic": lesson_plan.topic if lesson_plan else "Unknown",
                "percentComplete": prog.overallProgress.get("percentComplete", 0),
                "averageScore": avg_score,
                "totalSubtopics": prog.overallProgress.get("totalSubtopics", 0),
                "completedSubtopics": prog.overallProgress.get("completedSubtopics", 0)
            })
        
        return {
            "totalSubtopics": total_subtopics,
            "completedSubtopics": completed_subtopics,
            "overallPercentComplete": (completed_subtopics / total_subtopics * 100) if total_subtopics > 0 else 0,
            "totalStudyTime": total_study_time,
            "overallAverageScore": sum(all_scores) / len(all_scores) if all_scores else 0,
            "lessonPlans": plans_summary
        }
    
    def _get_or_create_progress(
        self,
        user_id: str,
        lesson_plan_id: str
    ) -> Progress:
        """Get existing progress or create new one"""
        progress = self.get_progress(user_id, lesson_plan_id)
        if not progress:
            progress = self.initialize_progress(user_id, lesson_plan_id)
        return progress
    
    def _calculate_mastery_level(
        self,
        best_score: float,
        avg_score: float,
        attempts: int
    ) -> str:
        """Calculate mastery level based on scores"""
        if attempts == 0:
            return "not_started"
        elif best_score >= 80 and avg_score >= 70:
            return "mastered"
        elif best_score >= 60 or avg_score >= 50:
            return "intermediate"
        else:
            return "beginner"
    
    def _recalculate_overall_progress(self, progress: Progress):
        """Recalculate overall progress statistics"""
        subtopics = progress.subtopicProgress
        
        if not subtopics:
            return
        
        completed = sum(
            1 for sp in subtopics.values()
            if sp.get("status") == "completed"
        )
        
        total = len(subtopics)
        
        scores = [
            sp.get("averageScore", 0)
            for sp in subtopics.values()
            if sp.get("quizAttempts", 0) > 0
        ]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        progress.overallProgress["completedSubtopics"] = completed
        progress.overallProgress["percentComplete"] = (completed / total * 100) if total > 0 else 0
        progress.overallProgress["averageScore"] = avg_score