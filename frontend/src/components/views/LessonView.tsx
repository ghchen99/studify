'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ActiveLesson, LessonSection } from '@/types/api';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import { LoadingButtonContent } from '@/components/ui/LoadingButtonContent';

interface LessonViewProps {
  lesson: ActiveLesson;
  userId: string;
  onExpandSection: (sectionId: string) => Promise<string | null>;
  onComplete: (lessonId: string) => void;
}

export default function LessonView({
  lesson,
  userId,
  onExpandSection,
  onComplete,
}: LessonViewProps) {
  const [sections, setSections] = useState<LessonSection[]>(lesson.sections);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [expandedDialogOpen, setExpandedDialogOpen] = useState(false);
  const [completing, setCompleting] = useState(false);

  const currentSection = sections[currentIndex];

  const handleExpand = async (sectionId: string) => {
    setLoadingId(sectionId);
    const expandedContent = await onExpandSection(sectionId);

    if (expandedContent) {
      setSections(prev =>
        prev.map(s =>
          s.sectionId === sectionId ? { ...s, expanded: expandedContent } : s
        )
      );
      setExpandedDialogOpen(true);
    }

    setLoadingId(null);
  };

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      {/* Lesson Header */}
      <div className="bg-white p-6 rounded shadow-sm border space-y-2">
        <div className="text-2xl font-bold text-gray-800">
          <MarkdownRenderer content={lesson.subtopic} />
        </div>

        <div className="text-gray-600">
          <MarkdownRenderer content={lesson.introduction} />
        </div>
      </div>


      {/* Section Card */}
      <div className="bg-gray-50 p-6 rounded border space-y-6">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-xl">
            {currentSection.title}
          </h3>
          <span className="text-sm text-gray-500">
            Section {currentIndex + 1} of {sections.length}
          </span>
        </div>

        {/* Section Content */}
        <MarkdownRenderer content={currentSection.content} />

        {/* Key Points */}
        <ul className="list-disc bg-blue-50 p-4 rounded pl-6 space-y-2">
        {currentSection.keyPoints.map((kp, i) => (
          <li key={i}>
            <MarkdownRenderer content={kp} />
          </li>
        ))}
      </ul>

        {/* Expand Button */}
        <div className="flex gap-2">
          {currentSection.expanded ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setExpandedDialogOpen(true)}
              className="gap-2"
            >
              <span className="text-lg">📖</span>
              View Detailed Explanation
            </Button>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExpand(currentSection.sectionId)}
              disabled={loadingId === currentSection.sectionId}
              className="gap-2"
            >
              {loadingId === currentSection.sectionId ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Generating...
                </>
              ) : (
                <>
                  <span className="text-lg">✨</span>
                  Get AI Deep Dive
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Expanded Content Modal */}
      <Dialog open={expandedDialogOpen} onOpenChange={setExpandedDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">
              Deep Dive: {currentSection.title}
            </DialogTitle>
          </DialogHeader>
          <div className="prose prose-sm max-w-none mt-4">
            <MarkdownRenderer content={currentSection.expanded || ''} />
          </div>
        </DialogContent>
      </Dialog>

      {/* Pagination Controls */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          disabled={currentIndex === 0}
          onClick={() => setCurrentIndex(i => i - 1)}
        >
          ← Previous
        </Button>

        <Button
          disabled={currentIndex === sections.length - 1}
          onClick={() => setCurrentIndex(i => i + 1)}
        >
          Next →
        </Button>
      </div>

      {/* Complete Lesson */}
      {currentIndex === sections.length - 1 && (
        <Button
          onClick={async () => {
            setCompleting(true);
            await onComplete(lesson.lesson_id);
            setCompleting(false);
          }}
          className="w-full gap-2"
          size="lg"
          disabled={completing}
        >
          <LoadingButtonContent
            loading={completing}
            loadingText="Preparing quiz..."
            idleIcon=""
            idleText="Complete Lesson & Start Quiz"
          />
        </Button>
      )}
    </div>
  );
}