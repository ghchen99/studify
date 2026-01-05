'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, MessageCircle, Send, Minimize2, Maximize2, Trash2, Image as ImageIcon } from 'lucide-react';
import MarkdownRenderer from '@/components/MarkdownRenderer';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  image?: string; // base64 image
}

interface AITutorChatProps {
  onStateChange: (state: { isOpen: boolean; isExpanded: boolean }) => void;
}

export default function AITutorChat({ onStateChange }: AITutorChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        "Hi! I'm your AI tutor assistant. Ask me anything about your lessons, concepts, or problems you're working on."
    }
  ]);
  const [input, setInput] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    onStateChange({ isOpen, isExpanded });
  }, [isOpen, isExpanded, onStateChange]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const sendMessage = async () => {
    if ((!input.trim() && !image) || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input || 'Analyze this image',
      ...(image && { image })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setImage(null);
    setLoading(true);

    try {
      const response = await fetch('/api/tutor-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage]
        })
      });

      if (!response.ok) throw new Error('Request failed');

      const data = await response.json();

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.content }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry — something went wrong.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        role: 'assistant',
        content:
          "Hi! I'm your AI tutor assistant. Ask me anything about your lessons, concepts, or problems you're working on."
      }
    ]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 z-50"
        >
          <MessageCircle />
        </button>
      )}

      {isOpen && (
        <div
          className={`fixed top-0 right-0 h-screen bg-white shadow-xl flex flex-col z-40 border-l transition-all ${
            isExpanded ? 'w-full md:w-3/4 lg:w-2/3' : 'w-full md:w-1/2 lg:w-2/5'
          }`}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 flex justify-between">
            <div>
              <h3 className="font-semibold">AI Tutor</h3>
              <p className="text-sm text-blue-100">Always here to help</p>
            </div>
            <div className="flex gap-2">
              <button onClick={clearConversation} title="Clear chat">
                <Trash2 size={18} />
              </button>
              <button onClick={() => setIsExpanded(!isExpanded)}>
                {isExpanded ? <Minimize2 /> : <Maximize2 />}
              </button>
              <button onClick={() => setIsOpen(false)}>
                <X />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50 space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-5 py-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border shadow-sm'
                  }`}
                >
                  {msg.image && (
                    <img
                      src={msg.image}
                      alt="Upload"
                      className="rounded-lg mb-2 max-h-64"
                    />
                  )}
                  {msg.role === 'assistant' ? (
                    <MarkdownRenderer content={msg.content} />
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="text-sm text-gray-400">AI is typing…</div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t bg-white">
            <input
              type="file"
              accept="image/*"
              hidden
              ref={fileInputRef}
              onChange={handleImageUpload}
            />

            {image && (
              <div className="mb-2 relative">
                <img src={image} className="max-h-40 rounded border" />
                <button
                  className="absolute top-1 right-1 bg-black/60 text-white p-1 rounded-full"
                  onClick={() => setImage(null)}
                >
                  <X size={14} />
                </button>
              </div>
            )}

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => fileInputRef.current?.click()}
              >
                <ImageIcon />
              </Button>

              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask something…"
                className="flex-1 border rounded-lg p-3 resize-none"
                rows={2}
              />

              <Button onClick={sendMessage} disabled={loading}>
                <Send />
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
