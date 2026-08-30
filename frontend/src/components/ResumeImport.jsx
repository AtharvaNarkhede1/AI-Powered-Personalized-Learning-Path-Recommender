import React, { useState } from 'react';
import { FileText, Plus, Check, ChevronDown } from 'lucide-react';
import { api } from '../api/client';

/**
 * Paste resume / bio text -> detect skills -> user picks which to add.
 * `existing` = current known_skills (excluded from detection); `onAdd(names[])`.
 */
export default function ResumeImport({ existing = [], onAdd }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [detected, setDetected] = useState(null);
  const [chosen, setChosen] = useState(new Set());
  const [err, setErr] = useState(null);

  const run = async () => {
    setBusy(true); setErr(null); setDetected(null);
    try {
      const res = await api.parseResume(text, existing);
      setDetected(res.detected_skills || []);
      setChosen(new Set((res.detected_skills || []).map((d) => d.name)));
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const toggle = (name) => {
    setChosen((c) => {
      const n = new Set(c);
      n.has(name) ? n.delete(name) : n.add(name);
      return n;
    });
  };

  const add = () => {
    onAdd([...chosen]);
    setDetected(null); setChosen(new Set()); setText(''); setOpen(false);
  };

  return (
    <div style={{ border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-sm)', padding: open ? '1rem' : '0.6rem 0.9rem' }}>
      <button type="button" onClick={() => setOpen((o) => !o)}
        style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent)', fontWeight: 600, fontSize: '0.86rem', padding: 0 }}>
        <FileText size={15} /> Paste resume / bio to auto-detect skills
        <ChevronDown size={14} style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .15s' }} />
      </button>

      {open && (
        <div style={{ marginTop: '0.85rem' }}>
          <textarea rows={5} value={text} onChange={(e) => setText(e.target.value)}
            placeholder="Paste your résumé text, LinkedIn 'About', or a short bio…" style={{ resize: 'vertical' }} />
          <div style={{ marginTop: '0.6rem' }}>
            <button type="button" className="btn-primary btn-sm" onClick={run} disabled={busy || text.trim().length < 20}>
              {busy ? 'Scanning…' : 'Detect skills'}
            </button>
          </div>

          {err && <div className="badge badge-bad" style={{ marginTop: '0.6rem', padding: '0.4rem 0.6rem' }}>{err}</div>}

          {detected && detected.length === 0 && (
            <p className="muted" style={{ fontSize: '0.85rem', marginTop: '0.6rem' }}>No new skills detected — add them manually below.</p>
          )}

          {detected && detected.length > 0 && (
            <div style={{ marginTop: '0.8rem' }}>
              <p className="faint" style={{ fontSize: '0.78rem', marginBottom: '0.5rem' }}>
                Tap to include / exclude, then add. You can still edit the list afterwards.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.8rem' }}>
                {detected.map((d) => {
                  const on = chosen.has(d.name);
                  return (
                    <button key={d.name} type="button" onClick={() => toggle(d.name)}
                      className={`badge ${on ? 'badge-good' : 'badge-neutral'}`}
                      style={{ cursor: 'pointer', border: `1px solid ${on ? 'var(--good)' : 'var(--border-strong)'}`, padding: '0.3rem 0.6rem' }}>
                      {on ? <Check size={12} /> : <Plus size={12} />} {d.name}
                      <span className="mono faint" style={{ fontSize: '0.68rem' }}>{Math.round(d.confidence * 100)}%</span>
                    </button>
                  );
                })}
              </div>
              <button type="button" className="btn-primary btn-sm" onClick={add} disabled={chosen.size === 0}>
                Add {chosen.size} skill{chosen.size === 1 ? '' : 's'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
