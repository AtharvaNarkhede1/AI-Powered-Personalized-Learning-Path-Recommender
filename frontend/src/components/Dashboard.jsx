import ProgressChart from "./ProgressChart.jsx";

// Progress dashboard: milestone completion stat tiles, skill-growth chart,
// and the "next recommended actions" list. Data comes from
// GET /api/progress/{learner_id} (progress_tracker.compute_progress).
export default function Dashboard({ progress }) {
  if (!progress) {
    return <p className="muted">Generate a learning path first to see your dashboard.</p>;
  }

  return (
    <div>
      <div className="stat-grid">
        <div className="stat-tile">
          <div className="value">{progress.completion_percent}%</div>
          <div className="label">Path completion</div>
        </div>
        <div className="stat-tile">
          <div className="value">{progress.completed_milestones}/{progress.total_milestones}</div>
          <div className="label">Milestones completed</div>
        </div>
        <div className="stat-tile">
          <div className="value">{Object.keys(progress.skill_growth || {}).length}</div>
          <div className="label">Skills in progress</div>
        </div>
      </div>

      <div className="card">
        <h3>Skill development</h3>
        <ProgressChart skillGrowth={progress.skill_growth} />
      </div>

      <div className="card">
        <h3>Next recommended actions</h3>
        <ul>
          {progress.next_actions.map((action, i) => (
            <li key={i}>{action}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
