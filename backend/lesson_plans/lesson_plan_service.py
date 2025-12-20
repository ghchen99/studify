"""
Lesson Plan Service
Handles lesson plan generation, approval, and management
"""
import os
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from openai import OpenAI
from pydantic import BaseModel
import logging

from shared.models import LessonPlan, LessonPlanItem
from shared.cosmos_client import get_cosmos_service

logger = logging.getLogger(__name__)


class LessonPlanSubtopicLLM(BaseModel):
    """LLM response schema for subtopic"""
    title: str
    estimatedDuration: Optional[int] = 30
    concepts: List[str]


class LessonPlanLLMResponse(BaseModel):
    """LLM response schema for lesson plan"""
    subject: str
    topic: str
    overview: str
    description: str  # AI-generated course overview (2-3 sentences)
    subtopics: List[LessonPlanSubtopicLLM]


class LessonPlanService:
    """Service for managing lesson plans"""
    
    def __init__(self):
        self.cosmos = get_cosmos_service()
        
        # Initialize OpenAI client
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4")
        
        self.client = OpenAI(
            base_url=f"{endpoint}/openai/v1/",
            api_key=api_key,
            default_headers={"api-key": api_key}
        )
    
    @staticmethod
    def _deterministic_id(*parts: str) -> str:
        """Generate deterministic ID from parts"""
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def generate_lesson_plan(
        self,
        user_id: str,
        subject: str,
        topic: str,
        level: str = "GCSE",
        preferences: Optional[Dict[str, Any]] = None
    ) -> LessonPlan:
        """
        Generate a lesson plan using AI
        
        Args:
            user_id: User identifier
            subject: Subject name (e.g., "Math", "Biology")
            topic: Topic name (e.g., "Algebra", "Cell Biology")
            level: Education level (default: "GCSE")
            preferences: Optional preferences like detail level, duration
        
        Returns:
            Generated LessonPlan object
        """
        logger.info(f"Generating lesson plan for {subject} - {topic}")
        
        preferences = preferences or {}
        detail_level = preferences.get("detailLevel", "detailed")
        max_subtopics = preferences.get("maxSubtopics", 8)
        
        # Build prompt based on preferences
        system_prompt = (
            f"You are an expert {level} curriculum designer. "
            "Generate a clear, well-structured lesson plan broken into logical subtopics. "
            f"Each subtopic should be {detail_level} and suitable for a 15–45 minute lesson. "
            "Include key concepts for each subtopic. "
            "Provide a brief course description (2-3 sentences) that gives an overview of what "
            "the entire lesson plan covers and what students will achieve by completing it."
        )
        
        user_prompt = (
            f"Generate a {level}-level lesson plan for:\n"
            f"Subject: {subject}\n"
            f"Topic: {topic}\n\n"
            f"Create up to {max_subtopics} subtopics that cover the topic comprehensively. "
            "Ensure subtopics build on each other logically. "
            "Include a description field with 2-3 sentences summarizing the entire course."
        )
        
        try:
            # Call OpenAI with structured output
            completion = self.client.beta.chat.completions.parse(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=LessonPlanLLMResponse,
            )
            
            llm_plan = completion.choices[0].message.parsed
            
            # Generate deterministic IDs
            lesson_plan_id = self._deterministic_id(user_id, subject, topic)
            
            # Convert LLM response to LessonPlan model
            lesson_plan = LessonPlan(
                id=lesson_plan_id,
                userId=user_id,
                subject=llm_plan.subject,
                topic=llm_plan.topic,
                description=llm_plan.description,  # Add AI-generated description
                status="draft",
                aiGeneratedAt=datetime.utcnow(),
                structure=[
                    LessonPlanItem(
                        subtopicId=self._deterministic_id(lesson_plan_id, sub.title),
                        title=sub.title,
                        order=i + 1,
                        estimatedDuration=sub.estimatedDuration or 30,
                        concepts=sub.concepts
                    )
                    for i, sub in enumerate(llm_plan.subtopics)
                ]
            )
            
            # Save to database
            created_plan = self.cosmos.upsert_item("LessonPlans", lesson_plan)
            logger.info(f"Created lesson plan: {created_plan.id}")
            
            return created_plan
            
        except Exception as e:
            logger.error(f"Error generating lesson plan: {e}")
            raise
    
    def get_lesson_plan(self, user_id: str, plan_id: str) -> Optional[LessonPlan]:
        """Get a lesson plan by ID"""
        return self.cosmos.get_item(
            container="LessonPlans",
            item_id=plan_id,
            partition_key=user_id,
            model_class=LessonPlan
        )
    
    def get_user_lesson_plans(self, user_id: str) -> List[LessonPlan]:
        """Get all lesson plans for a user"""
        return self.cosmos.get_items_by_user(
            container="LessonPlans",
            user_id=user_id,
            model_class=LessonPlan,
            item_type="lessonPlan"
        )
    
    def approve_lesson_plan(
        self,
        user_id: str,
        plan_id: str,
        modified_structure: Optional[List[LessonPlanItem]] = None
    ) -> LessonPlan:
        """
        Approve a lesson plan (optionally with modifications)
        
        Args:
            user_id: User identifier
            plan_id: Lesson plan ID
            modified_structure: Optional modified structure if user edited it
        
        Returns:
            Approved LessonPlan
        """
        plan = self.get_lesson_plan(user_id, plan_id)
        if not plan:
            raise ValueError(f"Lesson plan {plan_id} not found")
        
        # Update structure if modified
        if modified_structure:
            plan.structure = modified_structure
        
        # Approve the plan
        plan.status = "approved"
        plan.approvedAt = datetime.utcnow()
        
        # Save
        updated_plan = self.cosmos.update_item("LessonPlans", plan)
        logger.info(f"Approved lesson plan: {plan_id}")
        
        return updated_plan
    
    def update_lesson_plan_structure(
        self,
        user_id: str,
        plan_id: str,
        structure: List[LessonPlanItem]
    ) -> LessonPlan:
        """Update the structure of a lesson plan"""
        plan = self.get_lesson_plan(user_id, plan_id)
        if not plan:
            raise ValueError(f"Lesson plan {plan_id} not found")
        
        plan.structure = structure
        return self.cosmos.update_item("LessonPlans", plan)
    
    def delete_lesson_plan(self, user_id: str, plan_id: str) -> bool:
        """Delete a lesson plan"""
        return self.cosmos.delete_item(
            container="LessonPlans",
            item_id=plan_id,
            partition_key=user_id
        )