import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import Dashboard from "../components/Dashboard.jsx";

export default function DashboardPage({ learnerId }) {
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    api.getProgress(learnerId).then(setProgress).catch(() => setProgress(null));
  }, [learnerId]);

  return (
    <div>
      <h2>Progress Dashboard</h2>
      <Dashboard progress={progress} />
    </div>
  );
}
