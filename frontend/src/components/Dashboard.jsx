import React from 'react';
import { Award, Clock, BookOpen, CheckCircle2, TrendingUp, Zap, ChevronRight } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

export default function Dashboard({ metrics, onNavigate }) {
  if (!metrics) {
    return <div style={{ textAlign: 'center', padding: '4rem' }}>Loading dashboard metrics...</div>;
  }

  const {
    user_name, engineering_branch, target_career_title, job_readiness_pct,
    completed_milestones_count, total_milestones_count, hours_logged,
    estimated_total_hours, estimated_months_remaining, next_action, skill_radar_data
  } = metrics;

  return (
    <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Learner Overview: {user_name}</h2>
          <p style={{ color: '#64748B' }}>{engineering_branch} → Target Career: <strong>{target_career_title}</strong></p>
        </div>
        <button className="btn-primary" onClick={() => onNavigate('roadmap')}>
          Continue Roadmap <ChevronRight size={16} />
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            <span>JOB READINESS</span>
            <Award size={18} color="#10B981" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#10B981', lineHeight: 1 }}>
            {job_readiness_pct}%
          </div>
          <p style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.4rem' }}>Target benchmark: 80%+</p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            <span>STUDY TIME LOGGED</span>
            <Clock size={18} color="#4F46E5" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#4F46E5', lineHeight: 1 }}>
            {hours_logged} <span style={{ fontSize: '1rem', fontWeight: 600 }}>/ {estimated_total_hours} hrs</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.4rem' }}>Est. ~{estimated_months_remaining} months left</p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            <span>MILESTONES COMPLETED</span>
            <CheckCircle2 size={18} color="#8B5CF6" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#8B5CF6', lineHeight: 1 }}>
            {completed_milestones_count} <span style={{ fontSize: '1rem', fontWeight: 600 }}>/ {total_milestones_count}</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.4rem' }}>Prerequisite-aware phases</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
        <div className="glass-card" style={{ padding: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem' }}>Current vs Required Skill Proficiency</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={skill_radar_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="skill" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="current" name="Current Skill Level (%)" fill="#4F46E5" radius={[4, 4, 0, 0]} />
                <Bar dataKey="required" name="Required Target Level (%)" fill="#CBD5E1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div className="badge badge-indigo" style={{ marginBottom: '1rem' }}>Immediate Action Engine</div>
            <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>{next_action?.title || 'Continue Onboarding'}</h3>
            <p style={{ color: '#64748B', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              {next_action?.description || 'Follow your next step to advance your career readiness.'}
            </p>
          </div>

          <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => onNavigate('roadmap')}>
            Start Next Step <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
