"""
Learning Platform Usage Example
Demonstrates the complete student workflow
"""
try:
    from .platform import LearningPlatform
except Exception:
    # Allow running this file directly (python learning_platform_api/main.py)
    # by adding the project root to sys.path and importing the package module.
    import sys
    import os

    # If running the script directly from inside the package folder,
    # ensure the project root is used as the main entry on sys.path so
    # top-level stdlib modules (e.g., `platform`) don't get shadowed.
    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(script_dir)
    if sys.path and sys.path[0] == script_dir:
        sys.path[0] = project_root
    else:
        sys.path.insert(0, project_root)

    from learning_platform_api.platform import LearningPlatform
from pprint import pprint
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the platform
platform = LearningPlatform()

# User ID (would come from authentication in real app)
USER_ID = "alice123"

def print_section(title: str):
    """Helper to print section headers"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_complete_workflow():
    """Demonstrate a complete learning workflow"""
    
    # ========================================
    # STEP 1: Create Lesson Plan
    # ========================================
    print_section("STEP 1: Create Lesson Plan")
    
    print("Student says: 'I want to learn Math - Algebra'")
    
    result = platform.create_lesson_plan(
        user_id=USER_ID,
        subject="Math",
        topic="Algebra",
        level="GCSE",
        auto_approve=True  # Automatically approve for demo
    )
    
    lesson_plan = result["lessonPlan"]
    print(f"\n✓ Generated lesson plan: {lesson_plan.subject} - {lesson_plan.topic}")
    print(f"  Status: {result['status']}")
    print(f"  Subtopics: {len(result['subtopics'])}")
    print("\nSubtopics:")
    for st in result["subtopics"][:3]:  # Show first 3
        print(f"  {st['order']}. {st['title']} ({st['duration']} min)")
        print(f"     Concepts: {', '.join(st['concepts'][:3])}")
    
    # ========================================
    # STEP 2: Start First Lesson
    # ========================================
    print_section("STEP 2: Start First Lesson")
    
    first_subtopic = result["subtopics"][0]
    print(f"Student starts: '{first_subtopic['title']}'")
    
    lesson_result = platform.start_lesson(
        user_id=USER_ID,
        lesson_plan_id=lesson_plan.id,
        subtopic_id=first_subtopic['id']
    )
    
    lesson_id = lesson_result["lessonId"]
    print(f"\n✓ Lesson generated")
    print(f"\nIntroduction:")
    print(f"  {lesson_result['introduction'][:200]}...")
    print(f"\nSections: {len(lesson_result['sections'])}")
    for i, section in enumerate(lesson_result['sections'][:2], 1):
        print(f"  {i}. {section['title']}")
    print(f"\nKey Terms: {', '.join(lesson_result['keyTerms'][:5])}")
    
    # ========================================
    # STEP 3: Expand a Section
    # ========================================
    print_section("STEP 3: Expand Section for More Detail")
    
    first_section = lesson_result['sections'][0]
    print(f"Student clicks 'More Detail' on: '{first_section['title']}'")
    
    expanded = platform.expand_lesson_section(
        user_id=USER_ID,
        lesson_id=lesson_id,
        section_id=first_section['sectionId']
    )
    
    print(f"\n✓ Section expanded")
    print(f"\nExpanded Content:")
    print(f"  {expanded['expandedContent'][:300]}...")
    
    # ========================================
    # STEP 4: Complete Lesson
    # ========================================
    print_section("STEP 4: Complete Lesson")
    
    print("Student finishes reading and clicks 'Complete'")
    
    completion = platform.complete_lesson(
        user_id=USER_ID,
        lesson_id=lesson_id,
        study_time=25  # 25 minutes
    )
    
    print(f"\n✓ Lesson completed")
    print(f"  Progress: {completion['progress']['percentComplete']:.1f}%")
    print(f"  Total Study Time: {completion['progress']['totalStudyTime']} minutes")
    print(f"  Next Action: {completion['nextAction']}")
    
    # ========================================
    # STEP 5: Take Quiz
    # ========================================
    print_section("STEP 5: Take Quiz")
    
    print("Student starts the quiz")
    
    quiz_result = platform.start_quiz(
        user_id=USER_ID,
        lesson_id=lesson_id,
        subtopic_id=first_subtopic['id'],
        difficulty="mixed",
        question_count=5
    )
    
    quiz_id = quiz_result["quizId"]
    print(f"\n✓ Quiz generated with {quiz_result['totalQuestions']} questions")
    print("\nQuestions:")
    for i, q in enumerate(quiz_result['questions'][:2], 1):
        print(f"\n  Q{i}. [{q['type']}] {q['question'][:100]}...")
        if q['options']:
            for opt in q['options']:
                print(f"      - {opt}")
    
    # ========================================
    # STEP 6: Submit Quiz Answers
    # ========================================
    print_section("STEP 6: Submit Quiz Answers")
    
    print("Student submits answers...")
    
    # Simulate answers (in real app, these come from UI)
    responses = [
        {
            "questionId": "q1",
            "userAnswer": "Option A"  # Multiple choice
        },
        {
            "questionId": "q2",
            "userAnswer": "This is a short answer about the concept.",
            "userBulletPoints": None
        },
        {
            "questionId": "q3",
            "userAnswer": None,
            "userBulletPoints": [
                "First key point about the topic",
                "Second important concept",
                "Third aspect to consider"
            ]
        }
    ]
    
    submission_result = platform.submit_quiz(
        user_id=USER_ID,
        quiz_id=quiz_id,
        responses=responses[:3]  # Submit first 3
    )
    
    score = submission_result["score"]
    print(f"\n✓ Quiz graded")
    print(f"\nScore: {score['marksAwarded']}/{score['maxMarks']} ({score['percentage']:.1f}%)")
    print(f"Mastery Level: {submission_result['masteryLevel']}")
    print(f"\nFeedback on answers:")
    for i, resp in enumerate(submission_result['responses'][:2], 1):
        print(f"\n  Q{i}. {resp['feedback'][:100]}...")
        if resp.get('aiGeneratedAnswer'):
            print(f"      AI Generated: {resp['aiGeneratedAnswer'][:100]}...")
    
    # ========================================
    # STEP 7: AI Tutor (if struggling)
    # ========================================
    if submission_result.get('triggerTutor'):
        print_section("STEP 7: AI Tutor Session")
        
        print("Score below 40% - Starting AI tutor session...")
        weak_concepts = submission_result.get('weakConcepts', [])
        
        tutor_result = platform.start_tutor_session(
            user_id=USER_ID,
            trigger="quiz_struggle",
            lesson_id=lesson_id,
            subtopic_id=first_subtopic['id'],
            concept=weak_concepts[0] if weak_concepts else "the topic",
            initial_message="I'm confused about this concept"
        )
        
        session_id = tutor_result["sessionId"]
        print(f"\n✓ Tutor session started")
        print(f"\nTutor: {tutor_result['message']}")
        
        # Student asks follow-up
        print("\n\nStudent: Can you explain with an example?")
        
        tutor_response = platform.send_tutor_message(
            user_id=USER_ID,
            session_id=session_id,
            message="Can you explain with an example?"
        )
        
        print(f"\nTutor: {tutor_response['message'][:200]}...")
        
        # End session
        platform.end_tutor_session(USER_ID, session_id)
        print("\n✓ Session ended")
    else:
        print_section("STEP 7: AI Tutor Session")
        print("Score above 40% - No tutor needed! Moving to next topic...")
    
    # ========================================
    # STEP 8: View Dashboard
    # ========================================
    print_section("STEP 8: View Progress Dashboard")
    
    dashboard = platform.get_dashboard(USER_ID)
    
    user_stats = dashboard["user"]
    print(f"\nOverall Progress:")
    print(f"  Completion: {user_stats['overallProgress']:.1f}%")
    print(f"  Average Score: {user_stats['averageScore']:.1f}%")
    print(f"  Study Time: {user_stats['totalStudyTime']} minutes")
    
    print(f"\nActive Lesson Plans: {len(dashboard['lessonPlans'])}")
    for plan in dashboard['lessonPlans']:
        progress = plan.get('progress', {})
        print(f"\n  • {plan['subject']} - {plan['topic']}")
        print(f"    Status: {plan['status']}")
        print(f"    Progress: {progress.get('percentComplete', 0):.1f}%")
        print(f"    Avg Score: {progress.get('averageScore', 0):.1f}%")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(dashboard['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print_section("Complete Workflow Demo Finished")
    print("✓ Student successfully completed full learning cycle!")
    print("\nSummary:")
    print("  1. Created lesson plan (AI generated)")
    print("  2. Studied lesson content")
    print("  3. Expanded section for detail")
    print("  4. Completed lesson")
    print("  5. Took quiz")
    print("  6. Received AI grading & feedback")
    print("  7. Got tutor help (if needed)")
    print("  8. Tracked progress")


def demo_simple_workflow():
    """Simplified demo showing just the key steps"""
    
    print("\n" + "=" * 60)
    print("  SIMPLE WORKFLOW DEMO")
    print("=" * 60 + "\n")
    
    # 1. Create plan
    print("1. Student: 'I want to learn Biology - Cell Biology'")
    result = platform.create_lesson_plan(
        user_id=USER_ID,
        subject="Biology",
        topic="Cell Biology",
        auto_approve=False
    )
    print(f"   ✓ Created lesson plan with {len(result['subtopics'])} subtopics\n")
    
    # 2. Start lesson
    print("2. Student: Starts first lesson")
    lesson = platform.start_lesson(
        user_id=USER_ID,
        lesson_plan_id=result['lessonPlan'].id,
        subtopic_id=result['subtopics'][0]['id']
    )
    print(f"   ✓ Generated lesson content\n")
    
    # 3. Complete lesson
    print("3. Student: Completes lesson")
    completion = platform.complete_lesson(
        user_id=USER_ID,
        lesson_id=lesson['lessonId'],
        study_time=20
    )
    print(f"   ✓ Lesson complete - Progress: {completion['progress']['percentComplete']:.0f}%\n")
    
    # 4. Take quiz
    print("4. Student: Takes quiz")
    quiz = platform.start_quiz(
        user_id=USER_ID,
        lesson_id=lesson['lessonId'],
        subtopic_id=result['subtopics'][0]['id']
    )
    print(f"   ✓ Generated {quiz['totalQuestions']} questions\n")
    
    # 5. Submit quiz
    print("5. Student: Submits answers")
    submission = platform.submit_quiz(
        user_id=USER_ID,
        quiz_id=quiz['quizId'],
        responses=[
            {"questionId": "q1", "userAnswer": "Answer 1"},
            {"questionId": "q2", "userAnswer": "Answer 2"}
        ]
    )
    print(f"   ✓ Score: {submission['score']['percentage']:.0f}%")
    print(f"   ✓ Mastery: {submission['masteryLevel']}\n")
    
    # 6. View dashboard
    print("6. Student: Views dashboard")
    dashboard = platform.get_dashboard(USER_ID)
    print(f"   ✓ Overall progress: {dashboard['user']['overallProgress']:.0f}%")
    print(f"   ✓ Study time: {dashboard['user']['totalStudyTime']} minutes\n")
    
    print("=" * 60)
    print("  WORKFLOW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        # Run simple demo
        demo_simple_workflow()
    else:
        # Run complete demo
        demo_complete_workflow()