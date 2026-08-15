import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import ProfileForm from "../components/ProfileForm.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";

// Landing page: profile form (learner profiling engine) + live
// recommendations preview (recommendation engine) + entry point into the
// chat-based flow and the full learning path.
export default function Home({ learnerId }) {
  const [profile, setProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const navigate = useNavigate();

  async function loadProfile() {
    const p = await api.getProfile(learnerId);
    setProfile(p);
    if (p.goal || p.interests.length > 0) {
      const rec = await api.getRecommendations(learnerId);
      setRecommendations(rec.recommendations);
    }
  }

  useEffect(() => {
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSave(update) {
    await api.updateProfile(learnerId, update);
    await loadProfile();
  }

  return (
    <div>
      <div className="card">
        <h2>Welcome to Career PathFinder</h2>
        <p className="muted">
          Describe your goals in the chat, or fill out your profile below. We'll turn it into a
          personalized, milestone-based learning roadmap with explanations for every recommendation.
        </p>
        <button className="btn" onClick={() => navigate("/chat")}>Start with Chat</button>
      </div>

      <ProfileForm profile={profile} onSave={handleSave} />

      {recommendations.length > 0 && (
        <div>
          <h3>Recommended for you</h3>
          {recommendations.map((rec) => (
            <RecommendationCard key={rec.course_id} rec={rec} />
          ))}
          <button className="btn" onClick={() => navigate("/path")}>Generate Full Learning Path</button>
        </div>
      )}
    </div>
  );
}
