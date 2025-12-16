import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ActiveLesson, LessonSection } from '@/types/api';

interface LessonViewProps {
  lesson: ActiveLesson;
  userId: string;
  onExpandSection: (sectionId: string) => Promise<string | null>;
  onComplete: (lessonId: string) => void;
}

export default function LessonView({ lesson, userId, onExpandSection, onComplete }: LessonViewProps) {
  const [sections, setSections] = useState<LessonSection[]>(lesson.sections);
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const handleExpand = async (sectionId: string) => {
    setLoadingId(sectionId);
    const expandedContent = await onExpandSection(sectionId);
    if (expandedContent) {
      setSections(prev => prev.map(s => 
        s.sectionId === sectionId ? { ...s, expanded: expandedContent } : s
      ));
    }
    setLoadingId(null);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded shadow-sm border">
        <h2 className="text-2xl font-bold text-gray-800">{lesson.subtopic}</h2>
        <p className="text-gray-600 mt-2">{lesson.introduction}</p>
        
      </div>

      <div className="space-y-4">
        {sections.map((section, idx) => (
          <div key={section.sectionId} className="bg-gray-50 p-4 rounded border">
            <h3 className="font-semibold text-lg">{section.title}</h3>
            
            {/* Standard Content */}
            <div className="mt-2 text-gray-700 whitespace-pre-wrap">{section.content}</div>

            {/* Key Points */}
            <ul className="mt-4 list-disc list-inside bg-blue-50 p-3 rounded">
              {section.keyPoints.map((kp, i) => <li key={i} className="text-sm text-blue-800">{kp}</li>)}
            </ul>

            {/* Expanded Content (AI Generated) */}
            {section.expanded && (
              <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400">
                <h4 className="font-bold text-yellow-800 text-sm mb-2">Detailed Explanation:</h4>
                <div className="text-gray-800 whitespace-pre-wrap">{section.expanded}</div>
              </div>
            )}

            {!section.expanded && (
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-4"
                onClick={() => handleExpand(section.sectionId)}
                disabled={!!loadingId}
              >
                {loadingId === section.sectionId ? 'Expanding...' : 'Explain this more (AI)'}
              </Button>
            )}
          </div>
        ))}
      </div>

      <Button onClick={() => onComplete(lesson.lesson_id)} className="w-full" size="lg">
        Complete Lesson & Start Quiz
      </Button>
    </div>
  );
}