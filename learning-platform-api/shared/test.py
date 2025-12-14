import hashlib

def deterministic_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()

from datetime import datetime
from pprint import pprint
import uuid

from cosmos_client import get_cosmos_service
from models import User, LessonPlan, Lesson, Quiz, QuizAttempt, Question, QuizAttemptResponse

cosmos = get_cosmos_service()

USER_ID = "user123"

# --- 1. User (ONE per userId) ---
user = User(
    id=USER_ID,                 # 🔑 uniqueness enforced
    userId=USER_ID,
    email="user@example.com",
    name="Alice",
    profile={"role": "student"},
    createdAt=datetime.utcnow()
)

created_user = cosmos.upsert_item("Users", user)
print("Upserted User:")
pprint(created_user.model_dump())

# --- 2. LessonPlan (ONE per subject+topic) ---
lesson_plan_id = deterministic_id(
    created_user.userId,
    "Math",
    "Algebra"
)

lesson_plan = LessonPlan(
    id=lesson_plan_id,
    userId=created_user.userId,
    subject="Math",
    topic="Algebra",
    structure=[
        {
            "subtopicId": "sub1",
            "title": "Linear Equations",
            "order": 1,
            "estimatedDuration": 30,
            "concepts": ["variables", "equations"]
        },
        {
            "subtopicId": "sub2",
            "title": "Quadratic Equations",
            "order": 2,
            "estimatedDuration": 45,
            "concepts": ["quadratic formula", "roots"]
        }
    ],
    status="draft"
)

created_lesson_plan = cosmos.upsert_item("LessonPlans", lesson_plan)
print("\nUpserted LessonPlan:")
pprint(created_lesson_plan.model_dump())

# --- 3. Lesson (ONE per lessonPlan + subtopic) ---
lesson_id = deterministic_id(
    created_lesson_plan.id,
    "sub1"
)

lesson = Lesson(
    id=lesson_id,
    userId=created_user.userId,
    lessonPlanId=created_lesson_plan.id,
    subtopicId="sub1",
    subject="Math",
    topic="Algebra",
    subtopic="Linear Equations",
    content={"text": "This is a lesson on linear equations."}
)

created_lesson = cosmos.upsert_item("Lessons", lesson)
print("\nUpserted Lesson:")
pprint(created_lesson.model_dump())

# --- 4. Quiz (MANY allowed) ---
quiz = Quiz(
    id=str(uuid.uuid4()),        # ✅ always new
    userId=created_user.userId,
    lessonId=created_lesson.id,
    subtopicId="sub1",
    questions=[
        Question(
            questionId="q1",
            type="multiple-choice",
            question="What is x if 2x + 3 = 7?",
            options=["1", "2", "3", "4"],
            correctAnswer="2"
        )
    ],
    createdAt=datetime.utcnow()
)

created_quiz = cosmos.upsert_item("Quizzes", quiz)
print("\nCreated Quiz:")
pprint(created_quiz.model_dump())

# --- 5. QuizAttempt (MANY allowed) ---
quiz_attempt = QuizAttempt(
    id=str(uuid.uuid4()),        # ✅ always new
    userId=created_user.userId,
    quizId=created_quiz.id,
    lessonId=created_lesson.id,
    subtopicId="sub1",
    state="completed",
    responses=[
        QuizAttemptResponse(
            questionId="q1",
            userAnswer="2",
            marksAwarded=1,
            maxMarks=1,
            isCorrect=True
        )
    ],
    score={"total": 1, "max": 1},
    completedAt=datetime.utcnow()
)

created_attempt = cosmos.upsert_item("QuizAttempts", quiz_attempt)
print("\nCreated QuizAttempt:")
pprint(created_attempt.model_dump())

# --- Queries unchanged ---
user_lesson_plans = cosmos.get_items_by_user(
    "LessonPlans",
    created_user.userId,
    model_class=LessonPlan
)

print("\nAll LessonPlans for user:")
for lp in user_lesson_plans:
    pprint(lp.model_dump())

lessons = cosmos.get_items_by_filter(
    container="Lessons",
    filters={"subtopicId": "sub1"},
    partition_key=created_user.userId,
    model_class=Lesson
)

print("\nLessons with subtopicId 'sub1':")
for l in lessons:
    pprint(l.model_dump())

cosmos.close()
