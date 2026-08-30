import React, { useEffect, useRef, useState } from 'react';
import { Plus, X } from 'lucide-react';
import { api } from '../api/client';

/**
 * Tag input with server-backed autocomplete. `tone` controls the chip colour.
 */
export default function KeywordInput({ label, hint, values = [], onChange, tone = 'accent', placeholder }) {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const boxRef = useRef(null);

  useEffect(() => {
    let alive = true;
    if (!input.trim()) { setSuggestions([]); return; }
    api.searchKeywords(input).then((r) => { if (alive) setSuggestions(r || []); }).catch(() => {});
    return () => { alive = false; };
  }, [input]);

  useEffect(() => {
    const h = (e) => { if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);

  const add = (raw) => {
    const v = (raw || '').trim();
    if (!v || values.includes(v)) return;
    onChange([...values, v]);
    setInput('');
    setSuggestions([]);
  };
  const remove = (v) => onChange(values.filter((x) => x !== v));

  const chip = {
    accent: 'badge-accent',
    good: 'badge-good',
    neutral: 'badge-neutral',
  }[tone] || 'badge-accent';

  return (
    <div ref={boxRef}>
      {label && <label>{label}</label>}
      {hint && <p className="faint" style={{ fontSize: '0.8rem', marginBottom: '0.6rem' }}>{hint}</p>}

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: values.length ? '0.6rem' : 0 }}>
        {values.map((v) => (
          <span key={v} className={`badge ${chip}`} style={{ padding: '0.3rem 0.6rem' }}>
            {v}
            <button type="button" onClick={() => remove(v)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', color: 'inherit', padding: 0 }}>
              <X size={13} />
            </button>
          </span>
        ))}
      </div>

      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <input
            value={input}
            onChange={(e) => { setInput(e.target.value); setOpen(true); }}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add(input); } }}
            onFocus={() => setOpen(true)}
            placeholder={placeholder || 'Type and press Enter…'}
          />
          <button type="button" className="btn-secondary btn-sm" onClick={() => add(input)}>
            <Plus size={14} /> Add
          </button>
        </div>

        {open && input.trim() && suggestions.length > 0 && (
          <div className="card" style={{
            position: 'absolute', top: '100%', left: 0, right: 0, marginTop: 4,
            maxHeight: 200, overflowY: 'auto', zIndex: 30,
          }}>
            {suggestions.filter((s) => !values.includes(s)).map((s) => (
              <div key={s} onClick={() => add(s)}
                style={{ padding: '0.5rem 0.75rem', cursor: 'pointer', fontSize: '0.88rem', borderBottom: '1px solid var(--border)' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--surface-2)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}>
                {s}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
