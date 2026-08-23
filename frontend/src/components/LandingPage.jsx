import React from 'react';
import { ArrowRight, Compass, Target, ShieldAlert, Award, Clock, Cpu, CheckCircle2, Zap } from 'lucide-react';

export default function LandingPage({ onStartOnboarding, onDemoStart }) {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '3rem 1.5rem' }}>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', maxWidth: '850px', margin: '0 auto 4rem auto' }}>
        <div className="badge badge-indigo" style={{ marginBottom: '1.25rem', fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
          <Zap size={14} /> AI-Powered Gen-Z Engineering Career OS
        </div>
        
        <h1 style={{
          fontSize: '3.5rem',
          lineHeight: 1.15,
          letterSpacing: '-0.03em',
          marginBottom: '1.5rem',
          background: 'linear-gradient(135deg, #0F172A 0%, #334155 50%, #4F46E5 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Your career shouldn't be a guess.
        </h1>
        
        <p style={{
          fontSize: '1.25rem',
          color: '#475569',
          lineHeight: 1.6,
          marginBottom: '2.5rem',
          fontWeight: 400
        }}>
          Discover engineering careers that fit your true strengths, uncover exact skill gaps, avoid common career traps, and follow an explainable, prerequisite-aware roadmap.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <button className="btn-primary" style={{ fontSize: '1.05rem', padding: '0.9rem 2rem' }} onClick={onStartOnboarding}>
            Find My Career <ArrowRight size={18} />
          </button>
          <button className="btn-secondary" style={{ fontSize: '1.05rem', padding: '0.9rem 2rem' }} onClick={onDemoStart}>
            Explore Hackathon Demo Mode
          </button>
        </div>
      </div>

      {/* Feature Preview Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.75rem', marginBottom: '4rem' }}>
        {/* Card 1: Multi-Branch Discovery */}
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: '#EEF2FF',
            color: '#4F46E5',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1.25rem'
          }}>
            <Compass size={26} />
          </div>
          <h3 style={{ fontSize: '1.3rem', marginBottom: '0.75rem' }}>14 Branch Career Discovery</h3>
          <p style={{ color: '#64748B', lineHeight: 1.6, fontSize: '0.95rem' }}>
            Covers Computer Science, Robotics, ECE, Electrical, Mechanical, Civil, Chemical, Aerospace, and more. Calculates profile match % and cross-branch transition feasibility.
          </p>
        </div>

        {/* Card 2: Skill-Gap & DAG Roadmap */}
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: '#ECFDF5',
            color: '#10B981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1.25rem'
          }}>
            <Target size={26} />
          </div>
          <h3 style={{ fontSize: '1.3rem', marginBottom: '0.75rem' }}>Prerequisite DAG Roadmap</h3>
          <p style={{ color: '#64748B', lineHeight: 1.6, fontSize: '0.95rem' }}>
            Uses Directed Acyclic Graph (DAG) topological sorting to enforce prerequisite ordering before advanced topics, paired with realistic weekly calendar pacing.
          </p>
        </div>

        {/* Card 3: What NOT To Do */}
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: '#FEF3C7',
            color: '#D97706',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1.25rem'
          }}>
            <ShieldAlert size={26} />
          </div>
          <h3 style={{ fontSize: '1.3rem', marginBottom: '0.75rem' }}>Personalized "What NOT to Do"</h3>
          <p style={{ color: '#64748B', lineHeight: 1.6, fontSize: '0.95rem' }}>
            Protects engineering learners from certificate hoarding without projects, skipping math/logic prerequisites, or falling into hype-driven career traps.
          </p>
        </div>
      </div>

      {/* Differentiator Highlights Section */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: '20px',
        padding: '3rem 2.5rem',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)'
      }}>
        <h2 style={{ fontSize: '1.8rem', textAlign: 'center', marginBottom: '2rem' }}>
          Built differently for Gen-Z engineering learners
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <CheckCircle2 color="#10B981" size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '1.05rem', marginBottom: '0.35rem' }}>3-Way Career Comparison</h4>
              <p style={{ color: '#64748B', fontSize: '0.9rem' }}>Compare salaries, hard day-in-the-life realities, misconceptions, and job demand side-by-side.</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <CheckCircle2 color="#10B981" size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '1.05rem', marginBottom: '0.35rem' }}>Job Readiness Estimator</h4>
              <p style={{ color: '#64748B', fontSize: '0.9rem' }}>Calculate exact study hours and estimated months needed given your weekly available time.</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <CheckCircle2 color="#10B981" size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '1.05rem', marginBottom: '0.35rem' }}>Dual-Mode AI & RAG Fallback</h4>
              <p style={{ color: '#64748B', fontSize: '0.9rem' }}>Operates with Gemini or OpenAI API keys, or runs 100% offline out-of-the-box using grounded semantic heuristics.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
