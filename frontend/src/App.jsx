import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import OnboardingWizard from './components/OnboardingWizard';
import CareerDiscovery from './components/CareerDiscovery';
import LearningPathTimeline from './components/LearningPathTimeline';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import QuizModal from './components/QuizModal';
import SettingsModal from './components/SettingsModal';

import { api } from './api/client';
import './styles/index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('landing');
  const [userId, setUserId] = useState('demo_user_1');
  const [llmMode, setLlmMode] = useState('Offline Grounded Engine');

  // Core State
  const [profile, setProfile] = useState({
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

  const [discoveryData, setDiscoveryData] = useState(null);
  const [activePath, setActivePath] = useState(null);
  const [dashboardMetrics, setDashboardMetrics] = useState(null);
  
  // Modals
  const [quizSkillId, setQuizSkillId] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  // Initial demo load
  useEffect(() => {
    async function initSystem() {
      try {
        const sys = await api.getSystemStatus();
        setLlmMode(sys.active_llm_mode);
        
        // Auto-run discovery for initial profile
        const disc = await api.discoverCareers(profile);
        setDiscoveryData(disc);

        if (disc.top_matches && disc.top_matches.length > 0) {
          const topId = disc.top_matches[0].career_id;
          const pathRes = await api.generatePath(topId, profile);
          setActivePath(pathRes);
          
          const metrics = await api.getDashboardMetrics(profile, topId);
          setDashboardMetrics(metrics);
        }
      } catch (err) {
        console.error("System init error:", err);
      }
    }
    initSystem();
  }, []);

  // Handlers
  const handleStartOnboarding = () => {
    setActiveTab('onboarding');
  };

  const handleDemoStart = async () => {
    try {
      const authRes = await api.demoLogin();
      setUserId(authRes.user_id);
      
      const disc = await api.discoverCareers(profile);
      setDiscoveryData(disc);
      setActiveTab('discovery');
    } catch (err) {
      console.error(err);
    }
  };

  const handleCompleteOnboarding = async (newProfile) => {
    setProfile(newProfile);
    try {
      await api.saveOnboardingProfile(userId, newProfile);
      const disc = await api.discoverCareers(newProfile);
      setDiscoveryData(disc);
      setActiveTab('discovery');
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectCareer = async (careerId) => {
    try {
      const pathRes = await api.generatePath(careerId, profile);
      setActivePath(pathRes);
      
      const metrics = await api.getDashboardMetrics(profile, careerId);
      setDashboardMetrics(metrics);

      setActiveTab('roadmap');
    } catch (err) {
      console.error(err);
    }
  };

  const handleCompleteMilestone = async (careerId, milestoneId) => {
    try {
      const updatedPath = await api.completeMilestone(careerId, milestoneId, profile);
      setActivePath(updatedPath);
      
      const metrics = await api.getDashboardMetrics(profile, careerId);
      setDashboardMetrics(metrics);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#F8FAFC' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSettings={() => setShowSettings(true)}
        llmMode={llmMode}
      />

      <main style={{ flex: 1 }}>
        {activeTab === 'landing' && (
          <LandingPage
            onStartOnboarding={handleStartOnboarding}
            onDemoStart={handleDemoStart}
          />
        )}

        {activeTab === 'onboarding' && (
          <OnboardingWizard
            initialProfile={profile}
            onComplete={handleCompleteOnboarding}
          />
        )}

        {activeTab === 'discovery' && (
          <CareerDiscovery
            discoveryData={discoveryData}
            profile={profile}
            onSelectCareer={handleSelectCareer}
          />
        )}

        {activeTab === 'roadmap' && (
          <LearningPathTimeline
            path={activePath}
            profile={profile}
            onCompleteMilestone={handleCompleteMilestone}
            onOpenQuiz={(skillId) => setQuizSkillId(skillId)}
          />
        )}

        {activeTab === 'dashboard' && (
          <Dashboard
            metrics={dashboardMetrics}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === 'assistant' && (
          <ChatInterface
            activeCareerId={activePath?.career_id}
          />
        )}
      </main>

      {/* Diagnostic Quiz Modal */}
      {quizSkillId && (
        <QuizModal
          skillId={quizSkillId}
          onClose={() => setQuizSkillId(null)}
          onQuizCompleted={() => {
            if (activePath) {
              handleSelectCareer(activePath.career_id);
            }
          }}
        />
      )}

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          onClose={() => setShowSettings(false)}
          onKeysUpdated={(mode) => setLlmMode(mode)}
        />
      )}
    </div>
  );
}
