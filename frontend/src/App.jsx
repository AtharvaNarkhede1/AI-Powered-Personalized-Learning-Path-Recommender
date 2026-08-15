import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import PathPage from "./pages/PathPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";

// Prototype-level "auth": a single learner id persisted in localStorage.
// TODO: replace with real auth (sign-up/login) before this leaves prototype
// stage; every service call is scoped by learner_id today.
function getOrCreateLearnerId() {
  let id = localStorage.getItem("learner_id");
  if (!id) {
    id = "learner-" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem("learner_id", id);
  }
  return id;
}

export default function App() {
  const learnerId = getOrCreateLearnerId();

  return (
    <div className="app-shell">
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home learnerId={learnerId} />} />
          <Route path="/chat" element={<ChatPage learnerId={learnerId} />} />
          <Route path="/path" element={<PathPage learnerId={learnerId} />} />
          <Route path="/dashboard" element={<DashboardPage learnerId={learnerId} />} />
        </Routes>
      </main>
    </div>
  );
}
