
"""
Lesson Service
Handles lesson content generation, expansion, and management
"""
import os
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel
import logging

from shared.models import Lesson, LessonSection, LessonPlan
from shared.cosmos_client import get_cosmos_service

logger = logging.getLogger(__name__)


class LessonSectionLLM(BaseModel):
    """LLM response for lesson section"""
    title: str
    content: str
    keyPoints: List[str]


class LessonContentLLM(BaseModel):
    """LLM response for full lesson content"""
    introduction: str
    sections: List[LessonSectionLLM]
    summary: str
    keyTerms: List[str]


class LessonService:
    """Service for managing lessons"""
    
    def __init__(self):
        self.cosmos = get_cosmos_service()
        
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
        """Generate deterministic ID"""
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def generate_lesson(
        self,
        user_id: str,
        lesson_plan_id: str,
        subtopic_id: str,
        level: str = "GCSE"
    ) -> Lesson:
        """
        Generate lesson content for a specific subtopic
        
        Args:
            user_id: User identifier
            lesson_plan_id: Parent lesson plan ID
            subtopic_id: Subtopic ID from the lesson plan
            level: Education level
        
        Returns:
            Generated Lesson object
        """
        logger.info(f"Generating lesson for subtopic: {subtopic_id}")
        
        # Get the lesson plan to retrieve subtopic details
        lesson_plan = self.cosmos.get_item(
            container="LessonPlans",
            item_id=lesson_plan_id,
            partition_key=user_id,
            model_class=LessonPlan
        )
        
        if not lesson_plan:
            raise ValueError(f"Lesson plan {lesson_plan_id} not found")
        
        # Find the subtopic
        subtopic_item = next(
            (st for st in lesson_plan.structure if st.subtopicId == subtopic_id),
            None
        )
        
        if not subtopic_item:
            raise ValueError(f"Subtopic {subtopic_id} not found in lesson plan")
        
        # Generate lesson content
        system_prompt = (
            f"You are an expert {level} teacher. "
            "Generate comprehensive, engaging lesson content that is clear and age-appropriate. "
            "Break down complex concepts into understandable sections. "
            "Include examples and analogies where helpful. "
            "Output the lesson in **Markdown format**, using proper headings, bullet points, numbered lists, and LaTeX math where appropriate."
        )

        concepts_str = ", ".join(subtopic_item.concepts)
        user_prompt = (
            f"Create a detailed {level} lesson for:\n"
            f"Subject: {lesson_plan.subject}\n"
            f"Topic: {lesson_plan.topic}\n"
            f"Subtopic: {subtopic_item.title}\n"
            f"Key Concepts: {concepts_str}\n\n"
            f"The lesson should take approximately {subtopic_item.estimatedDuration} minutes.\n\n"
            "Lesson structure requirements:\n"
            "• Use clear, descriptive section titles instead of numeric labels (avoid formats like 1.1, 1.2).\n"
            "• Organize the lesson in a natural instructional flow that feels like a real classroom lesson.\n\n"
            "Include the following sections:\n\n"
            "## Introduction\n"
            "- Briefly introduce the subtopic and explain why it is important or relevant.\n\n"
            "## Core Lesson Sections\n"
            "- Create 2–4 main sections, each with an engaging, meaningful heading (e.g., conceptual names, guiding questions, or real-world connections).\n"
            "- Each section should clearly explain one or more key concepts using examples, explanations, or short activities where appropriate.\n\n"
            "## Summary & Key Takeaways\n"
            "- Concisely recap the most important ideas students should remember.\n\n"
            "## Key Terms\n"
            "- Provide a bullet-point list of essential vocabulary with brief definitions.\n\n"
            "Formatting and style guidelines:\n"
            "- Use Markdown for all formatting.\n"
            "- Use `#` and `##` for headings and subheadings.\n"
            "- Use `-` or `*` for bullet points.\n"
            "- Use `1.` for numbered lists only when sequence matters.\n"
            "- Use `$...$` for inline math and `$$...$$` for block math when needed.\n\n"
            "Ensure the lesson is engaging, clearly written, and ready to render in a Markdown/KaTeX environment."
        )

        
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=LessonContentLLM,
            )
            
            llm_lesson = completion.choices[0].message.parsed
            
            # Generate lesson ID
            lesson_id = self._deterministic_id(lesson_plan_id, subtopic_id)
            
            # Convert to Lesson model
            lesson = Lesson(
                id=lesson_id,
                userId=user_id,
                lessonPlanId=lesson_plan_id,
                subtopicId=subtopic_id,
                subject=lesson_plan.subject,
                topic=lesson_plan.topic,
                subtopic=subtopic_item.title,
                content={
                    "introduction": llm_lesson.introduction,
                    "sections": [
                        {
                            "sectionId": self._deterministic_id(lesson_id, f"section_{i}"),
                            "title": section.title,
                            "content": section.content,
                            "keyPoints": section.keyPoints,
                            "expanded": None
                        }
                        for i, section in enumerate(llm_lesson.sections)
                    ],
                    "summary": llm_lesson.summary,
                    "keyTerms": llm_lesson.keyTerms
                },
                status="active"
            )
            
            # Save to database
            created_lesson = self.cosmos.upsert_item("Lessons", lesson)
            logger.info(f"Created lesson: {created_lesson.id}")
            
            return created_lesson
            
        except Exception as e:
            logger.error(f"Error generating lesson: {e}")
            raise
    
    def expand_section(
        self,
        user_id: str,
        lesson_id: str,
        section_id: str
    ) -> Lesson:
        """
        Expand a specific section with more detailed content
        
        Args:
            user_id: User identifier
            lesson_id: Lesson ID
            section_id: Section ID to expand
        
        Returns:
            Updated Lesson with expanded section
        """
        logger.info(f"Expanding section {section_id} in lesson {lesson_id}")
        
        # Get the lesson
        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=lesson_id,
            partition_key=user_id,
            model_class=Lesson
        )
        
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        # Find the section
        section_index = None
        section_data = None
        for i, section in enumerate(lesson.content.get("sections", [])):
            if section.get("sectionId") == section_id:
                section_index = i
                section_data = section
                break
        
        if section_data is None:
            raise ValueError(f"Section {section_id} not found")
        
        # Generate expanded content
        system_prompt = (
            "You are an expert teacher. Expand on the given section with more depth, "
            "examples, and detailed explanations. Make it engaging and thorough."
        )
        
        user_prompt = (
            f"Expand this section with much more detail:\n\n"
            f"Title: {section_data.get('title')}\n"
            f"Current Content: {section_data.get('content')}\n\n"
            f"Provide:\n"
            "- More detailed explanations\n"
            "- 2-3 concrete examples\n"
            "- Step-by-step breakdowns where applicable\n"
            "- Real-world applications or analogies"
        )
        
        try:
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            expanded_content = completion.choices[0].message.content
            
            # Update the section
            lesson.content["sections"][section_index]["expanded"] = expanded_content
            
            # Save updated lesson
            updated_lesson = self.cosmos.update_item("Lessons", lesson)
            logger.info(f"Expanded section {section_id}")
            
            return updated_lesson
            
        except Exception as e:
            logger.error(f"Error expanding section: {e}")
            raise
    
    def mark_lesson_complete(
        self,
        user_id: str,
        lesson_id: str
    ) -> Lesson:
        """Mark a lesson as completed"""
        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=lesson_id,
            partition_key=user_id,
            model_class=Lesson
        )
        
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        lesson.status = "completed"
        lesson.completedAt = datetime.now(timezone.utc)
        
        return self.cosmos.update_item("Lessons", lesson)
    
    def get_lesson(self, user_id: str, lesson_id: str) -> Optional[Lesson]:
        """Get a lesson by ID"""
        return self.cosmos.get_item(
            container="Lessons",
            item_id=lesson_id,
            partition_key=user_id,
            model_class=Lesson
        )
    
    def get_lessons_for_plan(
        self,
        user_id: str,
        lesson_plan_id: str
    ) -> List[Lesson]:
        """Get all lessons for a lesson plan"""
        return self.cosmos.get_items_by_filter(
            container="Lessons",
            filters={"lessonPlanId": lesson_plan_id},
            partition_key=user_id,
            model_class=Lesson
        )
    
    def get_lesson_for_subtopic(
        self,
        user_id: str,
        subtopic_id: str
    ) -> Optional[Lesson]:
        """Get lesson for a specific subtopic"""
        lessons = self.cosmos.get_items_by_filter(
            container="Lessons",
            filters={"subtopicId": subtopic_id},
            partition_key=user_id,
            model_class=Lesson
        )
        return lessons[0] if lessons else None
    
