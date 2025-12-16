import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';

interface Message {
  role: 'user' | 'ai';
  text: string;
}

interface TutorViewProps {
  sessionId: string;
  initialMessage?: string;
  onSendMessage: (sessionId: string, message: string) => Promise<string>;
  onEndSession: (sessionId: string) => void;
}

export default function TutorView({ sessionId, initialMessage, onSendMessage, onEndSession }: TutorViewProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (initialMessage && messages.length === 0) {
      setMessages([{ role: 'user', text: initialMessage }]);
      // Ideally trigger an AI response immediately here if the backend supports it, 
      // otherwise we wait for user input.
    }
  }, [initialMessage]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setSending(true);

    const response = await onSendMessage(sessionId, userMsg);
    setMessages(prev => [...prev, { role: 'ai', text: response }]);
    setSending(false);
  };

  return (
    <div className="flex flex-col h-[600px] bg-white border rounded shadow-lg">
      <div className="p-4 bg-indigo-600 text-white flex justify-between items-center">
        <h3 className="font-bold">AI Tutor</h3>
        <Button size="sm" variant="secondary" onClick={() => onEndSession(sessionId)}>End Session</Button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-gray-800'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t bg-white flex gap-2">
        <input 
          className="flex-1 border rounded px-3 py-2"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <Button onClick={handleSend} disabled={sending}>Send</Button>
      </div>
    </div>
  );
}