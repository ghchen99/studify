'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

const SUBJECTS = ['Math', 'Physics', 'Chemistry', 'Biology', 'Computer Science'];
const LEVELS = ['GCSE', 'A-Level', 'Undergraduate'];

export default function CreateCourseView({
  onCreate
}: {
  onCreate: (data: {
    subject: string;
    topic: string;
    level: string;
  }) => void;
}) {
  const [subject, setSubject] = useState('');
  const [level, setLevel] = useState('GCSE');
  const [topicInput, setTopicInput] = useState('');
  const [topics, setTopics] = useState<string[]>([]);
  const [focus, setFocus] = useState('');

  const addTopic = () => {
    if (topicInput.trim() && !topics.includes(topicInput.trim())) {
      setTopics([...topics, topicInput.trim()]);
      setTopicInput('');
    }
  };

  const buildTopicString = () => {
    return [
      ...topics,
      focus && `Focus on: ${focus}`
    ]
      .filter(Boolean)
      .join('; ');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Create a New Course</h2>

      {/* Subject */}
      <div>
        <label className="block font-medium mb-1">Subject</label>
        <select
          className="w-full border rounded p-2"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        >
          <option value="">Select a subject</option>
          {SUBJECTS.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Level */}
      <div>
        <label className="block font-medium mb-1">Level</label>
        <select
          className="w-full border rounded p-2"
          value={level}
          onChange={(e) => setLevel(e.target.value)}
        >
          {LEVELS.map(l => (
            <option key={l}>{l}</option>
          ))}
        </select>
      </div>

      {/* Topics */}
      <div>
        <label className="block font-medium mb-1">Topics / Subtopics</label>

        <div className="flex gap-2">
          <input
            className="flex-1 border rounded p-2"
            placeholder="e.g. Quadratic equations"
            value={topicInput}
            onChange={(e) => setTopicInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addTopic();
              }
            }}
          />
          <Button type="button" onClick={addTopic}>
            Add
          </Button>
        </div>

        {topics.length > 0 && (
          <ul className="mt-2 text-sm text-gray-600 list-disc list-inside">
            {topics.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Focus / Intent */}
      <div>
        <label className="block font-medium mb-1">
          Learning focus (optional)
        </label>
        <textarea
          className="w-full border rounded p-2"
          placeholder="e.g. exam-style questions, step-by-step explanations"
          value={focus}
          onChange={(e) => setFocus(e.target.value)}
        />
      </div>

      <Button
        size="lg"
        disabled={!subject || topics.length === 0}
        onClick={() =>
          onCreate({
            subject,
            level,
            topic: buildTopicString()
          })
        }
      >
        Generate Course
      </Button>
    </div>
  );
}
