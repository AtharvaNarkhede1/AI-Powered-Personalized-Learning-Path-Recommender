/**
 * API client for the FastAPI backend. Attaches the JWT (if present) to every
 * request; a 401 dispatches a global "auth:logout" event.
 */
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') + '/api';

let authToken = null;
export function setAuthToken(token) {
  authToken = token || null;
}

// Endpoints where a 401 means "bad credentials", NOT "expired session" --
// these run before the user has a token, so they must never trigger a logout.
const AUTH_ENDPOINTS = ['/auth/login', '/auth/register'];

async function fetchJSON(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  const res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const isAuthCall = AUTH_ENDPOINTS.some((e) => endpoint.startsWith(e));

    // Only a 401 on an authenticated request means the session is gone.
    if (res.status === 401 && !isAuthCall) {
      window.dispatchEvent(new CustomEvent('auth:logout'));
      throw new Error('Session expired. Please sign in again.');
    }
    if (res.status === 503) {
      throw new Error(err.detail || 'Service temporarily unavailable. Please try again shortly.');
    }
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

const body = (data) => ({ method: 'POST', body: JSON.stringify(data) });

export const api = {
  // Auth
  register: (data) => fetchJSON('/auth/register', body(data)),
  login: (data) => fetchJSON('/auth/login', body(data)),
  me: () => fetchJSON('/auth/me'),

  // Profile
  getProfile: () => fetchJSON('/onboarding/profile'),
  saveProfile: (profile) => fetchJSON('/onboarding/profile', body(profile)),
  searchKeywords: (q) => fetchJSON(`/onboarding/keywords/search?q=${encodeURIComponent(q)}`),
  parseResume: (text, exclude = []) => fetchJSON('/onboarding/parse-resume', body({ text, exclude })),
  parseIntake: (text, excludeSkills = [], excludeInterests = []) =>
    fetchJSON('/onboarding/parse-intake', body({ text, exclude_skills: excludeSkills, exclude_interests: excludeInterests })),

  // Careers
  discoverCareers: (profile) => fetchJSON('/careers/discover', body(profile)),
  getCareerDetail: (id) => fetchJSON(`/careers/detail/${id}`),
  compareCareers: (ids) => fetchJSON('/careers/compare', body({ career_ids: ids })),

  // Skills
  analyzeSkillGaps: (careerId, profile) => fetchJSON(`/skills/analyze-gap/${careerId}`, body(profile)),

  // Recommendations
  getCourseRecommendations: ({ goalText = null, careerId = null, limit = 12 }) =>
    fetchJSON('/recommendations/resources', body({ goal_text: goalText, career_id: careerId, limit })),
  getLearnerModel: () => fetchJSON('/recommendations/model'),

  // Learning path
  generatePath: (careerId, profile) => fetchJSON(`/paths/generate/${careerId}`, body(profile)),
  regeneratePath: (careerId) => fetchJSON(`/paths/regenerate/${careerId}`, { method: 'POST' }),
  toggleResource: (careerId, resourceId) =>
    fetchJSON(`/paths/progress/${careerId}/resource/${resourceId}/toggle`, { method: 'POST' }),
  toggleMilestone: (careerId, milestoneKey) =>
    fetchJSON(`/paths/progress/${careerId}/milestone/${milestoneKey}/toggle`, { method: 'POST' }),
  addCourseToPath: (careerId, courseId, milestoneKey = null) =>
    fetchJSON(`/paths/courses/${careerId}/add`, body({ course_id: courseId, milestone_key: milestoneKey })),
  removeCourseFromPath: (careerId, resourceId, milestoneKey) =>
    fetchJSON(`/paths/courses/${careerId}/remove`, body({ resource_id: resourceId, milestone_key: milestoneKey })),
  getPathExplanation: (careerId) => fetchJSON(`/paths/explanation/${careerId}`),

  // Quizzes
  getQuiz: (skillId) => fetchJSON(`/assessments/quiz/${skillId}`),
  getCourseQuiz: (courseId) => fetchJSON(`/assessments/course-quiz/${courseId}`),
  submitQuiz: (assessmentId, answers, careerId = null, courseId = null) =>
    fetchJSON('/assessments/submit', body({ assessment_id: assessmentId, answers, career_id: careerId, course_id: courseId })),

  // Assistant
  sendChatMessage: (message, contextCareerId = null) =>
    fetchJSON('/assistant/chat', body({ message, context_career_id: contextCareerId })),

  // Analytics
  getDashboardMetrics: (careerId = null) =>
    fetchJSON(`/analytics/dashboard${careerId ? `?target_career_id=${encodeURIComponent(careerId)}` : ''}`, { method: 'POST' }),
};
