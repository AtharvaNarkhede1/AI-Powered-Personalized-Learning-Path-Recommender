import React, { useEffect, useRef, useState } from 'react';
import { Sparkles, X, Send } from 'lucide-react';
import { api } from '../api/client';
import { useAppData } from '../context/AppDataContext';
import Markdown from '../lib/Markdown';

const QUICK = [
  'Why is my path ordered this way?',
  'What should I start with today?',
  'What are my weak areas?',
  'How long until I am job ready?',
];

export default function AssistantWidget() {
  const { careerId } = useAppData();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'assistant', content: "Hi — I'm your learning assistant. Ask about your roadmap, skill gaps, or what to do next." },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const streamRef = useRef(null);

  useEffect(() => {
    streamRef.current?.scrollTo({ top: streamRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading, open]);

  const send = async (text) => {
    const q = (text ?? input).trim();
    if (!q || loading) return;
    setMessages((m) => [...m, { sender: 'user', content: q }]);
    setInput('');
    setLoading(true);
    try {
      const res = await api.sendChatMessage(q, careerId);
      setMessages((m) => [...m, { sender: 'assistant', content: res.reply, followups: res.suggested_followups || [] }]);
    } catch {
      setMessages((m) => [...m, { sender: 'assistant', content: 'Sorry — something went wrong answering that.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Open assistant"
        style={{
          position: 'fixed', top: 18, right: 18, zIndex: 60,
          width: 46, height: 46, borderRadius: 14,
          border: '1px solid var(--border-strong)', background: 'var(--surface)',
          color: 'var(--accent)', cursor: 'pointer', boxShadow: 'var(--shadow-md)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        {open ? <X size={20} /> : <Sparkles size={20} />}
      </button>

      <div style={{
        position: 'fixed', top: 0, right: 0, height: '100vh', width: 400, maxWidth: '92vw',
        background: 'var(--surface)', borderLeft: '1px solid var(--border)',
        boxShadow: open ? '-12px 0 40px rgba(16,24,40,0.12)' : 'none',
        transform: open ? 'translateX(0)' : 'translateX(102%)',
        transition: 'transform 0.24s ease', zIndex: 55,
        display: 'flex', flexDirection: 'column',
      }}>
        <div style={{ padding: '1rem 1.1rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--accent-weak)', color: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Sparkles size={16} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, fontSize: '0.92rem', fontFamily: 'var(--font-heading)' }}>Learning Assistant</div>
            <div className="faint" style={{ fontSize: '0.74rem' }}>Grounded in your real profile & path</div>
          </div>
          <button className="btn-ghost btn-sm" onClick={() => setOpen(false)}><X size={16} /></button>
        </div>

        <div ref={streamRef} style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
          {messages.map((m, i) => (
            <div key={i} style={{ alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start', maxWidth: '92%' }}>
              <div style={{
                padding: '0.7rem 0.9rem', borderRadius: 12, fontSize: '0.9rem',
                background: m.sender === 'user' ? 'var(--accent)' : 'var(--surface-2)',
                color: m.sender === 'user' ? '#fff' : 'var(--text)',
                border: m.sender === 'user' ? 'none' : '1px solid var(--border)',
              }}>
                {m.sender === 'user' ? m.content : <Markdown text={m.content} />}
              </div>
              {m.followups?.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.5rem' }}>
                  {m.followups.map((f) => (
                    <button key={f} onClick={() => send(f)} className="badge badge-neutral"
                      style={{ cursor: 'pointer', border: '1px solid var(--border-strong)' }}>
                      {f}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="faint" style={{ fontSize: '0.82rem', fontStyle: 'italic' }}>Thinking…</div>}
        </div>

        {messages.length <= 1 && (
          <div style={{ padding: '0 1rem 0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
            {QUICK.map((q) => (
              <button key={q} onClick={() => send(q)} className="badge badge-neutral"
                style={{ cursor: 'pointer', border: '1px solid var(--border)' }}>
                {q}
              </button>
            ))}
          </div>
        )}

        <div style={{ padding: '0.8rem 1rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.5rem' }}>
          <input value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask about your roadmap…" />
          <button className="btn-primary btn-sm" onClick={() => send()} disabled={loading}><Send size={15} /></button>
        </div>
      </div>
    </>
  );
}
