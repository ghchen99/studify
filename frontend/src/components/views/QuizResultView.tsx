'use client';

import { Button } from '@/components/ui/button';
import { QuizResult } from '@/types/api';
import MarkdownRenderer from '@/components/MarkdownRenderer';

interface QuizResultViewProps {
  result: QuizResult;
  onReturnDashboard: () => void;
}

export default function QuizResultView({
  result,
  onReturnDashboard,
}: QuizResultViewProps) {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-12">
      {/* Summary */}
      <div className="text-center space-y-4">
        <h2 className="text-4xl font-bold tracking-tight text-gray-900">
          Quiz Complete
        </h2>

        <div className="flex justify-center">
          <div className="h-32 w-32 rounded-full bg-gray-50 border-4 border-gray-300 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-gray-800">
              {result.score.percentage.toFixed(1)}%
            </span>
            <span className="text-xs text-gray-500 font-medium">Score</span>
          </div>
        </div>

        <p className="text-gray-600">
          {result.score.marksAwarded} / {result.score.maxMarks} marks
        </p>

        {result.mastery_level && (
          <p className="text-sm text-gray-500">
            Mastery level:{' '}
            <span className="font-semibold text-gray-700">
              {result.mastery_level}
            </span>
          </p>
        )}
      </div>

      {/* Question Feedback */}
      {result.responses && (
        <div className="space-y-6">
          <h3 className="text-2xl font-semibold text-gray-900">
            Question Breakdown
          </h3>

          {result.responses.map((r, i) => (
            <div
              key={r.questionId}
              className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-5"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="h-8 w-8 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center text-sm font-semibold border border-gray-200">
                    {i + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    Question {i + 1}
                  </span>
                </div>

                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    r.isCorrect === true
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : r.isCorrect === false
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}
                >
                  {r.isCorrect === true
                    ? 'Correct'
                    : r.isCorrect === false
                    ? 'Incorrect'
                    : 'Partially correct'}
                </span>
              </div>

              {/* Question */}
              <div>
                <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">
                  Question
                </p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <MarkdownRenderer
                    content={
                      r.originalQuestion || r.questionText || ''
                    }
                  />
                </div>
              </div>

              {/* Student Answer */}
              <div>
                <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">
                  Your Answer
                </p>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 prose prose-sm max-w-none text-gray-700">
                  <MarkdownRenderer
                    content={r.userAnswer || '_No answer provided_'}
                  />
                </div>
              </div>

              {/* Marks */}
              <div className="text-sm text-gray-600">
                Marks awarded:{' '}
                <span className="font-medium">
                  {r.marksAwarded} / {r.maxMarks}
                </span>
              </div>

              {/* Feedback */}
              {r.feedback && (
                <div>
                  <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">
                    Feedback
                  </p>
                  <div className="prose prose-sm max-w-none text-gray-700">
                    <MarkdownRenderer content={r.feedback} />
                  </div>
                </div>
              )}

              {/* Model Answer */}
              {r.aiGeneratedAnswer && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-xs uppercase tracking-wide text-gray-700 mb-1 font-medium">
                    Model Answer
                  </p>
                  <div className="prose prose-sm max-w-none text-gray-700">
                    <MarkdownRenderer content={r.aiGeneratedAnswer} />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Return */}
      <div className="flex justify-center pt-6">
        <Button onClick={onReturnDashboard}>
          Return to Dashboard
        </Button>
      </div>
    </div>
  );
}
