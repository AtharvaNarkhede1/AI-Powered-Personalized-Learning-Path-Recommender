import { useState, useRef, useEffect } from "react";
import { api } from "../api/client.js";

// Conversational front door: learner describes goals/interests in natural
// language; each message is sent to POST /api/chat, which both updates the
// LearnerProfile (via profiling_engine's extraction) and returns a reply.
export default function ChatInterface({ learnerId, onProfileUpdated }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! Tell me about your learning goals - for example, \"I want to become a data scientist, I'm a beginner with Python.\"",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.sendChatMessage(learnerId, userMessage.content);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
      if (Object.keys(res.extracted_profile_updates || {}).length > 0) {
        onProfileUpdated?.();
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Sorry, something went wrong: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3>Learning Assistant</h3>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.content}
          </div>
        ))}
        <div ref={endRef} />
      </div>
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your goals, interests, or ask a question..."
          disabled={loading}
        />
        <button className="btn" type="submit" disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}
