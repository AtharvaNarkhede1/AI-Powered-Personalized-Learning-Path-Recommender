import React, { useState } from 'react';
import { CheckCircle2, Clock, PlayCircle, ExternalLink, ThumbsUp, ThumbsDown, EyeOff, Award, ChevronRight, Zap, ShieldAlert, Sparkles } from 'lucide-react';
import { api } from '../api/client';

export default function LearningPathTimeline({ path, profile, userId, onCompleteMilestone, onOpenQuiz, onNavigate }) {
  const [feedbackState, setFeedbackState] = useState({});

  if (!path || !path.milestones) {
    return (
      <div style={{ maxWidth: '560px', margin: '4rem auto', textAlign: 'center', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '3rem 2rem' }}>
        <h3 style={{ fontSize: '1.3rem', marginBottom: '0.5rem' }}>No learning path yet</h3>
        <p style={{ color: '#64748B', marginBottom: '1.5rem' }}>
          Pick a career in Career Discovery and we'll build a prerequisite-ordered course roadmap for it.
        </p>
        <button className="btn-primary" onClick={() => onNavigate && onNavigate('discovery')}>
          Go to Career Discovery
        </button>
      </div>
    );
  }

  const handleFeedback = async (resourceId, type) => {
    setFeedbackState({ ...feedbackState, [resourceId]: type });
    try {
      await api.submitFeedback(resourceId, type, userId || profile?.user_id);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '2rem auto', padding: '0 1.5rem' }}>
      <div className="glass-card" style={{ padding: '2rem', marginBottom: '2.5rem', background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div className="badge badge-indigo" style={{ marginBottom: '0.5rem' }}>Active Career Path</div>
            <h2 style={{ fontSize: '2.2rem', lineHeight: 1.1, marginBottom: '0.5rem' }}>{path.career_title}</h2>
            <p style={{ color: '#64748B' }}>
              Estimated Duration: <strong>{path.estimated_weeks} Weeks (~{round(path.estimated_weeks/4.2)} Months)</strong> at <strong>{path.hours_per_week} hrs/week</strong>
            </p>
            {path.track_names && path.track_names.length > 0 && (
              <p style={{ color: '#94A3B8', fontSize: '0.85rem', marginTop: '0.35rem' }}>
                Tracks in this path: {path.track_names.join(' · ')}
              </p>
            )}
          </div>

          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            padding: '1.25rem 1.75rem',
            textAlign: 'center',
            border: '1px solid #E2E8F0',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.04)'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10B981', lineHeight: 1 }}>
              {path.job_readiness_score}%
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748B', marginTop: '0.25rem' }}>
              Job Readiness Score
            </div>
          </div>
        </div>
      </div>

      {path.next_action && (
        <div style={{
          background: 'linear-gradient(135deg, #4F46E5 0%, #6366F1 100%)',
          color: '#FFFFFF',
          borderRadius: '16px',
          padding: '1.5rem 2rem',
          marginBottom: '2.5rem',
          boxShadow: '0 8px 20px rgba(79, 70, 229, 0.25)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, opacity: 0.9 }}>
              ⚡ Your Next Best Recommended Step
            </div>
            <h3 style={{ fontSize: '1.4rem', color: '#FFFFFF', margin: '0.25rem 0' }}>
              {path.next_action.title}
            </h3>
            <p style={{ fontSize: '0.95rem', opacity: 0.9 }}>
              {path.next_action.description}
            </p>
          </div>
          <button
            className="btn-secondary"
            style={{ color: '#4F46E5', background: '#FFFFFF', border: 'none' }}
            onClick={() => onOpenQuiz(path.milestones[0]?.target_skills[0] || 'python_core')}
          >
            Execute Action <ChevronRight size={16} />
          </button>
        </div>
      )}

      {path.what_not_to_do_warnings && path.what_not_to_do_warnings.length > 0 && (
        <div style={{
          background: '#FEF2F2',
          border: '1px solid #FCA5A5',
          borderRadius: '16px',
          padding: '1.5rem',
          marginBottom: '2.5rem'
        }}>
          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', color: '#991B1B', fontWeight: 700, marginBottom: '0.75rem' }}>
            <ShieldAlert size={20} />
            <span>Personalized Guidance: "What NOT to Do" in this Path</span>
          </div>
          <ul style={{ paddingLeft: '1.25rem', color: '#7F1D1D', fontSize: '0.9rem', lineHeight: 1.6 }}>
            {path.what_not_to_do_warnings.map((w, idx) => <li key={idx}>{w}</li>)}
          </ul>
        </div>
      )}

      <div style={{ display: 'grid', gap: '2rem' }}>
        {path.milestones.map((m, idx) => {
          const isCompleted = m.status === 'completed';
          const isInProgress = m.status === 'in_progress';

          return (
            <div
              key={m.id}
              className="glass-card"
              style={{
                padding: '2rem',
                borderLeft: isCompleted ? '6px solid #10B981' : (isInProgress ? '6px solid #4F46E5' : '6px solid #CBD5E1')
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span className={`badge ${isCompleted ? 'badge-emerald' : (isInProgress ? 'badge-indigo' : 'badge-amber')}`}>
                      {isCompleted ? 'Completed' : (isInProgress ? 'In Progress' : 'Upcoming')}
                    </span>
                    <span style={{ fontSize: '0.85rem', color: '#64748B', fontWeight: 600 }}>
                      ~{m.estimated_hours} Hours ({m.estimated_weeks} Weeks)
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.35rem' }}>{m.title}</h3>
                  <p style={{ color: '#64748B', fontSize: '0.95rem' }}>{m.description}</p>
                </div>

                {!isCompleted && (
                  <button
                    className="btn-primary"
                    style={{ fontSize: '0.85rem', padding: '0.6rem 1rem' }}
                    onClick={() => onCompleteMilestone(path.career_id, m.id)}
                  >
                    <CheckCircle2 size={16} /> Mark Milestone Complete
                  </button>
                )}
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                {m.target_skills.map((skill, sIdx) => (
                  <span key={sIdx} style={{ background: '#F1F5F9', color: '#334155', padding: '0.25rem 0.65rem', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 600 }}>
                    {skill}
                  </span>
                ))}
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '0.95rem', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.75rem' }}>
                  Courses — do these in order ↓
                </h4>

                <div style={{ display: 'grid', gap: '0.75rem', borderLeft: '2px solid #E2E8F0', paddingLeft: '1rem', marginLeft: '0.25rem' }}>
                  {m.resources.map((res, rIdx) => {
                    const fb = feedbackState[res.id];
                    return (
                      <div
                        key={res.id}
                        style={{
                          background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '10px',
                          padding: '1rem 1.25rem', display: 'flex', justifyContent: 'space-between',
                          alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem'
                        }}
                      >
                        <div style={{ display: 'flex', gap: '0.85rem', flex: 1, minWidth: '260px' }}>
                          <div style={{
                            width: 26, height: 26, flexShrink: 0, borderRadius: '50%', background: '#4F46E5',
                            color: '#FFF', fontSize: '0.8rem', fontWeight: 700, display: 'flex',
                            alignItems: 'center', justifyContent: 'center'
                          }}>{rIdx + 1}</div>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
                              <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>{res.difficulty || res.type}</span>
                              <span style={{ fontSize: '0.8rem', color: '#64748B', fontWeight: 600 }}>{res.provider}</span>
                              <span style={{ fontSize: '0.8rem', color: '#64748B' }}>• {res.duration_hours} hrs</span>
                              {res.rating ? <span style={{ fontSize: '0.8rem', color: '#64748B' }}>• ★ {res.rating}</span> : null}
                            </div>
                            <a href={res.url} target="_blank" rel="noopener noreferrer"
                               style={{ fontWeight: 600, color: '#0F172A', textDecoration: 'none', fontSize: '0.95rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                              {res.title} <ExternalLink size={14} color="#4F46E5" />
                            </a>
                            {res.why_now && (
                              <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '0.3rem' }}>{res.why_now}</div>
                            )}
                            {res.unlocks && res.unlocks.length > 0 && (
                              <div style={{ fontSize: '0.78rem', color: '#059669', marginTop: '0.2rem' }}>
                                → prepares you for: {res.unlocks.slice(0, 2).join(', ')}
                              </div>
                            )}
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <button onClick={() => handleFeedback(res.course_id || res.id, 'upvote')}
                                  style={{ padding: '0.4rem', border: '1px solid #CBD5E1', borderRadius: '6px', background: fb === 'upvote' ? '#ECFDF5' : '#FFFFFF', cursor: 'pointer' }}
                                  title="Helpful recommendation">
                            <ThumbsUp size={14} color={fb === 'upvote' ? '#10B981' : '#64748B'} />
                          </button>
                          <button onClick={() => handleFeedback(res.course_id || res.id, 'downvote')}
                                  style={{ padding: '0.4rem', border: '1px solid #CBD5E1', borderRadius: '6px', background: fb === 'downvote' ? '#FEF2F2' : '#FFFFFF', cursor: 'pointer' }}
                                  title="Not relevant">
                            <ThumbsDown size={14} color={fb === 'downvote' ? '#EF4444' : '#64748B'} />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {m.youtube_extras && m.youtube_extras.length > 0 && (
                <div style={{ marginBottom: '1.5rem', background: '#FEF9F9', border: '1px solid #FECACA', borderRadius: '10px', padding: '1rem 1.25rem' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#B91C1C', marginBottom: '0.5rem' }}>
                    📺 Also recommended on YouTube (free supplements)
                  </div>
                  <div style={{ display: 'grid', gap: '0.4rem' }}>
                    {m.youtube_extras.map((yt) => (
                      <a key={yt.id} href={yt.url} target="_blank" rel="noopener noreferrer"
                         style={{ fontSize: '0.88rem', color: '#0F172A', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                        {yt.title} <ExternalLink size={12} color="#B91C1C" />
                        <span style={{ color: '#94A3B8', fontSize: '0.78rem' }}>· {yt.provider}</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {m.project && (
                <div style={{ marginBottom: '1rem', background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: '10px', padding: '1rem 1.25rem' }}>
                  <div style={{ fontWeight: 700, color: '#15803D', fontSize: '0.9rem' }}>🛠️ {m.project.title}</div>
                  <div style={{ color: '#166534', fontSize: '0.85rem', marginTop: '0.2rem' }}>{m.project.description}</div>
                  <div style={{ color: '#16A34A', fontSize: '0.78rem', marginTop: '0.2rem' }}>Deliverable: {m.project.required_deliverable}</div>
                </div>
              )}

              {m.assessment && (
                <div style={{ background: '#EEF2FF', borderRadius: '10px', padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div>
                    <div style={{ fontWeight: 700, color: '#3730A3', fontSize: '0.9rem' }}>🎯 Milestone Diagnostic Quiz</div>
                    <div style={{ color: '#4338CA', fontSize: '0.85rem' }}>{m.assessment.title}</div>
                  </div>
                  <button
                    className="btn-primary"
                    style={{ fontSize: '0.8rem', padding: '0.5rem 1rem' }}
                    onClick={() => onOpenQuiz(m.assessment.assessment_id)}
                  >
                    Take Quiz <ChevronRight size={14} />
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function round(val) {
  return Math.round(val * 10) / 10;
}
