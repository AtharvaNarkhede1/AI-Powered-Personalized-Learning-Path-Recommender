import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ListOrdered, GitBranch, Target, Bot, PencilLine, Compass, Route as RouteIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const STEPS = [
  {
    icon: PencilLine,
    title: 'Describe yourself once',
    body: 'Write a sentence or two — your background, weekly hours and what you want to learn. We pull out the keywords and build your profile automatically.',
  },
  {
    icon: Compass,
    title: 'Get matched to a career',
    body: 'Your interests, skills and branch are scored against real engineering roles. You see the top matches with the gaps you would need to close.',
  },
  {
    icon: RouteIcon,
    title: 'Follow an ordered roadmap',
    body: 'Pick a career and get a prerequisite-ordered path of ranked courses, split into phases you can track course by course.',
  },
];

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

      <section className="landing-hero" style={{ maxWidth: 820, margin: '0 auto', padding: '4.5rem 1.5rem 3rem', textAlign: 'center' }}>
        <span className="badge badge-accent" style={{ marginBottom: '1.1rem' }}>For engineering students & early-career engineers</span>
        <h1 style={{ fontSize: '2.7rem', lineHeight: 1.14, marginBottom: '1.1rem' }}>
          From “I want to learn X” to a roadmap you can actually follow.
        </h1>
        <p className="muted" style={{ fontSize: '1.08rem', marginBottom: '2rem', maxWidth: 640, marginLeft: 'auto', marginRight: 'auto' }}>
          CareerPath reads a short description of your goals, matches you to a real engineering
          career, ranks courses from a large public catalog for it, and orders them into a
          prerequisite-aware learning path you track course by course.
        </p>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link className="btn-primary" to={primaryTo} style={{ padding: '0.75rem 1.5rem' }}>
            {isAuthed ? 'Go to Find My Career' : 'Get started free'} <ArrowRight size={16} />
          </Link>
          {!isAuthed && <Link className="btn-secondary" to="/login" style={{ padding: '0.75rem 1.5rem' }}>Sign in</Link>}
        </div>
      </section>

      <section style={{ maxWidth: 1080, margin: '0 auto', padding: '0 1.5rem 4rem' }}>
        <h2 style={{ fontSize: '1.3rem', textAlign: 'center', marginBottom: '0.4rem' }}>How it works</h2>
        <p className="muted" style={{ textAlign: 'center', fontSize: '0.92rem', marginBottom: '2rem' }}>
          Three steps. The only thing you write is the first one.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
          {STEPS.map(({ icon: Icon, title, body }, i) => (
            <div key={title} className="card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.8rem' }}>
                <span className="step-num">{i + 1}</span>
                <Icon size={18} style={{ color: 'var(--accent)' }} />
              </div>
              <h3 style={{ fontSize: '1.02rem', marginBottom: '0.4rem' }}>{title}</h3>
              <p className="muted" style={{ fontSize: '0.88rem' }}>{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section style={{ background: 'var(--surface)', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', padding: '3.5rem 1.5rem' }}>
          <h2 style={{ fontSize: '1.3rem', textAlign: 'center', marginBottom: '2rem' }}>What you get</h2>
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
        </div>
      </section>

      <section style={{ maxWidth: 640, margin: '0 auto', padding: '3.5rem 1.5rem 4rem', textAlign: 'center' }}>
        <h2 style={{ fontSize: '1.35rem', marginBottom: '0.7rem' }}>Ready to see your roadmap?</h2>
        <p className="muted" style={{ fontSize: '0.95rem', marginBottom: '1.5rem' }}>
          Create an account, describe your goal, and get your first ranked path in a couple of minutes.
        </p>
        <Link className="btn-primary" to={primaryTo} style={{ padding: '0.75rem 1.5rem' }}>
          {isAuthed ? 'Open the app' : 'Create your free account'} <ArrowRight size={16} />
        </Link>
        <p className="faint" style={{ fontSize: '0.82rem', marginTop: '2.5rem' }}>Created by Team TopG</p>
      </section>
    </div>
  );
}
