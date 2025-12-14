# AI-Powered Learning Platform Design Document

## Overview
A personalized learning platform that uses generative AI to create lessons, quizzes, and interactive support. It adapts to each user’s progress and acts as a personal tutor, helping students study efficiently for exams like the GCSEs.

---

## Key Features

### 1. Lesson Plan Generation
- AI generates a **full lesson plan** for selected topics (e.g., Biology Topic A: Subtopics 1, 2, 3, 4).  
- Users can **review, approve, or edit** the lesson plan.  
- Once approved, the lesson plan becomes a **grounded progress tracker**.  
- Acts as a roadmap for dynamic lesson generation.

### 2. Dynamic Lesson Generation
- AI generates **individual lessons for each approved subtopic**.  
- Lessons include explanations, examples, diagrams, and summaries.  
- Typical lesson duration: ~15 minutes.

### 3. Practice and Quizzes
- AI generates practice questions for each lesson:
  - Multiple-choice
  - Short-answer
  - Long-answer (actually take bullet points as input, AI geenrates your long answer, mark schemes tend to have short bullet points for long-answers, reverse-engineering)
  - Scenario-based  
- Instant feedback with explanations.

### 4. AI Tutor Support (Optional Callout)
- Triggered when:
  - The user repeatedly answers similar questions incorrectly.
  - The user clicks “Need help?” or "Expand" on the lesson content
- Provides bite-sized explanations and diagrams.
- Fully optional, user chooses when to engage.

### 5. Adaptive Learning
- Tracks performance per subtopic and question type.
- Adjusts future lessons and quizzes based on strengths and weaknesses.
- Prioritizes weaker areas for review.

### 6. User Progress & Motivation
- Progress tracker tied to the **approved lesson plan**.
- Dashboard shows completed subtopics, mastered areas, and pending lessons.
- Everything that's generated dynamically e.g. lessons, expanding sections of notes, support with any quizzes answers are stored permanently in the database for the user to revise with and have a record of.

---

## User Flow

1. **Onboarding**
   - User selects level, subject, topics, and learning style.
   - Optional: set study goals and exam dates.

2. **Lesson Plan Generation**
   - AI generates full topic breakdown with subtopics.
   - User reviews, edits, and approves lesson plan.
   - Approved plan becomes a **static roadmap** for progress tracking.

3. **Dynamic Lesson Generation**
   - AI generates a lesson for each subtopic.
   - Includes explanations, diagrams, examples, and summary.

4. **Practice**
   - AI generates practice questions for each lesson.
   - Tracks correct/incorrect answers.

5. **AI Tutor Callout (Optional)**
   - Appears only if the user struggles with content or requests help during quizzes.
   - Provides simplified explanations, diagrams, and additional exercises.

6. **Adaptive Next Steps**
   - Platform adjusts future lessons based on performance.
   - Focuses on weaker subtopics or concepts.

---

## Technical Overview
- **Frontend:** Web app with interactive lessons, quizzes, lesson plan editor, and chat support.
- **Backend:** 
  - AI engine for lesson plan, lesson, and quiz generation.
  - Database for user profiles, approved lesson plans, progress tracking, and generated content.
  - Adaptive engine for dynamic lesson generation.
  - Media service for diagrams, animations, and visual content, Nano Banana or DALLE.