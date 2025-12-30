"""
Quiz Service
Handles quiz generation, submission, and grading
"""
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from openai import OpenAI
from pydantic import BaseModel
import logging

from shared.models import Quiz, Question, QuizAttempt, QuizAttemptResponse, Lesson
from shared.cosmos_client import get_cosmos_service

logger = logging.getLogger(__name__)


class QuestionLLM(BaseModel):
    """LLM response for a question"""
    type: str  # multiple_choice, short_answer, long_answer
    question: str
    options: Optional[List[str]] = None
    correctAnswer: Optional[str] = None
    markScheme: Optional[List[str]] = None
    maxMarks: Optional[float] = None
    difficulty: str


class QuizLLM(BaseModel):
    """LLM response for quiz"""
    questions: List[QuestionLLM]


class QuizGradingLLM(BaseModel):
    """LLM response for grading"""
    marksAwarded: float
    maxMarks: float
    feedback: str
    generatedAnswer: Optional[str] = None


class QuizService:
    """Service for managing quizzes"""
    
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
    
    def generate_quiz(
        self,
        user_id: str,
        lesson_id: str,
        subtopic_id: str,
        question_types: Optional[List[str]] = None,
        difficulty: str = "mixed",
        count: int = 5
    ) -> Quiz:
        """Generate a quiz for a lesson"""
        logger.info(f"Generating quiz for lesson: {lesson_id}")
        
        lesson = self.cosmos.get_item(
            container="Lessons",
            item_id=lesson_id,
            partition_key=user_id,
            model_class=Lesson
        )
        
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        question_types = question_types or ["multiple_choice", "short_answer", "long_answer"]
        
        lesson_summary = lesson.content.get("summary", "")
        key_terms = lesson.content.get("keyTerms", [])
        sections = lesson.content.get("sections", [])
        
        sections_text = "\n\n".join([
            f"Section: {s.get('title')}\n{s.get('content')}"
            for s in sections
        ])
        
        system_prompt = (
            "You are an expert GCSE assessment designer. "
            "Create fair, clear questions that test understanding of the lesson content. "
            "Multiple choice questions should have plausible distractors. "
            "Short answer questions should be answerable in 1-2 sentences. "
            "Long answer questions should require 3-5 sentences and deeper understanding."
        )
        
        user_prompt = (
            f"Create {count} questions based on this lesson:\n\n"
            f"Subject: {lesson.subject}\n"
            f"Topic: {lesson.topic}\n"
            f"Subtopic: {lesson.subtopic}\n\n"
            f"Lesson Content:\n{sections_text}\n\n"
            f"Summary: {lesson_summary}\n\n"
            f"Key Terms: {', '.join(key_terms)}\n\n"
            f"Question Types to Include: {', '.join(question_types)}\n"
            f"Difficulty: {difficulty}\n\n"
            "Distribute questions across the content. "
            "For multiple choice, provide 4 options. "
            "For short/long answers, provide detailed mark schemes. "
            "For every question include a numeric `maxMarks` field indicating the total marks available. "
            "For multiple choice questions, use 1 mark unless there is a reason to use more. "
        )
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=QuizLLM,
            )
            
            llm_quiz = completion.choices[0].message.parsed
            quiz_id = str(uuid.uuid4())
            
            quiz = Quiz(
                id=quiz_id,
                userId=user_id,
                lessonId=lesson_id,
                subtopicId=subtopic_id,
                questions=[
                    # Determine per-question marks: prefer explicit mark scheme length,
                    # otherwise fall back to sensible defaults by type.
                    Question(
                        questionId=f"q{i+1}",
                        type=q.type,
                        question=q.question,
                        options=q.options,
                        correctAnswer=q.correctAnswer,
                        markScheme=q.markScheme,
                        maxMarks=float(q.maxMarks),
                        difficulty=q.difficulty
                    )
                    for i, q in enumerate(llm_quiz.questions)
                ],
                createdAt=datetime.now(timezone.utc)
            )
            
            created_quiz = self.cosmos.create_item("Quizzes", quiz)
            logger.info(f"Created quiz: {created_quiz.id}")
            
            return created_quiz
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            raise
    
    def submit_quiz(
        self,
        user_id: str,
        quiz_id: str,
        responses: List[Dict[str, Any]]
    ) -> QuizAttempt:
        """Submit and grade a quiz attempt"""
        logger.info(f"Submitting quiz: {quiz_id}")
        
        quiz = self.cosmos.query_items(
            container="Quizzes",
            query="SELECT * FROM c WHERE c.id = @quizId",
            partition_key=user_id,
            model_class=Quiz,
            parameters=[{"name": "@quizId", "value": quiz_id}]
        )
        
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        quiz = quiz[0]
        
        graded_responses = []
        total_correct = 0
        total_marks = 0
        max_marks = 0
        
        for resp in responses:
            question_id = resp.get("questionId")
            user_answer = resp.get("userAnswer")
            
            question = next(
                (q for q in quiz.questions if q.questionId == question_id),
                None
            )
            
            if not question:
                continue
            
            if question.type == "multiple_choice":
                is_correct = user_answer == question.correctAnswer
                q_max = float(question.maxMarks) if getattr(question, 'maxMarks', None) is not None else 1.0
                awarded = q_max if is_correct else 0.0
                graded_responses.append(QuizAttemptResponse(
                    questionId=question_id,
                    userAnswer=user_answer,
                    isCorrect=is_correct,
                    marksAwarded=awarded,
                    maxMarks=q_max,
                    feedback="Correct!" if is_correct else f"The correct answer is {question.correctAnswer}"
                ))
                if is_correct:
                    total_correct += 1
                total_marks += awarded
                max_marks += q_max
            
            else:
                grading = self._grade_written_answer(
                    question=question.question,
                    mark_scheme=question.markScheme or [],
                    user_answer=user_answer or "",
                    question_type=question.type,
                    question_max_marks=getattr(question, 'maxMarks', None)
                )
                
                graded_responses.append(QuizAttemptResponse(
                    questionId=question_id,
                    userAnswer=user_answer,
                    aiGeneratedAnswer=grading.generatedAnswer,
                    marksAwarded=grading.marksAwarded,
                    maxMarks=grading.maxMarks,
                    feedback=grading.feedback
                ))
                
                total_marks += grading.marksAwarded
                max_marks += grading.maxMarks
        
        percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
        trigger_tutor = percentage < 40 or self._has_repeated_mistakes(graded_responses)
        weak_concepts = self._identify_weak_concepts(graded_responses, quiz.questions)
        
        attempt = QuizAttempt(
            id=str(uuid.uuid4()),
            userId=user_id,
            quizId=quiz_id,
            lessonId=quiz.lessonId,
            subtopicId=quiz.subtopicId,
            state="completed",
            responses=graded_responses,
            score={
                "correct": total_correct,
                "total": len(responses),
                "percentage": percentage,
                "marksAwarded": total_marks,
                "maxMarks": max_marks,
                "triggerTutor": trigger_tutor,
                "weakConcepts": weak_concepts
            },
            completedAt=datetime.now(timezone.utc)
        )
        
        created_attempt = self.cosmos.create_item("QuizAttempts", attempt)
        logger.info(f"Created quiz attempt: {created_attempt.id}")
        
        return created_attempt
    
    def _grade_written_answer(
        self,
        question: str,
        mark_scheme: List[str],
        user_answer: str,
        question_type: str
        ,
        question_max_marks: Optional[float] = None
    ) -> QuizGradingLLM:
        """Grade a written answer using AI"""
        
        # Prefer the explicit per-question max provided when the quiz was generated.
        if question_max_marks is not None:
            max_marks = float(question_max_marks)
        else:
            max_marks = float(len(mark_scheme)) if mark_scheme else (3.0 if question_type == "short_answer" else 6.0)
        
        generated_answer = None
        # Grade based only on the student's submitted answer. Bullet-point
        # entry was removed from the backend — do not rely on any notes.
        original_student_answer = user_answer or ""

        mark_scheme_text = "\n".join(f"{i+1}. {m}" for i, m in enumerate(mark_scheme))

        grade_prompt = (
            f"Grade this answer according to the mark scheme:\n\n"
            f"Question: {question}\n\n"
            f"Mark Scheme ({max_marks} marks total):\n{mark_scheme_text}\n\n"
            f"Student Answer: {original_student_answer}\n\n"
            "Award partial marks for partially correct points based on the student's answer. "
            "Provide constructive feedback on what was good and what was missing."
        )
        
        try:
            grade_response = self.client.beta.chat.completions.parse(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a fair, constructive GCSE examiner."},
                    {"role": "user", "content": grade_prompt}
                ],
                response_format=QuizGradingLLM
            )
            
            grading = grade_response.choices[0].message.parsed
            grading.generatedAnswer = generated_answer
            grading.maxMarks = max_marks
            
            return grading
            
        except Exception as e:
            logger.error(f"Error grading answer: {e}")
            return QuizGradingLLM(
                marksAwarded=0.0,
                maxMarks=max_marks,
                feedback="Unable to grade answer automatically.",
                generatedAnswer=generated_answer
            )
    
    def _has_repeated_mistakes(self, responses: List[QuizAttemptResponse]) -> bool:
        """Check if student made 3+ similar mistakes"""
        incorrect = sum(1 for r in responses if r.isCorrect is False or (r.marksAwarded or 0) < (r.maxMarks or 1) * 0.5)
        return incorrect >= 3
    
    def _identify_weak_concepts(
        self,
        responses: List[QuizAttemptResponse],
        questions: List[Question]
    ) -> List[str]:
        """Identify concepts the student struggled with"""
        weak = []
        for resp in responses:
            if resp.isCorrect is False or (resp.marksAwarded or 0) < (resp.maxMarks or 1) * 0.5:
                question = next((q for q in questions if q.questionId == resp.questionId), None)
                if question:
                    weak.append(question.question[:50])
        return weak[:3]
    
    def get_quiz(self, user_id: str, quiz_id: str) -> Optional[Quiz]:
        """Get a quiz by ID"""
        quizzes = self.cosmos.query_items(
            container="Quizzes",
            query="SELECT * FROM c WHERE c.id = @quizId",
            partition_key=user_id,
            model_class=Quiz,
            parameters=[{"name": "@quizId", "value": quiz_id}]
        )
        return quizzes[0] if quizzes else None
    
    def get_quiz_attempts(
        self,
        user_id: str,
        quiz_id: Optional[str] = None,
        subtopic_id: Optional[str] = None
    ) -> List[QuizAttempt]:
        """Get quiz attempts for a user"""
        filters = {}
        if quiz_id:
            filters["quizId"] = quiz_id
        if subtopic_id:
            filters["subtopicId"] = subtopic_id
        
        if filters:
            return self.cosmos.get_items_by_filter(
                container="QuizAttempts",
                filters=filters,
                partition_key=user_id,
                model_class=QuizAttempt
            )
        else:
            return self.cosmos.get_items_by_user(
                container="QuizAttempts",
                user_id=user_id,
                model_class=QuizAttempt,
                item_type="quizAttempt"
            )
    