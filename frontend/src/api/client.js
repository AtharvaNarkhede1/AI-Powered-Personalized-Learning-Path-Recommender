/**
 * API Client for interacting with FastAPI Backend endpoints.
 */
const BASE_URL = 'http://127.0.0.1:8000/api';

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

  // Recommendations & Feedback
  getRecommendations: (profileData, filters = {}) =>
    fetchJSON('/recommendations/resources', {
      method: 'POST',
      body: JSON.stringify({ ...filters, ...profileData })
    }),
  submitFeedback: (resourceId, feedbackType, comment = '') =>
    fetchJSON('/recommendations/feedback', {
      method: 'POST',
      body: JSON.stringify({ resource_id: resourceId, feedback_type: feedbackType, comment })
    }),

  // Learning Path
  generatePath: (careerId, profileData) =>
    fetchJSON(`/paths/generate/${careerId}`, { method: 'POST', body: JSON.stringify(profileData) }),
  completeMilestone: (careerId, milestoneId, profileData) =>
    fetchJSON(`/paths/milestone/${careerId}/complete/${milestoneId}`, { method: 'POST', body: JSON.stringify(profileData) }),

  // Quizzes & Assessments
  getQuiz: (skillId) => fetchJSON(`/assessments/quiz/${skillId}`),
  submitQuiz: (assessmentId, answers) =>
    fetchJSON('/assessments/submit', { method: 'POST', body: JSON.stringify({ assessment_id: assessmentId, answers }) }),

  // Assistant & Chat
  sendChatMessage: (message, contextCareerId = null) =>
    fetchJSON('/assistant/chat', { method: 'POST', body: JSON.stringify({ message, context_career_id: contextCareerId }) }),

  // Analytics & System
  getDashboardMetrics: (profileData, targetCareerId = 'robotics_eng') =>
    fetchJSON('/analytics/dashboard', { method: 'POST', body: JSON.stringify(profileData) }),
  getSystemStatus: () => fetchJSON('/system/status'),
  configureKeys: (geminiKey, openaiKey) =>
    fetchJSON('/system/keys', { method: 'POST', body: JSON.stringify({ gemini_api_key: geminiKey, openai_api_key: openaiKey }) })
};
