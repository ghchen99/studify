
"""
AI Tutor Service
Handles one-on-one tutoring sessions with AI
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from openai import OpenAI
import logging

from ..shared.models import TutorSession, Lesson
from ..shared.cosmos_client import get_cosmos_service

logger = logging.getLogger(__name__)


class TutorService:
    """Service for AI tutoring sessions"""
    
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
    
    def start_session(
        self,
        user_id: str,
        trigger: str,
        context: Dict[str, Any],
        initial_message: Optional[str] = None
    ) -> TutorSession:
        """Start a new tutoring session"""
        logger.info(f"Starting tutor session for user {user_id}, trigger: {trigger}")
        
        lesson_id = context.get("lessonId")
        lesson_content = ""
        
        if lesson_id:
            lesson = self.cosmos.get_item(
                container="Lessons",
                item_id=lesson_id,
                partition_key=user_id,
                model_class=Lesson
            )
            if lesson:
                lesson_content = self._extract_lesson_context(lesson, context)
        
        system_context = self._build_tutor_system_prompt(context, lesson_content)
        
        conversation = []
        
        if initial_message:
            conversation.append({
                "role": "user",
                "content": initial_message,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        opening = self._generate_tutor_response(
            system_context=system_context,
            conversation_history=conversation,
            context=context
        )
        
        conversation.append({
            "role": "assistant",
            "content": opening,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        session = TutorSession(
            id=str(uuid.uuid4()),
            userId=user_id,
            trigger=trigger,
            context=context,
            conversation=conversation,
            resolved=False,
            createdAt=datetime.utcnow()
        )
        
        created_session = self.cosmos.create_item("TutorSessions", session)
        logger.info(f"Created tutor session: {created_session.id}")
        
        return created_session
    
    def send_message(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> TutorSession:
        """Send a message in an existing session"""
        logger.info(f"Sending message in session {session_id}")
        
        session = self.cosmos.get_item(
            container="TutorSessions",
            item_id=session_id,
            partition_key=user_id,
            model_class=TutorSession
        )
        
        if not session:
            raise ValueError(f"Tutor session {session_id} not found")
        
        session.conversation.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        lesson_id = session.context.get("lessonId")
        lesson_content = ""
        
        if lesson_id:
            lesson = self.cosmos.get_item(
                container="Lessons",
                item_id=lesson_id,
                partition_key=user_id,
                model_class=Lesson
            )
            if lesson:
                lesson_content = self._extract_lesson_context(lesson, session.context)
        
        system_context = self._build_tutor_system_prompt(session.context, lesson_content)
        response = self._generate_tutor_response(
            system_context=system_context,
            conversation_history=session.conversation,
            context=session.context
        )
        
        session.conversation.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        updated_session = self.cosmos.update_item("TutorSessions", session)
        
        return updated_session
    
    def resolve_session(self, user_id: str, session_id: str) -> TutorSession:
        """Mark a session as resolved"""
        session = self.cosmos.get_item(
            container="TutorSessions",
            item_id=session_id,
            partition_key=user_id,
            model_class=TutorSession
        )
        
        if not session:
            raise ValueError(f"Tutor session {session_id} not found")
        
        session.resolved = True
        return self.cosmos.update_item("TutorSessions", session)
    
    def _build_tutor_system_prompt(
        self,
        context: Dict[str, Any],
        lesson_content: str
    ) -> str:
        """Build the system prompt for the tutor"""
        concept = context.get("concept", "this topic")
        question = context.get("question", "")
        
        base_prompt = (
            "You are a patient, encouraging GCSE tutor. Your goal is to help students "
            "understand concepts through guided discovery, not just giving answers. "
            "Use the Socratic method: ask questions, provide hints, and break down complex ideas. "
            "Be warm and supportive. Celebrate small wins. "
            "Use analogies and real-world examples when helpful."
        )
        
        context_prompt = f"\n\nYou're helping with: {concept}"
        
        if question:
            context_prompt += f"\n\nRelated question: {question}"
        
        if lesson_content:
            context_prompt += f"\n\nLesson context:\n{lesson_content}"
        
        return base_prompt + context_prompt
    
    def _generate_tutor_response(
        self,
        system_context: str,
        conversation_history: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Generate a tutor response"""
        
        messages = [{"role": "system", "content": system_context}]
        
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating tutor response: {e}")
            return "I'm having trouble right now. Could you rephrase your question?"
    
    def _extract_lesson_context(
        self,
        lesson: Lesson,
        context: Dict[str, Any]
    ) -> str:
        """Extract relevant lesson content based on context"""
        
        concept = context.get("concept", "").lower()
        
        summary = lesson.content.get("summary", "")
        sections = lesson.content.get("sections", [])
        
        relevant_section = None
        if concept:
            for section in sections:
                section_text = (section.get("content", "") + " " + section.get("title", "")).lower()
                if concept in section_text:
                    relevant_section = section
                    break
        
        if relevant_section:
            return (
                f"Lesson Summary: {summary}\n\n"
                f"Relevant Section - {relevant_section.get('title')}:\n"
                f"{relevant_section.get('content')}"
            )
        else:
            sections_brief = "\n".join([
                f"- {s.get('title')}: {s.get('content', '')[:200]}..."
                for s in sections[:2]
            ])
            return f"Lesson Summary: {summary}\n\nKey Sections:\n{sections_brief}"
    
    def get_session(self, user_id: str, session_id: str) -> Optional[TutorSession]:
        """Get a tutor session by ID"""
        return self.cosmos.get_item(
            container="TutorSessions",
            item_id=session_id,
            partition_key=user_id,
            model_class=TutorSession
        )
    
    def get_user_sessions(
        self,
        user_id: str,
        resolved: Optional[bool] = None
    ) -> List[TutorSession]:
        """Get all tutor sessions for a user"""
        if resolved is not None:
            return self.cosmos.get_items_by_filter(
                container="TutorSessions",
                filters={"resolved": resolved},
                partition_key=user_id,
                model_class=TutorSession
            )
        else:
            return self.cosmos.get_items_by_user(
                container="TutorSessions",
                user_id=user_id,
                model_class=TutorSession,
                item_type="tutorSession"
            )
        