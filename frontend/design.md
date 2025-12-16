1️⃣ Hierarchy Mapping

Your data has a clear hierarchy already:

Lesson Plan (Course)
 ├─ Subtopic (Lesson)
 │    ├─ Sections (Content units)
 │    └─ Quiz(es)
 └─ Progress & Quiz scores


So in the UI, you should reflect this naturally:

Lesson Plans Tab → Lists all courses (Math - Algebra, etc.)

Lessons Tab → Lists all subtopics of the selected lesson plan

Quizzes Tab → Shows quizzes associated with the selected lesson/subtopic

2️⃣ UI Tab Structure

Here’s one approach:

a) Sidebar / Top Tabs for Lesson Plans (Courses)

Show all lesson plans in a list or cards.

Clicking a lesson plan loads its lessons and progress in the main area.

[Lesson Plans] [Lessons] [Quizzes]

b) Lessons Tab

Contextual: Only shows lessons (subtopics) of the currently selected lesson plan.

Columns / Cards could include:

Subtopic title

Duration

Status (not started / in progress / completed)

Quiz available? (icon or button)

Optional: Collapsible sections for content (sections of that subtopic).

c) Quizzes Tab

Contextual: Filters quizzes by the selected lesson plan.

Grouping options:

By Lesson/Subtopic: e.g., “2. Expanding and Factorising Single Brackets” → Quiz 1, Quiz 2

By Status: Pending, Completed, Needs Review

Show: Score, attempts, mastery level

3️⃣ Linking Lessons & Quizzes to Lesson Plans

There are two key approaches:

a) Contextual Filtering (Recommended)

Store a selected lesson plan ID in the app state.

All other tabs (Lessons / Quizzes) filter based on that lesson plan ID.

Example:

selectedLessonPlanId = "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdf9faef815120c"
lessons = getLessons(selectedLessonPlanId)
quizzes = getQuizzes(selectedLessonPlanId)

b) Nested Tabs / Drill-Down

Inside Lesson Plans, allow expanding a course to show subtopics and quizzes inline.

Pros: Less navigation

Cons: Can get cluttered if lesson plans have many subtopics

4️⃣ Optional Enhancements

Breadcrumb navigation: Lesson Plans > Algebra > Subtopic 2 > Quiz

Progress Indicators:

Show % completed per lesson plan

Show mastery level per subtopic/quiz

Quick Actions:

Start Lesson / Take Quiz / Review Weak Concepts

Collapsible Views: Sections inside lessons can expand for reading or collapse for overview.

5️⃣ Example Layout
[Lesson Plans Tab]                       [Lessons Tab]                  [Quizzes Tab]
-------------------------------------------------------------
Course: Math - Algebra                   Subtopic: Expanding ...       Quiz: Expanding Single Brackets
Status: Approved                          Duration: 45 min             Attempts: 1
Progress: 0%                              Status: In Progress          Score: 31%
Start Lesson | Review                     Start Lesson                 Retake Quiz | Review Answers

1️⃣ Data Structure & Caching Strategy

Think about your UI hierarchy:

Lesson Plans (Courses)
 ├─ Lessons (Subtopics)
 │   └─ Quiz


You want to avoid calling the backend for every tab click, so:

Frontload high-level info

On page load, fetch all lesson plans for the user:

GET /api/lesson-plans/:user_id


This gives you lesson plan IDs, subject, topic, status, and subtopic count. Enough to populate the Lesson Plans tab.

Lazy-load subtopic details

When the user clicks a lesson plan, fetch the detailed lesson plan info:

GET /api/lesson-plans/details/:lesson_plan_id?user_id=:user_id


This gives you subtopics, which populate the Lessons tab.

Lazy-load quiz info

When the user clicks a subtopic, start or fetch the quiz:

POST /api/quizzes/start


Save the quiz_id and question_ids in your UI state.

✅ Benefit: Only fetch heavy or detailed data when needed, reducing load time and backend stress.