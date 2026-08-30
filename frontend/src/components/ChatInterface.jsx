import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, MessageSquare } from 'lucide-react';
import { api } from '../api/client';

const QUICK_PROMPTS = [
  "Why was this path recommended?",
  "What NOT to do in this field?",
  "How long will it take to reach job readiness?",
  "Compare Robotics vs AI Engineering"
];

export default function ChatInterface({ activeCareerId, userId }) {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      content: "Hello! I'm your AI Career & Learning Path Assistant. Ask me anything about your recommendations, skill gaps, or career strategy!"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg = { sender: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.sendChatMessage(query, activeCareerId, userId);
      const botMsg = {
        sender: 'assistant',
        content: res.reply,
        followups: res.suggested_followups || []
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'assistant', content: 'Sorry, I encountered an error processing your question.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '2rem auto', padding: '0 1.5rem' }}>
      <div className="glass-card" style={{ padding: '2rem', minHeight: '600px', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', pb: '1rem', borderBottom: '1px solid #E2E8F0' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#EEF2FF', color: '#4F46E5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Bot size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.2rem', margin: 0 }}>AI Conversational Career Assistant</h3>
            <span style={{ fontSize: '0.8rem', color: '#64748B' }}>Grounded in structured taxonomy & learner context</span>
          </div>
        </div>

        {/* Message Stream */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '1.5rem', paddingRight: '0.5rem' }}>
          {messages.map((m, idx) => {
            const isUser = m.sender === 'user';
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  gap: '0.75rem',
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '85%'
                }}
              >
                {!isUser && (
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: '#4F46E5', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Bot size={18} />
                  </div>
                )}
                <div>
                  <div style={{
                    background: isUser ? '#4F46E5' : '#F1F5F9',
                    color: isUser ? '#FFFFFF' : '#0F172A',
                    padding: '1rem 1.25rem',
                    borderRadius: isUser ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                    fontSize: '0.95rem',
                    lineHeight: 1.5,
                    whiteSpace: 'pre-line'
                  }}>
                    {m.content}
                  </div>

                  {/* Followup Prompt Chips */}
                  {m.followups && m.followups.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                      {m.followups.map((chip, cIdx) => (
                        <button
                          key={cIdx}
                          onClick={() => handleSend(chip)}
                          style={{
                            background: '#FFFFFF',
                            border: '1px solid #C7D2FE',
                            color: '#4F46E5',
                            padding: '0.35rem 0.75rem',
                            borderRadius: '999px',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          {chip}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {loading && <div style={{ color: '#64748B', fontStyle: 'italic', fontSize: '0.85rem' }}>AI Assistant is thinking...</div>}
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {QUICK_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                color: '#475569',
                padding: '0.4rem 0.85rem',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 500,
                cursor: 'pointer'
              }}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask AI about recommendations, career realities, or prerequisites..."
            style={{
              flex: 1,
              padding: '0.85rem 1.25rem',
              borderRadius: '10px',
              border: '1px solid #CBD5E1',
              fontSize: '0.95rem'
            }}
          />
          <button className="btn-primary" onClick={() => handleSend()}>
            <Send size={16} /> Send
          </button>
        </div>
      </div>
    </div>
  );
}
