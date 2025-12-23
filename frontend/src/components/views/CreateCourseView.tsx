'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { LoadingButtonContent } from '@/components/ui/LoadingButtonContent';

const SUBJECT_SUGGESTIONS = [
  'Math',
  'Physics',
  'Chemistry',
  'Biology',
  'Computer Science'
];

const LEVELS = ['GCSE', 'A-Level', 'Undergraduate'];

type CreateCourseData = {
  subject: string;
  topic: string;
  level: string;
};

export default function CreateCourseView({
  onCreate
}: {
  onCreate: (data: CreateCourseData) => void;
}) {
  const [subject, setSubject] = useState('');
  const [level, setLevel] = useState('GCSE');
  const [topicInput, setTopicInput] = useState('');
  const [topics, setTopics] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);

  const addTopic = () => {
    const trimmed = topicInput.trim();
    if (!trimmed || topics.includes(trimmed)) return;
    setTopics((prev) => [...prev, trimmed]);
    setTopicInput('');
  };

  const removeTopic = (topic: string) => {
    setTopics((prev) => prev.filter((t) => t !== topic));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Create a New Course</h2>

      {/* Subject */}
      <div>
        <label className="block font-medium mb-1">Subject</label>
        <input
          list="subject-suggestions"
          className="w-full border rounded p-2"
          placeholder="e.g. Mathematics, Economics, Data Science"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />
        <datalist id="subject-suggestions">
          {SUBJECT_SUGGESTIONS.map((s) => (
            <option key={s} value={s} />
          ))}
        </datalist>
      </div>

      {/* Topics */}
      <div>
        <label className="block font-medium mb-1">Topics</label>

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
          <div className="mt-3 flex flex-wrap gap-2">
            {topics.map((topic) => (
              <span
                key={topic}
                className="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-sm"
              >
                {topic}
                <button
                  type="button"
                  onClick={() => removeTopic(topic)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Level */}
      <div>
        <label className="block font-medium mb-1">Level</label>
        <select
          className="w-full border rounded p-2"
          value={level}
          onChange={(e) => setLevel(e.target.value)}
        >
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
      </div>

      {/* Create Button */}
      <Button
        size="lg"
        disabled={!subject || topics.length === 0 || creating}
        onClick={async () => {
          setCreating(true);
          await onCreate({
            subject,
            level,
            topic: topics.join('; ')
          });
          setCreating(false);
        }}
        className="gap-2"
      >
        <LoadingButtonContent
          loading={creating}
          loadingText="Generating course..."
          idleIcon=""
          idleText="Generate Course"
        />
      </Button>

    </div>
  );
}
