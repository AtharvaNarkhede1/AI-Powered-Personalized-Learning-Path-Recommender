/**
 * API Client for interacting with FastAPI Backend endpoints.
 */
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') + '/api';

async function fetchJSON(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Auth
  demoLogin: () => fetchJSON('/auth/demo-login', { method: 'POST' }),
  login: (email, password) => fetchJSON('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  
  // Onboarding & Profile
  saveOnboardingProfile: (userId, profileData) =>
    fetchJSON(`/onboarding/${userId}`, { method: 'POST', body: JSON.stringify(profileData) }),
  getOnboardingProfile: (userId) => fetchJSON(`/onboarding/${userId}`),
  searchKeywords: (query) => fetchJSON(`/onboarding/keywords/search?q=${encodeURIComponent(query)}`),

  // Careers & Discovery
  discoverCareers: (profileData) =>
    fetchJSON('/careers/discover', { method: 'POST', body: JSON.stringify(profileData) }),
  getCareerDetail: (careerId) => fetchJSON(`/careers/detail/${careerId}`),
  compareCareers: (careerIds) =>
    fetchJSON('/careers/compare', { method: 'POST', body: JSON.stringify({ career_ids: careerIds }) }),
  getCareerCatalog: () => fetchJSON('/careers/catalog'),

  // Skills & Gaps
  analyzeSkillGaps: (careerId, profileData) =>
    fetchJSON(`/skills/analyze-gap/${careerId}`, { method: 'POST', body: JSON.stringify(profileData) }),

  // Course Recommendations & Feedback
  getCourseRecommendations: ({ userId, goalText = null, careerId = null, limit = 12, excludePlanned = false }) =>
    fetchJSON('/recommendations/resources', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, goal_text: goalText, career_id: careerId, limit, exclude_planned: excludePlanned })
    }),
  getLearnerModel: (userId) => fetchJSON(`/recommendations/model/${userId}`),
  submitFeedback: (resourceId, feedbackType, userId, comment = '') =>
    fetchJSON('/recommendations/feedback', {
      method: 'POST',
      body: JSON.stringify({ resource_id: resourceId, feedback_type: feedbackType, user_id: userId, comment })
    }),

  // Learning Path
  generatePath: (careerId, profileData) =>
    fetchJSON(`/paths/generate/${careerId}`, { method: 'POST', body: JSON.stringify(profileData) }),
  completeMilestone: (careerId, milestoneId, profileData) =>
    fetchJSON(`/paths/milestone/${careerId}/complete/${milestoneId}`, { method: 'POST', body: JSON.stringify(profileData) }),

  // Quizzes & Assessments
  getQuiz: (skillId) => fetchJSON(`/assessments/quiz/${skillId}`),
  submitQuiz: (assessmentId, answers, userId, careerId = null) =>
    fetchJSON('/assessments/submit', { method: 'POST', body: JSON.stringify({ assessment_id: assessmentId, answers, user_id: userId, career_id: careerId }) }),

  // Assistant & Chat
  sendChatMessage: (message, contextCareerId = null, userId) =>
    fetchJSON('/assistant/chat', { method: 'POST', body: JSON.stringify({ message, context_career_id: contextCareerId, user_id: userId }) }),

  // Analytics & System
  getDashboardMetrics: (profileData, targetCareerId = 'robotics_eng') =>
    fetchJSON(`/analytics/dashboard?target_career_id=${encodeURIComponent(targetCareerId)}`, { method: 'POST', body: JSON.stringify(profileData) }),
  getSystemStatus: () => fetchJSON('/system/status')
};
