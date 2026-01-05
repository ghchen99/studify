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
        <h2 className="text-4xl font-bold tracking-tight">Quiz Complete 🎉</h2>

        <div className="flex justify-center">
          <div className="h-32 w-32 rounded-full bg-blue-50 border-4 border-blue-600 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-blue-600">
              {result.score.percentage.toFixed(1)}%
            </span>
            <span className="text-xs text-blue-600 font-medium">Score</span>
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
          <h3 className="text-2xl font-semibold">Question Breakdown</h3>

          {result.responses.map((r, i) => (
            <div
              key={r.questionId}
              className="bg-white rounded-xl border shadow-sm p-6 space-y-5"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="h-8 w-8 rounded-full bg-gray-900 text-white flex items-center justify-center text-sm font-semibold">
                    {i + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    Question {i + 1}
                  </span>
                </div>

                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    r.isCorrect === true
                      ? 'bg-green-100 text-green-700'
                      : r.isCorrect === false
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
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
                <div className="prose prose-sm max-w-none">
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
                <div className="bg-gray-50 border rounded-lg p-4 prose prose-sm max-w-none">
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
                  <div className="prose prose-sm max-w-none">
                    <MarkdownRenderer content={r.feedback} />
                  </div>
                </div>
              )}

              {/* Model Answer */}
              {r.aiGeneratedAnswer && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-xs uppercase tracking-wide text-blue-700 mb-1">
                    Model Answer
                  </p>
                  <div className="prose prose-sm max-w-none">
                    <MarkdownRenderer content={r.aiGeneratedAnswer} />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
