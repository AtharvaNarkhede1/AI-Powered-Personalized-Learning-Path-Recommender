import React, { useState, useEffect, useCallback } from 'react';
import { ExternalLink, ThumbsUp, ThumbsDown, Search, Star, Clock, Compass, Info } from 'lucide-react';
import { api } from '../api/client';

const FACTOR_LABEL = {
  goal_fit: 'matches your goal', skill_gain: 'closes skill gaps', level_fit: 'fits your level',
  quality: 'highly rated', prereq_ready: "you're ready", effort_fit: 'fits your time', format_pref: 'preferred format'
};

export default function RecommendationsView({ userId, careerId, careerTitle, onNavigate }) {
  const [goalText, setGoalText] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [hasSearched, setHasSearched] = useState(false);

  const load = useCallback(async (goal) => {
    setLoading(true); setError(null); setHasSearched(true);
    try {
      const res = await api.getCourseRecommendations({ userId, goalText: goal || null, careerId, limit: 12 });
      setData(res);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }, [userId, careerId]);

  useEffect(() => {
    if (careerId) load('');
  }, [careerId, load]);

  const handleFeedback = async (r, type) => {
    setFeedback({ ...feedback, [r.id]: type });
    try { await api.submitFeedback(r.course_id || r.id, type, userId); } catch (e) { console.error(e); }
  };

  const results = data?.results || [];

  return (
    <div style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1.5rem' }}>
      <h2 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Course Recommendations</h2>
      <p style={{ color: '#64748B', marginBottom: '1rem' }}>
        Courses ranked from the catalog against your goal
        {careerTitle ? <> for <strong>{careerTitle}</strong></> : null} and what you already know.
      </p>

      <div style={{
        display: 'flex', gap: '0.5rem', alignItems: 'flex-start',
        background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '10px',
        padding: '0.75rem 1rem', marginBottom: '1.5rem', fontSize: '0.82rem', color: '#475569'
      }}>
        <Info size={15} style={{ flexShrink: 0, marginTop: '2px' }} color="#4F46E5" />
        <span>
          Each course shows the ranking <strong>drivers</strong> (goal fit, skill gaps closed, level fit,
          rating, prerequisite readiness, time fit, format) as a % of why it was picked.
          Thumbs&nbsp;up/down tunes future rankings to you.
        </span>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); load(goalText); }}
        style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}
      >
        <input
          value={goalText}
          onChange={(e) => setGoalText(e.target.value)}
          placeholder="Type a goal, e.g. 'learn computer vision for robotics'"
          style={{ flex: 1, minWidth: '260px', padding: '0.75rem 1rem', border: '1px solid #CBD5E1', borderRadius: '10px', fontSize: '0.95rem' }}
        />
        <button className="btn-primary" type="submit"><Search size={16} /> Get courses</button>
      </form>

      {data?.goal && (
        <p style={{ fontSize: '0.82rem', color: '#94A3B8', marginBottom: '1.5rem' }}>
          Ranking against: <em>{data.goal}</em>
        </p>
      )}

      {loading && <p style={{ color: '#64748B' }}>Ranking courses…</p>}
      {error && (
        <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', color: '#991B1B', borderRadius: '10px', padding: '1rem' }}>
          Couldn't load recommendations: {error}
        </div>
      )}

      {!loading && !error && !careerId && !hasSearched && (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '16px' }}>
          <Compass size={30} color="#4F46E5" style={{ marginBottom: '0.75rem' }} />
          <p style={{ color: '#475569', marginBottom: '1rem' }}>
            Pick a career first so we can rank courses for it — or just type a goal above.
          </p>
          <button className="btn-primary" onClick={() => onNavigate && onNavigate('discovery')}>
            Go to Career Discovery
          </button>
        </div>
      )}

      {!loading && !error && hasSearched && results.length === 0 && (
        <p style={{ color: '#64748B' }}>No matching courses found — try a broader goal.</p>
      )}

      <div style={{ display: 'grid', gap: '1rem' }}>
        {results.map((r, idx) => {
          const fb = feedback[r.id];
          const drivers = Object.entries(r.factor_contributions || {})
            .sort((a, b) => b[1] - a[1]).slice(0, 3).filter(([, v]) => v >= 0.08);
          return (
            <div key={r.id} className="glass-card" style={{ padding: '1.25rem 1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: '260px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 800, color: '#4F46E5' }}>#{idx + 1}</span>
                    <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>{r.difficulty}</span>
                    <span style={{ fontSize: '0.8rem', color: '#64748B' }}>{r.track} · {r.branch}</span>
                  </div>
                  <a href={r.url} target="_blank" rel="noopener noreferrer"
                     style={{ fontWeight: 700, color: '#0F172A', textDecoration: 'none', fontSize: '1.05rem', display: 'inline-flex', gap: '0.35rem', alignItems: 'center' }}>
                    {r.title} <ExternalLink size={14} color="#4F46E5" />
                  </a>
                  <div style={{ display: 'flex', gap: '1rem', color: '#64748B', fontSize: '0.82rem', margin: '0.4rem 0', flexWrap: 'wrap' }}>
                    <span>{r.provider}</span>
                    <span><Clock size={12} style={{ verticalAlign: -2 }} /> {r.duration_hours} hrs</span>
                    <span><Star size={12} style={{ verticalAlign: -2 }} /> {r.rating} ({(r.num_reviews || 0).toLocaleString()})</span>
                    {r.is_free ? <span style={{ color: '#059669', fontWeight: 600 }}>Free</span> : null}
                  </div>
                  {r.match_reason && <p style={{ fontSize: '0.88rem', color: '#475569', margin: '0.25rem 0' }}>{r.match_reason}</p>}
                  {drivers.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                      {drivers.map(([f, v]) => (
                        <span key={f} style={{ background: '#EEF2FF', color: '#3730A3', padding: '0.15rem 0.5rem', borderRadius: '6px', fontSize: '0.72rem', fontWeight: 600 }}>
                          {FACTOR_LABEL[f] || f} {Math.round(v * 100)}%
                        </span>
                      ))}
                    </div>
                  )}
                  {r.skills_covered?.length > 0 && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#64748B' }}>
                      Skills: {r.skills_covered.slice(0, 5).join(', ')}
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.35rem' }}>
                  <button onClick={() => handleFeedback(r, 'upvote')} title="Helpful"
                          style={{ padding: '0.4rem', border: '1px solid #CBD5E1', borderRadius: '6px', background: fb === 'upvote' ? '#ECFDF5' : '#FFF', cursor: 'pointer' }}>
                    <ThumbsUp size={14} color={fb === 'upvote' ? '#10B981' : '#64748B'} />
                  </button>
                  <button onClick={() => handleFeedback(r, 'downvote')} title="Not relevant"
                          style={{ padding: '0.4rem', border: '1px solid #CBD5E1', borderRadius: '6px', background: fb === 'downvote' ? '#FEF2F2' : '#FFF', cursor: 'pointer' }}>
                    <ThumbsDown size={14} color={fb === 'downvote' ? '#EF4444' : '#64748B'} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {results.length > 0 && onNavigate && (
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button className="btn-secondary" onClick={() => onNavigate('roadmap')}>
            See these as an ordered learning path →
          </button>
        </div>
      )}
    </div>
  );
}
