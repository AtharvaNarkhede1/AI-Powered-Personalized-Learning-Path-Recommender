import React, { useState } from 'react';
import { Sparkles, Check, Plus, Wand2 } from 'lucide-react';
import { api } from '../api/client';

export default function IntakeBox({ form, onApply }) {
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const [result, setResult] = useState(null);
  const [chosenSkills, setChosenSkills] = useState(new Set());
  const [applied, setApplied] = useState(false);

  const run = async () => {
    setBusy(true);
    setErr(null);
    setApplied(false);
    try {
      const res = await api.parseIntake(text, form.known_skills || [], form.interests || []);
      setResult(res);
      setChosenSkills(new Set((res.detected_skills || []).map((d) => d.name)));
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const toggleSkill = (name) => {
    setChosenSkills((c) => {
      const n = new Set(c);
      if (n.has(name)) n.delete(name);
      else n.add(name);
      return n;
    });
  };

  const apply = () => {
    const patch = {};
    const interests = [...new Set([...(form.interests || []), ...(result.detected_interests || []), ...(result.new_keywords || [])])];
    const skills = [...new Set([...(form.known_skills || []), ...chosenSkills, ...(result.new_keywords || [])])];
    patch.interests = interests;
    patch.known_skills = skills;
    if (result.hours_per_week) patch.hours_per_week = result.hours_per_week;
    if (result.experience_level) patch.experience_level = result.experience_level;
    if (result.user_status) patch.user_status = result.user_status;
    if (result.engineering_branch) patch.engineering_branch = result.engineering_branch;
    if (result.target_timeline_months) patch.target_timeline_months = result.target_timeline_months;
    onApply(patch);
    setApplied(true);
  };

  return (
    <div className="intake-box">
      <div style={{ display: 'flex', gap: '0.55rem', alignItems: 'center', marginBottom: '0.4rem' }}>
        <Wand2 size={18} style={{ color: 'var(--accent)' }} />
        <h3 style={{ fontSize: '1.05rem' }}>Describe yourself in a sentence or two</h3>
      </div>
      <p className="muted" style={{ fontSize: '0.86rem', marginBottom: '0.85rem' }}>
        Tell us who you are, how much time you have and what you want to learn. We read it,
        pull out the keywords and fill in the profile below — you can still change anything afterwards.
      </p>
      <textarea
        rows={4}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="e.g. I'm a 3rd year computer engineering student. I know Python and a bit of SQL, I have about 10 hours a week and I want to learn Java and machine learning over the next 6 months."
        style={{ resize: 'vertical' }}
      />
      <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', marginTop: '0.7rem', flexWrap: 'wrap' }}>
        <button type="button" className="btn-primary btn-sm" onClick={run} disabled={busy || text.trim().length < 15}>
          {busy ? 'Reading…' : <>Build my profile <Sparkles size={14} /></>}
        </button>
        {applied && <span className="badge badge-good"><Check size={12} /> Applied to the form below</span>}
      </div>

      {err && <div className="badge badge-bad" style={{ marginTop: '0.7rem', padding: '0.4rem 0.6rem' }}>{err}</div>}

      {result && (
        <div style={{ marginTop: '1rem', display: 'grid', gap: '0.85rem' }}>
          <ul className="md-ul" style={{ fontSize: '0.85rem', margin: 0 }}>
            {result.summary.map((s, i) => <li key={i}>{s}</li>)}
          </ul>

          {result.detected_skills.length > 0 && (
            <div>
              <p className="faint" style={{ fontSize: '0.78rem', marginBottom: '0.45rem' }}>
                Tap to include the skills we found, then apply:
              </p>
              <div className="chip-row">
                {result.detected_skills.map((d) => {
                  const on = chosenSkills.has(d.name);
                  return (
                    <button
                      key={d.name}
                      type="button"
                      onClick={() => toggleSkill(d.name)}
                      className={`badge ${on ? 'badge-good' : 'badge-neutral'}`}
                      style={{ cursor: 'pointer', border: `1px solid ${on ? 'var(--good)' : 'var(--border-strong)'}`, padding: '0.3rem 0.6rem' }}
                    >
                      {on ? <Check size={12} /> : <Plus size={12} />} {d.name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {(result.detected_interests.length > 0 || result.new_keywords.length > 0) && (
            <div>
              <p className="faint" style={{ fontSize: '0.78rem', marginBottom: '0.45rem' }}>Interests & keywords to add:</p>
              <div className="chip-row">
                {[...result.detected_interests, ...result.new_keywords].map((k) => (
                  <span key={k} className="badge badge-accent" style={{ padding: '0.3rem 0.6rem' }}>{k}</span>
                ))}
              </div>
            </div>
          )}

          <div>
            <button type="button" className="btn-primary btn-sm" onClick={apply}>
              Apply to profile
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
