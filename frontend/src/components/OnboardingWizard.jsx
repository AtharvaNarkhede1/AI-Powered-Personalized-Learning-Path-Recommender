import React, { useState, useEffect } from 'react';
import { Check, ArrowRight, ArrowLeft, Plus, X, Search } from 'lucide-react';
import { api } from '../api/client';

const BRANCHES = [
  "Computer Engineering / IT",
  "Electronics & Communication Engineering",
  "Electrical Engineering",
  "Mechanical Engineering",
  "Civil Engineering",
  "Chemical Engineering",
  "Aerospace Engineering",
  "Biomedical Engineering",
  "Instrumentation & Control",
  "Industrial / Production Engineering",
  "Automobile Engineering",
  "Robotics / Mechatronics",
  "Environmental Engineering",
  "Materials / Metallurgy"
];

export default function OnboardingWizard({ initialProfile, onComplete }) {
  const [step, setStep] = useState(1);
  const [profile, setProfile] = useState(initialProfile || {
    user_status: "Engineering Student",
    engineering_branch: "Mechanical Engineering",
    college_name: "HCL Institute of Technology",
    current_year: "3rd Year",
    graduation_year: 2026,
    interests: ["Robotics", "Artificial Intelligence", "Embedded Systems"],
    career_goal_status: "I have 2-3 careers in mind",
    known_skills: ["Python", "SolidWorks", "Basic Electronics"],
    experience_level: "Intermediate",
    hours_per_week: 10,
    preferred_format: "project-based",
    learning_style: "practical",
    max_budget: "free-and-paid",
    target_timeline_months: 6
  });

  // Autocomplete state
  const [interestInput, setInterestInput] = useState('');
  const [interestSuggestions, setInterestSuggestions] = useState([]);
  const [skillInput, setSkillInput] = useState('');
  const [skillSuggestions, setSkillSuggestions] = useState([]);

  // Fetch predictive interest suggestions
  useEffect(() => {
    let active = true;
    async function fetchInterestSuggestions() {
      try {
        const res = await api.searchKeywords(interestInput);
        if (active) setInterestSuggestions(res || []);
      } catch (err) {
        console.error(err);
      }
    }
    fetchInterestSuggestions();
    return () => { active = false; };
  }, [interestInput]);

  // Fetch predictive skill suggestions
  useEffect(() => {
    let active = true;
    async function fetchSkillSuggestions() {
      try {
        const res = await api.searchKeywords(skillInput);
        if (active) setSkillSuggestions(res || []);
      } catch (err) {
        console.error(err);
      }
    }
    fetchSkillSuggestions();
    return () => { active = false; };
  }, [skillInput]);

  const addInterest = (item) => {
    const clean = item.trim();
    if (!clean || profile.interests.includes(clean)) return;
    setProfile({ ...profile, interests: [...profile.interests, clean] });
    setInterestInput('');
  };

  const removeInterest = (item) => {
    setProfile({ ...profile, interests: profile.interests.filter(i => i !== item) });
  };

  const addSkill = (item) => {
    const clean = item.trim();
    if (!clean || profile.known_skills.includes(clean)) return;
    setProfile({ ...profile, known_skills: [...profile.known_skills, clean] });
    setSkillInput('');
  };

  const removeSkill = (item) => {
    setProfile({ ...profile, known_skills: profile.known_skills.filter(s => s !== item) });
  };

  const handleNext = () => {
    if (step < 5) {
      setStep(step + 1);
    } else {
      onComplete(profile);
    }
  };

  const handlePrev = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '0 1rem' }}>
      {/* Progress Header */}
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>Personalize Your Career Journey</h2>
        <p style={{ color: '#64748B' }}>Step {step} of 5 — {getStepTitle(step)}</p>

        {/* Step Progress Bar */}
        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem' }}>
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              style={{
                flex: 1,
                height: '6px',
                borderRadius: '999px',
                background: s <= step ? '#4F46E5' : '#E2E8F0',
                transition: 'all 0.3s ease'
              }}
            />
          ))}
        </div>
      </div>

      {/* Step Content Container */}
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        {step === 1 && (
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>What is your current academic/career status?</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {["Engineering Student", "Recent Graduate", "Working Professional", "Career Switcher"].map((st) => (
                <div
                  key={st}
                  onClick={() => setProfile({ ...profile, user_status: st })}
                  style={{
                    padding: '1.25rem',
                    borderRadius: '12px',
                    border: profile.user_status === st ? '2px solid #4F46E5' : '1px solid #E2E8F0',
                    background: profile.user_status === st ? '#EEF2FF' : '#FFFFFF',
                    cursor: 'pointer',
                    fontWeight: 600,
                    color: profile.user_status === st ? '#4F46E5' : '#0F172A'
                  }}
                >
                  {st}
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Educational Background</h3>
            <div style={{ display: 'grid', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem', fontSize: '0.9rem' }}>Engineering Branch</label>
                <select
                  value={profile.engineering_branch}
                  onChange={(e) => setProfile({ ...profile, engineering_branch: e.target.value })}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.95rem' }}
                >
                  {BRANCHES.map(b => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem', fontSize: '0.9rem' }}>Current Academic Year</label>
                  <select
                    value={profile.current_year}
                    onChange={(e) => setProfile({ ...profile, current_year: e.target.value })}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.95rem' }}
                  >
                    {["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"].map(y => <option key={y} value={y}>{y}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem', fontSize: '0.9rem' }}>Expected Graduation Year</label>
                  <input
                    type="number"
                    value={profile.graduation_year}
                    onChange={(e) => setProfile({ ...profile, graduation_year: parseInt(e.target.value) || 2026 })}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.95rem' }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Predictive Autocomplete & Custom Technical Interests */}
        {step === 3 && (
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Areas of Technical Interest</h3>
            <p style={{ color: '#64748B', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Type any custom technical interest or pick from predictive suggestions across 14 engineering branches.
            </p>

            {/* Selected Tags Chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {profile.interests.map((item) => (
                <span
                  key={item}
                  style={{
                    background: '#EEF2FF',
                    border: '1px solid #C7D2FE',
                    color: '#4F46E5',
                    padding: '0.4rem 0.85rem',
                    borderRadius: '999px',
                    fontWeight: 600,
                    fontSize: '0.85rem',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  {item}
                  <button onClick={() => removeInterest(item)} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex' }}>
                    <X size={14} color="#4F46E5" />
                  </button>
                </span>
              ))}
            </div>

            {/* Search Input Box */}
            <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                  <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                  <input
                    type="text"
                    value={interestInput}
                    onChange={(e) => setInterestInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addInterest(interestInput)}
                    placeholder="Type to search or add custom interest (e.g. Autonomous Drones, Quantum ML)..."
                    style={{ width: '100%', padding: '0.75rem 0.75rem 0.75rem 2.25rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.9rem' }}
                  />
                </div>
                <button className="btn-primary" onClick={() => addInterest(interestInput)}>
                  <Plus size={16} /> Add Tag
                </button>
              </div>

              {/* Autocomplete Dropdown List */}
              {interestInput.trim() && interestSuggestions.length > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  background: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
                  zIndex: 20,
                  maxHeight: '200px',
                  overflowY: 'auto',
                  marginTop: '4px'
                }}>
                  {interestSuggestions.map((sug, idx) => (
                    <div
                      key={idx}
                      onClick={() => addInterest(sug)}
                      style={{
                        padding: '0.75rem 1rem',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        borderBottom: '1px solid #F1F5F9',
                        color: '#334155'
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#F8FAFC'}
                      onMouseLeave={(e) => e.target.style.background = '#FFFFFF'}
                    >
                      + {sug}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 4: Predictive Autocomplete & Custom Known Skills */}
        {step === 4 && (
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Skills & Experience Level</h3>
            <p style={{ color: '#64748B', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              Search or add any software tool, programming language, or hardware skill you know.
            </p>

            {/* Selected Skill Chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {profile.known_skills.map((sk) => (
                <span
                  key={sk}
                  style={{
                    background: '#ECFDF5',
                    border: '1px solid #A7F3D0',
                    color: '#047857',
                    padding: '0.4rem 0.85rem',
                    borderRadius: '8px',
                    fontWeight: 600,
                    fontSize: '0.85rem',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  {sk}
                  <button onClick={() => removeSkill(sk)} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex' }}>
                    <X size={14} color="#047857" />
                  </button>
                </span>
              ))}
            </div>

            {/* Skill Search Input */}
            <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                  <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addSkill(skillInput)}
                    placeholder="Search or add custom skill (e.g. PyTorch, Rust, ROS 2, ANSYS)..."
                    style={{ width: '100%', padding: '0.75rem 0.75rem 0.75rem 2.25rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.9rem' }}
                  />
                </div>
                <button className="btn-primary" onClick={() => addSkill(skillInput)}>
                  <Plus size={16} /> Add Skill
                </button>
              </div>

              {/* Skill Dropdown Suggestions */}
              {skillInput.trim() && skillSuggestions.length > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  background: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
                  zIndex: 20,
                  maxHeight: '200px',
                  overflowY: 'auto',
                  marginTop: '4px'
                }}>
                  {skillSuggestions.map((sug, idx) => (
                    <div
                      key={idx}
                      onClick={() => addSkill(sug)}
                      style={{
                        padding: '0.75rem 1rem',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        borderBottom: '1px solid #F1F5F9',
                        color: '#334155'
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#F8FAFC'}
                      onMouseLeave={(e) => e.target.style.background = '#FFFFFF'}
                    >
                      + {sug}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem', fontSize: '0.9rem' }}>Overall Skill Baseline</label>
              <select
                value={profile.experience_level}
                onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.95rem' }}
              >
                <option value="Beginner">Beginner (Starting fresh with fundamentals)</option>
                <option value="Intermediate">Intermediate (Comfortable with programming & basic math)</option>
                <option value="Advanced">Advanced (Built projects & familiar with systems)</option>
              </select>
            </div>
          </div>
        )}

        {step === 5 && (
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Learning Preferences & Schedule</h3>
            <div style={{ display: 'grid', gap: '1.5rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <label style={{ fontWeight: 600, fontSize: '0.9rem' }}>Available Time Commitment</label>
                  <span style={{ fontWeight: 700, color: '#4F46E5' }}>{profile.hours_per_week} hours / week</span>
                </div>
                <input
                  type="range"
                  min={3}
                  max={35}
                  value={profile.hours_per_week}
                  onChange={(e) => setProfile({ ...profile, hours_per_week: parseInt(e.target.value) })}
                  style={{ width: '100%', accentColor: '#4F46E5' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem', fontSize: '0.9rem' }}>Preferred Learning Format</label>
                <select
                  value={profile.preferred_format}
                  onChange={(e) => setProfile({ ...profile, preferred_format: e.target.value })}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '0.95rem' }}
                >
                  <option value="project-based">Project-based (Learn by building working code/hardware)</option>
                  <option value="video">Video Lectures & Structured Courses</option>
                  <option value="text">Interactive Documentation & Tutorials</option>
                  <option value="mixed">Balanced Mixed Format</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Wizard Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2.5rem', paddingTop: '1.5rem', borderTop: '1px solid #E2E8F0' }}>
          <button
            className="btn-secondary"
            onClick={handlePrev}
            disabled={step === 1}
            style={{ opacity: step === 1 ? 0.5 : 1, cursor: step === 1 ? 'not-allowed' : 'pointer' }}
          >
            <ArrowLeft size={16} /> Back
          </button>

          <button className="btn-primary" onClick={handleNext}>
            {step === 5 ? 'Analyze Career Matches' : 'Next Step'} <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

function getStepTitle(step) {
  switch (step) {
    case 1: return "Current Status";
    case 2: return "Branch & Education";
    case 3: return "Interests & Goals";
    case 4: return "Skills & Baseline";
    case 5: return "Pacing & Preferences";
    default: return "";
  }
}
