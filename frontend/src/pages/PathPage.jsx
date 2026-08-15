import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import LearningPathTimeline from "../components/LearningPathTimeline.jsx";

// Learning path generator page: (re)generate a roadmap from the current
// profile, mark milestones' progress, and ask the assistant "why" questions
// about individual recommendations.
export default function PathPage({ learnerId }) {
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  async function loadPath() {
    try {
      const p = await api.getPath(learnerId);
      setPath(p);
    } catch {
      setPath(null);
    }
  }

  useEffect(() => {
    loadPath();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleGenerate() {
    setLoading(true);
    try {
      const p = await api.generatePath(learnerId);
      setPath(p);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusChange(milestoneId, status) {
    await api.updateMilestoneStatus(learnerId, milestoneId, status);
    await loadPath();
  }

  async function handleAsk(e) {
    e.preventDefault();
    if (!question.trim()) return;
    const res = await api.askAssistant(learnerId, question);
    setAnswer(res.answer);
  }

  return (
    <div>
      <div className="card">
        <h2>Your Learning Path</h2>
        <p className="muted">
          Generated from your profile: goal, interests, skill level, and completed courses. Complete your
          profile via Chat or the Home page first for the best results.
        </p>
        <button className="btn" onClick={handleGenerate} disabled={loading}>
          {loading ? "Generating..." : path ? "Regenerate Path" : "Generate Path"}
        </button>
      </div>

      <LearningPathTimeline path={path} onStatusChange={handleStatusChange} />

      <div className="card">
        <h3>Ask the assistant</h3>
        <form onSubmit={handleAsk} style={{ display: "flex", gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder='e.g. "why this course?" or "how long will this take?"'
          />
          <button className="btn" type="submit">Ask</button>
        </form>
        {answer && <p style={{ marginTop: 12 }}>{answer}</p>}
      </div>
    </div>
  );
}
