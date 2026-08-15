// Thin wrapper around the Career PathFinder backend REST API.
// Base URL comes from VITE_API_BASE_URL (see .env.example); defaults to the
// local backend dev server so `npm run dev` works with zero config.
//
// TODO: add error toasts / centralized error handling once the UI has a
// notification system; right now callers must catch rejected promises.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export const api = {
  getProfile: (learnerId) => request(`/api/profile/${learnerId}`),
  updateProfile: (learnerId, data) =>
    request(`/api/profile/${learnerId}`, { method: "PUT", body: JSON.stringify(data) }),

  sendChatMessage: (learnerId, message) =>
    request(`/api/chat`, { method: "POST", body: JSON.stringify({ learner_id: learnerId, message }) }),

  getRecommendations: (learnerId) => request(`/api/recommend/${learnerId}`),
  explainRecommendation: (learnerId, courseId) =>
    request(`/api/recommend/${learnerId}/explain`, {
      method: "POST",
      body: JSON.stringify({ learner_id: learnerId, course_id: courseId }),
    }),
  askAssistant: (learnerId, question) =>
    request(`/api/recommend/${learnerId}/ask`, {
      method: "POST",
      body: JSON.stringify({ learner_id: learnerId, question }),
    }),

  generatePath: (learnerId) => request(`/api/path/${learnerId}/generate`, { method: "POST" }),
  getPath: (learnerId) => request(`/api/path/${learnerId}`),

  getProgress: (learnerId) => request(`/api/progress/${learnerId}`),
  updateMilestoneStatus: (learnerId, milestoneId, status) =>
    request(`/api/progress/${learnerId}`, {
      method: "PUT",
      body: JSON.stringify({ learner_id: learnerId, milestone_id: milestoneId, status }),
    }),
};
