import os
import hashlib
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint

from models import LessonPlan, LessonPlanItem  # your existing Pydantic models
from pydantic import BaseModel
from typing import List, Optional

# -----------------------------
# Deterministic ID function
# -----------------------------
def deterministic_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()

# -----------------------------
# Load env + OpenAI client
# -----------------------------
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-5.1")
api_key = os.getenv("AZURE_OPENAI_KEY")

client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=api_key,
    default_headers={"api-key": api_key}
)

# -----------------------------
# LLM RESPONSE SCHEMA
# -----------------------------
class LessonPlanSubtopicLLM(BaseModel):
    title: str
    estimatedDuration: Optional[int]
    concepts: List[str]

class LessonPlanLLMResponse(BaseModel):
    subject: str
    topic: str
    subtopics: List[LessonPlanSubtopicLLM]

# -----------------------------
# GENERATE LESSON PLAN
# -----------------------------
try:
    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert GCSE curriculum designer. "
                    "Generate a clear, well-structured lesson plan broken into logical subtopics."
                )
            },
            {
                "role": "user",
                "content": (
                    "Generate a GCSE-level lesson plan for:\n"
                    "Subject: Math\n"
                    "Topic: Algebra\n\n"
                    "Each subtopic should be concise and suitable for a 15–45 minute lesson."
                )
            }
        ],
        response_format=LessonPlanLLMResponse,
    )

    llm_plan = completion.choices[0].message.parsed

    # -----------------------------
    # Map LLM Output → LessonPlan (using LessonPlanItem)
    # -----------------------------
    user_id = "user123"  # from auth/session in real system
    lesson_plan_id = deterministic_id(user_id, llm_plan.subject, llm_plan.topic)

    lesson_plan = LessonPlan(
        id=lesson_plan_id,
        userId=user_id,
        subject=llm_plan.subject,
        topic=llm_plan.topic,
        status="draft",
        aiGeneratedAt=datetime.now(timezone.utc),
        structure=[
            LessonPlanItem(
                subtopicId=deterministic_id(lesson_plan_id, sub.title),
                title=sub.title,
                order=i + 1,
                estimatedDuration=sub.estimatedDuration,
                concepts=sub.concepts
            )
            for i, sub in enumerate(llm_plan.subtopics)
        ]
    )

    print("\nGenerated LessonPlan with deterministic IDs:")
    pprint(lesson_plan.model_dump())

except Exception as e:
    print(f"Error: {e}")
