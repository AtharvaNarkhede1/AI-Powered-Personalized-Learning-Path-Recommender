import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertCircle, Award } from 'lucide-react';
import { api } from '../api/client';

export default function QuizModal({ skillId, onClose, onQuizCompleted }) {
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submissionResult, setSubmissionResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadQuiz() {
      try {
        const data = await api.getQuiz(skillId);
        setQuiz(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadQuiz();
  }, [skillId]);

  const handleSelectOption = (questionId, optionIdx) => {
    setAnswers({ ...answers, [questionId]: optionIdx });
  };

  const handleSubmit = async () => {
    try {
      const res = await api.submitQuiz(quiz.id, answers);
      setSubmissionResult(res);
      if (onQuizCompleted) onQuizCompleted(res);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ background: '#FFF', padding: '2rem', borderRadius: '12px' }}>Loading Diagnostic Quiz...</div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(15, 23, 42, 0.6)',
      backdropFilter: 'blur(4px)',
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem'
    }}>
      <div style={{
        background: '#FFFFFF',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '750px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '2rem'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <span className="badge badge-indigo" style={{ marginBottom: '0.25rem' }}>Diagnostic Assessment</span>
            <h3 style={{ fontSize: '1.4rem' }}>{quiz?.title}</h3>
            <p style={{ color: '#64748B', fontSize: '0.85rem' }}>{quiz?.description}</p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={24} color="#64748B" />
          </button>
        </div>

        {/* Submission Result Screen */}
        {submissionResult ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: submissionResult.passed ? '#ECFDF5' : '#FEF2F2',
              color: submissionResult.passed ? '#10B981' : '#EF4444',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem auto'
            }}>
              {submissionResult.passed ? <CheckCircle2 size={36} /> : <AlertCircle size={36} />}
            </div>

            <h3 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>
              Score: {submissionResult.score_percentage}%
            </h3>
            <p style={{ color: '#475569', marginBottom: '1.5rem', lineHeight: 1.6 }}>
              {submissionResult.feedback}
            </p>

            <button className="btn-primary" onClick={onClose}>
              Return to Roadmap
            </button>
          </div>
        ) : (
          /* Question Stream */
          <div>
            <div style={{ display: 'grid', gap: '1.75rem', marginBottom: '2rem' }}>
              {quiz?.questions.map((q, qIdx) => (
                <div key={q.id} style={{ background: '#F8FAFC', padding: '1.25rem', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
                  <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.85rem', color: '#0F172A' }}>
                    {qIdx + 1}. {q.question_text}
                  </div>

                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    {q.options.map((opt, oIdx) => {
                      const isSelected = answers[q.id] === oIdx;
                      return (
                        <button
                          key={oIdx}
                          onClick={() => handleSelectOption(q.id, oIdx)}
                          style={{
                            padding: '0.75rem 1rem',
                            borderRadius: '8px',
                            border: isSelected ? '2px solid #4F46E5' : '1px solid #CBD5E1',
                            background: isSelected ? '#EEF2FF' : '#FFFFFF',
                            color: isSelected ? '#4F46E5' : '#334155',
                            fontWeight: isSelected ? 600 : 400,
                            textAlign: 'left',
                            cursor: 'pointer',
                            fontSize: '0.9rem'
                          }}
                        >
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            <button
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={handleSubmit}
            >
              Submit Quiz Assessment
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
