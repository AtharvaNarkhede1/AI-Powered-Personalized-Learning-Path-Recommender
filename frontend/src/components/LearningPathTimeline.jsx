const STATUS_LABEL = {
  not_started: "Not started",
  in_progress: "In progress",
  completed: "Completed",
};

// Renders milestones in order with prerequisite chips and a status control,
// used by pages/PathPage.jsx. Status changes call PUT /api/progress/{id}.
export default function LearningPathTimeline({ path, onStatusChange }) {
  if (!path) return null;

  return (
    <div className="card">
      <h3>Roadmap toward: {path.goal}</h3>
      <p className="muted">Total estimated effort: {path.total_estimated_hours} hours</p>

      {path.milestones.map((m) => (
        <div key={m.milestone_id} className={`milestone ${m.status === "completed" ? "completed" : ""}`}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <strong>{m.title}</strong>
            <span className={`status-pill ${m.status}`}>{STATUS_LABEL[m.status]}</span>
          </div>
          {m.prerequisites?.length > 0 && (
            <p className="muted" style={{ margin: "4px 0" }}>
              Prerequisites: {m.prerequisites.join(", ")}
            </p>
          )}
          {m.assessment && <p className="muted" style={{ margin: "4px 0" }}>Assessment: {m.assessment}</p>}
          <select
            value={m.status}
            onChange={(e) => onStatusChange(m.milestone_id, e.target.value)}
            style={{ width: "auto", marginTop: 6 }}
          >
            <option value="not_started">Not started</option>
            <option value="in_progress">In progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      ))}
    </div>
  );
}
