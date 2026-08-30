import React, { useEffect, useState } from 'react';
import { X, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';

export default function QuizModal({ skillId, courseId, careerId, onClose }) {
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const p = courseId ? api.getCourseQuiz(courseId) : api.getQuiz(skillId);
    p.then(setQuiz).catch((e) => setErr(e.message)).finally(() => setLoading(false));
  }, [skillId, courseId]);

  const submit = async () => {
    setSubmitting(true);
    try {
      setResult(await api.submitQuiz(quiz.id, answers, careerId, courseId || null));
    } catch (e) {
      setErr(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(16,24,40,0.5)', zIndex: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
      <div className="card" style={{ padding: '1.75rem', width: 680, maxWidth: '100%', maxHeight: '88vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
          <div>
            <span className="badge badge-accent">Diagnostic quiz</span>
            <h3 style={{ fontSize: '1.2rem', marginTop: '0.35rem' }}>{quiz?.title || 'Loading…'}</h3>
            {quiz?.description && <p className="muted" style={{ fontSize: '0.85rem' }}>{quiz.description}</p>}
          </div>
          <button className="btn-ghost btn-sm" onClick={onClose}><X size={16} /></button>
        </div>

        {loading && <p className="muted">Loading quiz…</p>}
        {err && !loading && <div className="badge badge-bad" style={{ padding: '0.5rem 0.7rem' }}>{err}</div>}

        {result ? (
          <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
            <div style={{ width: 56, height: 56, borderRadius: '50%', margin: '0 auto 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', background: result.passed ? 'var(--good-weak)' : 'var(--bad-weak)', color: result.passed ? 'var(--good)' : 'var(--bad)' }}>
              {result.passed ? <CheckCircle2 size={30} /> : <AlertCircle size={30} />}
            </div>
            <h3 className="mono" style={{ fontSize: '1.6rem', marginBottom: '0.4rem' }}>{result.score_percentage}%</h3>
            <p className="muted" style={{ marginBottom: '1.25rem' }}>{result.feedback}</p>
            <button className="btn-primary" onClick={onClose}>Back to roadmap</button>
          </div>
        ) : quiz && (
          <div>
            <div style={{ display: 'grid', gap: '1.25rem', marginBottom: '1.5rem' }}>
              {quiz.questions.map((q, qi) => (
                <div key={q.id} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '0.7rem' }}>{qi + 1}. {q.question_text}</div>
                  <div style={{ display: 'grid', gap: '0.4rem' }}>
                    {q.options.map((opt, oi) => {
                      const sel = answers[q.id] === oi;
                      return (
                        <button key={oi} onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                          style={{
                            textAlign: 'left', padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
                            border: `1px solid ${sel ? 'var(--accent)' : 'var(--border-strong)'}`,
                            background: sel ? 'var(--accent-weak)' : 'var(--surface)',
                            color: sel ? 'var(--accent)' : 'var(--text)', fontWeight: sel ? 600 : 400, fontSize: '0.88rem',
                          }}>
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
            <button className="btn-primary" style={{ width: '100%' }} disabled={submitting} onClick={submit}>
              {submitting ? 'Submitting…' : 'Submit quiz'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
