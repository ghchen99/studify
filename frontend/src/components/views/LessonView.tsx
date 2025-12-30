'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
  const progress = ((currentIndex + 1) / sections.length) * 100;

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
    <div className="max-w-4xl mx-auto px-4 pb-24 space-y-10">
      {/* Lesson Header */}
      <div className="bg-white rounded-xl border shadow-sm p-8 space-y-4">
        <div className="text-3xl font-bold tracking-tight">
          <MarkdownRenderer content={lesson.subtopic} />
        </div>

        <div className="text-gray-600 leading-relaxed">
          <MarkdownRenderer content={lesson.introduction} />
        </div>

        {/* Progress */}
        <div className="pt-4">
          <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Section {currentIndex + 1} of {sections.length}
          </p>
        </div>
      </div>

      {/* Section Card */}
      <div className="bg-white rounded-xl border shadow-sm p-8 space-y-6">
        {/* Section Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="h-8 w-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-semibold">
              {currentIndex + 1}
            </span>
            <h3 className="text-xl font-semibold">
              {currentSection.title}
            </h3>
          </div>

          <span className="text-sm text-gray-500">
            {currentIndex + 1} / {sections.length}
          </span>
        </div>

        {/* Section Content */}
        <div className="prose max-w-none">
          <MarkdownRenderer content={currentSection.content} />
        </div>

        {/* Key Points */}
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-5">
          <p className="text-sm font-semibold text-blue-800 mb-2">
            Key Takeaways
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm">
            {currentSection.keyPoints.map((kp, i) => (
              <li key={i}>
                <MarkdownRenderer content={kp} />
              </li>
            ))}
          </ul>
        </div>

        {/* AI Deep Dive */}
        <div className="flex">
          {currentSection.expanded ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setExpandedDialogOpen(true)}
              className="gap-2"
            >
              📖 View Detailed Explanation
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
                  Generating…
                </>
              ) : (
                <>
                  ✨ Get AI Deep Dive
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Expanded Content Modal */}
      <Dialog open={expandedDialogOpen} onOpenChange={setExpandedDialogOpen}>
        <DialogContent className="max-w-5xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl">
              Deep Dive: {currentSection.title}
            </DialogTitle>
          </DialogHeader>

          <div className="prose max-w-none mt-6">
            <MarkdownRenderer content={currentSection.expanded || ''} />
          </div>
        </DialogContent>
      </Dialog>

      {/* Navigation */}
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
          size="lg"
          className="w-full h-12"
          disabled={completing}
          onClick={async () => {
            setCompleting(true);
            await onComplete(lesson.lesson_id);
            setCompleting(false);
          }}
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
