import React, { useState } from 'react';
import { Award, ArrowRight, HelpCircle, Check, X, ShieldAlert, Sparkles, Columns, DollarSign, Activity } from 'lucide-react';
import { api } from '../api/client';

export default function CareerDiscovery({ discoveryData, profile, onSelectCareer }) {
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonDetails, setComparisonDetails] = useState([]);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [clarificationAnswered, setClarificationAnswered] = useState(false);

  if (!discoveryData || !discoveryData.top_matches) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <p>No career matches calculated yet. Complete onboarding first.</p>
      </div>
    );
  }

  const { top_matches, clarification_needed, clarification_question, cross_branch_advice } = discoveryData;

  const handleOpenComparison = async () => {
    setShowComparison(true);
    if (comparisonDetails.length === 0) {
      setLoadingComparison(true);
      try {
        const ids = top_matches.map(m => m.career_id);
        const res = await api.compareCareers(ids);
        setComparisonDetails(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingComparison(false);
      }
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Top 3 Career Recommendations</h2>
          <p style={{ color: '#64748B' }}>Analyzed against your {profile.engineering_branch} background & interests</p>
        </div>
        <button className="btn-secondary" onClick={handleOpenComparison}>
          <Columns size={16} /> 3-Way Career Comparison
        </button>
      </div>

      {clarification_needed && !clarificationAnswered && clarification_question && (
        <div style={{
          background: 'linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%)',
          border: '1px solid #FCD34D',
          borderRadius: '16px',
          padding: '1.5rem',
          marginBottom: '2rem',
          boxShadow: '0 4px 12px rgba(245, 158, 11, 0.15)'
        }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '0.75rem' }}>
            <HelpCircle color="#D97706" size={24} />
            <h4 style={{ color: '#92400E', fontSize: '1.1rem', margin: 0 }}>Targeted Clarification Question</h4>
          </div>
          <p style={{ color: '#78350F', marginBottom: '1.25rem', fontSize: '0.95rem' }}>
            {clarification_question.question_text}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.85rem' }}>
            {clarification_question.options.map((opt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setClarificationAnswered(true);
                  onSelectCareer(opt.impact_career);
                }}
                style={{
                  padding: '0.85rem 1.25rem',
                  borderRadius: '10px',
                  border: '1px solid #F59E0B',
                  background: '#FFFFFF',
                  color: '#92400E',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {cross_branch_advice && (
        <div style={{
          background: '#EEF2FF',
          border: '1px solid #C7D2FE',
          borderRadius: '12px',
          padding: '1rem 1.25rem',
          marginBottom: '2rem',
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'center',
          color: '#3730A3',
          fontSize: '0.9rem'
        }}>
          <Sparkles color="#4F46E5" size={20} style={{ flexShrink: 0 }} />
          <span>{cross_branch_advice}</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.75rem', marginBottom: '3rem' }}>
        {top_matches.map((item, idx) => (
          <div
            key={item.career_id}
            className="glass-card"
            style={{
              padding: '2rem',
              position: 'relative',
              border: item.is_top_match ? '2px solid #4F46E5' : '1px solid #E2E8F0'
            }}
          >
            {item.is_top_match && (
              <div style={{
                position: 'absolute',
                top: '-12px',
                right: '20px',
                background: 'linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%)',
                color: '#FFFFFF',
                padding: '0.25rem 0.85rem',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase'
              }}>
                #1 Best Fit
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <div>
                <h3 style={{ fontSize: '1.3rem', marginBottom: '0.25rem' }}>{item.title}</h3>
                <span className="badge badge-indigo">{item.branch_primary}</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#4F46E5', lineHeight: 1 }}>
                  {item.match_percentage}%
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>Profile Match</div>
              </div>
            </div>

            <p style={{ color: '#475569', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              {item.match_reason}
            </p>

            <div style={{ display: 'grid', gap: '0.6rem', marginBottom: '1.5rem', background: '#F8FAFC', padding: '1rem', borderRadius: '10px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.2rem' }}>
                  <span>Branch Compatibility</span>
                  <span>{item.branch_compatibility_score}%</span>
                </div>
                <div style={{ height: '4px', background: '#E2E8F0', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{ width: `${item.branch_compatibility_score}%`, height: '100%', background: '#4F46E5' }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.2rem' }}>
                  <span>Interest Alignment</span>
                  <span>{item.interest_alignment_score}%</span>
                </div>
                <div style={{ height: '4px', background: '#E2E8F0', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{ width: `${item.interest_alignment_score}%`, height: '100%', background: '#10B981' }} />
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '1.75rem', fontSize: '0.85rem' }}>
              {item.missing_critical_skills.length > 0 && (
                <div style={{ marginBottom: '0.5rem', color: '#B91C1C' }}>
                  <strong>Critical Missing Gaps:</strong> {item.missing_critical_skills.join(', ')}
                </div>
              )}
              {item.transferable_skills.length > 0 && (
                <div style={{ color: '#047857' }}>
                  <strong>Transferable Baseline:</strong> {item.transferable_skills.join(', ')}
                </div>
              )}
            </div>

            <button
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={() => onSelectCareer(item.career_id)}
            >
              Select Career & Build Path <ArrowRight size={16} />
            </button>
          </div>
        ))}
      </div>

      {showComparison && (
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
            maxWidth: '1100px',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '2rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.5rem' }}>Side-by-Side 3-Way Career Comparison</h3>
              <button onClick={() => setShowComparison(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <X size={24} color="#64748B" />
              </button>
            </div>

            {loadingComparison ? (
              <p style={{ textAlign: 'center', padding: '2rem' }}>Loading detailed career metrics...</p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: `repeat(${comparisonDetails.length}, 1fr)`, gap: '1.5rem' }}>
                {comparisonDetails.map(c => (
                  <div key={c.career_id} style={{ background: '#F8FAFC', padding: '1.25rem', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
                    <h4 style={{ fontSize: '1.15rem', color: '#4F46E5', marginBottom: '0.25rem' }}>{c.title}</h4>
                    <div style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '0.75rem' }}>{c.avg_salary_range}</div>

                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ fontSize: '0.85rem' }}>Day in the Life:</strong>
                      <p style={{ fontSize: '0.8rem', color: '#475569', marginTop: '0.2rem' }}>{c.day_in_the_life}</p>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ fontSize: '0.85rem', color: '#B91C1C' }}>Hard Realities:</strong>
                      <ul style={{ paddingLeft: '1.1rem', fontSize: '0.8rem', color: '#475569', marginTop: '0.2rem' }}>
                        {c.hard_realities.map((r, i) => <li key={i}>{r}</li>)}
                      </ul>
                    </div>

                    <button
                      className="btn-primary"
                      style={{ width: '100%', fontSize: '0.85rem', padding: '0.6rem' }}
                      onClick={() => {
                        setShowComparison(false);
                        onSelectCareer(c.career_id);
                      }}
                    >
                      Select This Career
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
