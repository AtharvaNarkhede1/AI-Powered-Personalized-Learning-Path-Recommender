import { useState } from "react";

// Structured form counterpart to the chat-based profiling flow (see
// ChatInterface.jsx). Both write to the same LearnerProfile via the
// profiling engine's PUT /api/profile/{id} endpoint.
export default function ProfileForm({ profile, onSave }) {
  const [form, setForm] = useState({
    name: profile?.name || "",
    goal: profile?.goal || "",
    skill_level: profile?.skill_level || "beginner",
    interests: (profile?.interests || []).join(", "),
    hours_per_week: profile?.hours_per_week || 5,
  });

  function handleSubmit(e) {
    e.preventDefault();
    onSave({
      name: form.name,
      goal: form.goal,
      skill_level: form.skill_level,
      interests: form.interests.split(",").map((s) => s.trim()).filter(Boolean),
      hours_per_week: Number(form.hours_per_week),
    });
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>Your Learner Profile</h3>
      <label>Name</label>
      <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />

      <label style={{ display: "block", marginTop: 10 }}>Goal (e.g. "become a data scientist")</label>
      <input value={form.goal} onChange={(e) => setForm({ ...form, goal: e.target.value })} />

      <label style={{ display: "block", marginTop: 10 }}>Skill level</label>
      <select value={form.skill_level} onChange={(e) => setForm({ ...form, skill_level: e.target.value })}>
        <option value="beginner">Beginner</option>
        <option value="intermediate">Intermediate</option>
        <option value="advanced">Advanced</option>
      </select>

      <label style={{ display: "block", marginTop: 10 }}>Interests (comma separated)</label>
      <input value={form.interests} onChange={(e) => setForm({ ...form, interests: e.target.value })} />

      <label style={{ display: "block", marginTop: 10 }}>Hours per week</label>
      <input
        type="number"
        min="1"
        max="40"
        value={form.hours_per_week}
        onChange={(e) => setForm({ ...form, hours_per_week: e.target.value })}
      />

      <button className="btn" type="submit" style={{ marginTop: 14 }}>
        Save Profile
      </button>
    </form>
  );
}
