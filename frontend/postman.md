1️⃣ Health Check (Sanity Test)

Method: GET
URL:

http://localhost:8000/health


✅ Confirms the API is running.

2️⃣ Create Lesson Plan

Method: POST
URL:

http://localhost:8000/api/lesson-plans


Body (JSON):

{
  "user_id": "test_user_1",
  "subject": "Math",
  "topic": "Algebra",
  "level": "GCSE",
  "auto_approve": false
}


📌 Save from response:

lesson_plan_id

subtopics[].id

3️⃣ Approve Lesson Plan

Method: POST
URL:

http://localhost:8000/api/lesson-plans/approve


Body (JSON):

{
  "user_id": "test_user_1",
  "plan_id": "PASTE_LESSON_PLAN_ID_HERE"
}


✅ Progress tracking is now initialized.

4️⃣ Get All Lesson Plans for User

Method: GET
URL:

http://localhost:8000/api/lesson-plans/test_user_1


Useful to confirm plan state and subtopic count.

5️⃣ Start a Lesson (Pick One Subtopic)

Method: POST
URL:

http://localhost:8000/api/lessons/start


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_plan_id": "PASTE_LESSON_PLAN_ID_HERE",
  "subtopic_id": "PASTE_SUBTOPIC_ID_HERE"
}


📌 Save from response:

lesson_id

sections[].section_id

6️⃣ Expand a Lesson Section

Method: POST
URL:

http://localhost:8000/api/lessons/expand-section


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "PASTE_LESSON_ID_HERE",
  "section_id": "PASTE_SECTION_ID_HERE"
}


✅ Returns expanded explanation for that section only.

7️⃣ Complete Lesson

Method: POST
URL:

http://localhost:8000/api/lessons/complete


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "PASTE_LESSON_ID_HERE",
  "study_time": 20
}


📌 Look for next_action → usually "quiz"

8️⃣ Start Quiz

Method: POST
URL:

http://localhost:8000/api/quizzes/start


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "PASTE_LESSON_ID_HERE",
  "subtopic_id": "PASTE_SUBTOPIC_ID_HERE",
  "difficulty": "mixed",
  "question_count": 3
}


📌 Save from response:

quiz_id

questions[].question_id

9️⃣ Submit Quiz (Mixed Answer Types)

Method: POST
URL:

http://localhost:8000/api/quizzes/submit


Body (JSON):

{
  "user_id": "test_user_1",
  "quiz_id": "PASTE_QUIZ_ID_HERE",
  "responses": [
    {
      "questionId": "q1",
      "userAnswer": "A symbol for an unknown value"
    },
    {
      "questionId": "q2",
      "userAnswer": "Variables can change and are used in equations."
    },
    {
      "questionId": "q3",
      "userBulletPoints": [
        "Represent unknown values",
        "Usually letters",
        "Used in expressions"
      ]
    }
  ]
}


📌 Watch for:

score.percentage

trigger_tutor

🔟 Start Tutor Session (Optional)

Method: POST
URL:

http://localhost:8000/api/tutor/start


Body (JSON):

{
  "user_id": "test_user_1",
  "trigger": "manual",
  "lesson_id": "PASTE_LESSON_ID_HERE",
  "concept": "variables",
  "initial_message": "I'm still confused about variables"
}


📌 Save session_id

1️⃣1️⃣ Send Message to Tutor

Method: POST
URL:

http://localhost:8000/api/tutor/message


Body (JSON):

{
  "user_id": "test_user_1",
  "session_id": "PASTE_SESSION_ID_HERE",
  "message": "Can you give me a simple example?"
}

1️⃣2️⃣ End Tutor Session

Method: POST
URL:

http://localhost:8000/api/tutor/end/test_user_1/PASTE_SESSION_ID_HERE

1️⃣3️⃣ View Dashboard

Method: GET
URL:

http://localhost:8000/api/dashboard/test_user_1


Shows:

Overall progress

Lesson plans

Recommendations

1️⃣4️⃣ View Lesson Plan Progress

Method: GET
URL:

http://localhost:8000/api/progress/test_user_1/PASTE_LESSON_PLAN_ID_HERE