import hashlib
from datetime import datetime
from pprint import pprint
import uuid

from cosmos_client import get_cosmos_service
from models import User, LessonPlan, Lesson, Quiz, QuizAttempt, Question, QuizAttemptResponse, LessonPlanItem

# Deterministic ID function
def deterministic_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()

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
subtopics = [
    LessonPlanItem(
        subtopicId=deterministic_id(USER_ID, "Math", "Algebra", "Linear Equations"),
        title="Linear Equations",
        order=1,
        estimatedDuration=30,
        concepts=["variables", "equations"]
    ),
    LessonPlanItem(
        subtopicId=deterministic_id(USER_ID, "Math", "Algebra", "Quadratic Equations"),
        title="Quadratic Equations",
        order=2,
        estimatedDuration=45,
        concepts=["quadratic formula", "roots"]
    )
]

lesson_plan_id = deterministic_id(USER_ID, "Math", "Algebra")
lesson_plan = LessonPlan(
    id=lesson_plan_id,
    userId=USER_ID,
    subject="Math",
    topic="Algebra",
    structure=subtopics,  # now a list of LessonPlanItem
    status="draft"
)
created_lesson_plan = cosmos.upsert_item("LessonPlans", lesson_plan)
print("\nUpserted LessonPlan:")
pprint(created_lesson_plan.model_dump())

# --- 3. Lessons (ONE per lessonPlan + subtopic) ---
lessons_created = []
for st in subtopics:
    lesson_id = deterministic_id(created_lesson_plan.id, st.subtopicId)
    lesson = Lesson(
        id=lesson_id,
        userId=USER_ID,
        lessonPlanId=created_lesson_plan.id,
        subtopicId=st.subtopicId,  # reuse deterministic subtopicId
        subject="Math",
        topic="Algebra",
        subtopic=st.title,
        content={"text": f"This is a lesson on {st.title}."}
    )
    created_lesson = cosmos.upsert_item("Lessons", lesson)
    lessons_created.append(created_lesson)
print("\nUpserted Lessons:")
for l in lessons_created:
    pprint(l.model_dump())

# --- 4. Quiz (MANY allowed per lesson/subtopic) ---
quiz = Quiz(
    id=str(uuid.uuid4()),  # always new
    userId=USER_ID,
    lessonId=lessons_created[0].id,
    subtopicId=lessons_created[0].subtopicId,  # match lesson
    questions=[Question(
        questionId="q1",
        type="multiple-choice",
        question="What is x if 2x + 3 = 7?",
        options=["1", "2", "3", "4"],
        correctAnswer="2"
    )],
    createdAt=datetime.utcnow()
)
created_quiz = cosmos.upsert_item("Quizzes", quiz)
print("\nCreated Quiz:")
pprint(created_quiz.model_dump())

# --- 5. QuizAttempt (MANY allowed) ---
quiz_attempt = QuizAttempt(
    id=str(uuid.uuid4()),  # always new
    userId=USER_ID,
    quizId=created_quiz.id,
    lessonId=lessons_created[0].id,
    subtopicId=lessons_created[0].subtopicId,  # match lesson
    responses=[QuizAttemptResponse(
        questionId="q1",
        userAnswer="2",
        marksAwarded=1,
        maxMarks=1,
        isCorrect=True
    )],
    score={"total": 1, "max": 1},
    completedAt=datetime.utcnow(),
    state="completed"
)
created_attempt = cosmos.upsert_item("QuizAttempts", quiz_attempt)
print("\nCreated QuizAttempt:")
pprint(created_attempt.model_dump())

# --- Queries ---
user_lesson_plans = cosmos.get_items_by_user(
    "LessonPlans",
    USER_ID,
    model_class=LessonPlan
)
print("\nAll LessonPlans for user:")
for lp in user_lesson_plans:
    pprint(lp.model_dump())

lessons = cosmos.get_items_by_filter(
    container="Lessons",
    filters={"subtopicId": lessons_created[0].subtopicId},
    partition_key=USER_ID,
    model_class=Lesson
)
print(f"\nLessons with subtopicId '{lessons_created[0].subtopicId}':")
for l in lessons:
    pprint(l.model_dump())

cosmos.close()
