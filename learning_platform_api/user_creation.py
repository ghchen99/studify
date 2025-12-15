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

cosmos.close()
