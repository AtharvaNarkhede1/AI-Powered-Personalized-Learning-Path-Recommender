import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Route as RouteIcon, BookOpen, UserRound, ExternalLink, CheckCircle2, Circle } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { useAppData } from '../context/AppDataContext';

function Stat({ label, value, sub, tone = 'accent' }) {
  const color = { accent: 'var(--accent)', good: 'var(--good)', text: 'var(--text)' }[tone];
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div className="faint mono" style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.4rem' }}>{label}</div>
      <div className="mono" style={{ fontSize: '1.8rem', fontWeight: 700, color, lineHeight: 1 }}>{value}</div>
      {sub && <div className="faint" style={{ fontSize: '0.78rem', marginTop: '0.35rem' }}>{sub}</div>}
    </div>
  );
}

export default function DashboardPage() {
  const { dashboard, loadingProfile } = useAppData();

  if (loadingProfile) return <div className="page">Loading your dashboard…</div>;

  if (!dashboard || !dashboard.has_path) {
    return (
      <div className="page">
        <h1 style={{ fontSize: '1.6rem', marginBottom: '0.3rem' }}>Dashboard</h1>
        <div className="card" style={{ padding: '2.5rem', textAlign: 'center', marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>No roadmap yet</h3>
          <p className="muted" style={{ marginBottom: '1.25rem' }}>
            Complete your profile, then run Find My Career to generate a tracked learning roadmap.
          </p>
          <div style={{ display: 'flex', gap: '0.6rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link className="btn-secondary btn-sm" to="/app/profile">Edit profile</Link>
            <Link className="btn-primary btn-sm" to="/app/discover">Find my career</Link>
          </div>
        </div>
      </div>
    );
  }

  const d = dashboard;

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', marginBottom: '0.2rem' }}>{d.user_name}</h1>
          <p className="muted">{d.engineering_branch} → <strong>{d.target_career_title}</strong></p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Link className="btn-secondary btn-sm" to="/app/discover"><Compass size={14} /> Find My Career</Link>
          <Link className="btn-secondary btn-sm" to="/app/courses"><BookOpen size={14} /> Courses</Link>
          <Link className="btn-primary btn-sm" to="/app/roadmap"><RouteIcon size={14} /> Roadmap</Link>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <Stat label="Job readiness" value={`${d.job_readiness_pct}%`} sub="Target: 80%+" tone="good" />
        <Stat label="Study hours" value={d.hours_logged} sub={`of ${d.estimated_total_hours} hrs · ~${d.estimated_months_remaining} mo left`} tone="accent" />
        <Stat label="Phases done" value={`${d.completed_milestones_count}/${d.total_milestones_count}`} sub="Prerequisite-ordered" tone="text" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem' }}>
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Current vs required skill level</h3>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={d.skill_radar_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="skill" stroke="var(--muted)" fontSize={11} interval={0} angle={-15} textAnchor="end" height={60} />
                <YAxis stroke="var(--muted)" fontSize={11} domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="current" name="Current %" fill="var(--accent)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="required" name="Required %" fill="var(--border-strong)" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Recent course progress</h3>
          {d.recent_courses?.length ? (
            <div style={{ display: 'grid', gap: '0.6rem' }}>
              {d.recent_courses.map((r) => (
                <div key={r.id} style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start' }}>
                  <span style={{ color: r.completed ? 'var(--good)' : 'var(--faint)', flexShrink: 0, marginTop: 2 }}>
                    {r.completed ? <CheckCircle2 size={16} /> : <Circle size={16} />}
                  </span>
                  <div style={{ minWidth: 0 }}>
                    <a href={r.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text)', display: 'inline-flex', gap: '0.3rem', alignItems: 'center' }}>
                      {r.title} <ExternalLink size={11} style={{ color: 'var(--accent)' }} />
                    </a>
                    <div className="faint" style={{ fontSize: '0.78rem' }}>
                      {r.provider} · {r.duration_hours} hrs · {r.completed ? 'Completed' : 'Up next'}
                    </div>
                  </div>
                </div>
              ))}
              <Link to="/app/roadmap" className="btn-ghost btn-sm" style={{ marginTop: '0.4rem', alignSelf: 'flex-start' }}>Open roadmap →</Link>
            </div>
          ) : (
            <p className="muted" style={{ fontSize: '0.88rem' }}>Mark courses done in your roadmap to see progress here.</p>
          )}
        </div>
      </div>

      {d.next_action && (
        <div className="card" style={{ padding: '1.25rem 1.5rem', marginTop: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div>
            <div className="mono faint" style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Next step</div>
            <div style={{ fontWeight: 600 }}>{d.next_action.title}</div>
            <div className="muted" style={{ fontSize: '0.87rem' }}>{d.next_action.description}</div>
          </div>
          <Link className="btn-primary btn-sm" to="/app/roadmap">Go to roadmap</Link>
        </div>
      )}

      <div style={{ marginTop: '1.25rem' }}>
        <Link className="btn-ghost btn-sm" to="/app/profile"><UserRound size={14} /> Edit profile</Link>
      </div>
    </div>
  );
}
