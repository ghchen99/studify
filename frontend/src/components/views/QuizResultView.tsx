'use client';

import { Button } from '@/components/ui/button';
import { QuizResult } from '@/types/api';
import MarkdownRenderer from '@/components/MarkdownRenderer';

interface QuizResultViewProps {
  result: QuizResult;
  onReturnDashboard: () => void;
  onStartTutor: (concept: string) => void;
}

export default function QuizResultView({
  result,
  onReturnDashboard,
  onStartTutor,
}: QuizResultViewProps) {
  return (
    <div className="space-y-8 py-10 max-w-3xl mx-auto">
      {/* Summary */}
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold">Quiz Complete</h2>
        <div className="text-6xl font-bold text-blue-600">
          {result.score.percentage}%
        </div>
        <p className="text-gray-600">
          {result.score.marksAwarded} / {result.score.maxMarks} marks
        </p>

        {result.mastery_level && (
          <p className="text-sm text-gray-500">
            Mastery level: <strong>{result.mastery_level}</strong>
          </p>
        )}
      </div>

      {/* Per-question feedback */}
      {result.responses && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">Question Feedback</h3>

          {result.responses.map((r, i) => (
            <div
              key={r.questionId}
              className="border rounded-lg p-5 bg-white space-y-4"
            >
              {/* Header */}
              <div className="flex justify-between items-center">
                <span className="font-medium">Question {i + 1}</span>

                <span
                  className={`text-sm font-semibold px-2 py-1 rounded ${
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
                    : 'Partially marked'}
                </span>
              </div>

              {/* Question */}
              <div>
                <p className="font-semibold text-sm mb-1">Question</p>
                <MarkdownRenderer content={r.originalQuestion || r.questionText || ''} />
              </div>

              {/* Student Answer */}
              <div>
                <p className="font-semibold text-sm mb-1">Your answer</p>
                <div className="bg-gray-50 border rounded p-3">
                  <MarkdownRenderer
                    content={r.userAnswer || '_No answer provided_'}
                  />
                </div>
              </div>

              {/* Marks */}
              <div className="text-sm text-gray-600">
                Marks: {r.marksAwarded} / {r.maxMarks}
              </div>

              {/* Feedback */}
              {r.feedback && (
                <div>
                  <p className="font-semibold text-sm mb-1">Feedback</p>
                  <MarkdownRenderer content={r.feedback} />
                </div>
              )}

              {/* Model Answer */}
              {r.aiGeneratedAnswer && (
                <div className="bg-gray-50 border rounded p-3 text-sm">
                  <strong>Model answer:</strong>
                  <MarkdownRenderer content={r.aiGeneratedAnswer} />
                </div>
              )}
            </div>

          ))}
        </div>
      )}

      {/* Tutor / Next Action */}
      {result.trigger_tutor ? (
        <div className="bg-orange-50 p-6 rounded border border-orange-200">
          <h3 className="font-bold text-orange-800 mb-2">
            Recommended: AI Tutor
          </h3>

          <ul className="list-disc list-inside mb-4 text-sm">
            {result.weak_concepts.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>

          <Button onClick={() => onStartTutor(result.weak_concepts[0])}>
            Chat with AI Tutor
          </Button>
        </div>
      ) : (
        <Button size="lg" onClick={onReturnDashboard}>
          Return to Dashboard
        </Button>
      )}
    </div>
  );
}
