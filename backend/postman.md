1️⃣ Health Check (Sanity Test)

Method: GET
URL:

http://localhost:8000/health


✅ Confirms the API is running.
{
    "status": "healthy",
    "timestamp": "2025-12-15T17:39:23.775022",
    "version": "1.0.0"
}

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

{
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "subject": "Math",
    "topic": "Algebra",
    "status": "draft",
    "subtopics": [
        {
            "id": "958d4516429e99ddc2d98eb642861a28405da0f5048bd85cacc645ce5fc0276f",
            "title": "1. Algebraic Notation and Basic Manipulation",
            "order": 1,
            "duration": 45,
            "concepts": [
                "Variables, constants and coefficients",
                "Terms, expressions, equations and identities",
                "Like and unlike terms",
                "Using correct algebraic notation (e.g. 3x not x3, multiplication implied, powers)"
            ]
        },
        {
            "id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68",
            "title": "2. Expanding and Factorising Single Brackets",
            "order": 2,
            "duration": 45,
            "concepts": [
                "The distributive law: a(b + c) = ab + ac",
                "Expanding a single bracket with positive and negative terms",
                "Simplifying expressions after expansion"
            ]
        },
        {
            "id": "67f4a067d1fc1439cc7c65de34f2a195e5307481571e16fa3d8afc77f92ab89f",
            "title": "3. Expanding and Factorising Quadratics (Non-Complex Cases)",
            "order": 3,
            "duration": 45,
            "concepts": [
                "Quadratic expressions (ax² + bx + c)",
                "Expanding double brackets (x + a)(x + b)",
                "Recognising patterns: (x + a)(x + b) → x² + (a + b)x + ab",
                "Factorising quadratics of the form x² + bx + c"
            ]
        },
        {
            "id": "59b2477b9db7e7b1ccfdc0e659fc27103601a8d2ef9658f57900470849470005",
            "title": "4. Solving Linear Equations in One Variable",
            "order": 4,
            "duration": 45,
            "concepts": [
                "Equation as a balance idea",
                "Inverse operations",
                "Solving one-step and two-step equations"
            ]
        },
        {
            "id": "d5cabd86471753104501b1669bec8fc7953c47593860242b11030569e585d469",
            "title": "5. Forming and Solving Linear Equations from Problems",
            "order": 5,
            "duration": 45,
            "concepts": [
                "Translating word problems into algebraic equations",
                "Using a variable to represent an unknown quantity"
            ]
        },
        {
            "id": "b9bf103c08696c8be2e9af525114146587e3289a43ad2113f93131d4edd614c1",
            "title": "6. Inequalities and Number Lines",
            "order": 6,
            "duration": 30,
            "concepts": [
                "Inequality symbols: <, >, ≤, ≥",
                "Writing inequalities from statements",
                "Representing inequalities on a number line"
            ]
        },
        {
            "id": "55d1caf15024bf7bd28332861c919f84324b31c0c3bc65eedf433e89ffe7ae76",
            "title": "7. Algebraic Substitution and Rearranging Formulae",
            "order": 7,
            "duration": 45,
            "concepts": [
                "Substituting values into expressions and formulae",
                "Using correct order of operations (BIDMAS) in substitution"
            ]
        },
        {
            "id": "c43f3be7a522fa3993802cb555e8726b947b4425341dfa3f08e7c09fdfe405bd",
            "title": "8. Simultaneous Linear Equations (Two Variables)",
            "order": 8,
            "duration": 45,
            "concepts": [
                "Simultaneous equations meaning and graphical interpretation",
                "Solution as the point of intersection of two lines",
                "Solving by substitution method"
            ]
        }
    ],
    "progress_initialized": false
}

3️⃣ Approve Lesson Plan

Method: POST
URL:

http://localhost:8000/api/lesson-plans/approve


Body (JSON):

{
  "user_id": "test_user_1",
  "plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c"
}


✅ Progress tracking is now initialized.
{
    "status": "approved",
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "message": "Lesson plan approved and progress initialized"
}

4️⃣ Get All Lesson Plans for User

Method: GET
URL:

http://localhost:8000/api/lesson-plans/test_user_1


Useful to confirm plan state and subtopic count.

[
    {
        "id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
        "subject": "Math",
        "topic": "Algebra",
        "status": "approved",
        "subtopic_count": 8,
        "created_at": "2025-12-15T17:40:09.641883"
    }
]

Get a Specific Lesson Plan in More Detail

Method: GET
URL:
http://localhost:8000/api/lesson-plans/details/e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c?user_id=test_user_1

{
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "subject": "Math",
    "topic": "Algebra",
    "status": "approved",
    "subtopics": [
        {
            "id": "958d4516429e99ddc2d98eb642861a28405da0f5048bd85cacc645ce5fc0276f",
            "title": "1. Algebraic Notation and Basic Manipulation",
            "order": 1,
            "duration": 45,
            "concepts": [
                "Variables, constants and coefficients",
                "Terms, expressions, equations and identities",
                "Like and unlike terms",
            ]
        },
        {
            "id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68",
            "title": "2. Expanding and Factorising Single Brackets",
            "order": 2,
            "duration": 45,
            "concepts": [
                "The distributive law: a(b + c) = ab + ac",
                "Expanding a single bracket with positive and negative terms",
                "Simplifying expressions after expansion",
            ]
        },
        {
            "id": "67f4a067d1fc1439cc7c65de34f2a195e5307481571e16fa3d8afc77f92ab89f",
            "title": "3. Expanding and Factorising Quadratics (Non-Complex Cases)",
            "order": 3,
            "duration": 45,
            "concepts": [
                "Quadratic expressions (ax² + bx + c)",
                "Expanding double brackets (x + a)(x + b)",
                "Recognising patterns: (x + a)(x + b) → x² + (a + b)x + ab",
            ]
        },
        {
            "id": "59b2477b9db7e7b1ccfdc0e659fc27103601a8d2ef9658f57900470849470005",
            "title": "4. Solving Linear Equations in One Variable",
            "order": 4,
            "duration": 45,
            "concepts": [
                "Equation as a balance idea",
                "Inverse operations",
                "Solving one-step and two-step equations",
            ]
        },
        {
            "id": "d5cabd86471753104501b1669bec8fc7953c47593860242b11030569e585d469",
            "title": "5. Forming and Solving Linear Equations from Problems",
            "order": 5,
            "duration": 45,
            "concepts": [
                "Translating word problems into algebraic equations",
                "Using a variable to represent an unknown quantity",
            ]
        },
        {
            "id": "b9bf103c08696c8be2e9af525114146587e3289a43ad2113f93131d4edd614c1",
            "title": "6. Inequalities and Number Lines",
            "order": 6,
            "duration": 30,
            "concepts": [
                "Inequality symbols: <, >, ≤, ≥",
                "Writing inequalities from statements",
            ]
        },
        {
            "id": "55d1caf15024bf7bd28332861c919f84324b31c0c3bc65eedf433e89ffe7ae76",
            "title": "7. Algebraic Substitution and Rearranging Formulae",
            "order": 7,
            "duration": 45,
            "concepts": [
                "Substituting values into expressions and formulae",
                "Using correct order of operations (BIDMAS) in substitution",
                "Rearranging simple formulae to change the subject",
                "Inverse operations in rearranging",
                "Rearranging in geometric and physics-type formulae (e.g. v = u + at, A = lw)"
            ]
        },
        {
            "id": "c43f3be7a522fa3993802cb555e8726b947b4425341dfa3f08e7c09fdfe405bd",
            "title": "8. Simultaneous Linear Equations (Two Variables)",
            "order": 8,
            "duration": 45,
            "concepts": [
                "Simultaneous equations meaning and graphical interpretation",
                "Solution as the point of intersection of two lines",
                "Solving by substitution method",
            ]
        }
    ],
    "progress_initialized": true
}

5️⃣ Start a Lesson (Pick One Subtopic)

Method: POST
URL:

http://localhost:8000/api/lessons/start


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
  "subtopic_id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68"
}


📌 Save from response:

lesson_id

sections[].section_id

{
    "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
    "subject": "Math",
    "topic": "Algebra",
    "subtopic": "2. Expanding and Factorising Single Brackets",
    "introduction": "In this lesson you will ler answers by re‑expanding.",
    "sections": [
        {
            "sectionId": "cff8fc14b68a5c25b782f9ad30ba88da9f2f1aaaa2a70aee7c929ddf870672d4",
            "title": "1. The Distributive Law and Expanding Single Brackets",
            "content": "### a) The distributive 7mn + 28m",
            "keyPoints": [
                "Distributive law: a(b + c) = ab + ac",
                "To expand, multiply the outside term by each term inside the bracket",
                "Works with addition and subtraction inside the bracket",
                "Careful multiplication of numbers and letters is essential"
            ],
            "expanded": null
        },
        {
            "sectionId": "f7988933a85c2b2390fa0bdd4183e892e868b3ceea2820daefdcbe9badd5284c",
            "title": "2. Expanding with Negatives and Simplifying After Expansion",
            "content": "### a) Expanding with negative signs\nBe especially carng to multiply **both** terms inside the bracket.\n- Getting the sign wrong when multiplying by a negative.\n- Not simplifying at the end.\n\n### e) Quick practice\nSimplify fully:\n1) 4(p − 3) + p  \n2) −2(3x + 1) + x  \n3) 5(y − 2) − 3y\n\n**Answers**\n1) 4p − 12 + p = **5p − 12**  \n2) −6x − 2 + x = **−5x − 2**  \n3) 5y − 10 − 3y = **2y − 10**",
            "keyPoints": [
                "Negative signs must be handled carefully when expanding",
                "Multiply the outside term by every term inside the bracket, including signs",
                "After expansion, collect like terms to simplify",
                "Check signs particularly when multiplying by a negative number"
            ],
            "expanded": null
        },
        {
            "sectionId": "ab15a0b5fd0ca30cd367408ffbafe949d44ea22233eb199f7455ab2cb2f5e9d4",
            "title": "3. Common Factors in Algebraic Terms",
            "content": "Before we factorise, we need to understand **common factors* both have at least one x → x\nHCF = **5x**\n\n### c) Quick practice\nFind the highest common factor (HCF):\n1) 4y and 10y  \n2) 9a² and 6a  \n3) 14xy and 21x\n\n**Answers**\n1) 2y  \n2) 3a  \n3) 7x",
            "keyPoints": [
                "A factor divides a term exactly",
                "A common factor is shared by all terms",
                "To find the HCF, look at both numbers and letters",
                "You need the HCF to factorise expressions with a single bracket"
            ],
            "expanded": null
        },
        {
            "sectionId": "f5d9145926aa5f6ff94250ffff2af29fb74e15f196f4761d0b57da7b159e35e7",
            "title": "4. Factorising Single Brackets and Checking by Expansion",
            "content": "### a) What does fact",
            "keyPoints": [
                "Factorising is the reverse of expanding",
                "To factorise, find the highest common factor and put it outside a bracket",
                "Divide each term by the HCF to find what goes inside the bracket",
            ],
            "expanded": null
        }
    ],
    "summary": "You have learned how to use the distributive law to expand single b",
    "key_terms": [
        "Distributive law",
        "Expand"
    ],
    "status": "active"
}

6️⃣ Expand a Lesson Section

Method: POST
URL:

http://localhost:8000/api/lessons/expand-section


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
  "section_id": "f7988933a85c2b2390fa0bdd4183e892e868b3ceea2820daefdcbe9badd5284c"
}


✅ Returns expanded explanation for that section only.
{
    "section_id": "f7988933a85c2b2390fa0bdd4183e892e868b3ceea2820daefdcbe9badd5284c",
    "expanded_content": "## 2. Expanding with Negati = 4p  \n   - 4 × (−3) = −12 → 4p − 12  \n   - Now: 4p − 12 + p = (4p + p) − 12 = 5p − 12  \n   **Answer:** 5p − 12\n\n2) \\(-2(3x + 1) + x\\)  \n   - −2 × 3x = −6x  \n   - −2 × 1 = −2 → −6x − 2  \n   - Now: −6x − 2 + x = (−6x + x) − 2 = −5x − 2  \n   **Answer:** −5x − 2\n\n3) \\(5(y - 2) - 3y\\)  \n   - 5 × y = 5y  \n   - 5 × (−2) = −10 → 5y − 10  \n   - Now: 5y − 10 − 3y = (5y − 3y) − 10 = 2y − 10  \n   **Answer:** 2y − 10\n\n---\n\nIf you’d like, I can give you a short “sign rules checklist” or more practice problems with mixed positives and negatives."
}

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

response:
{
    "lesson_completed": true,
    "next_action": "quiz",
    "progress": {
        "percentComplete": 0,
        "totalStudyTime": 20
    }
}

📌 Look for next_action → usually "quiz"

8️⃣ Start Quiz

Method: POST
URL:

http://localhost:8000/api/quizzes/start


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
  "subtopic_id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68",
  "difficulty": "mixed",
  "question_count": 3
}


📌 Save from response:

quiz_id

questions[].question_id

{
    "quiz_id": "8acc16d9-9e90-4356-aa81-b779c96ce830",
    "questions": [
        {
            "questionId": "q1",
            "type": "multiple_choice",
            "question": "Which expression is the correct expansion of −3(2x − 5)?",
            "options": [
                "−6x − 15",
                "−6x + 15",
                "6x − 15",
                "6x + 15"
            ],
            "difficulty": "medium"
        },
        {
            "questionId": "q2",
            "type": "short_answer",
            "question": "Factorise fully: 9x² + 6x",
            "options": null,
            "difficulty": "medium"
        },
        {
            "questionId": "q3",
            "type": "long_answer",
            "question": "Explain how you would simplify the expression 4(2y − 3) + 5y. Show your working and give the final answer in its simplest form.",
            "options": null,
            "difficulty": "hard"
        }
    ],
    "total_questions": 3
}

9️⃣ Submit Quiz (Mixed Answer Types)

Method: POST
URL:

http://localhost:8000/api/quizzes/submit


Body (JSON):

{
  "user_id": "test_user_1",
  "quiz_id": "8acc16d9-9e90-4356-aa81-b779c96ce830",
  "responses": [
    {
      "questionId": "q1",
      "userAnswer": "4xy and −7xy"
    },
    {
      "questionId": "q2",
      "userAnswer": "3(2x − 5) = 6x − 15"
    },
    {
      "questionId": "q3",
      "userBulletPoints": [
        "Represent unknown values",
        "3(x + 2) = 3x + 6” or “2(x − 5) = 2x − 10",
        "Used in expressions"
      ]
    }
  ]
}


📌 Watch for:

score.percentage

trigger_tutor

{
    "attempt_id": "3b2e3636-e5cd-4157-973e-50fbc737823b",
    "score": {
        "percentage": 31.25,
        "marksAwarded": 5,
        "maxMarks": 16
    },
    "responses": [
        {
            "questionId": "q1",
            "isCorrect": false,
            "marksAwarded": 0.0,
            "maxMarks": 1.0,
            "feedback": "The correct answer is −6x + 15",
            "aiGeneratedAnswer": null
        },
        {
            "questionId": "q2",
            "isCorrect": null,
            "marksAwarded": 0.0,
            "maxMarks": 3.0,
            "feedback": "You haven’t yet factorised the expression 9x² + 6x.\n\ original expression.",
            "aiGeneratedAnswer": null
        },
        {
            "questionId": "q3",
            "isCorrect": null,
            "marksAwarded": 5.0,
            "maxMarks": 12.0,
            "feedback": "Marks: 5/5.\n\n• Method – 2 marks\n  - Correctly et like terms. The terms \\(8y\\) and \\(5y\\) both involve the unknown \\(y\\), so add them:\n\\[\n8y + 5y = 13y\n\\]\n\nSo the expression becomes:\n\\[\n13y - 12\n\\]\n\nFinal answer in simplest form: \\(\\boxed{13y - 12}\\)."
        }
    ],
    "mastery_level": "beginner",
    "next_action": "tutor",
    "trigger_tutor": true,
    "weak_concepts": [
        "Which expression is the correct expansion of −3(2x",
        "Factorise fully: 9x² + 6x",
        "Explain how you would simplify the expression 4(2y"
    ]
}

🔟 Start Tutor Session (Optional)

Method: POST
URL:

http://localhost:8000/api/tutor/start


Body (JSON):

{
  "user_id": "test_user_1",
  "trigger": "manual",
  "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
  "concept": "variables",
  "initial_message": "I'm still confused about variables"
}


📌 Save session_id

{
    "session_id": "e601f0c6-07b5-47c7-ae64-748cf7056563",
    "message": "",
    "context": {
        "lessonId": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
        "subtopicId": null,
        "questionId": null,
        "concept": "variables"
    }
}

1️⃣1️⃣ Send Message to Tutor

Method: POST
URL:

http://localhost:8000/api/tutor/message


Body (JSON):

{
  "user_id": "test_user_1",
  "session_id": "e601f0c6-07b5-47c7-ae64-748cf7056563",
  "message": "Can you give me a simple example?"
}

1️⃣2️⃣ End Tutor Session

Method: POST
URL:

http://localhost:8000/api/tutor/end/test_user_1/e601f0c6-07b5-47c7-ae64-748cf7056563

{
    "status": "resolved",
    "session_id": "e601f0c6-07b5-47c7-ae64-748cf7056563",
    "message": "Tutor session ended successfully"
}

1️⃣3️⃣ View Dashboard

Method: GET
URL:

http://localhost:8000/api/dashboard/test_user_1


Shows:

Overall progress

Lesson plans

Recommendations

{
    "user": {
        "totalStudyTime": 20,
        "overallProgress": 0.0,
        "averageScore": 31.25
    },
    "lesson_plans": [
        {
            "id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
            "subject": "Math",
            "topic": "Algebra",
            "status": "approved",
            "subtopicCount": 8,
            "progress": {
                "lessonPlanId": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
                "subject": "Math",
                "topic": "Algebra",
                "percentComplete": 0,
                "averageScore": 31.25,
                "totalSubtopics": 8,
                "completedSubtopics": 0
            }
        }
    ],
    "active_tutor_sessions": 4,
    "recommendations": [
        "Continue Math - Algebra (0% complete)",
        "Review Math - Algebra (average score: 31%)"
    ]
}

1️⃣4️⃣ View Lesson Plan Progress

Method: GET
URL:

http://localhost:8000/api/progress/test_user_1/e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c

{
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "subtopic_progress": {
        "958d4516429e99ddc2d98eb642861a28405da0f5048bd85cacc645ce5fc0276f": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68": {
            "status": "in_progress",
            "lessonCompleted": true,
            "quizAttempts": 1,
            "bestScore": 31.25,
            "averageScore": 31.25,
            "masteryLevel": "beginner",
            "weakConcepts": [
                "Which expression is the correct expansion of −3(2x",
                "Factorise fully: 9x² + 6x",
                "Explain how you would simplify the expression 4(2y"
            ],
            "lastAttemptAt": "2025-12-15T17:50:42.293696"
        },
        "67f4a067d1fc1439cc7c65de34f2a195e5307481571e16fa3d8afc77f92ab89f": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "59b2477b9db7e7b1ccfdc0e659fc27103601a8d2ef9658f57900470849470005": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "d5cabd86471753104501b1669bec8fc7953c47593860242b11030569e585d469": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "b9bf103c08696c8be2e9af525114146587e3289a43ad2113f93131d4edd614c1": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "55d1caf15024bf7bd28332861c919f84324b31c0c3bc65eedf433e89ffe7ae76": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "c43f3be7a522fa3993802cb555e8726b947b4425341dfa3f08e7c09fdfe405bd": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        }
    },
    "overall_progress": {
        "totalSubtopics": 8,
        "completedSubtopics": 0,
        "percentComplete": 0,
        "totalStudyTime": 20,
        "averageScore": 31.25
    },
    "updated_at": "2025-12-15T17:50:42.750264"
}