export default function RecommendationCard({ rec }) {
  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>{rec.title}</h3>
      <p className="muted" style={{ margin: "0 0 8px" }}>
        {rec.provider} - {rec.difficulty} - ~{rec.estimated_hours}h
      </p>
      <div style={{ marginBottom: 8 }}>
        {rec.skill_tags.map((tag) => (
          <span className="tag" key={tag}>{tag}</span>
        ))}
      </div>
      <p style={{ fontSize: 14 }}>
        <strong>Why this: </strong>
        {rec.reason}
      </p>
    </div>
  );
}
