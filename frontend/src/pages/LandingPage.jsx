import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ListOrdered, GitBranch, Target, Bot } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const FEATURES = [
  {
    icon: ListOrdered,
    title: 'Ranked course recommendations',
    body: 'Every course in an ~18,000-row catalog is scored against your goal, the skill gaps it closes, your level, its rating and your time budget — and shows why it was picked.',
  },
  {
    icon: GitBranch,
    title: 'Prerequisite-ordered path',
    body: 'The recommended courses are sequenced with a prerequisite graph into phases, so you always take the foundation before the thing that needs it.',
  },
  {
    icon: Target,
    title: 'Skill-gap analysis',
    body: 'Your known skills are compared against what the target role actually requires — current vs required level, per skill, with an overall readiness score.',
  },
  {
    icon: Bot,
    title: 'Grounded AI assistant',
    body: 'Ask why your path is ordered the way it is or what to do next. Answers are built from your real path and gaps — not generic advice.',
  },
];

export default function LandingPage() {
  const { isAuthed } = useAuth();
  const primaryTo = isAuthed ? '/app/discover' : '/register';

  return (
    <div>
      <header style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface)' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, letterSpacing: '-0.02em' }}>CareerPath</div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {isAuthed ? (
              <Link className="btn-primary btn-sm" to="/app/dashboard">Open app</Link>
            ) : (
              <>
                <Link className="btn-ghost btn-sm" to="/login">Sign in</Link>
                <Link className="btn-primary btn-sm" to="/register">Create account</Link>
              </>
            )}
          </div>
        </div>
      </header>

      <section style={{ maxWidth: 760, margin: '0 auto', padding: '4.5rem 1.5rem 3rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.6rem', lineHeight: 1.15, marginBottom: '1.1rem' }}>
          A ranked course list, and a path to follow it in.
        </h1>
        <p className="muted" style={{ fontSize: '1.08rem', marginBottom: '2rem' }}>
          Tell us your engineering background and goal. We match you to a career, rank real
          courses for it, and order them into a prerequisite-aware learning path you can
          track course by course.
        </p>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link className="btn-primary" to={primaryTo} style={{ padding: '0.7rem 1.4rem' }}>
            Find my career <ArrowRight size={16} />
          </Link>
          {!isAuthed && <Link className="btn-secondary" to="/login" style={{ padding: '0.7rem 1.4rem' }}>Sign in</Link>}
        </div>
      </section>

      <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.5rem 5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="card" style={{ padding: '1.5rem' }}>
              <div style={{ width: 38, height: 38, borderRadius: 9, background: 'var(--accent-weak)', color: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '0.9rem' }}>
                <Icon size={19} />
              </div>
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.4rem' }}>{title}</h3>
              <p className="muted" style={{ fontSize: '0.9rem' }}>{body}</p>
            </div>
          ))}
        </div>
        <p className="faint" style={{ fontSize: '0.82rem', textAlign: 'center', marginTop: '2rem' }}>
          Course ranking and path planning run locally (TF-IDF + SVD). No data leaves the server except optional AI-assistant queries.
        </p>
      </section>
    </div>
  );
}
