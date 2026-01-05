"""Simplified Progress Service
This version removes deep per-subtopic analytics that aren't referenced by the frontend.
It keeps the minimal operations used by the API: initialize, update lesson completion,
update quiz completion, and basic summary aggregation.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import logging

from shared.models import Progress, LessonPlan, QuizAttempt, Lesson
from shared.cosmos_client import get_cosmos_service

logger = logging.getLogger(__name__)


class ProgressService:
    """Lightweight service for tracking overall progress per lesson plan."""

    def __init__(self):
        self.cosmos = get_cosmos_service()

    def initialize_progress(self, user_id: str, lesson_plan_id: str) -> Progress:
        """Create a minimal progress record for a lesson plan."""
        logger.info("Initializing progress for lesson plan: %s", lesson_plan_id)

        lesson_plan = self.cosmos.get_item(
            container="LessonPlans",
            item_id=lesson_plan_id,
            partition_key=user_id,
            model_class=LessonPlan,
        )

        if not lesson_plan:
            raise ValueError(f"Lesson plan {lesson_plan_id} not found")

        progress = Progress(
            id=f"progress_{lesson_plan_id}",
            userId=user_id,
            lessonPlanId=lesson_plan_id,
            subtopicProgress={},
            overallProgress={
                "totalSubtopics": len(lesson_plan.structure),
                "completedSubtopics": 0,
                "percentComplete": 0.0,
                "totalStudyTime": 0,
            },
            updatedAt=datetime.now(timezone.utc),
        )

        return self.cosmos.upsert_item("Progress", progress)

    def update_lesson_completion(self, user_id: str, lesson_id: str, study_time: int = 0) -> Progress:
        """Mark a lesson completed and update overall counters.

        This keeps only the minimal fields required by the frontend (`percentComplete`, `totalStudyTime`).
        """
        logger.info("Updating lesson completion for: %s", lesson_id)

        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=lesson_id,
            partition_key=user_id,
            model_class=Lesson,
        )

        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        lesson_plan_id = lesson.lessonPlanId
        progress = self._get_or_create_progress(user_id, lesson_plan_id)

        # Ensure overallProgress structure
        overall = progress.overallProgress or {}
        total = overall.get("totalSubtopics") or 0
        completed = overall.get("completedSubtopics") or 0

        subtopic_id = lesson.subtopicId
        subprog = progress.subtopicProgress or {}

        # If this subtopic wasn't previously marked complete, mark it and increment completed count
        if subtopic_id and not subprog.get(subtopic_id, {}).get("lessonCompleted"):
            subprog.setdefault(subtopic_id, {})
            subprog[subtopic_id]["lessonCompleted"] = True
            completed += 1

        overall["completedSubtopics"] = completed
        overall["percentComplete"] = (completed / total * 100) if total > 0 else 0
        overall["totalStudyTime"] = overall.get("totalStudyTime", 0) + int(study_time or 0)

        progress.subtopicProgress = subprog
        progress.overallProgress = overall
        progress.updatedAt = datetime.now(timezone.utc)

        return self.cosmos.update_item("Progress", progress)

    def update_quiz_completion(self, user_id: str, quiz_attempt_id: str) -> Progress:
        """Update minimal quiz stats for the subtopic tied to a quiz attempt.

        This method updates `quizAttempts`, `bestScore`, and a running `averageScore` on the
        subtopicProgress entry when available. It intentionally avoids heavy aggregation queries.
        """
        logger.info("Updating quiz completion for attempt: %s", quiz_attempt_id)

        attempts = self.cosmos.query_items(
            container="QuizAttempts",
            query="SELECT * FROM c WHERE c.id = @attemptId",
            partition_key=user_id,
            model_class=QuizAttempt,
            parameters=[{"name": "@attemptId", "value": quiz_attempt_id}],
        )

        if not attempts:
            raise ValueError(f"Quiz attempt {quiz_attempt_id} not found")

        attempt = attempts[0]

        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=attempt.lessonId,
            partition_key=user_id,
            model_class=Lesson,
        )

        if not lesson:
            raise ValueError(f"Lesson {attempt.lessonId} not found")

        progress = self._get_or_create_progress(user_id, lesson.lessonPlanId)

        subtopic_id = attempt.subtopicId
        subprog = progress.subtopicProgress or {}
        entry = subprog.setdefault(subtopic_id, {})

        prev_count = int(entry.get("quizAttempts", 0))
        prev_avg = float(entry.get("averageScore", 0.0))
        score_pct = float((attempt.score or {}).get("percentage", 0.0))

        # Update counts and rolling average
        new_count = prev_count + 1
        new_avg = (prev_avg * prev_count + score_pct) / new_count if new_count > 0 else 0.0

        entry["quizAttempts"] = new_count
        entry["averageScore"] = new_avg
        entry["bestScore"] = max(float(entry.get("bestScore", 0.0)), score_pct)
        entry["lastAttemptAt"] = attempt.completedAt.isoformat() if attempt.completedAt else None

        # If best score reaches threshold, mark completed
        if entry.get("bestScore", 0) >= 80:
            entry["status"] = "completed"
        else:
            entry["status"] = "in_progress"

        progress.subtopicProgress = subprog
        progress.updatedAt = datetime.now(timezone.utc)

        return self.cosmos.update_item("Progress", progress)
    
    def get_progress(self, user_id: str, lesson_plan_id: str) -> Optional[Progress]:
        """Retrieve a single progress record."""
        progress_id = f"progress_{lesson_plan_id}"
        return self.cosmos.get_item(
            container="Progress",
            item_id=progress_id,
            partition_key=user_id,
            model_class=Progress,
        )

    def _get_or_create_progress(self, user_id: str, lesson_plan_id: str) -> Progress:
            progress = self.get_progress(user_id, lesson_plan_id)
            if not progress:
                progress = self.initialize_progress(user_id, lesson_plan_id)
            return progress