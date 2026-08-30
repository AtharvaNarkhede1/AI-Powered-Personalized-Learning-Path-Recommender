import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { useAppData } from '../context/AppDataContext';
import KeywordInput from '../components/KeywordInput';
import ResumeImport from '../components/ResumeImport';

const BRANCHES = [
  'Computer Engineering / IT', 'Electronics & Communication Engineering', 'Electrical Engineering',
  'Mechanical Engineering', 'Civil Engineering', 'Chemical Engineering', 'Aerospace Engineering',
  'Biomedical Engineering', 'Instrumentation & Control', 'Industrial / Production Engineering',
  'Automobile Engineering', 'Robotics / Mechatronics', 'Environmental Engineering', 'Materials / Metallurgy',
];

const DEFAULTS = {
  user_status: 'Engineering Student',
  engineering_branch: 'Computer Engineering / IT',
  college_name: '',
  current_year: '3rd Year',
  graduation_year: 2026,
  interests: [],
  career_goal_status: 'I have 2-3 careers in mind',
  known_skills: [],
  experience_level: 'Intermediate',
  hours_per_week: 10,
  preferred_format: 'project-based',
  learning_style: 'practical',
  max_budget: 'free-and-paid',
  target_timeline_months: 6,
};

export default function ProfilePage() {
  const { profile, saveProfile } = useAppData();
  const navigate = useNavigate();
  const [form, setForm] = useState(DEFAULTS);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (profile) setForm({ ...DEFAULTS, ...profile, college_name: profile.college_name || '' });
  }, [profile]);

  const set = (k, v) => { setForm((f) => ({ ...f, [k]: v })); setSaved(false); };

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await saveProfile(form);
      setSaved(true);
      navigate('/app/dashboard');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page page-narrow">
      <h1 style={{ fontSize: '1.6rem', marginBottom: '0.3rem' }}>Your profile</h1>
      <p className="muted" style={{ marginBottom: '1.75rem' }}>
        Keep this current — Find My Career and every recommendation is built from it.
      </p>

      <form onSubmit={submit} style={{ display: 'grid', gap: '1.5rem' }}>
        <div className="card" style={{ padding: '1.5rem', display: 'grid', gap: '1.1rem' }}>
          <h3 style={{ fontSize: '1rem' }}>Background</h3>
          <div>
            <label>Current status</label>
            <select value={form.user_status} onChange={(e) => set('user_status', e.target.value)}>
              {['Engineering Student', 'Recent Graduate', 'Working Professional', 'Career Switcher'].map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label>Engineering branch</label>
            <select value={form.engineering_branch} onChange={(e) => set('engineering_branch', e.target.value)}>
              {BRANCHES.map((b) => <option key={b}>{b}</option>)}
            </select>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label>College (optional)</label>
              <input value={form.college_name} onChange={(e) => set('college_name', e.target.value)} />
            </div>
            <div>
              <label>Graduation year</label>
              <input type="number" value={form.graduation_year} onChange={(e) => set('graduation_year', parseInt(e.target.value) || 2026)} />
            </div>
          </div>
          <div>
            <label>Academic year</label>
            <select value={form.current_year} onChange={(e) => set('current_year', e.target.value)}>
              {['1st Year', '2nd Year', '3rd Year', '4th Year', 'Graduated'].map((y) => <option key={y}>{y}</option>)}
            </select>
          </div>
        </div>

        <div className="card" style={{ padding: '1.5rem', display: 'grid', gap: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem' }}>Interests & skills</h3>
          <KeywordInput
            label="Areas of technical interest"
            hint="Type any interest or pick from suggestions across 14 engineering branches."
            values={form.interests}
            onChange={(v) => set('interests', v)}
            tone="accent"
            placeholder="e.g. Autonomous Drones, Computer Vision"
          />
          <KeywordInput
            label="Skills you already know"
            hint="Languages, tools, hardware — anything. Off-list skills still count via semantic matching."
            values={form.known_skills}
            onChange={(v) => set('known_skills', v)}
            tone="good"
            placeholder="e.g. Python, SolidWorks, ROS 2"
          />
          <ResumeImport
            existing={form.known_skills}
            onAdd={(names) => set('known_skills', [...new Set([...form.known_skills, ...names])])}
          />
          <div>
            <label>Overall experience level</label>
            <select value={form.experience_level} onChange={(e) => set('experience_level', e.target.value)}>
              <option value="Beginner">Beginner — starting with fundamentals</option>
              <option value="Intermediate">Intermediate — comfortable with programming & basic math</option>
              <option value="Advanced">Advanced — built projects, familiar with systems</option>
            </select>
          </div>
        </div>

        <div className="card" style={{ padding: '1.5rem', display: 'grid', gap: '1.1rem' }}>
          <h3 style={{ fontSize: '1rem' }}>Preferences & schedule</h3>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <label>Weekly time commitment</label>
              <span className="mono" style={{ fontWeight: 600, color: 'var(--accent)' }}>{form.hours_per_week} hrs/week</span>
            </div>
            <input type="range" min={3} max={35} value={form.hours_per_week}
              onChange={(e) => set('hours_per_week', parseInt(e.target.value))} style={{ accentColor: 'var(--accent)', padding: 0 }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label>Preferred format</label>
              <select value={form.preferred_format} onChange={(e) => set('preferred_format', e.target.value)}>
                <option value="project-based">Project-based</option>
                <option value="video">Video courses</option>
                <option value="text">Reading / docs</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>
            <div>
              <label>Target timeline</label>
              <select value={form.target_timeline_months} onChange={(e) => set('target_timeline_months', parseInt(e.target.value))}>
                {[3, 6, 9, 12, 18, 24].map((m) => <option key={m} value={m}>{m} months</option>)}
              </select>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button className="btn-primary" type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save profile'}
          </button>
          {saved && <span className="badge badge-good"><Check size={13} /> Saved</span>}
        </div>
      </form>
    </div>
  );
}
