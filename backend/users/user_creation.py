import hashlib
from datetime import datetime, timezone
from pprint import pprint

from shared.cosmos_client import get_cosmos_service
from shared.models import User
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
    createdAt=datetime.now(timezone.utc)
)
created_user = cosmos.upsert_item("Users", user)
print("Upserted User:")
pprint(created_user.model_dump())

cosmos.close()
