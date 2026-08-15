import { useState } from "react";
import ChatInterface from "../components/ChatInterface.jsx";

// Full-page conversational interface. Profile updates extracted from chat
// are silently persisted server-side (see ChatInterface -> POST /api/chat);
// this page just nudges the learner to check their updated profile/path.
export default function ChatPage({ learnerId }) {
  const [updated, setUpdated] = useState(false);

  return (
    <div>
      <h2>Chat with your Learning Assistant</h2>
      <ChatInterface learnerId={learnerId} onProfileUpdated={() => setUpdated(true)} />
      {updated && (
        <p className="muted">
          Your profile was updated from this conversation - visit the Home page or Learning Path tab to
          see refreshed recommendations.
        </p>
      )}
    </div>
  );
}
