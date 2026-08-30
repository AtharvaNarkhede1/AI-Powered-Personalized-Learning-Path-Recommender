import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft, Columns, HelpCircle, X, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { useAppData } from '../context/AppDataContext';
import KeywordInput from '../components/KeywordInput';
import ResumeImport from '../components/ResumeImport';

export default function DiscoverPage() {
  const { profile, discovery, setDiscovery, runDiscovery, selectCareer } = useAppData();
  const navigate = useNavigate();

  const [step, setStep] = useState(discovery ? 4 : 1);
  const [interests, setInterests] = useState([]);
  const [skills, setSkills] = useState([]);
  const [experience, setExperience] = useState('Intermediate');
  const [hours, setHours] = useState(10);
  const [format, setFormat] = useState('project-based');
  const [timeline, setTimeline] = useState(6);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);

  // compare modal
  const [showCompare, setShowCompare] = useState(false);
  const [compareData, setCompareData] = useState([]);
  const [selecting, setSelecting] = useState(null);

  useEffect(() => {
    if (!profile) return;
    setInterests(profile.interests || []);
    setSkills(profile.known_skills || []);
    setExperience(profile.experience_level || 'Intermediate');
    setHours(profile.hours_per_week || 10);
    setFormat(profile.preferred_format || 'project-based');
    setTimeline(profile.target_timeline_months || 6);
  }, [profile]);

  const merged = useMemo(() => ({
    ...(profile || {}),
    interests, known_skills: skills, experience_level: experience,
    hours_per_week: hours, preferred_format: format, target_timeline_months: timeline,
  }), [profile, interests, skills, experience, hours, format, timeline]);

  const doDiscover = async () => {
    setBusy(true); setErr(null);
    try {
      await runDiscovery(merged);
      setStep(4);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const openCompare = async () => {
    setShowCompare(true);
    if (compareData.length === 0 && discovery?.top_matches) {
      try {
        setCompareData(await api.compareCareers(discovery.top_matches.map((m) => m.career_id)));
      } catch { /* ignore */ }
    }
  };

  const pick = async (cid) => {
    setSelecting(cid);
    try {
      await selectCareer(cid);
      navigate('/app/roadmap');
    } catch (e) {
      setErr(e.message);
      setSelecting(null);
    }
  };

  if (!profile) return <div className="page">Loading your profile…</div>;

  return (
    <div className="page">
      <h1 style={{ fontSize: '1.6rem', marginBottom: '0.3rem' }}>Find my career</h1>
      <p className="muted" style={{ marginBottom: '1.5rem' }}>
        These are pre-filled from your profile. Adjust anything, then run the match.
      </p>

      {step < 4 && (
        <>
          <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '1.5rem' }}>
            {[1, 2, 3].map((s) => (
              <div key={s} style={{ flex: 1, height: 4, borderRadius: 999, background: s <= step ? 'var(--accent)' : 'var(--border)' }} />
            ))}
          </div>

          <div className="card" style={{ padding: '1.75rem' }}>
            {step === 1 && (
              <>
                <h3 style={{ fontSize: '1.05rem', marginBottom: '1rem' }}>Areas of technical interest</h3>
                <KeywordInput values={interests} onChange={setInterests} tone="accent"
                  placeholder="Add another interest…" />
              </>
            )}
            {step === 2 && (
              <>
                <h3 style={{ fontSize: '1.05rem', marginBottom: '1rem' }}>Skills & experience level</h3>
                <KeywordInput values={skills} onChange={setSkills} tone="good" placeholder="Add another skill…" />
                <div style={{ marginTop: '1rem' }}>
                  <ResumeImport existing={skills} onAdd={(names) => setSkills([...new Set([...skills, ...names])])} />
                </div>
                <div style={{ marginTop: '1.25rem' }}>
                  <label>Experience level</label>
                  <select value={experience} onChange={(e) => setExperience(e.target.value)}>
                    <option>Beginner</option><option>Intermediate</option><option>Advanced</option>
                  </select>
                </div>
              </>
            )}
            {step === 3 && (
              <>
                <h3 style={{ fontSize: '1.05rem', marginBottom: '1rem' }}>Learning preferences & schedule</h3>
                <div style={{ display: 'grid', gap: '1.1rem' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <label>Weekly time</label>
                      <span className="mono" style={{ fontWeight: 600, color: 'var(--accent)' }}>{hours} hrs/week</span>
                    </div>
                    <input type="range" min={3} max={35} value={hours} onChange={(e) => setHours(parseInt(e.target.value))}
                      style={{ accentColor: 'var(--accent)', padding: 0 }} />
                  </div>
                  <div>
                    <label>Preferred format</label>
                    <select value={format} onChange={(e) => setFormat(e.target.value)}>
                      <option value="project-based">Project-based</option>
                      <option value="video">Video courses</option>
                      <option value="text">Reading / docs</option>
                      <option value="mixed">Mixed</option>
                    </select>
                  </div>
                  <div>
                    <label>Target timeline</label>
                    <select value={timeline} onChange={(e) => setTimeline(parseInt(e.target.value))}>
                      {[3, 6, 9, 12, 18, 24].map((m) => <option key={m} value={m}>{m} months</option>)}
                    </select>
                  </div>
                </div>
              </>
            )}

            {err && <div className="badge badge-bad" style={{ marginTop: '1rem', padding: '0.5rem 0.7rem' }}>{err}</div>}

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.75rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border)' }}>
              <button className="btn-secondary" onClick={() => setStep((s) => Math.max(1, s - 1))} disabled={step === 1}>
                <ArrowLeft size={15} /> Back
              </button>
              {step < 3 ? (
                <button className="btn-primary" onClick={() => setStep((s) => s + 1)}>Next <ArrowRight size={15} /></button>
              ) : (
                <button className="btn-primary" onClick={doDiscover} disabled={busy}>
                  {busy ? 'Matching…' : 'Find my career'} <Sparkles size={15} />
                </button>
              )}
            </div>
          </div>
        </>
      )}

      {step === 4 && discovery?.top_matches && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.2rem' }}>Top career matches</h2>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn-ghost btn-sm" onClick={() => { setDiscovery(null); setStep(1); }}>Redo</button>
              <button className="btn-secondary btn-sm" onClick={openCompare}><Columns size={14} /> Compare all 3</button>
            </div>
          </div>

          {discovery.clarification_needed && discovery.clarification_question && (
            <div className="card" style={{ padding: '1.25rem', marginBottom: '1.25rem', borderColor: 'var(--warn)' }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--warn)', fontWeight: 600, marginBottom: '0.5rem' }}>
                <HelpCircle size={17} /> One quick question
              </div>
              <p style={{ fontSize: '0.9rem', marginBottom: '0.9rem' }}>{discovery.clarification_question.question_text}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {discovery.clarification_question.options.map((o) => (
                  <button key={o.label} className="btn-secondary btn-sm" onClick={() => pick(o.impact_career)}>{o.label}</button>
                ))}
              </div>
            </div>
          )}

          {discovery.cross_branch_advice && (
            <div className="card" style={{ padding: '0.9rem 1.1rem', marginBottom: '1.25rem', display: 'flex', gap: '0.6rem', fontSize: '0.88rem' }}>
              <Sparkles size={17} style={{ color: 'var(--accent)', flexShrink: 0 }} />
              <span className="muted">{discovery.cross_branch_advice}</span>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {discovery.top_matches.map((m) => (
              <div key={m.career_id} className="card" style={{ padding: '1.5rem', borderColor: m.is_top_match ? 'var(--accent)' : 'var(--border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '0.3rem' }}>{m.title}</h3>
                    <span className="badge badge-neutral">{m.branch_primary}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent)', lineHeight: 1 }}>{m.match_percentage}%</div>
                    <div className="faint" style={{ fontSize: '0.7rem' }}>match</div>
                  </div>
                </div>
                <p className="muted" style={{ fontSize: '0.87rem', margin: '0.9rem 0' }}>{m.match_reason}</p>

                <div style={{ display: 'grid', gap: '0.5rem', margin: '0 0 1rem' }}>
                  {[['Branch fit', m.branch_compatibility_score], ['Interest fit', m.interest_alignment_score], ['Skill overlap', m.skill_alignment_score]].map(([k, v]) => (
                    <div key={k}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--muted)', marginBottom: 3 }}>
                        <span>{k}</span><span className="mono">{Math.round(v)}%</span>
                      </div>
                      <div style={{ height: 4, background: 'var(--surface-2)', borderRadius: 999 }}>
                        <div style={{ width: `${Math.round(v)}%`, height: '100%', background: 'var(--accent)', borderRadius: 999 }} />
                      </div>
                    </div>
                  ))}
                </div>

                {m.missing_critical_skills?.length > 0 && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--bad)', marginBottom: '0.35rem' }}>
                    <strong>Gaps:</strong> {m.missing_critical_skills.join(', ')}
                  </p>
                )}
                {m.transferable_skills?.length > 0 && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--good)', marginBottom: '1rem' }}>
                    <strong>You already have:</strong> {m.transferable_skills.join(', ')}
                  </p>
                )}

                <button className="btn-primary" style={{ width: '100%' }} disabled={selecting} onClick={() => pick(m.career_id)}>
                  {selecting === m.career_id ? 'Building roadmap…' : <>Select & build roadmap <ArrowRight size={15} /></>}
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {showCompare && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(16,24,40,0.5)', zIndex: 80, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
          <div className="card" style={{ padding: '1.75rem', maxWidth: 1000, width: '100%', maxHeight: '88vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.2rem' }}>Compare careers</h3>
              <button className="btn-ghost btn-sm" onClick={() => setShowCompare(false)}><X size={16} /></button>
            </div>
            {compareData.length === 0 ? <p className="muted">Loading…</p> : (
              <div style={{ display: 'grid', gridTemplateColumns: `repeat(${compareData.length}, 1fr)`, gap: '1rem' }}>
                {compareData.map((c) => (
                  <div key={c.career_id} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                    <h4 style={{ fontSize: '1rem', color: 'var(--accent)' }}>{c.title}</h4>
                    <div className="faint" style={{ fontSize: '0.8rem', marginBottom: '0.6rem' }}>{c.avg_salary_range}</div>
                    <p style={{ fontSize: '0.8rem', marginBottom: '0.6rem' }}><strong>Day in the life:</strong> {c.day_in_the_life}</p>
                    <p style={{ fontSize: '0.8rem', color: 'var(--bad)', marginBottom: '0.6rem' }}><strong>Hard realities:</strong></p>
                    <ul style={{ fontSize: '0.78rem', paddingLeft: '1rem', color: 'var(--muted)', marginBottom: '0.8rem' }}>
                      {c.hard_realities.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                    <button className="btn-primary btn-sm" style={{ width: '100%' }} onClick={() => { setShowCompare(false); pick(c.career_id); }}>Select</button>
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
