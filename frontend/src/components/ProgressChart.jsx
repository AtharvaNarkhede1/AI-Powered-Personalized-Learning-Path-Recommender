import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// Skill growth chart: a single series (percent proficiency per skill), so it
// uses one categorical hue throughout rather than a color-per-bar scheme -
// identity here is carried by the axis label, not color. See dataviz skill
// (color-formula.md): single-series bar charts don't need a legend.
export default function ProgressChart({ skillGrowth }) {
  const data = Object.entries(skillGrowth || {})
    .map(([skill, value]) => ({ skill, value }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return <p className="muted">No skill progress yet - complete a milestone to see growth here.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 24, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--gridline)" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 12 }} unit="%" />
        <YAxis type="category" dataKey="skill" width={110} tick={{ fill: "var(--text-secondary)", fontSize: 12 }} />
        <Tooltip
          contentStyle={{ background: "var(--surface-1)", border: "1px solid var(--border)", borderRadius: 8 }}
          formatter={(value) => [`${value}%`, "Proficiency"]}
        />
        <Bar dataKey="value" fill="var(--series-1)" radius={[0, 4, 4, 0]} barSize={16} />
      </BarChart>
    </ResponsiveContainer>
  );
}
