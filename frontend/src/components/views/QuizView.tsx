'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { QuizQuestion } from '@/types/api';
import { LoadingButtonContent } from '@/components/ui/LoadingButtonContent';

interface QuizViewProps {
  quizId: string;
  questions: QuizQuestion[];
  onSubmit: (quizId: string, responses: any[]) => void;
}

export default function QuizView({ quizId, questions, onSubmit }: QuizViewProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const handleInputChange = (qId: string, val: string) => {
    setAnswers(prev => ({ ...prev, [qId]: val }));
  };

  const handleSubmit = async () => {
    const formattedResponses = questions.map(q => ({
      questionId: q.questionId,
      userAnswer: answers[q.questionId] || '',
    }));

    await onSubmit(quizId, formattedResponses);
  };

  const answeredCount = Object.keys(answers).length;

  return (
    <div className="max-w-3xl mx-auto px-4 pb-24 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Concept Check</h2>
        <p className="text-gray-500 text-sm">
          Answer all questions before submitting
        </p>

        {/* Progress */}
        <div className="mt-4">
          <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all"
              style={{ width: `${(answeredCount / questions.length) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {answeredCount} / {questions.length} answered
          </p>
        </div>
      </div>

      {/* Questions */}
      {questions.map((q, index) => (
        <div
          key={q.questionId}
          className="bg-white rounded-xl border shadow-sm p-6 space-y-5"
        >
          {/* Meta */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="h-8 w-8 flex items-center justify-center rounded-full bg-blue-600 text-white text-sm font-semibold">
                {index + 1}
              </span>

              <span className="text-xs uppercase tracking-wide px-2 py-1 rounded bg-gray-100 text-gray-600">
                {q.type.replace('_', ' ')}
              </span>
            </div>

            <div className="flex items-center gap-3 text-xs text-gray-500">
              {q.difficulty && (
                <span className="capitalize px-2 py-1 rounded bg-gray-100">
                  {q.difficulty}
                </span>
              )}
              {q.maxMarks && (
                <span>{q.maxMarks} mark{q.maxMarks > 1 ? 's' : ''}</span>
              )}
            </div>
          </div>

          {/* Question */}
          <p className="text-lg font-medium leading-relaxed">
            {q.question}
          </p>

          {/* Multiple Choice */}
          {q.type === 'multiple_choice' && q.options && (
            <div className="space-y-3">
              {q.options.map((opt) => {
                const selected = answers[q.questionId] === opt;
                return (
                  <label
                    key={opt}
                    className={`flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition
                      ${selected
                        ? 'border-blue-600 bg-blue-50'
                        : 'hover:bg-gray-50'
                      }`}
                  >
                    <input
                      type="radio"
                      name={q.questionId}
                      value={opt}
                      checked={selected}
                      onChange={(e) =>
                        handleInputChange(q.questionId, e.target.value)
                      }
                      className="h-4 w-4 text-blue-600"
                    />
                    <span className="text-sm">{opt}</span>
                  </label>
                );
              })}
            </div>
          )}

          {/* Short Answer */}
          {q.type === 'short_answer' && (
            <input
              type="text"
              className="w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Type your answer..."
              onChange={(e) =>
                handleInputChange(q.questionId, e.target.value)
              }
            />
          )}

          {/* Long Answer */}
          {q.type === 'long_answer' && (
            <textarea
              className="w-full rounded-lg border px-4 py-3 h-36 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Explain your reasoning clearly..."
              onChange={(e) =>
                handleInputChange(q.questionId, e.target.value)
              }
            />
          )}
        </div>
      ))}

      {/* Sticky Submit */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg">
        <div className="max-w-3xl mx-auto p-4">
          <Button
            onClick={async () => {
              setSubmitting(true);
              await handleSubmit();
              setSubmitting(false);
            }}
            className="w-full h-12 text-base"
            disabled={submitting}
          >
            <LoadingButtonContent
              loading={submitting}
              loadingText="Submitting answers..."
              idleIcon=""
              idleText="Submit Quiz"
            />
          </Button>
        </div>
      </div>
    </div>
  );
}
