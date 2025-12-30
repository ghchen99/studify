'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { QuizQuestion, QuizResult } from '@/types/api';
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
    const formattedResponses = questions.map(q => {
      const val = answers[q.questionId] || "";
      // Always submit a single string `userAnswer` for every question type.
      return { questionId: q.questionId, userAnswer: val };
    });

    await onSubmit(quizId, formattedResponses);
  };


  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold">Concept Check</h2>
      
      {questions.map((q, index) => (
        <div key={q.questionId} className="bg-white p-6 rounded shadow-sm border">
          <div className="flex justify-between items-start mb-4">
            <span className="bg-gray-200 text-gray-700 px-2 py-1 text-xs rounded uppercase font-bold">{q.type.replace('_', ' ')}</span>
            <span className="text-xs text-gray-500 capitalize">{q.difficulty}</span>
          </div>
          
          <p className="font-medium text-lg mb-4">{index + 1}. {q.question}</p>

          {q.type === 'multiple_choice' && q.options && (
            <div className="space-y-2">
              {q.options.map((opt) => (
                <label key={opt} className="flex items-center space-x-3 p-3 border rounded cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name={q.questionId}
                    value={opt}
                    onChange={(e) => handleInputChange(q.questionId, e.target.value)}
                    className="h-4 w-4 text-blue-600"
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
          )}

          {q.type === 'short_answer' && (
            <input
              type="text"
              className="w-full p-2 border rounded"
              placeholder="Type your answer..."
              onChange={(e) => handleInputChange(q.questionId, e.target.value)}
            />
          )}

          {q.type === 'long_answer' && (
            <textarea
              className="w-full p-2 border rounded h-32"
              placeholder="Explain your reasoning (each line is a point)..."
              onChange={(e) => handleInputChange(q.questionId, e.target.value)}
            />
          )}
        </div>
      ))}

      
      <Button
        onClick={async () => {
          setSubmitting(true);
          await handleSubmit();
          setSubmitting(false);
        }}
        className="w-full gap-2"
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
  );
}