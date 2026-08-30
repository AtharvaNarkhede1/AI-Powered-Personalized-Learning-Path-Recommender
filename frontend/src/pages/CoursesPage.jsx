import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink, Search, Star, Clock, Plus, Check, Info } from 'lucide-react';
import { api } from '../api/client';
import { useAppData } from '../context/AppDataContext';

const FACTOR_LABEL = {
  goal_fit: 'goal match', skill_gain: 'closes skill gaps', level_fit: 'level fit',
  quality: 'highly rated', prereq_ready: "prereqs ready", effort_fit: 'time fit', format_pref: 'format',
};

export default function CoursesPage() {
  const { careerId, activePath, addCourse, removeCourse } = useAppData();
  const [goal, setGoal] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const [pending, setPending] = useState({});

  const load = useCallback(async (g) => {
    setLoading(true); setErr(null);
    try {
      setData(await api.getCourseRecommendations({ goalText: g || null, careerId, limit: 12 }));
    } catch (e) { setErr(e.message); } finally { setLoading(false); }
  }, [careerId]);

  useEffect(() => { load(''); }, [load]);

  const planIndex = useMemo(() => {
    const map = new Map();
    (activePath?.milestones || []).forEach((m) => {
      (m.resources || []).forEach((r) => map.set(r.course_id || r.id, { milestoneKey: m.id, resourceId: r.id }));
    });
    return map;
  }, [activePath]);

  const toggle = async (course) => {
    const key = course.course_id || course.id;
    setPending((p) => ({ ...p, [key]: true }));
    try {
      const inPlan = planIndex.get(key);
      if (inPlan) await removeCourse(careerId, inPlan.resourceId, inPlan.milestoneKey);
      else await addCourse(careerId, key, null);
    } catch (e) { setErr(e.message); } finally {
      setPending((p) => ({ ...p, [key]: false }));
    }
  };

  const results = data?.results || [];

  return (
    <div className="page">
      <h1 style={{ fontSize: '1.6rem', marginBottom: '0.3rem' }}>Course recommendations</h1>
      <p className="muted" style={{ marginBottom: '1.25rem' }}>
        Ranked from the catalog against your goal{activePath ? <> for <strong>{activePath.career_title}</strong></> : null} and what you already know.
        {careerId && ' Add or remove any course from your roadmap.'}
      </p>

      {!careerId && (
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', marginBottom: '1.5rem' }}>
          <p className="muted" style={{ marginBottom: '0.9rem' }}>Pick a career first so recommendations can be ranked and added to a roadmap.</p>
          <Link className="btn-primary btn-sm" to="/app/discover">Find my career</Link>
        </div>
      )}

      <form onSubmit={(e) => { e.preventDefault(); load(goal); }} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="Optional goal, e.g. 'computer vision for robotics'" style={{ flex: 1, minWidth: 240 }} />
        <button className="btn-primary" type="submit"><Search size={15} /> Search</button>
      </form>

      <div className="card" style={{ padding: '0.7rem 0.9rem', marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', fontSize: '0.8rem' }}>
        <Info size={14} style={{ color: 'var(--accent)', flexShrink: 0, marginTop: 2 }} />
        <span className="muted">Each course shows the ranking drivers (goal fit, gaps closed, level, rating, time) as a share of why it was picked.</span>
      </div>

      {loading && <p className="muted">Ranking courses…</p>}
      {err && <div className="badge badge-bad" style={{ padding: '0.5rem 0.7rem' }}>{err}</div>}

      <div style={{ display: 'grid', gap: '0.75rem' }}>
        {results.map((r, i) => {
          const key = r.course_id || r.id;
          const inPlan = planIndex.has(key);
          const drivers = Object.entries(r.factor_contributions || {}).sort((a, b) => b[1] - a[1]).slice(0, 3).filter(([, v]) => v >= 0.08);
          return (
            <div key={r.id} className="card" style={{ padding: '1.1rem 1.3rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: 240 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem', flexWrap: 'wrap' }}>
                    <span className="mono faint">#{i + 1}</span>
                    <span className="badge badge-neutral">{r.difficulty}</span>
                    <span className="faint" style={{ fontSize: '0.78rem' }}>{r.track} · {r.branch}</span>
                  </div>
                  <a href={r.url} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 600, color: 'var(--text)', fontSize: '1rem', display: 'inline-flex', gap: '0.35rem', alignItems: 'center' }}>
                    {r.title} <ExternalLink size={13} style={{ color: 'var(--accent)' }} />
                  </a>
                  <div className="muted" style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', margin: '0.4rem 0', flexWrap: 'wrap' }}>
                    <span>{r.provider}</span>
                    <span><Clock size={11} style={{ verticalAlign: -1 }} /> {r.duration_hours} hrs</span>
                    <span><Star size={11} style={{ verticalAlign: -1 }} /> {r.rating} ({(r.num_reviews || 0).toLocaleString()})</span>
                    {r.is_free && <span style={{ color: 'var(--good)', fontWeight: 600 }}>Free</span>}
                  </div>
                  {drivers.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.4rem' }}>
                      {drivers.map(([f, v]) => (
                        <span key={f} className="badge badge-accent">{FACTOR_LABEL[f] || f} {Math.round(v * 100)}%</span>
                      ))}
                    </div>
                  )}
                </div>
                {careerId && (
                  <div>
                    <button className={inPlan ? 'btn-secondary btn-sm' : 'btn-primary btn-sm'} disabled={pending[key]} onClick={() => toggle(r)}>
                      {inPlan ? <><Check size={14} /> In roadmap</> : <><Plus size={14} /> Add to roadmap</>}
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {results.length > 0 && careerId && (
        <div style={{ textAlign: 'center', marginTop: '1.75rem' }}>
          <Link className="btn-secondary" to="/app/roadmap">View ordered roadmap →</Link>
        </div>
      )}
    </div>
  );
}
