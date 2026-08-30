import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckCircle2, Circle, ExternalLink, ChevronRight, ShieldAlert, RefreshCw, Trash2, Sparkles, HelpCircle,
} from 'lucide-react';
import { api } from '../api/client';
import { useAppData } from '../context/AppDataContext';
import QuizModal from '../components/QuizModal';
import Markdown from '../lib/Markdown';

export default function RoadmapPage() {
  const { activePath, careerId, regeneratePath, toggleResource, toggleMilestone, removeCourse, refreshDashboard } = useAppData();
  const [quizCourse, setQuizCourse] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [regening, setRegening] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [explLoading, setExplLoading] = useState(false);
  const firstIncompleteRef = useRef(null);

  const path = activePath;

  useEffect(() => {
    if (!careerId) return;
    setExplLoading(true);
    api.getPathExplanation(careerId)
      .then(setExplanation)
      .catch(() => setExplanation(null))
      .finally(() => setExplLoading(false));
  }, [careerId, path?.milestones?.length]);

  if (!path || !path.milestones) {
    return (
      <div className="page">
        <div className="card" style={{ padding: '2.5rem', textAlign: 'center', maxWidth: 520, margin: '2rem auto' }}>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>No roadmap yet</h3>
          <p className="muted" style={{ marginBottom: '1.25rem' }}>Pick a career and we&apos;ll build a prerequisite-ordered course roadmap.</p>
          <Link className="btn-primary" to="/app/discover">Find my career</Link>
        </div>
      </div>
    );
  }

  const doToggleResource = async (rid) => {
    setBusyId(rid);
    try { await toggleResource(careerId, rid); } finally { setBusyId(null); }
  };
  const doTogglePhase = async (mk) => {
    setBusyId(mk);
    try { await toggleMilestone(careerId, mk); } finally { setBusyId(null); }
  };
  const doRemove = async (mk, rid) => {
    setBusyId(rid);
    try { await removeCourse(careerId, rid, mk); } finally { setBusyId(null); }
  };
  const doRegen = async () => {
    if (!window.confirm('Rebuild the roadmap from scratch? Your course progress for this career will be reset.')) return;
    setRegening(true);
    try { await regeneratePath(careerId); } finally { setRegening(false); }
  };

  const totalCourses = path.milestones.reduce((n, m) => n + m.resources.length, 0);
  const doneCourses = path.milestones.reduce((n, m) => n + m.resources.filter((r) => r.completed).length, 0);
  let seenIncomplete = false;

  return (
    <div className="page">
      {/* header */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>
          <div>
            <span className="badge badge-accent" style={{ marginBottom: '0.5rem' }}>Active roadmap</span>
            <h1 style={{ fontSize: '1.6rem', marginBottom: '0.35rem' }}>{path.career_title}</h1>
            <p className="muted" style={{ fontSize: '0.9rem' }}>
              ~{path.estimated_weeks} weeks at {path.hours_per_week} hrs/week · {path.track_names?.join(' · ')}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="mono" style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--good)', lineHeight: 1 }}>{path.job_readiness_score}%</div>
            <div className="faint" style={{ fontSize: '0.75rem', marginBottom: '0.5rem' }}>job readiness</div>
            <button className="btn-secondary btn-sm" onClick={doRegen} disabled={regening}>
              <RefreshCw size={13} /> {regening ? 'Rebuilding…' : 'Regenerate'}
            </button>
          </div>
        </div>
        <div style={{ marginTop: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--muted)', marginBottom: 4 }}>
            <span>{doneCourses} of {totalCourses} courses done</span>
            <span className="mono">{totalCourses ? Math.round((doneCourses / totalCourses) * 100) : 0}%</span>
          </div>
          <div style={{ height: 6, background: 'var(--surface-2)', borderRadius: 999 }}>
            <div style={{ width: `${totalCourses ? (doneCourses / totalCourses) * 100 : 0}%`, height: '100%', background: 'var(--good)', borderRadius: 999 }} />
          </div>
        </div>
      </div>

      {/* next action */}
      {path.next_action && (
        <div className="card" style={{ padding: '1.1rem 1.4rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', borderColor: 'var(--accent)' }}>
          <div>
            <div className="mono faint" style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Next step</div>
            <div style={{ fontWeight: 600 }}>{path.next_action.title}</div>
            <div className="muted" style={{ fontSize: '0.87rem' }}>{path.next_action.description}</div>
          </div>
          <button className="btn-primary btn-sm" onClick={() => firstIncompleteRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })}>
            Jump to it <ChevronRight size={14} />
          </button>
        </div>
      )}

      {/* warnings */}
      {path.what_not_to_do_warnings?.length > 0 && (
        <div className="card" style={{ padding: '1.2rem', marginBottom: '1.5rem', background: 'var(--bad-weak)', borderColor: 'var(--bad)' }}>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--bad)', fontWeight: 600, marginBottom: '0.5rem' }}>
            <ShieldAlert size={17} /> What not to do
          </div>
          <ul style={{ paddingLeft: '1.2rem', color: 'var(--bad)', fontSize: '0.86rem' }}>
            {path.what_not_to_do_warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {/* phases */}
      <div style={{ display: 'grid', gap: '1.25rem' }}>
        {path.milestones.map((m) => {
          const done = m.status === 'completed';
          const allIds = m.resources.map((r) => r.id);
          return (
            <div key={m.id} className="card" style={{ padding: '1.5rem', borderLeft: `3px solid ${done ? 'var(--good)' : 'var(--accent)'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
                    <span className={`badge ${done ? 'badge-good' : m.status === 'in_progress' ? 'badge-accent' : 'badge-neutral'}`}>
                      {done ? 'Completed' : m.status === 'in_progress' ? 'In progress' : 'Upcoming'}
                    </span>
                    <span className="faint mono" style={{ fontSize: '0.78rem' }}>
                      {m.resources.filter((r) => r.completed).length}/{m.resources.length} · ~{m.estimated_hours}h
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem' }}>{m.title}</h3>
                  <p className="muted" style={{ fontSize: '0.88rem' }}>{m.description}</p>
                </div>
                <button className="btn-secondary btn-sm" disabled={busyId === m.id || !allIds.length} onClick={() => doTogglePhase(m.id)}>
                  {done ? 'Mark phase pending' : 'Mark phase complete'}
                </button>
              </div>

              {m.target_skills?.length > 0 && (
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                  {m.target_skills.map((s) => <span key={s} className="badge badge-neutral">{s}</span>)}
                </div>
              )}

              <div style={{ display: 'grid', gap: '0.6rem' }}>
                {m.resources.map((r) => {
                  const isFirstIncomplete = !r.completed && !seenIncomplete;
                  if (isFirstIncomplete) seenIncomplete = true;
                  return (
                    <div key={r.id} ref={isFirstIncomplete ? firstIncompleteRef : null}
                      style={{
                        border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '0.85rem 1rem',
                        display: 'flex', gap: '0.75rem', alignItems: 'flex-start',
                        background: r.completed ? 'var(--good-weak)' : 'var(--surface)',
                      }}>
                      <button onClick={() => doToggleResource(r.id)} disabled={busyId === r.id} title={r.completed ? 'Mark pending' : 'Mark done'}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: r.completed ? 'var(--good)' : 'var(--faint)', flexShrink: 0, marginTop: 2 }}>
                        {r.completed ? <CheckCircle2 size={20} /> : <Circle size={20} />}
                      </button>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.15rem' }}>
                          <span className="badge badge-neutral">{r.difficulty}</span>
                          <span className="faint" style={{ fontSize: '0.78rem' }}>{r.provider} · {r.duration_hours} hrs{r.rating ? ` · ★ ${r.rating}` : ''}</span>
                        </div>
                        <a href={r.url} target="_blank" rel="noopener noreferrer"
                          style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.94rem', textDecoration: r.completed ? 'line-through' : 'none', display: 'inline-flex', gap: '0.3rem', alignItems: 'center' }}>
                          {r.title} <ExternalLink size={12} style={{ color: 'var(--accent)' }} />
                        </a>
                        {r.why_now && <div className="muted" style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>{r.why_now}</div>}
                        {r.unlocks?.length > 0 && (
                          <div style={{ fontSize: '0.76rem', color: 'var(--good)', marginTop: '0.15rem' }}>→ prepares you for: {r.unlocks.slice(0, 2).join(', ')}</div>
                        )}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', flexShrink: 0 }}>
                        <button className="btn-secondary btn-sm" title="Take a short quiz on this course"
                          onClick={() => setQuizCourse({ id: r.course_id || r.id, title: r.title })} style={{ padding: '0.3rem 0.5rem' }}>
                          <HelpCircle size={13} /> Quiz
                        </button>
                        <button className="btn-ghost btn-sm" title="Remove from roadmap" disabled={busyId === r.id}
                          onClick={() => doRemove(m.id, r.id)} style={{ padding: '0.3rem 0.5rem' }}>
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {m.youtube_extras?.length > 0 && (
                <div style={{ marginTop: '1rem', background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '0.85rem 1rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.4rem' }}>Free YouTube supplements</div>
                  <div style={{ display: 'grid', gap: '0.3rem' }}>
                    {m.youtube_extras.map((yt) => (
                      <a key={yt.id} href={yt.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.85rem', display: 'inline-flex', gap: '0.3rem', alignItems: 'center', color: 'var(--text)' }}>
                        {yt.title} <ExternalLink size={11} style={{ color: 'var(--accent)' }} /> <span className="faint" style={{ fontSize: '0.76rem' }}>· {yt.provider}</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {m.project && (
                <div style={{ marginTop: '1rem', background: 'var(--good-weak)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '0.85rem 1rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', color: 'var(--good)' }}>Project: {m.project.title}</div>
                  <div className="muted" style={{ fontSize: '0.83rem' }}>{m.project.description}</div>
                  <div className="faint" style={{ fontSize: '0.78rem', marginTop: '0.2rem' }}>Deliverable: {m.project.required_deliverable}</div>
                </div>
              )}

              <p className="faint" style={{ fontSize: '0.78rem', marginTop: '0.75rem' }}>
                Tip: take the short <strong>Quiz</strong> on each course to verify you&apos;ve learned it — passing raises your readiness score.
              </p>
            </div>
          );
        })}
      </div>

      {/* AI explanation */}
      <div className="card" style={{ padding: '1.5rem', marginTop: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.9rem' }}>
          <Sparkles size={17} style={{ color: 'var(--accent)' }} />
          <h3 style={{ fontSize: '1.1rem' }}>Why this path works</h3>
        </div>
        {explLoading && <p className="muted">Generating explanation…</p>}
        {explanation && (
          <>
            <Markdown text={explanation.overview} />
            <div style={{ display: 'grid', gap: '0.9rem', marginTop: '1rem' }}>
              {explanation.phases.map((p) => (
                <div key={p.milestone_key} style={{ borderLeft: '2px solid var(--border-strong)', paddingLeft: '0.9rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.2rem' }}>{p.title}</div>
                  <Markdown text={p.explanation} className="muted" />
                </div>
              ))}
            </div>
          </>
        )}
        {!explLoading && !explanation && <p className="muted">Explanation unavailable right now.</p>}
      </div>

      {quizCourse && (
        <QuizModal
          courseId={quizCourse.id}
          careerId={careerId}
          onClose={() => { setQuizCourse(null); refreshDashboard(careerId); }}
        />
      )}
    </div>
  );
}
