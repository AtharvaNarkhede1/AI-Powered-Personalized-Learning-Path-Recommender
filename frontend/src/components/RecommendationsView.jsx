import React, { useState, useEffect, useCallback } from 'react';
import { ExternalLink, ThumbsUp, ThumbsDown, Search, Star, Clock } from 'lucide-react';
import { api } from '../api/client';

const FACTOR_LABEL = {
  goal_fit: 'matches your goal', skill_gain: 'closes skill gaps', level_fit: 'fits your level',
  quality: 'highly rated', prereq_ready: "you're ready", effort_fit: 'fits your time', format_pref: 'preferred format'
};

export default function RecommendationsView({ userId, careerId }) {
  const [goalText, setGoalText] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState({});

  const load = useCallback(async (goal) => {
    setLoading(true); setError(null);
    try {
      const res = await api.getCourseRecommendations({ userId, goalText: goal || null, careerId, limit: 12 });
      setData(res);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }, [userId, careerId]);

  useEffect(() => { load(''); }, [load]);

  const handleFeedback = async (r, type) => {
    setFeedback({ ...feedback, [r.id]: type });
    try { await api.submitFeedback(r.course_id || r.id, type, userId); } catch (e) { console.error(e); }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1.5rem' }}>
      <h2 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Course Recommendations</h2>
      <p style={{ color: '#64748B', marginBottom: '1.5rem' }}>
        Ranked from the course catalog against your goal and what you already know.
        {data?.goal && <> Current goal: <strong>{data.goal}</strong></>}
      </p>

      <form
        onSubmit={(e) => { e.preventDefault(); load(goalText); }}
        style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}
      >
        <input
          value={goalText}
          onChange={(e) => setGoalText(e.target.value)}
          placeholder="Optional: type a goal, e.g. 'learn computer vision for robotics'"
          style={{ flex: 1, padding: '0.75rem 1rem', border: '1px solid #CBD5E1', borderRadius: '10px', fontSize: '0.95rem' }}
        />
        <button className="btn-primary" type="submit"><Search size={16} /> Get courses</button>
      </form>

      {loading && <p>Ranking courses…</p>}
      {error && <p style={{ color: '#EF4444' }}>Error: {error}</p>}

      <div style={{ display: 'grid', gap: '1rem' }}>
        {data?.results?.map((r, idx) => {
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
                  <div style={{ display: 'flex', gap: '1rem', color: '#64748B', fontSize: '0.82rem', margin: '0.4rem 0' }}>
                    <span>{r.provider}</span>
                    <span><Clock size={12} style={{ verticalAlign: -2 }} /> {r.duration_hours} hrs</span>
                    <span><Star size={12} style={{ verticalAlign: -2 }} /> {r.rating} ({r.num_reviews.toLocaleString()})</span>
                  </div>
                  <p style={{ fontSize: '0.88rem', color: '#475569', margin: '0.25rem 0' }}>{r.match_reason}</p>
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
      {data && !loading && data.results.length === 0 && <p>No matching courses found.</p>}
    </div>
  );
}
